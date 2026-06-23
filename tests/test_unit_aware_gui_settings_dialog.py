from dataclasses import asdict
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import metax.gui.unit_aware_settings_dialog as unit_aware_settings_dialog
import pandas as pd
import pytest
from PyQt5 import QtWidgets
from metax.gui.main_gui import MetaXGUI
from metax.gui.unit_aware_settings_dialog import (
    UnitAwareGuiConfig,
    UnitAwareSettingsDialog,
    UnitAwareValidationResultDialog,
    validate_unit_aware_manifest_for_gui,
)


def _write_manifest(tmp_path):
    path = tmp_path / "unit_aware_manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "metaumbra.unit_aware_manifest.v1",
                "generated_by": {"tool": "MetaUmbra", "version": "1.3.5"},
                "default_genome_threshold": "q0.05",
                "files": {},
                "units": {
                    "u1": {
                        "sample_columns": ["s1", "s2"],
                        "n_samples": 2,
                        "genome_ids_q005": ["g1", "g2"],
                        "genome_ids_q001": ["g1"],
                    },
                    "u2": {
                        "sample_columns": ["s3"],
                        "n_samples": 1,
                        "genome_ids_q005": ["g3"],
                        "genome_ids_q001": ["g3"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_peptide_table(tmp_path, columns):
    path = tmp_path / "peptides.tsv"
    path.write_text("\t".join(columns) + "\n", encoding="utf-8")
    return path


def test_unit_aware_gui_config_defaults_and_override():
    default = UnitAwareGuiConfig()
    assert asdict(default) == {
        "manifest_path": "",
        "genome_threshold": "auto",
        "input_sample_col_prefix": "",
        "on_missing_sample": "error",
        "on_empty_unit": "warn-skip",
        "save_per_unit_outputs": False,
        "n_jobs": None,
    }

    config = UnitAwareGuiConfig(
        manifest_path="unit_aware_manifest.json",
        genome_threshold="q0.01",
        input_sample_col_prefix="LFQ intensity ",
        on_missing_sample="warn-skip",
        on_empty_unit="error",
        save_per_unit_outputs=True,
        n_jobs=4,
    )

    assert config.manifest_path == "unit_aware_manifest.json"
    assert config.genome_threshold == "q0.01"
    assert config.input_sample_col_prefix == "LFQ intensity "
    assert config.on_missing_sample == "warn-skip"
    assert config.on_empty_unit == "error"
    assert config.save_per_unit_outputs is True
    assert config.n_jobs == 4


def test_unit_aware_gui_validation_missing_manifest_points_to_main_window():
    result = validate_unit_aware_manifest_for_gui(manifest_path="")

    assert result.ok is False
    assert "main Peptide Direct to OTF window" in result.message


def test_unit_aware_settings_dialog_uses_main_window_owned_values():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    dialog = UnitAwareSettingsDialog(
        current_config=UnitAwareGuiConfig(
            manifest_path="unit_aware_manifest.json",
            genome_threshold="q0.01",
        )
    )

    assert dialog.lineEdit_current_manifest_path.text() == "unit_aware_manifest.json"
    assert dialog.lineEdit_current_manifest_path.isReadOnly() is True
    assert not hasattr(dialog, "pushButton_browse_manifest")
    assert not hasattr(dialog, "comboBox_genome_threshold")
    assert dialog.get_config().genome_threshold == "q0.01"
    assert dialog.tabs.count() == 1
    assert dialog.spinBox_n_jobs.specialValueText() == "Auto"

    dialog.close()
    app.processEvents()


def test_main_window_controls_own_genome_threshold():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    gui = object.__new__(MetaXGUI)
    gui.unit_aware_gui_config = UnitAwareGuiConfig(
        manifest_path="old.json",
        genome_threshold="q0.05",
        on_missing_sample="warn-skip",
    )
    gui.lineEdit_pep_direct_to_otf_unit_aware_manifest_path = QtWidgets.QLineEdit()
    gui.lineEdit_pep_direct_to_otf_unit_aware_manifest_path.setText("current.json")
    gui.comboBox_pep_direct_to_otf_use_unit_aware_genome_threshold = QtWidgets.QComboBox()
    gui.comboBox_pep_direct_to_otf_use_unit_aware_genome_threshold.addItems(["q0.05", "q0.01"])
    gui.comboBox_pep_direct_to_otf_use_unit_aware_genome_threshold.setCurrentText("q0.01")

    config = gui._get_unit_aware_gui_config_from_controls()

    assert config.manifest_path == "current.json"
    assert config.genome_threshold == "q0.01"
    assert config.on_missing_sample == "warn-skip"
    app.processEvents()


def test_unit_aware_gui_validation_passes_with_matching_peptide_header(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    peptide_path = _write_peptide_table(
        tmp_path,
        ["Sequence", "Intensity_s1", "Intensity_s2", "Intensity_s3"],
    )

    result = validate_unit_aware_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        peptide_col="Sequence",
        peptide_table_separator="\t",
        genome_threshold="q0.01",
    )

    assert result.ok is True
    assert result.manifest_samples == ["s1", "s2", "s3"]
    assert result.mapped_samples == {
        "s1": "Intensity_s1",
        "s2": "Intensity_s2",
        "s3": "Intensity_s3",
    }
    assert result.missing_samples == []
    assert "Selected genome threshold: q0.01" in result.message
    assert "u1: samples=2, genomes=1" in result.message


def test_unit_aware_gui_validation_fails_for_missing_sample_by_default(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    peptide_path = _write_peptide_table(tmp_path, ["Sequence", "Intensity_s1", "Intensity_s2"])

    result = validate_unit_aware_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        peptide_col="Sequence",
        peptide_table_separator="\t",
        on_missing_sample="error",
    )

    assert result.ok is False
    assert result.missing_samples == ["s3"]
    assert "Manifest sample-column validation failed" in result.message
    assert "Missing samples: 1" in result.message
    assert "s3" in result.message
    assert result.details == "Missing manifest samples:\ns3"


@pytest.mark.parametrize("intensity_col", ["Precursor.Normalised", "Precursor.Quantity"])
def test_unit_aware_gui_validation_supports_long_format_parquet(
    tmp_path,
    monkeypatch,
    intensity_col,
):
    manifest_path = _write_manifest(tmp_path)
    peptide_path = tmp_path / "report.parquet"
    peptide_path.write_bytes(b"parquet placeholder")
    monkeypatch.setattr(
        unit_aware_settings_dialog,
        "_read_peptide_table_header_columns",
        lambda peptide_table_path, separator: ["Stripped.Sequence", "Run", intensity_col],
    )
    monkeypatch.setattr(
        unit_aware_settings_dialog,
        "_read_long_format_run_columns",
        lambda peptide_table_path: ["s1.raw", "s2.raw", "s3.raw"],
    )

    result = validate_unit_aware_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        peptide_col="Stripped.Sequence",
    )

    assert result.ok is True
    assert result.mapped_samples == {"s1": "s1.raw", "s2": "s2.raw", "s3": "s3.raw"}
    assert result.missing_samples == []
    assert "long-format DIA-NN parquet" in result.message
    assert "Run values validated as sample columns" in result.message
    assert f"intensity={intensity_col}" in result.message


def test_normal_direct_otf_gui_uses_shared_parquet_preparation(tmp_path):
    parquet_path = tmp_path / "report.parquet"
    pd.DataFrame(
        {
            "Run": ["s1.raw"],
            "Stripped.Sequence": ["PEPA"],
            "Evidence": [2.0],
            "Q.Value": [0.01],
            "Precursor.Quantity": [10.0],
        }
    ).to_parquet(parquet_path)
    gui = object.__new__(MetaXGUI)

    prepared_path, separator, peptide_col, intensity_prefix, metadata = (
        gui._prepare_diann_parquet_for_pep_direct_to_otf(
            str(parquet_path),
            str(tmp_path / "OTF.tsv"),
        )
    )

    prepared_df = pd.read_csv(prepared_path, sep="\t")
    assert separator == "\t"
    assert peptide_col == "Stripped.Sequence"
    assert intensity_prefix == "Precursor.Quantity."
    assert prepared_df.loc[0, "Precursor.Quantity.s1"] == 10.0
    assert metadata["diann_intensity_column"] == "Precursor.Quantity"


def test_validation_result_dialog_is_scrollable_and_screen_bounded():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    result = unit_aware_settings_dialog.UnitAwareManifestValidationResult(
        ok=False,
        message="Missing samples: 1000",
        manifest_samples=[],
        mapped_samples={},
        missing_samples=[],
        details="\n".join(f"sample_{index}" for index in range(1000)),
    )
    dialog = UnitAwareValidationResultDialog(result)

    assert dialog.result_text.isReadOnly()
    assert dialog.result_text.lineWrapMode() == QtWidgets.QPlainTextEdit.NoWrap
    assert dialog.result_text.toPlainText().endswith("sample_999")
    available = app.primaryScreen().availableGeometry()
    assert dialog.width() <= available.width()
    assert dialog.height() <= available.height()

    dialog.close()
    app.processEvents()


def test_unit_aware_gui_validation_warn_skip_passes_with_missing_sample(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    peptide_path = _write_peptide_table(tmp_path, ["Sequence", "Intensity_s1", "Intensity_s2"])

    result = validate_unit_aware_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        peptide_col="Sequence",
        peptide_table_separator="\t",
        on_missing_sample="warn-skip",
    )

    assert result.ok is True
    assert result.mapped_samples == {"s1": "Intensity_s1", "s2": "Intensity_s2"}
    assert result.missing_samples == ["s3"]
    assert "Missing samples: s3" in result.message


def test_unit_aware_gui_validation_fails_for_missing_peptide_column(tmp_path):
    manifest_path = _write_manifest(tmp_path)
    peptide_path = _write_peptide_table(tmp_path, ["Modified sequence", "Intensity_s1"])

    result = validate_unit_aware_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        peptide_col="Sequence",
        peptide_table_separator="\t",
    )

    assert result.ok is False
    assert "Peptide column 'Sequence' was not found" in result.message


def test_unit_aware_gui_validation_marks_parquet_header_skip_as_not_checked(tmp_path, monkeypatch):
    manifest_path = _write_manifest(tmp_path)
    peptide_path = tmp_path / "peptides.parquet"
    peptide_path.write_bytes(b"not a real parquet file")
    monkeypatch.setattr(
        unit_aware_settings_dialog,
        "_read_peptide_table_header_columns",
        lambda peptide_table_path, separator: None,
    )

    result = validate_unit_aware_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        peptide_col="Sequence",
        peptide_table_separator="\t",
    )

    assert result.ok is True
    assert result.mapped_samples == {}
    assert result.missing_samples == []
    assert "Peptide table header validation: skipped" in result.message
    assert "Mapped peptide table samples: not checked" in result.message
    assert "Missing samples: not checked" in result.message
    assert "Reason: parquet header metadata could not be read without pyarrow" in result.message
