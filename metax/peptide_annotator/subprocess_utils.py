from __future__ import annotations

import os
import signal
import subprocess
from collections.abc import Callable, Mapping, Sequence
from os import PathLike
from typing import Any


def terminate_process(
    process: subprocess.Popen[Any],
    *,
    timeout: float = 5.0,
    process_group: bool = False,
) -> None:
    """Best-effort termination for an active child and its process group/tree."""
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
        elif process_group:
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name != "nt" and process_group:
            os.killpg(process.pid, signal.SIGKILL)
        else:
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
