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
