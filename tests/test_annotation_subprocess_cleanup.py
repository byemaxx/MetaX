from __future__ import annotations

import os

import pytest

import metax.peptide_annotator.subprocess_utils as subprocess_utils


class _InterruptingStdout:
    def __init__(self) -> None:
        self.closed = False

    def __iter__(self):
        return self

    def __next__(self):
        raise KeyboardInterrupt

    def close(self) -> None:
        self.closed = True


class _FakeProcess:
    pid = 12345

    def __init__(self) -> None:
        self.stdout = _InterruptingStdout()


class _ExitedProcess:
    pid = 12345

    def poll(self) -> int:
        return 0

    def wait(self, timeout=None):
        raise AssertionError("An exited process-group leader must not be waited on")


def test_streaming_subprocess_cleans_up_on_keyboard_interrupt(monkeypatch):
    process = _FakeProcess()
    cleanup_calls = []
    monkeypatch.setattr(
        subprocess_utils.subprocess,
        "Popen",
        lambda *_args, **_kwargs: process,
    )
    monkeypatch.setattr(
        subprocess_utils,
        "terminate_process",
        lambda active_process, **kwargs: cleanup_calls.append(
            (active_process, kwargs)
        ),
    )

    with pytest.raises(KeyboardInterrupt):
        subprocess_utils.run_streaming_subprocess(["fake", "command"])

    assert cleanup_calls == [
        (process, {"process_group": os.name != "nt"})
    ]
    assert process.stdout.closed is True


def test_terminate_process_signals_group_when_leader_has_exited(monkeypatch):
    process = _ExitedProcess()
    signals = []
    monkeypatch.setattr(
        subprocess_utils.os,
        "killpg",
        lambda process_group_id, sig: signals.append((process_group_id, sig)),
        raising=False,
    )
    monkeypatch.setattr(
        subprocess_utils,
        "_wait_for_process_group_exit",
        lambda _process_group_id, _timeout: True,
    )

    subprocess_utils.terminate_process(process, process_group=True)

    assert signals == [(process.pid, subprocess_utils.signal.SIGTERM)]


def test_terminate_process_escalates_when_group_ignores_sigterm(monkeypatch):
    process = _ExitedProcess()
    signals = []
    group_exit_checks = iter((False, True))
    sigkill = getattr(subprocess_utils.signal, "SIGKILL", 9)
    monkeypatch.setattr(
        subprocess_utils.signal,
        "SIGKILL",
        sigkill,
        raising=False,
    )
    monkeypatch.setattr(
        subprocess_utils.os,
        "killpg",
        lambda process_group_id, sig: signals.append((process_group_id, sig)),
        raising=False,
    )
    monkeypatch.setattr(
        subprocess_utils,
        "_wait_for_process_group_exit",
        lambda _process_group_id, _timeout: next(group_exit_checks),
    )

    subprocess_utils.terminate_process(process, process_group=True)

    assert signals == [
        (process.pid, subprocess_utils.signal.SIGTERM),
        (process.pid, sigkill),
    ]
