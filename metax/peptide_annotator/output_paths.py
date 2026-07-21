from __future__ import annotations

from datetime import datetime
from pathlib import Path


def available_output_path(requested_path: str | Path) -> Path:
    """Return the requested path or a non-existing timestamped sibling.

    Scientific outputs are preserved when the requested target already exists.
    Stable automation files such as result JSON are handled separately and may
    intentionally use atomic replacement at their exact requested path.
    """
    requested = Path(requested_path)
    if not requested.exists():
        return requested

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    candidate = requested.with_name(f"{requested.stem}_{timestamp}{requested.suffix}")
    counter = 2
    while candidate.exists():
        candidate = requested.with_name(
            f"{requested.stem}_{timestamp}_{counter}{requested.suffix}"
        )
        counter += 1
    return candidate
