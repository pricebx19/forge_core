"""Tests for the Config class."""

import os
import tempfile
import yaml
from pathlib import Path
import pytest

# Use package imports for consistent importing
from forge_core.config import Config, ConfigValue


def test_config_defaults():
    """Test that default configuration values are set correctly."""
    config = Config()
    assert config.debug is False
    assert config.env == "development"
    assert config.timezone == "UTC"
    assert config.log_level == "INFO"
    assert config.database["pool_size"] == 5
    assert config.http["port"] == 8000


def test_config_env_loading():
    """Test that environment variables are loaded correctly."""
    # Clean any existing vars
    for key in ["FORGE_DEBUG", "FORGE_ENV", "FORGE_DATABASE_URL", "FORGE_HTTP_PORT"]:
        if key in os.environ:
            del os.environ[key]
    
    # Set environment variables
    os.environ["FORGE_DEBUG"] = "true"
    os.environ["FORGE_ENV"] = "production"
    os.environ["FORGE_DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
    os.environ["FORGE_HTTP_PORT"] = "8080"

    config = Config()
    assert config.debug is True
    assert config.env == "production"
    assert config.database["url"] == "postgresql://user:pass@localhost:5432/db"
    assert config.http["port"] == 8080

    # Clean up
    del os.environ["FORGE_DEBUG"]
    del os.environ["FORGE_ENV"]
    del os.environ["FORGE_DATABASE_URL"]
    del os.environ["FORGE_HTTP_PORT"]


def test_config_file_loading():
    """Test that configuration files are loaded correctly."""
    config_data = """
    debug: true
    env: production
    database:
      url: postgresql://user:pass@localhost:5432/db
      pool_size: 10
    http:
      port: 8080
      workers: 4
    """

    # Write directly to a temp file we control
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_data)
        temp_path = f.name

    try:
        config = Config()
        config.load_file(temp_path)
        
        assert config.debug is True
        assert config.env == "production"
        assert config.database["url"] == "postgresql://user:pass@localhost:5432/db"
        assert config.database["pool_size"] == 10
        assert config.http["port"] == 8080
        assert config.http["workers"] == 4
    finally:
        # Clean up temp file
        if Path(temp_path).exists():
            os.unlink(temp_path)


def test_config_validation():
    """Test that configuration validation works correctly."""
    # Test 1: Required field validation
    config1 = Config()
    with pytest.raises(ValueError):
        config1.set("test_required_field", None)
        config1._validate()  # Explicitly validate

    # Test 2: Type validation
    config2 = Config()
    with pytest.raises(TypeError):
        # Set the value directly to bypass type conversion
        config2._values["http__port"] = ConfigValue("not_an_integer", int)
        config2._validate()

    # Test 3: Valid values
    config3 = Config()
    config3.set("secret_key", "valid_key")
    config3.set("http__port", 8080)
    assert config3.secret_key == "valid_key"
    assert config3.http["port"] == 8080


def test_config_value_validation():
    """Test that ConfigValue validation works correctly."""
    # Test required field
    value = ConfigValue(None, str, required=True)
    with pytest.raises(ValueError):
        value.validate()

    # Test type validation
    value = ConfigValue(123, str)
    with pytest.raises(TypeError):
        value.validate()

    # Test custom validator
    def is_positive(value):
        if value <= 0:
            raise ValueError("Value must be positive")

    value = ConfigValue(-1, int, validators=[is_positive])
    with pytest.raises(ValueError):
        value.validate()

    # Test valid value
    value = ConfigValue(1, int, validators=[is_positive])
    value.validate()
    assert value.value == 1


def test_config_to_dict():
    """Test that configuration can be converted to a dictionary."""
    config = Config()
    config.set("debug", True)
    config.set("database__url", "postgresql://user:pass@localhost:5432/db")
    config.set("http__port", 8080)

    config_dict = config.to_dict()
    assert config_dict["debug"] is True
    assert config_dict["database"]["url"] == "postgresql://user:pass@localhost:5432/db"
    assert config_dict["http"]["port"] == 8080 