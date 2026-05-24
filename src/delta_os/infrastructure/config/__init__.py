"""Config infrastructure."""

from delta_os.infrastructure.config.schema_validation import validate_config_shape
from delta_os.infrastructure.config.yaml_config_loader import YamlConfigLoader

__all__ = ["YamlConfigLoader", "validate_config_shape"]
