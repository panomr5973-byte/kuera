"""Tests for World Bank data connector."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.data.worldbank_connector import get_latest_economic_data, get_indicators_list


def test_latest_data_returns_dict():
    result = get_latest_economic_data()
    assert isinstance(result, dict)
    assert "status" in result


def test_indicators_list_returns_dict():
    result = get_indicators_list()
    assert isinstance(result, dict)
    assert "status" in result
