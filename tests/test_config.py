# @generated [all] Gemini
from geochange.config import SETTINGS


def test_config_is_loaded():
    """Test that the config is loaded and is a dictionary"""
    assert isinstance(SETTINGS, dict)


def test_config_has_required_keys():
    """Test that the most critical configuration sections exist"""
    assert "api" in SETTINGS
    assert "analysis" in SETTINGS

    # Check if hemisphere data exists
    assert "northern_hemisphere" in SETTINGS["analysis"]
    assert "southern_hemisphere" in SETTINGS["analysis"]