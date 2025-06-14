import os
import sys
from pathlib import Path
import importlib.util
from types import ModuleType

PROJECT_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "yaml_config",
    PROJECT_ROOT / "app" / "utils" / "yaml_config.py",
)
yaml_config = importlib.util.module_from_spec(spec)
fake_yaml = ModuleType("yaml")
fake_yaml.safe_load = lambda f: {}
sys.modules.setdefault("yaml", fake_yaml)
spec.loader.exec_module(yaml_config)


def test_load_config_from_different_cwd(tmp_path, monkeypatch):
    """load_config should work even if current working directory is elsewhere."""
    # Change to a temporary directory
    cwd = os.getcwd()
    monkeypatch.chdir(tmp_path)

    def fake_loader(path):
        if path.endswith("default.yaml"):
            return {"app": {"name": "Crowbank Intranet"}}
        elif path.endswith("dev.yaml"):
            return {}
        elif path.endswith("secret.yaml"):
            return {}
        return {}

    monkeypatch.setattr(yaml_config, "load_yaml_file", fake_loader)

    try:
        config = yaml_config.load_config(env="dev")
    finally:
        os.chdir(cwd)

    assert config["nested"]["app"]["name"] == "Crowbank Intranet"
