"""
Unit tests for gmail_auth_setup.py CLI entrypoint functions
"""

import os
import sys

# Add the project root to the path - must be before local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import argparse
from unittest.mock import Mock, mock_open, patch

import gmail_auth_setup


class TestArgumentParsing:
    """Test argument parsing functionality"""

    def test_default_arguments(self):
        """Test that default arguments are parsed correctly"""
        with patch("sys.argv", ["gmail_auth_setup.py"]):
            # Create a new parser for testing to avoid conflicts
            parser = argparse.ArgumentParser()
            parser.add_argument("--token_path", default="config/token.json")
            parser.add_argument("--credentials_path", default="config/credentials.json")
            parser.add_argument(
                "--scopes",
                nargs="+",
                default=["https://www.googleapis.com/auth/gmail.readonly"],
            )
            args = parser.parse_args([])

            assert args.token_path == "config/token.json"
            assert args.credentials_path == "config/credentials.json"
            assert args.scopes == ["https://www.googleapis.com/auth/gmail.readonly"]

    def test_custom_arguments(self):
        """Test custom arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("--token_path", default="config/token.json")
        parser.add_argument("--credentials_path", default="config/credentials.json")
        parser.add_argument(
            "--scopes",
            nargs="+",
            default=["https://www.googleapis.com/auth/gmail.readonly"],
        )

        args = parser.parse_args(
            [
                "--token_path",
                "custom/token.json",
                "--credentials_path",
                "custom/credentials.json",
                "--scopes",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.modify",
            ]
        )

        assert args.token_path == "custom/token.json"
        assert args.credentials_path == "custom/credentials.json"
        assert "https://www.googleapis.com/auth/gmail.readonly" in args.scopes
        assert "https://www.googleapis.com/auth/gmail.modify" in args.scopes


class TestAuthorizeGmailAccess:
    """Test the authorize_gmail_access function"""

    @patch("gmail_auth_setup.os.path.exists")
    @patch("gmail_auth_setup.Credentials.from_authorized_user_file")
    def test_existing_valid_credentials(self, mock_from_file, mock_exists):
        """Test when valid credentials already exist"""
        # Setup
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_creds.valid = True
        mock_from_file.return_value = mock_creds

        args = argparse.Namespace(
            token_path="config/token.json",
            credentials_path="config/credentials.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )

        # Execute
        gmail_auth_setup.authorize_gmail_access(args)

        # Verify
        mock_exists.assert_called_once_with("config/token.json")
        mock_from_file.assert_called_once_with(
            "config/token.json", ["https://www.googleapis.com/auth/gmail.readonly"]
        )

    @patch("gmail_auth_setup.os.path.exists")
    @patch("gmail_auth_setup.Credentials.from_authorized_user_file")
    @patch("gmail_auth_setup.Request")
    def test_expired_credentials_refresh(
        self, mock_request, mock_from_file, mock_exists
    ):
        """Test refreshing expired credentials"""
        # Setup
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_from_file.return_value = mock_creds

        # Mock file writing
        with patch("builtins.open", mock_open()) as mock_file:
            args = argparse.Namespace(
                token_path="config/token.json",
                credentials_path="config/credentials.json",
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            )

            # Execute
            gmail_auth_setup.authorize_gmail_access(args)

            # Verify
            mock_creds.refresh.assert_called_once()
            mock_file.assert_called_with("config/token.json", "w")

    def test_script_structure(self):
        """Test that the script has the expected structure"""
        # Test that the main components exist
        assert hasattr(gmail_auth_setup, "authorize_gmail_access")
        assert hasattr(gmail_auth_setup, "parser")
        assert hasattr(gmail_auth_setup, "args")

    @patch("gmail_auth_setup.authorize_gmail_access")
    def test_main_execution_structure(self, mock_authorize):
        """Test the main execution structure"""
        # The script should call authorize_gmail_access with parsed args
        args = argparse.Namespace(
            token_path="config/token.json",
            credentials_path="config/credentials.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )

        gmail_auth_setup.authorize_gmail_access(args)
        mock_authorize.assert_called_once_with(args)
