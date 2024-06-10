import pytest
import shelve
from unittest.mock import MagicMock

from fetch import save_to_cache, load_from_cache

@pytest.fixture
def mock_shelve(monkeypatch):
    # Create a mock shelf object
    mock_shelf = MagicMock()
    # Mock the shelve.open method to return the mock shelf
    monkeypatch.setattr(shelve, 'open', MagicMock(return_value=mock_shelf))
    return mock_shelf

def test_save_to_cache(mock_shelve):
    key = 'test_key'
    value = 'test_value'
    
    save_to_cache(key, value)
    
    # Assert that the value was set correctly in the mock shelf
    mock_shelve.__enter__.return_value.__setitem__.assert_called_once_with(key, value)

def test_load_from_cache(mock_shelve):
    key = 'test_key'
    value = 'test_value'
    
    # Set the return value for the mock shelf
    mock_shelve.__enter__.return_value.get.return_value = value
    
    result = load_from_cache(key)

    # Assert that the returned value is as expected
    assert result == value
    mock_shelve.__enter__.return_value.get.assert_called_once_with(key)

def test_load_empty_from_cache(mock_shelve):
    value = 'true_value'
    false_key = 'false_key'

    result = load_from_cache(false_key)

    assert result != value
