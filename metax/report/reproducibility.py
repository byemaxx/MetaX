from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from .config import AutoReportConfig, save_config_to_yaml


CONFIG_FILE_NAME = "config_used.yaml"
PYTHON_SCRIPT_NAME = "run_metax_report.py"
WINDOWS_SCRIPT_NAME = "run_metax_report.bat"


def save_reproducibility_artifacts(config: AutoReportConfig, output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    config_path = output_path / CONFIG_FILE_NAME
    python_script_path = output_path / PYTHON_SCRIPT_NAME
    windows_script_path = output_path / WINDOWS_SCRIPT_NAME

    save_config_to_yaml(config, config_path)
    python_script_path.write_text(_python_script_text(), encoding="utf-8")
    windows_script_path.write_text(_windows_script_text(), encoding="utf-8")

    return {
        "python_script": python_script_path,
        "windows_script": windows_script_path,
        "config": config_path,
    }


def _python_script_text() -> str:
    return dedent(
        f"""\
        from __future__ import annotations

        import argparse
        from pathlib import Path

        from metax.report.config import load_config_from_yaml
        from metax.report.workflow import AutoOTFReport


        DEFAULT_CONFIG = Path(__file__).resolve().with_name("{CONFIG_FILE_NAME}")


        def main() -> int:
            parser = argparse.ArgumentParser(description="Re-run the MetaX Auto OTF report saved by the GUI.")
            parser.add_argument(
                "--config",
                default=str(DEFAULT_CONFIG),
                help="Path to the saved MetaX report YAML config.",
            )
            parser.add_argument(
                "--out",
                help="Optional output directory override. Defaults to the directory saved in the config.",
            )
            args = parser.parse_args()

            config_path = Path(args.config).expanduser().resolve()
            config = load_config_from_yaml(config_path)
            if args.out:
                config.report.output_dir = args.out

            result = AutoOTFReport(config).run()
            print(result.index_html_path)
            return 0


        if __name__ == "__main__":
            raise SystemExit(main())
        """
    )


def _windows_script_text() -> str:
    return dedent(
        f"""\
        @echo off
        setlocal
        cd /d "%~dp0"
        if not "%METAX_PYTHON%"=="" (
            "%METAX_PYTHON%" "{PYTHON_SCRIPT_NAME}" %*
        ) else (
            python "{PYTHON_SCRIPT_NAME}" %*
        )
        """
    )
