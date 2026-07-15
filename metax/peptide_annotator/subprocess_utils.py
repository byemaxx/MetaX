from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from os import PathLike
from typing import Any


def _process_group_exists(process_group_id: int) -> bool:
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _wait_for_process_group_exit(
    process_group_id: int,
    timeout: float,
) -> bool:
    deadline = time.monotonic() + timeout
    while _process_group_exists(process_group_id):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(0.05, remaining))
    return True


def _terminate_posix_process_group(
    process: subprocess.Popen[Any],
    timeout: float,
) -> None:
    process_group_id = process.pid
    try:
        os.killpg(process_group_id, signal.SIGTERM)
    except ProcessLookupError:
        return

    deadline = time.monotonic() + timeout
    if process.poll() is None:
        try:
            process.wait(timeout=max(0.0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass

    if _wait_for_process_group_exit(
        process_group_id,
        max(0.0, deadline - time.monotonic()),
    ):
        return

    try:
        os.killpg(process_group_id, signal.SIGKILL)
    except ProcessLookupError:
        return
    if process.poll() is None:
        process.wait()
    _wait_for_process_group_exit(process_group_id, timeout)


def terminate_process(
    process: subprocess.Popen[Any],
    *,
    timeout: float = 5.0,
    process_group: bool = False,
) -> None:
    """Best-effort termination for an active child and its process group/tree."""
    if process_group:
        try:
            _terminate_posix_process_group(process, timeout)
        except OSError:
            if process.poll() is None:
                process.kill()
                process.wait()
        return

    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        else:
            process.terminate()
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    except OSError:
        if process.poll() is None:
            process.kill()
            process.wait()
        return


def run_streaming_subprocess(
    command: Sequence[str],
    *,
    cwd: str | PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
    creationflags: int = 0,
    max_captured_lines: int = 50,
    emit_line: Callable[[str], None] | None = None,
) -> tuple[int, list[str]]:
    """Run a command without a shell, stream output, and clean up on interruption."""
    process = subprocess.Popen(
        list(command),
        cwd=cwd,
        env=dict(env) if env is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        creationflags=creationflags,
        start_new_session=os.name != "nt",
    )
    captured: list[str] = []
    try:
        assert process.stdout is not None
        for line in process.stdout:
            if emit_line is not None:
                emit_line(line.rstrip("\n"))
            captured.append(line)
            if len(captured) > max_captured_lines:
                captured = captured[-max_captured_lines:]
        return process.wait(), captured
    except BaseException:
        terminate_process(process, process_group=os.name != "nt")
        raise
    finally:
        if process.stdout is not None:
            process.stdout.close()
