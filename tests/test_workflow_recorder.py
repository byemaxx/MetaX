import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from metax.workflow_recorder.recorder import (
    _current_python_notebook_metadata,
    _environment_setup_code,
    register_current_python_kernel,
)
from metax.workflow_recorder import (
    AnalysisStep,
    WorkflowRecorder,
    auto_otf_report_step,
    gui_action_step,
    set_multi_tables_step,
    taxafunc_analyzer_step,
    deseq2_step,
    limma_step,
    unit_specific_otf_step,
)


def test_workflow_recorder_exports_yaml_python_and_notebook(tmp_path: Path):
    recorder = WorkflowRecorder(metadata={"source": "test"})
    recorder.add_step(
        AnalysisStep(
            title="Example Analysis",
            step_type="example",
            inputs={"input": "data.tsv"},
            outputs={"output": "result.tsv"},
            parameters={"top_n": 10},
            code="print('run example')\n",
        )
    )

    paths = recorder.export_all(tmp_path)

    assert paths.yaml_path.exists()
    assert paths.python_path.exists()
    assert paths.notebook_path.exists()

    workflow_yaml = yaml.safe_load(paths.yaml_path.read_text(encoding="utf-8"))
    assert workflow_yaml["metadata"]["source"] == "test"
    assert workflow_yaml["steps"][0]["title"] == "Example Analysis"

    script = paths.python_path.read_text(encoding="utf-8")
    assert "# %%" in script
    assert "print('run example')" in script

    notebook = json.loads(paths.notebook_path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert notebook["metadata"]["metax"]["python_executable"] == str(
        Path(sys.executable).resolve()
    )
    assert any(cell["cell_type"] == "code" for cell in notebook["cells"])
    assert any("print('run example')" in "".join(cell["source"]) for cell in notebook["cells"])


def test_workflow_recorder_exports_only_selected_formats(tmp_path: Path):
    recorder = WorkflowRecorder()

    paths = recorder.export_all(tmp_path, "notebook_only", formats={".ipynb"})

    assert paths.notebook_path == tmp_path / "notebook_only.ipynb"
    assert paths.notebook_path.exists()
    assert paths.python_path is None
    assert paths.yaml_path is None
    assert paths.as_dict() == {"workflow_notebook": paths.notebook_path}
    assert not (tmp_path / "notebook_only.py").exists()
    assert not (tmp_path / "notebook_only.yaml").exists()


@pytest.mark.parametrize("formats", [(), {"html"}])
def test_workflow_recorder_rejects_invalid_format_selections(tmp_path: Path, formats):
    recorder = WorkflowRecorder()

    with pytest.raises(ValueError):
        recorder.export_all(tmp_path, formats=formats)


def test_notebook_uses_the_python_environment_running_the_gui(tmp_path: Path):
    prefix = tmp_path / "miniconda3" / "envs" / "metax313"
    executable = prefix / "python.exe"

    metadata = _current_python_notebook_metadata(
        executable=executable,
        prefix=prefix,
        python_version="3.13.13",
    )

    assert metadata["kernelspec"] == {
        "display_name": "Python (metax313)",
        "language": "python",
        "name": "metax313",
    }
    assert metadata["language_info"]["version"] == "3.13.13"
    assert metadata["metax"]["python_environment"] == "metax313"
    assert metadata["metax"]["python_executable"] == str(executable.resolve())
    assert metadata["metax"]["python_prefix"] == str(prefix.resolve())


def test_registered_metax_kernel_is_used_in_notebook_metadata(tmp_path: Path):
    calls = []
    prefix = tmp_path / "MetaX" / "pyenv"

    kernel_name, display_name = register_current_python_kernel(
        installer=lambda **kwargs: calls.append(kwargs),
        executable=prefix / "python.exe",
        prefix=prefix,
    )
    recorder = WorkflowRecorder(
        notebook_kernel_name=kernel_name,
        notebook_kernel_display_name=display_name,
    )
    metadata = recorder.to_notebook()["metadata"]

    assert calls == [
        {
            "user": True,
            "kernel_name": "metax-pyenv",
            "display_name": "Python (MetaX GUI - pyenv)",
        }
    ]
    assert metadata["kernelspec"] == {
        "display_name": "Python (MetaX GUI - pyenv)",
        "language": "python",
        "name": "metax-pyenv",
    }


def test_auto_otf_report_step_uses_saved_config(tmp_path: Path):
    config_path = tmp_path / "config_used.yaml"
    config_path.write_text("input: {}\n", encoding="utf-8")
    result = SimpleNamespace(
        output_dir=tmp_path / "report",
        index_html_path=tmp_path / "report" / "index.html",
    )

    step = auto_otf_report_step(config_path, result)

    assert step.title == "Generate Auto OTF Report"
    assert step.step_type == "auto_otf_report"
    assert step.inputs["config_path"] == str(config_path.resolve())
    assert "load_config_from_yaml" in step.code
    assert "AutoOTFReport(config).run()" in step.code
    assert step.outputs["index_html_path"].endswith("index.html")


def test_unit_specific_otf_step_records_replayable_parameters():
    params = {
        "peptide_table_path": "peptides.tsv",
        "unit_specific_manifest_path": "manifest.json",
        "taxafunc_anno_db_path": "taxafunc.db",
        "output_path": "out.tsv",
        "digested_genome_folders": "digested",
        "genome_threshold": "q0.05",
        "peptide_col": "Sequence",
        "table_separator": "\t",
        "input_sample_col_prefix": None,
        "lca_threshold": 1.0,
        "protein_genome_separator": "_",
        "duplicate_peptide_handling_mode": "max",
        "on_missing_sample": "error",
        "on_empty_unit": "warn-skip",
        "save_per_unit_outputs": True,
        "n_jobs": None,
    }

    step = unit_specific_otf_step(params)

    assert step.step_type == "unit_specific_peptide_direct_to_otf"
    assert step.parameters == params
    assert step.inputs["unit_specific_manifest_path"] == "manifest.json"
    assert step.outputs["output_path"] == "out.tsv"
    assert "UnitSpecificOTFAnnotator(**unit_specific_otf_params)" in step.code
    compile(step.code, "<unit-specific-workflow-step>", "exec")


def test_taxafunc_and_multi_table_steps_generate_runnable_cells():
    load_step = taxafunc_analyzer_step(
        {
            "df_path": "OTF.tsv",
            "meta_path": "Meta.tsv",
            "any_df_mode": False,
            "peptide_col_name": "Sequence",
            "protein_col_name": "Proteins",
            "sample_col_prefix": "Intensity",
            "custom_col_name": "",
        },
        group_name="Sugar_type"
    )
    multi_step = set_multi_tables_step(
        "KEGG_ko_name",
        {
            "level": "s",
            "taxa_levels": ["p", "g", "s"],
            "group_list": ["A", "B", "C"],
            "func_threshold": 1.0,
            "outlier_params": {"detect_method": "missing-value", "handle_method": "fillzero"},
            "data_preprocess_params": {"normalize_method": None, "transform_method": None},
            "peptide_num_threshold": {"taxa": 3, "func": 3, "taxa_func": 3},
        },
    )

    assert "TaxaFuncAnalyzer(**taxafunc_params)" in load_step.code
    assert "tfa.set_group('Sugar_type')" in load_step.code
    assert "tfa.set_func('KEGG_ko_name')" in multi_step.code
    assert "'taxa_levels': ['p', 'g', 's']" in multi_step.code
    assert "'group_list': ['A', 'B', 'C']" in multi_step.code
    assert "    'level': 's'," in multi_step.code
    assert "tfa.set_multi_tables(**set_multi_table_params)" in multi_step.code


def test_notebook_setup_and_gui_action_replay_cells_keep_lists_compact():
    sample_list = [f"Intensity Sample {index}" for index in range(30)]
    recorder = WorkflowRecorder(metadata={"metax_package_root": r"C:\MetaX"})
    recorder.add_step(
        gui_action_step(
            title="Plot PCA",
            step_type="plot",
            action_name="plot_basic_info_sns",
            parameters={
                "method": "pca",
                "table_name": "Taxa",
                "sample_list": sample_list,
            },
        )
    )

    notebook = recorder.to_notebook()
    code_cells = ["".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code"]

    assert "sys.path.insert(0, str(metax_package_root))" in code_cells[0]
    assert "expected_python_prefix" in code_cells[0]
    assert "This workflow was exported from a different Python environment" in code_cells[0]
    assert "raise RuntimeError" not in code_cells[0]
    assert "def replay_metax_gui_action" in code_cells[1]
    assert "replay_metax_gui_action(tfa, action_name, parameters, stats_tables=stats_results)" in code_cells[-1]
    assert "'sample_list': [" in code_cells[-1]
    assert "\n        'Intensity Sample 1'," not in code_cells[-1]
    for code in code_cells:
        compile(code, "<workflow-notebook-cell>", "exec")


def test_notebook_setup_continues_with_a_different_python_environment(
    tmp_path: Path,
    monkeypatch,
):
    expected_prefix = tmp_path / "MetaX" / "pyenv"
    monkeypatch.setattr(sys, "path", sys.path.copy())
    setup_code = _environment_setup_code(
        {"metax_package_root": str(tmp_path)},
        expected_python_prefix=expected_prefix,
    )
    namespace = {}

    with pytest.warns(RuntimeWarning, match="Continuing with the current kernel"):
        exec(setup_code, namespace)

    assert namespace["expected_python_prefix"] == expected_prefix.resolve()
    assert namespace["current_python_prefix"] == Path(sys.prefix).resolve()
    assert namespace["stats_results"] == {}
    assert str(tmp_path) in sys.path


def test_all_gui_actions_generation():
    recorder = WorkflowRecorder()
    actions = [
        ("Plot PCA", "plot_basic_info_sns", {"method": "pca", "table_name": "Taxa"}),
        ("Plot PCA 3D", "plot_basic_info_sns", {"method": "pca_3d", "table_name": "Taxa"}),
        ("Plot t-SNE", "plot_basic_info_sns", {"method": "tsne", "table_name": "Taxa"}),
        ("Plot Box", "plot_basic_info_sns", {"method": "box", "table_name": "Taxa"}),
        ("Plot Correlation", "plot_basic_info_sns", {"method": "corr", "table_name": "Taxa"}),
        ("Plot Sunburst", "plot_basic_info_sns", {"method": "sunburst", "table_name": "Taxa"}),
        ("Plot Treemap", "plot_basic_info_sns", {"method": "treemap", "table_name": "Taxa"}),
        ("Plot Sankey", "plot_basic_info_sns", {"method": "sankey", "table_name": "Taxa"}),
        ("Plot Alpha Diversity", "plot_basic_info_sns", {"method": "alpha_div", "table_name": "Taxa", "metric": "shannon"}),
        ("Plot Beta Diversity", "plot_basic_info_sns", {"method": "beta_div", "table_name": "Taxa", "metric": "braycurtis"}),
        ("Plot Number Bar", "plot_basic_info_sns", {"method": "num_bar", "table_name": "Taxa"}),
        ("Plot UpSet Plot", "plot_basic_info_sns", {"method": "upset", "table_name": "Taxa"}),
        ("Plot Heatmap", "plot_basic_list", {"plot_type": "heatmap", "table_name": "Taxa"}),
        ("Plot Intensity Bar", "plot_basic_list", {"plot_type": "bar", "table_name": "Taxa"}),
        ("Plot PCA List", "plot_basic_list", {"plot_type": "pca", "table_name": "Taxa"}),
        ("Plot Intensity Sankey", "plot_basic_list", {"plot_type": "sankey", "table_name": "Taxa"}),
        ("Get Table", "plot_basic_list", {"plot_type": "get_table", "table_name": "Taxa"}),
        ("Plot Trends Cluster", "plot_trends_cluster", {"table_name": "Taxa", "num_cluster": 4}),
        ("Plot Trends Interactive Line", "plot_trends_interactive_line", {"table_name": "Taxa", "cluster_num": 0}),
        ("Plot Co-expression Heatmap", "plot_co_expr", {"plot_type": "heatmap", "df_type": "taxa", "corr_method": "pearson"}),
        ("Plot Co-expression Network", "plot_co_expr", {"plot_type": "network", "df_type": "taxa", "corr_method": "pearson"}),
        ("Plot Taxa-Func Link Network", "plot_network", {}),
        ("Plot Taxa-Func Link Heatmap", "plot_tflink_heatmap", {"taxa": "Taxon1", "func": "Func1"}),
        ("Plot Taxa-Func Link Intensity Bar", "plot_tflink_bar", {"taxa": "Taxon1", "func": "Func1"}),
        ("Plot Tukey HSD", "plot_tukey", {"table_name": "tukey_test"}),
        ("Plot Top Heatmap", "plot_top_heatmap", {"table_name": "anova(taxa)"}),
        ("Plot DESeq2 Volcano", "plot_deseq2_volcano", {"table_name": "deseq2(taxa)"}),
    ]

    for title, action_name, params in actions:
        recorder.add_step(
            gui_action_step(
                title=title,
                step_type="plot",
                action_name=action_name,
                parameters=params,
            )
        )

    # Test DESeq2 dynamic keys too
    recorder.add_step(
        deseq2_step(
            title="Run DESeq2 Two Group",
            method_name="get_stats_deseq2",
            df_type="taxa",
            parameters={"group1": "A", "group2": "B"},
        )
    )
    recorder.add_step(
        deseq2_step(
            title="Run DESeq2 Against Control",
            method_name="get_stats_deseq2_against_control",
            df_type="taxa",
            parameters={"control_group": "A", "group_list": ["B", "C"]},
        )
    )
    recorder.add_step(
        deseq2_step(
            title="Run DESeq2 Against Control with Condition",
            method_name="get_stats_deseq2_against_control_with_conditon",
            df_type="taxa",
            parameters={"control_group": "A", "group_list": ["B", "C"], "condition": "Cond1"},
        )
    )
    recorder.add_step(
        limma_step(
            title="Run Limma Two Group",
            method_name="get_stats_limma",
            df_type="taxa",
            parameters={"group1": "A", "group2": "B", "log2_transform": True, "zero_to_nan": True},
        )
    )
    recorder.add_step(
        limma_step(
            title="Run Limma Against Control",
            method_name="get_stats_limma_against_control",
            df_type="taxa",
            parameters={"control_group": "A", "group_list": ["B", "C"], "zero_to_nan": True},
        )
    )
    recorder.add_step(
        limma_step(
            title="Run Limma Against Control with Condition",
            method_name="get_stats_limma_against_control_with_conditon",
            df_type="taxa",
            parameters={
                "control_group": "A",
                "group_list": ["B", "C"],
                "condition": "Cond1",
                "invert_transform": "log10",
                "log2_transform": True,
                "zero_to_nan": True,
            },
        )
    )

    notebook = recorder.to_notebook()
    code_cells = ["".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code"]
    
    # Verify that all cells compile without syntax errors
    for code in code_cells:
        compile(code, "<workflow-notebook-cell>", "exec")
        
    # Verify DESeq2 key logic is present in generated cells
    deseq2_cells = [code for code in code_cells if "tfa.CrossTest.get_stats_deseq2" in code]
    assert len(deseq2_cells) == 3
    assert "stats_results['deseq2(' + df_type.lower() + ')']" in deseq2_cells[0]
    assert "stats_results['deseq2all(' + df_type.lower() + ')']" in deseq2_cells[1]
    assert "stats_results['deseq2allinCondition(' + df_type.lower() + ')']" in deseq2_cells[2]
    # Verify new helper
    assert "prepare_deseq2_input" in deseq2_cells[0]
    assert "_get_metax_df_by_type" in deseq2_cells[0]

    limma_cells = [code for code in code_cells if "tfa.CrossTest.get_stats_limma" in code]
    assert len(limma_cells) == 3
    assert "stats_results['limma(' + df_type.lower() + ')']" in limma_cells[0]
    assert "stats_results['limmaall(' + df_type.lower() + ')']" in limma_cells[1]
    assert "stats_results['limmaallinCondition(' + df_type.lower() + ')']" in limma_cells[2]
    assert "prepare_limma_input" not in limma_cells[0]
    assert "'log2_transform': True" in limma_cells[0]
    assert "'zero_to_nan': True" in limma_cells[0]
    assert "_get_metax_df_by_type" in limma_cells[0]


def test_plot_basic_list_pca_replay_imports_basic_plot():
    recorder = WorkflowRecorder()
    recorder.add_step(
        gui_action_step(
            title="Plot PCA List",
            step_type="plot",
            action_name="plot_basic_list",
            parameters={"plot_type": "pca", "table_name": "Taxa", "use_3d_pca": False},
        )
    )

    notebook = recorder.to_notebook()
    helper_cell = next(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code" and "def replay_metax_gui_action" in "".join(cell["source"])
    )
    plot_basic_list_branch = helper_cell.split('if action_name == "plot_basic_list":', 1)[1]

    assert "from metax.taxafunc_ploter.basic_plot import BasicPlot" in plot_basic_list_branch
    assert "return BasicPlot(tfa).plot_pca_sns" in plot_basic_list_branch


def test_table_replay_helper_does_not_eagerly_resolve_unrequested_tables():
    recorder = WorkflowRecorder()
    notebook = recorder.to_notebook()
    helper_cell = next(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code" and "def replay_metax_gui_action" in "".join(cell["source"])
    )
    namespace = {}
    exec(helper_cell, namespace)
    taxa_table = object()

    class FakeAnalyzer:
        taxa_df = taxa_table

        def get_func_taxa_df(self):
            raise AssertionError("Unrequested functions-taxa table was resolved")

        def get_peptide_df(self):
            raise AssertionError("Unrequested peptide table was resolved")

    assert namespace["_metax_table_from_tfa"](FakeAnalyzer(), "Taxa") is taxa_table


def test_limma_step_defaults_zero_to_nan_false():
    step = limma_step(
        title="Run Limma Two Group",
        method_name="get_stats_limma",
        df_type="taxa",
        parameters={"group1": "A", "group2": "B"},
    )

    assert "'zero_to_nan': False" in step.code
    assert "'log2_transform': False" in step.code
    assert "'invert_transform': None" in step.code
    assert "zero_to_nan" in step.parameters


def test_async_workflow_step_preserves_current_tfa_group():
    main_gui = pytest.importorskip("metax.gui.main_gui", exc_type=ImportError)

    gui = main_gui.MetaXGUI.__new__(main_gui.MetaXGUI)
    gui.tfa = SimpleNamespace(meta_name="Treatment")
    gui.workflow_recorder = WorkflowRecorder()
    gui.logger = SimpleNamespace(write_log=lambda *args, **kwargs: None)

    gui._record_async_workflow_step(
        AnalysisStep(
            title="Run ANOVA",
            step_type="anova_test",
            code="# Requires `tfa` from the OTF loading step.\nparams = {}\nresult = tfa.CrossTest.get_stats_anova(**params)",
        ),
        result=None,
    )

    assert len(gui.workflow_recorder.steps) == 1
    assert "tfa.set_group('Treatment')" in gui.workflow_recorder.steps[0].code
    assert gui.workflow_recorder.steps[0].code.index("tfa.set_group('Treatment')") < gui.workflow_recorder.steps[0].code.index(
        "params = {}"
    )


def test_workflow_export_dialog_defaults_to_notebook_only():
    main_gui = pytest.importorskip("metax.gui.main_gui", exc_type=ImportError)
    step = AnalysisStep(title="Plot PCA", step_type="plot", code="print('pca')")

    dialog = main_gui.WorkflowStepsSelectionDialog([step])
    try:
        assert dialog.width() == 800
        assert dialog.height() == 600
        assert dialog.list_widget.count() == 1
        assert dialog.get_selected_formats() == ("ipynb",)

        dialog.format_checkboxes["ipynb"].setChecked(False)
        dialog.format_checkboxes["py"].setChecked(True)
        dialog.format_checkboxes["yaml"].setChecked(True)
        assert dialog.get_selected_formats() == ("py", "yaml")
    finally:
        dialog.close()


def test_export_recovers_missing_processed_tables_step_from_live_analyzer(
    tmp_path: Path,
    monkeypatch,
):
    main_gui = pytest.importorskip("metax.gui.main_gui", exc_type=ImportError)
    load_step = taxafunc_analyzer_step(
        {
            "df_path": "OTF.tsv",
            "meta_path": "Meta.tsv",
            "any_df_mode": False,
            "peptide_col_name": "Sequence",
            "protein_col_name": "Proteins",
            "sample_col_prefix": "Intensity",
            "custom_col_name": "",
        },
        group_name="Treatment",
    )
    plot_step = gui_action_step(
        title="Plot PCA",
        step_type="plot",
        action_name="plot_basic_info_sns",
        parameters={"method": "pca", "table_name": "Taxa"},
    )
    recorder = WorkflowRecorder()
    recorder.add_step(load_step)
    recorder.add_step(plot_step)
    gui = main_gui.MetaXGUI.__new__(main_gui.MetaXGUI)
    gui.MainWindow = None
    gui.workflow_recorder = recorder
    gui.last_path = str(tmp_path)
    gui.logger = SimpleNamespace(write_log=lambda *args, **kwargs: None)
    gui._record_current_taxafunc_if_needed = lambda: None
    gui.tfa = SimpleNamespace(
        func_name="KEGG_ko_name",
        _last_set_multi_tables_params={
            "level": "s",
            "func_name": "KEGG_ko_name",
            "func_threshold": 1.0,
            "outlier_params": {"detect_method": "none", "handle_method": "drop+drop"},
            "data_preprocess_params": {
                "normalize_method": None,
                "transform_method": None,
                "batch_meta": None,
                "processing_order": [],
            },
            "peptide_num_threshold": {"taxa": 1, "func": 1, "taxa_func": 1},
            "keep_unknow_func": False,
            "split_func": False,
            "split_func_params": {"split_by": "|", "share_intensity": False},
            "taxa_and_func_only_from_otf": False,
            "quant_method": "sum",
            "remove_unknown_taxa": True,
        },
    )

    class FakeExportDialog:
        def __init__(self, steps, parent):
            self.steps = steps

        def exec_(self):
            return main_gui.QDialog.Accepted

        def get_selected_steps(self):
            return self.steps

        def get_selected_formats(self):
            return ("ipynb",)

    monkeypatch.setattr(main_gui, "WorkflowStepsSelectionDialog", FakeExportDialog)
    monkeypatch.setattr(
        main_gui.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(tmp_path / "recovered.ipynb"), "Jupyter Notebook (*.ipynb)"),
    )
    monkeypatch.setattr(main_gui.QMessageBox, "information", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_gui.QMessageBox, "warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        main_gui,
        "register_current_python_kernel",
        lambda: ("metax-test", "Python (MetaX GUI - test)"),
    )

    gui.export_workflow_notebook()

    assert [step.step_type for step in recorder.steps] == [
        "load_taxafunc_analyzer",
        "set_multi_tables",
        "plot",
    ]
    processed_step = recorder.steps[1]
    assert "tfa.set_func('KEGG_ko_name')" in processed_step.code
    assert "tfa.set_multi_tables(**set_multi_table_params)" in processed_step.code
    assert "'func_name'" not in processed_step.code
    exported_notebook = json.loads((tmp_path / "recovered.ipynb").read_text(encoding="utf-8"))
    assert exported_notebook["metadata"]["kernelspec"]["name"] == "metax-test"
    exported_code = [
        "".join(cell["source"])
        for cell in exported_notebook["cells"]
        if cell["cell_type"] == "code"
    ]
    processed_cell_index = next(
        index for index, code in enumerate(exported_code) if "tfa.set_multi_tables" in code
    )
    plot_cell_index = next(
        index for index, code in enumerate(exported_code) if "action_name = 'plot_basic_info_sns'" in code
    )
    assert processed_cell_index < plot_cell_index


def test_gui_workflow_export_honors_selected_formats(tmp_path: Path, monkeypatch):
    main_gui = pytest.importorskip("metax.gui.main_gui", exc_type=ImportError)
    recorder = WorkflowRecorder()
    recorder.add_step(AnalysisStep(title="Plot PCA", step_type="plot", code="print('pca')"))
    gui = main_gui.MetaXGUI.__new__(main_gui.MetaXGUI)
    gui.MainWindow = None
    gui.workflow_recorder = recorder
    gui.last_path = str(tmp_path)
    gui.logger = SimpleNamespace(write_log=lambda *args, **kwargs: None)
    gui._record_current_taxafunc_if_needed = lambda: None

    class FakeExportDialog:
        def __init__(self, steps, parent):
            self.steps = steps

        def exec_(self):
            return main_gui.QDialog.Accepted

        def get_selected_steps(self):
            return self.steps

        def get_selected_formats(self):
            return ("ipynb",)

    monkeypatch.setattr(main_gui, "WorkflowStepsSelectionDialog", FakeExportDialog)
    monkeypatch.setattr(
        main_gui.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(tmp_path / "selected.ipynb"), "Jupyter Notebook (*.ipynb)"),
    )
    monkeypatch.setattr(main_gui.QMessageBox, "information", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_gui.QMessageBox, "warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        main_gui,
        "register_current_python_kernel",
        lambda: ("metax-test", "Python (MetaX GUI - test)"),
    )

    gui.export_workflow_notebook()

    assert (tmp_path / "selected.ipynb").exists()
    assert not (tmp_path / "selected.py").exists()
    assert not (tmp_path / "selected.yaml").exists()
