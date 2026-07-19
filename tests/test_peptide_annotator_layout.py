import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from metax.gui.main_gui import MetaXGUI


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

        ui.comboBox_pep_direct_to_otf_input_source.setCurrentIndex(1)
        ui.update_pep_direct_to_otf_mode_state()
        assert ui.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.isHidden()
        assert ui.pushButton_pep_direct_to_otf_open_genome_list_file.isHidden()

        ui.comboBox_pep_direct_to_otf_input_source.setCurrentIndex(2)
        ui.update_pep_direct_to_otf_mode_state()
        assert ui.lineEdit_pep_direct_to_otf_unit_specific_manifest_path.isHidden()
        assert not ui.pushButton_pep_direct_to_otf_open_genome_list_file.isHidden()
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
        assert captured["selection_mode"] == "automatic"
        assert captured["selected_genome_source"] is None
    finally:
        window.close()
        app.processEvents()
