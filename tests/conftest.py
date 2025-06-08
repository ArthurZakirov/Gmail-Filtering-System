"""
Pytest configuration and shared fixtures
"""

import os
import sys
import tempfile
from unittest.mock import Mock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service for testing"""
    service = Mock()
    messages_mock = service.users.return_value.messages.return_value
    messages_mock.list.return_value.execute.return_value = {
        "messages": [{"id": "test_message_id"}],
        "resultSizeEstimate": 1,
    }
    messages_mock.get.return_value.execute.return_value = {
        "id": "test_message_id",
        "payload": {
            "headers": [
                {"name": "From", "value": "test@example.com"},
                {"name": "Subject", "value": "Test Subject"},
                {"name": "Date", "value": "Mon, 1 Jan 2025 12:00:00 +0000"},
            ]
        },
        "labelIds": ["INBOX"],
    }
    return service


@pytest.fixture
def sample_credentials():
    """Sample credentials for testing"""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "token": "test_token",
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Store original sys.argv
    original_argv = sys.argv.copy()
    yield
    # Restore original sys.argv
    sys.argv = original_argv
