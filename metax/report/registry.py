from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class ResultRegistry:
    def __init__(self) -> None:
        self.tables: list[dict[str, Any]] = []
        self.stats: list[dict[str, Any]] = []
        self.figures: list[dict[str, Any]] = []
        self.html: list[dict[str, Any]] = []
        self.warnings: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self.runtime: dict[str, Any] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    def add_table(
        self,
        key: str,
        path: str | Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.tables.append(self._artifact(key, path, title, description))

    def add_stat(
        self,
        key: str,
        path: str | Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.stats.append(self._artifact(key, path, title, description))

    def add_figure(
        self,
        key: str,
        path: str | Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
        figure_type: Optional[str] = None,
        **metadata: Any,
    ) -> None:
        item = self._artifact(key, path, title, description)
        if figure_type:
            item["figure_type"] = figure_type
        item.update(metadata)
        self.figures.append(item)

    def add_html(
        self,
        key: str,
        path: str | Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.html.append(self._artifact(key, path, title, description))

    def add_warning(
        self,
        message: str,
        source: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        item: dict[str, Any] = {"message": message, "source": source}
        if details:
            item["details"] = details
        self.warnings.append(item)

    def add_error(self, message: str, source: Optional[str] = None) -> None:
        self.errors.append({"message": message, "source": source})

    def set_runtime(self, key: str, value: Any) -> None:
        self.runtime[key] = value

    def finish(self) -> None:
        self.runtime["finished_at"] = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "tables": self.tables,
            "stats": self.stats,
            "figures": self.figures,
            "html": self.html,
            "warnings": self.warnings,
            "errors": self.errors,
            "runtime": self.runtime,
        }

    def save_json(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)

    @staticmethod
    def _artifact(
        key: str,
        path: str | Path,
        title: Optional[str],
        description: Optional[str],
    ) -> dict[str, Any]:
        return {
            "key": key,
            "path": str(path),
            "title": title or key,
            "description": description,
        }
