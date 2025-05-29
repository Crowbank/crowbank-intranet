import importlib.util
import sys
import types
from pathlib import Path

# Provide a minimal stub for the unavailable `yaml` package
sys.modules['yaml'] = types.SimpleNamespace()

# Dynamically load the yaml_config module without importing the whole `app` package
spec = importlib.util.spec_from_file_location(
    'yaml_config', Path('app/utils/yaml_config.py')
)
yaml_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yaml_config)


def stub_load_yaml_file(path: str):
    """Return in-memory config data for the requested YAML file."""
    if path.endswith('default.yaml'):
        return {
            'session': {
                'permanent_lifetime': 86400,
                'type': 'filesystem',
            },
            'sqlalchemy': {
                'track_modifications': False,
            },
        }
    if path.endswith('dev.yaml'):
        return {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'crowbank',
            },
            'sqlalchemy': {
                'echo': True,
                'track_modifications': True,
            },
            'logging': {
                'level': 'DEBUG',
            },
            'development': {
                'debug_toolbar_enabled': True,
                'debug_toolbar_intercept_redirects': False,
            },
        }
    if path.endswith('secret.yaml'):
        return {
            'database': {
                'user': 'devuser',
                'password': 'devpass',
            }
        }
    return {}


def test_load_config_dev(monkeypatch):
    """Ensure environment configs merge correctly and produce a flat mapping."""
    # Patch the YAML loader with our stub data
    monkeypatch.setattr(yaml_config, 'load_yaml_file', stub_load_yaml_file)

    config = yaml_config.load_config('dev')

    nested = config['nested']
    flat = config['flat']

    # Nested values from environment config should be present
    assert nested['development']['debug_toolbar_enabled'] is True
    # Default values should remain
    assert nested['session']['permanent_lifetime'] == 86400

    # Flattened configuration should contain upper-case keys
    assert 'SQLALCHEMY_DATABASE_URI' in flat
    assert (
        flat['SQLALCHEMY_DATABASE_URI']
        == 'postgresql://devuser:devpass@localhost:5432/crowbank'
    )
