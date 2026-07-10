import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtWidgets

from metax.gui.metax_gui.auto_otf_report_dialog import AutoOTFReportDialog


def test_auto_report_dialog_exposes_statistics_and_figure_settings(tmp_path):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    dialog = AutoOTFReportDialog(
        initial_params={
            "otf_path": "input.tsv",
            "output_dir": str(tmp_path / "MetaX_Report"),
            "selected_taxa_levels": ["s"],
            "function_choices": ["Gene"],
            "selected_functions": ["Gene"],
            "diff_method": "dunnett",
            "figure_formats": ["png", "pdf"],
            "dpi": 450,
        }
    )

    params = dialog.get_params()

    assert params["diff_method"] == "dunnett"
    assert params["figure_formats"] == ["png", "pdf"]
    assert params["dpi"] == 450
    dialog.close()
    app.processEvents()
