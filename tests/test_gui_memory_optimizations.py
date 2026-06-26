import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pandas as pd
from PyQt5 import QtWidgets

from metax.gui import main_gui
from metax.gui.main_gui import MetaXGUI
from metax.gui.metax_gui import ui_table_view
from metax.gui.metax_gui.ui_table_view import Ui_Table_view


class FakeComboBox:
    def __init__(self, current_text=""):
        self.items = []
        self._current_text = current_text
        self.clear_count = 0

    def addItem(self, item):
        self.items.append(item)

    def addItems(self, items):
        self.items.extend(list(items))

    def clear(self):
        self.items.clear()
        self.clear_count += 1

    def currentText(self):
        return self._current_text


class FakeLogger:
    def __init__(self):
        self.messages = []

    def write_log(self, message, level="i"):
        self.messages.append((message, level))


class FakeSettings:
    def contains(self, key):
        return False


class FakeListWidget:
    def __init__(self):
        self.items = []

    def addItems(self, items):
        self.items.extend(list(items))


class FakeIndexedWidget:
    def __init__(self):
        self.indexes = []

    def setCurrentIndex(self, index):
        self.indexes.append(index)


class FakeButton:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, enabled):
        self.enabled = enabled


def _taxa_func_df(count=5):
    index = pd.MultiIndex.from_tuples(
        [(f"taxon_{i}", f"func_{i}") for i in range(count)],
        names=["Taxa", "Function"],
    )
    return pd.DataFrame({"s1": range(count)}, index=index)


def _fake_gui_with_taxa_func_df(count=5):
    gui = object.__new__(MetaXGUI)
    gui.tfa = SimpleNamespace(taxa_func_df=_taxa_func_df(count))
    gui.MAX_EAGER_COMBOBOX_ITEMS = 50000
    return gui


def test_taxa_function_combobox_population_is_limited():
    gui = _fake_gui_with_taxa_func_df(count=5)
    combo = FakeComboBox()

    gui._add_items_to_combobox_by_df_type(combo, "Taxa-Functions", "Taxa-Functions", limit=2)

    assert combo.items == [
        "taxon_0 <func_0>",
        "taxon_1 <func_1>",
        "[Showing first 2 of 5 Taxa-Functions; type or paste an exact item to use it]",
    ]


def test_taxa_function_validation_accepts_exact_items_beyond_preview():
    gui = _fake_gui_with_taxa_func_df(count=5)

    assert gui._item_exists_in_df_type("taxon_4 <func_4>", "Taxa-Functions") is True
    assert gui._item_exists_in_df_type("taxon_4 func_4", "Taxa-Functions") is False
    assert gui._item_exists_in_df_type("taxon_99 <func_99>", "Taxa-Functions") is False


def test_run_after_set_multi_tables_does_not_eagerly_cache_taxa_functions(monkeypatch):
    gui = object.__new__(MetaXGUI)
    taxa_func_df = _taxa_func_df(count=6)
    gui.tfa = SimpleNamespace(
        peptide_df=pd.DataFrame({"s1": [1, 2]}, index=["pep1", "pep2"]),
        func_df=pd.DataFrame({"s1": [1, 2]}, index=["func_0", "func_1"]),
        taxa_df=pd.DataFrame({"s1": [1, 2]}, index=["taxon_0", "taxon_1"]),
        taxa_func_df=taxa_func_df,
        protein_df=None,
        any_df_mode=False,
        original_df=pd.DataFrame({"s1": range(10)}),
        peptide_num_used={"taxa": 2, "func": 2, "taxa_func": 2},
        taxa_level="Species",
        func_name="Function",
    )
    gui.table_dict = {"existing": pd.DataFrame()}
    gui.listWidget_table_list = FakeListWidget()
    gui.settings = FakeSettings()
    gui.comboBox_basic_heatmap_selection_list = FakeComboBox()
    gui.MAX_EAGER_COMBOBOX_ITEMS = 2
    gui.logger = FakeLogger()
    gui.MainWindow = None
    gui.stackedWidget = FakeIndexedWidget()
    gui.tabWidget_TaxaFuncAnalyzer = FakeIndexedWidget()
    gui.tabWidget_4 = FakeIndexedWidget()
    gui.pushButton_set_multi_table = FakeButton()
    monkeypatch.setattr(main_gui.QMessageBox, "information", lambda *args, **kwargs: None)

    no_op_methods = [
        "add_or_remove_protein_custom_label",
        "update_func_taxa_group_to_combobox",
        "clean_basic_heatmap_list",
        "_update_basic_peptide_query_combobox",
        "clear_tfnet_focus_list",
        "set_basic_heatmap_selection_list",
        "disable_button_after_multiple",
        "enable_multi_button",
        "auto_save_metax_obj_to_file",
        "change_event_checkBox_basic_plot_table",
        "change_event_comboBox_basic_heatmap_table",
        "update_co_expr_select_list",
        "update_trends_select_list",
        "update_tfnet_select_list",
        "restore_table_names_to_combox_after_load_taxafunc_obj",
    ]
    for method_name in no_op_methods:
        monkeypatch.setattr(gui, method_name, lambda *args, **kwargs: None)

    MetaXGUI.run_after_set_multi_tables(gui)

    assert gui.peptide_list == []
    assert gui.taxa_func_list == []


def test_table_view_keeps_original_dataframe_and_renders_current_page(monkeypatch):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    df = pd.DataFrame({"value": range(105)}, index=pd.Index([f"id_{i}" for i in range(105)], name="id"))
    original_columns = list(df.columns)
    captured = {}

    dialog = Ui_Table_view(df=df, title="large table")

    assert dialog.df is df
    assert list(df.columns) == original_columns
    assert dialog.tableWidget.rowCount() == 100
    assert dialog.tableWidget.columnCount() == 2
    assert dialog.tableWidget.horizontalHeaderItem(0).text() == "id"
    assert dialog.tableWidget.item(0, 0).text() == "id_0"

    dialog.next_page()
    assert dialog.tableWidget.rowCount() == 5
    assert dialog.tableWidget.item(0, 0).text() == "id_100"

    def fake_export(parent, export_df, title, last_path, save_index=False):
        captured["df"] = export_df
        captured["save_index"] = save_index
        return last_path, True

    monkeypatch.setattr(ui_table_view, "export_dataframe_with_dialog", fake_export)
    dialog.export_tsv()

    assert captured["df"] is df
    assert captured["save_index"] is True
    dialog.close()
    app.processEvents()


def test_auto_save_skips_large_tables(monkeypatch):
    gui = object.__new__(MetaXGUI)
    gui.AUTO_SAVE_MAX_TABLE_MEMORY_MB = 2048
    gui.metax_home_path = "unused"
    gui.logger = FakeLogger()
    gui.tfa = object()
    save_calls = []
    monkeypatch.setattr(gui, "_estimate_metax_table_memory_mb", lambda: 4096.0)
    monkeypatch.setattr(gui, "save_metax_obj_to_file", lambda *args, **kwargs: save_calls.append((args, kwargs)))

    gui.auto_save_metax_obj_to_file()

    assert save_calls == []
    assert gui.logger.messages[-1][1] == "w"


def test_close_event_save_and_close_uses_auto_save_guard(monkeypatch):
    gui = object.__new__(MetaXGUI)
    gui.MainWindow = None
    gui.tfa = object()
    gui.web_list = []
    gui.table_dialogs = []
    gui.plt_dialogs = []
    gui.executors = []
    gui.logger = FakeLogger()
    gui.show_message = lambda *args, **kwargs: None
    gui.save_basic_settings = lambda *args, **kwargs: None
    auto_save_calls = []
    direct_save_calls = []
    gui.auto_save_metax_obj_to_file = lambda: auto_save_calls.append(True)
    gui.save_metax_obj_to_file = lambda *args, **kwargs: direct_save_calls.append((args, kwargs))

    class FakeButton:
        def __init__(self, text, parent=None):
            self.text = text

    class FakeMessageBox:
        YesRole = 0
        NoRole = 1
        RejectRole = 2

        def __init__(self, parent=None):
            self.buttons = []

        def setWindowTitle(self, title):
            pass

        def setText(self, text):
            pass

        def addButton(self, button, role):
            self.buttons.append(button)

        def exec(self):
            pass

        def clickedButton(self):
            return self.buttons[0]

    class FakeEvent:
        def __init__(self):
            self.accepted = False

        def accept(self):
            self.accepted = True

        def ignore(self):
            self.accepted = False

    monkeypatch.setattr(main_gui, "QMessageBox", FakeMessageBox)
    monkeypatch.setattr(main_gui, "QPushButton", FakeButton)
    event = FakeEvent()

    gui.closeEvent(event)

    assert auto_save_calls == [True]
    assert direct_save_calls == []
    assert event.accepted is True


def test_manual_save_large_table_respects_confirmation(tmp_path, monkeypatch):
    gui = object.__new__(MetaXGUI)
    gui.AUTO_SAVE_MAX_TABLE_MEMORY_MB = 2048
    gui.MainWindow = None
    gui.tfa = SimpleNamespace(peptide_df=pd.DataFrame({"s1": [1]}))
    gui.table_dict = {}
    gui.metax_home_path = str(tmp_path)
    gui.last_path = str(tmp_path)
    gui.logger = FakeLogger()
    gui.save_basic_settings = lambda *args, **kwargs: None
    gui.save_set_multi_table_settings = lambda *args, **kwargs: None
    monkeypatch.setattr(gui, "_estimate_metax_table_memory_mb", lambda: 4096.0)
    (tmp_path / "settings.ini").write_text("settings", encoding="utf-8")

    cancelled_path = tmp_path / "cancelled.pkl"
    monkeypatch.setattr(main_gui.QMessageBox, "question", lambda *args, **kwargs: main_gui.QMessageBox.No)

    gui.save_metax_obj_to_file(save_path=str(cancelled_path), no_message=True, warn_large=True)

    assert not cancelled_path.exists()

    saved_path = tmp_path / "confirmed.pkl"
    monkeypatch.setattr(main_gui.QMessageBox, "question", lambda *args, **kwargs: main_gui.QMessageBox.Yes)

    gui.save_metax_obj_to_file(save_path=str(saved_path), no_message=True, warn_large=True)

    assert saved_path.exists()
