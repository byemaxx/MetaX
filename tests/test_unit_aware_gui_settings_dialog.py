from dataclasses import asdict

from metax.gui.unit_aware_settings_dialog import UnitAwareGuiConfig


def test_unit_aware_gui_config_defaults_and_override():
    default = UnitAwareGuiConfig()
    assert asdict(default) == {
        "manifest_path": "",
        "genome_threshold": "auto",
        "input_sample_col_prefix": "",
        "on_missing_sample": "error",
        "on_empty_unit": "warn-skip",
        "save_per_unit_outputs": False,
    }

    config = UnitAwareGuiConfig(
        manifest_path="unit_aware_manifest.json",
        genome_threshold="q0.01",
        input_sample_col_prefix="LFQ intensity ",
        on_missing_sample="warn-skip",
        on_empty_unit="error",
        save_per_unit_outputs=True,
    )

    assert config.manifest_path == "unit_aware_manifest.json"
    assert config.genome_threshold == "q0.01"
    assert config.input_sample_col_prefix == "LFQ intensity "
    assert config.on_missing_sample == "warn-skip"
    assert config.on_empty_unit == "error"
    assert config.save_per_unit_outputs is True
