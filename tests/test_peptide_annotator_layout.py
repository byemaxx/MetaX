import json
import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from metax.gui.main_gui import MetaXGUI
from metax.gui.unit_specific_settings_dialog import (
    validate_genome_selection_manifest_for_gui,
)


def _build_layout_harness():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    ui = MetaXGUI.__new__(MetaXGUI)
    ui.setupUi(window)
    ui.label_pep_direct_to_otf_input_source = QtWidgets.QLabel("Genome selection source")
    ui.comboBox_pep_direct_to_otf_input_source = QtWidgets.QComboBox()
    ui.comboBox_pep_direct_to_otf_input_source.addItem("Manifest", "metaumbra-manifest")
    ui.comboBox_pep_direct_to_otf_input_source.addItem("Automatic", "metax-automatic")
    ui.comboBox_pep_direct_to_otf_input_source.addItem("Genome list", "genome-list")
    ui.label_pep_direct_to_otf_manifest_summary = QtWidgets.QLabel("summary")
    ui.gridLayout_74.addWidget(ui.label_pep_direct_to_otf_input_source, ui.gridLayout_74.rowCount(), 0)
    ui.gridLayout_74.addWidget(ui.comboBox_pep_direct_to_otf_input_source, ui.gridLayout_74.rowCount(), 2)
    ui._arrange_pep_direct_to_otf_layout()
    return app, window, ui


def _position(layout, target):
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item.widget() is target or item.layout() is target:
            return layout.getItemPosition(index)
    raise AssertionError(f"Layout item not found: {target}")


def test_manifest_gui_validation_requires_peptide_table():
    manifest_path = Path(__file__).parent / "fixtures" / "genome_selection_manifest.v1.json"

    result = validate_genome_selection_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path="",
    )

    assert not result.ok
    assert "Please select a peptide table" in result.message
    assert result.mapped_samples == {}
    assert result.missing_samples == result.manifest_samples


def test_manifest_gui_validation_accepts_diann_wide_matrix_compound_suffixes(tmp_path):
    samples = [
        "20250211_Ailing_Pro2_P1_V48_PBS_1",
        "20250211_Ailing_Pro2_P1_V48_PBS_2",
        "20250211_Ailing_Pro2_P1_V48_PBS_3",
    ]
    fixture_path = Path(__file__).parent / "fixtures" / "genome_selection_manifest.v1.json"
    manifest_data = json.loads(fixture_path.read_text(encoding="utf-8"))
    unit_template = next(iter(manifest_data["units"].values()))
    manifest_data["unit_definition"].update(
        {
            "mode": "per-sample",
            "analysis_unit_column": None,
            "n_units": len(samples),
        }
    )
    manifest_data["units"] = {
        sample: {
            **unit_template,
            "sample_ids": [sample],
            "n_samples": 1,
        }
        for sample in samples
    }
    manifest_path = tmp_path / "genome_selection_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

    sample_columns = [
        rf"D:\Qing\v48_from_aling_proj2\raw\{sample}.raw.dia"
        for sample in samples
    ]
    peptide_path = tmp_path / "report.pr_matrix.tsv"
    peptide_path.write_text(
        "\t".join(["Stripped.Sequence", *sample_columns]) + "\n",
        encoding="utf-8",
    )

    result = validate_genome_selection_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        peptide_col="Stripped.Sequence",
    )

    assert result.ok
    assert result.missing_samples == []
    assert result.mapped_samples == dict(zip(samples, sample_columns))


def test_manifest_gui_validation_respects_empty_genome_unit_policy(tmp_path):
    fixture_path = Path(__file__).parent / "fixtures" / "genome_selection_manifest.v1.json"
    manifest_data = json.loads(fixture_path.read_text(encoding="utf-8"))
    manifest_data["units"]["u1"]["genome_ids_q001"] = []
    manifest_path = tmp_path / "genome_selection_manifest.json"
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")
    peptide_path = tmp_path / "peptides.tsv"
    peptide_path.write_text("Sequence\ts2\nPEP\t1\n", encoding="utf-8")

    warn_result = validate_genome_selection_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        genome_threshold="q0.01",
        on_empty_unit="warn-skip",
    )
    error_result = validate_genome_selection_manifest_for_gui(
        manifest_path=str(manifest_path),
        peptide_table_path=str(peptide_path),
        genome_threshold="q0.01",
        on_empty_unit="error",
    )

    assert warn_result.ok
    assert warn_result.manifest_samples == ["s1", "s2"]
    assert warn_result.mapped_samples == {"s2": "s2"}
    assert warn_result.missing_samples == []
    assert "Required peptide table samples: 1" in warn_result.message
    assert "Empty genome units to skip: u1" in warn_result.message
    assert not error_result.ok
    assert "Unit 'u1' has no genomes at selected threshold q0.01" in error_result.message


def test_annotation_layout_follows_source_input_output_order():
    app, window, ui = _build_layout_harness()
    try:
        assert _position(ui.gridLayout_74, ui.label_pep_direct_to_otf_input_source) == (0, 0, 1, 2)
        assert _position(ui.gridLayout_74, ui.comboBox_pep_direct_to_otf_input_source) == (0, 2, 1, 2)
        assert _position(ui.gridLayout_74, ui.lineEdit_pep_direct_to_otf_peptide_path)[0] == 1
        assert _position(ui.gridLayout_74, ui.lineEdit_pep_direct_to_otf_unit_specific_manifest_path)[0] == 2
        assert _position(ui.gridLayout_74, ui.label_pep_direct_to_otf_custom_genome_list)[0] == 2
        assert _position(ui.gridLayout_74, ui.label_pep_direct_to_otf_manifest_summary) == (4, 0, 1, 4)
        assert _position(ui.gridLayout_74, ui.lineEdit_pep_direct_to_otf_digestied_genome_pep_path)[0] == 5
        assert _position(ui.gridLayout_74, ui.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path)[0] == 6
        assert _position(ui.gridLayout_74, ui.lineEdit_pep_direct_to_otf_output_path)[0] == 7
        assert _position(ui.gridLayout_74, ui.pushButton_run_pep_direct_to_otf)[0] == 11
    finally:
        window.close()
        app.processEvents()


def test_source_choice_hides_irrelevant_manifest_or_list_controls():
    app, window, ui = _build_layout_harness()
    try:
        ui.comboBox_pep_direct_to_otf_input_source.setCurrentIndex(0)
        ui.update_pep_direct_to_otf_mode_state()
        assert not ui.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.isHidden()
        assert ui.pushButton_pep_direct_to_otf_open_genome_list_file.isHidden()
        assert not ui.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.isEnabled()

        ui.comboBox_pep_direct_to_otf_input_source.setCurrentIndex(1)
        ui.update_pep_direct_to_otf_mode_state()
        assert ui.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.isHidden()
        assert ui.pushButton_pep_direct_to_otf_open_genome_list_file.isHidden()
        assert ui.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.isEnabled()

        ui.comboBox_pep_direct_to_otf_input_source.setCurrentIndex(2)
        ui.update_pep_direct_to_otf_mode_state()
        assert ui.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.isHidden()
        assert not ui.pushButton_pep_direct_to_otf_open_genome_list_file.isHidden()
        assert ui.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.isEnabled()
        assert not ui.label_pep_direct_to_otf_custom_genome_list.isHidden()
        assert ui.pushButton_pep_direct_to_otf_reset_selected_genome_list.text() == "Reset"
    finally:
        window.close()
        app.processEvents()


def test_non_manifest_gui_forwards_custom_intensity_prefix(monkeypatch, tmp_path):
    app, window, ui = _build_layout_harness()
    try:
        peptide = tmp_path / "peptides.tsv"
        database = tmp_path / "taxafunc.db"
        digests = tmp_path / "digests"
        output = tmp_path / "OTF.tsv"
        peptide.write_text("Sequence\tAbundance_s1\nPEP\t1\n", encoding="utf-8")
        database.write_text("x", encoding="utf-8")
        digests.mkdir()

        ui.MainWindow = window
        ui.logger = SimpleNamespace(write_log=lambda *args, **kwargs: None)
        ui.pep_direct_to_otf_selected_genomes = []
        ui.pep_direct_to_otf_selected_genome_source = ""
        ui.lineEdit_pep_direct_to_otf_peptide_path.setText(str(peptide))
        ui.lineEdit_pep_direct_to_otf_digestied_genome_pep_path.setText(str(digests))
        ui.lineEdit_pep_direct_to_otf_pro2taxafunc_db_path.setText(str(database))
        ui.lineEdit_pep_direct_to_otf_output_path.setText(str(output))
        ui.comboBox_pep_direct_to_otf_peptide_col_name.clear()
        ui.comboBox_pep_direct_to_otf_peptide_col_name.addItem("Sequence")
        ui.comboBox_pep_direct_to_otf_intensity_column.setEditable(True)
        ui.comboBox_pep_direct_to_otf_intensity_column.setEditText("Abundance")
        ui.doubleSpinBox_pep_direct_to_otf_protein_coverage_cutoff.setValue(0.42)

        captured = {}

        class FakeAnnotator:
            def __init__(self, **kwargs):
                captured.update(kwargs)

            def run(self):
                return None

        monkeypatch.setattr("metax.gui.main_gui.GlobalOTFAnnotator", FakeAnnotator)
        ui.run_in_new_window = lambda function, **kwargs: function()
        ui.run_pep_direct_to_otf_non_metaumbra("metax-automatic")

        assert captured["intensity_col_prefix"] == "Abundance"
        assert captured["protein_peptide_coverage_cutoff"] == 0.42
        assert captured["selection_mode"] == "automatic"
        assert captured["selected_genome_source"] is None
    finally:
        window.close()
        app.processEvents()
