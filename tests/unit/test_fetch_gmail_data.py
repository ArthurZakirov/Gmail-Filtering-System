"""
Unit tests for fetch_gmail_data.py CLI entrypoint functions
"""

import os
import sys

# Add the project root to the path - must be before local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import argparse
from datetime import datetime
from unittest.mock import Mock, patch

import fetch_gmail_data


class TestParseArguments:
    """Test argument parsing functionality"""

    def test_default_arguments(self):
        """Test that default arguments are parsed correctly"""
        with patch("sys.argv", ["fetch_gmail_data.py"]):
            args = fetch_gmail_data.parse_arguments()
            assert args.query == "after:2025/03/01 before:2025/03/30"
            assert args.output == "data.csv"
            assert args.token == "config/token.json"
            assert args.verbose is False
            assert args.after is None
            assert args.before is None
            assert args.last_days is None

    def test_custom_query_argument(self):
        """Test custom query argument"""
        with patch("sys.argv", ["fetch_gmail_data.py", "-q", "from:test@example.com"]):
            args = fetch_gmail_data.parse_arguments()
            assert args.query == "from:test@example.com"

    def test_output_file_argument(self):
        """Test custom output file argument"""
        with patch("sys.argv", ["fetch_gmail_data.py", "-o", "custom_output.csv"]):
            args = fetch_gmail_data.parse_arguments()
            assert args.output == "custom_output.csv"

    def test_token_path_argument(self):
        """Test custom token path argument"""
        with patch("sys.argv", ["fetch_gmail_data.py", "-t", "custom/token.json"]):
            args = fetch_gmail_data.parse_arguments()
            assert args.token == "custom/token.json"

    def test_verbose_flag(self):
        """Test verbose flag"""
        with patch("sys.argv", ["fetch_gmail_data.py", "-v"]):
            args = fetch_gmail_data.parse_arguments()
            assert args.verbose is True

    def test_date_arguments(self):
        """Test after and before date arguments"""
        with patch(
            "sys.argv",
            ["fetch_gmail_data.py", "--after", "2025/01/01", "--before", "2025/01/31"],
        ):
            args = fetch_gmail_data.parse_arguments()
            assert args.after == "2025/01/01"
            assert args.before == "2025/01/31"

    def test_last_days_argument(self):
        """Test last days argument"""
        with patch("sys.argv", ["fetch_gmail_data.py", "--last-days", "7"]):
            args = fetch_gmail_data.parse_arguments()
            assert args.last_days == 7

    def test_long_form_arguments(self):
        """Test long form arguments"""
        with patch(
            "sys.argv",
            [
                "fetch_gmail_data.py",
                "--query",
                "from:test@example.com",
                "--output",
                "test.csv",
                "--token",
                "custom.json",
                "--verbose",
            ],
        ):
            args = fetch_gmail_data.parse_arguments()
            assert args.query == "from:test@example.com"
            assert args.output == "test.csv"
            assert args.token == "custom.json"
            assert args.verbose is True


class TestBuildQuery:
    """Test query building functionality"""

    def test_build_query_default(self):
        """Test building query with default arguments"""
        args = argparse.Namespace(
            query="default query", last_days=None, after=None, before=None
        )
        query = fetch_gmail_data.build_query(args)
        assert query == "default query"

    def test_build_query_last_days(self):
        """Test building query with last_days parameter"""
        args = argparse.Namespace(
            query="default query", last_days=7, after=None, before=None
        )
        with patch("fetch_gmail_data.datetime") as mock_datetime:
            mock_now = datetime(2025, 6, 7, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime

            query = fetch_gmail_data.build_query(args)
            expected = "after:2025/05/31 before:2025/06/07"
            assert query == expected

    def test_build_query_date_range(self):
        """Test building query with after and before dates"""
        args = argparse.Namespace(
            query="default query",
            last_days=None,
            after="2025/01/01",
            before="2025/01/31",
        )
        query = fetch_gmail_data.build_query(args)
        assert query == "after:2025/01/01 before:2025/01/31"

    def test_build_query_only_after(self):
        """Test building query with only after date"""
        args = argparse.Namespace(
            query="default query", last_days=None, after="2025/01/01", before=None
        )
        query = fetch_gmail_data.build_query(args)
        assert query == "after:2025/01/01"

    def test_build_query_only_before(self):
        """Test building query with only before date"""
        args = argparse.Namespace(
            query="default query", last_days=None, after=None, before="2025/01/31"
        )
        query = fetch_gmail_data.build_query(args)
        assert query == "before:2025/01/31"

    def test_build_query_last_days_priority(self):
        """Test that last_days takes priority over other date options"""
        args = argparse.Namespace(
            query="default query", last_days=5, after="2025/01/01", before="2025/01/31"
        )
        with patch("fetch_gmail_data.datetime") as mock_datetime:
            mock_now = datetime(2025, 6, 7, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime

            query = fetch_gmail_data.build_query(args)
            expected = "after:2025/06/02 before:2025/06/07"
            assert query == expected


class TestFetchGmailDataFunction:
    """Test individual components of the fetch_gmail_data function"""

    @patch("fetch_gmail_data.fetch_gmail_messages_as_df")
    @patch("fetch_gmail_data.build")
    @patch("fetch_gmail_data.Credentials.from_authorized_user_file")
    @patch("fetch_gmail_data.os.path.exists")
    @patch("fetch_gmail_data.parse_arguments")
    def test_successful_data_fetch_flow(
        self, mock_parse_args, mock_exists, mock_creds, mock_build, mock_fetch_df
    ):
        """Test the successful flow of fetching Gmail data"""
        # Setup mocks
        mock_args = Mock()
        mock_args.token = "config/token.json"
        mock_args.output = "test_output.csv"
        mock_args.verbose = False
        mock_args.query = "test query"
        mock_args.after = None
        mock_args.before = None
        mock_args.last_days = None
        mock_parse_args.return_value = mock_args

        mock_exists.return_value = True
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Create a mock DataFrame
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=5)
        mock_fetch_df.return_value = mock_df

        # Execute
        fetch_gmail_data.fetch_gmail_data()

        # Verify
        mock_exists.assert_called_once_with("config/token.json")
        mock_creds.assert_called_once()
        mock_build.assert_called_once_with(
            "gmail", "v1", credentials=mock_creds.return_value
        )
        mock_fetch_df.assert_called_once_with(mock_service, q="test query")
        mock_df.to_csv.assert_called_once_with("test_output.csv", index=False)

    @patch("fetch_gmail_data.os.path.exists")
    @patch("fetch_gmail_data.parse_arguments")
    @patch("fetch_gmail_data.sys.exit")
    def test_missing_token_file_handling(self, mock_exit, mock_parse_args, mock_exists):
        """Test handling when token file is missing"""
        mock_args = Mock()
        mock_args.token = "config/token.json"
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args

        mock_exists.return_value = False

        fetch_gmail_data.fetch_gmail_data()

        mock_exit.assert_called_once_with(1)

    @patch("fetch_gmail_data.fetch_gmail_messages_as_df")
    @patch("fetch_gmail_data.build")
    @patch("fetch_gmail_data.Credentials.from_authorized_user_file")
    @patch("fetch_gmail_data.os.path.exists")
    @patch("fetch_gmail_data.parse_arguments")
    @patch("fetch_gmail_data.sys.exit")
    def test_api_error_handling(
        self,
        mock_exit,
        mock_parse_args,
        mock_exists,
        mock_creds,
        mock_build,
        mock_fetch_df,
    ):
        """Test handling of API errors"""
        mock_args = Mock()
        mock_args.token = "config/token.json"
        mock_args.verbose = False
        mock_args.query = "test query"
        mock_args.after = None
        mock_args.before = None
        mock_args.last_days = None
        mock_parse_args.return_value = mock_args

        mock_exists.return_value = True
        mock_fetch_df.side_effect = Exception("API Error")

        fetch_gmail_data.fetch_gmail_data()

        mock_exit.assert_called_once_with(1)

    @patch("fetch_gmail_data.fetch_gmail_messages_as_df")
    @patch("fetch_gmail_data.build")
    @patch("fetch_gmail_data.Credentials.from_authorized_user_file")
    @patch("fetch_gmail_data.os.path.exists")
    @patch("fetch_gmail_data.parse_arguments")
    @patch("fetch_gmail_data.sys.exit")
    def test_file_not_found_error_handling(
        self,
        mock_exit,
        mock_parse_args,
        mock_exists,
        mock_creds,
        mock_build,
        mock_fetch_df,
    ):
        """Test handling of FileNotFoundError"""
        mock_args = Mock()
        mock_args.token = "config/token.json"
        mock_args.verbose = False
        mock_args.query = "test query"
        mock_args.after = None
        mock_args.before = None
        mock_args.last_days = None
        mock_parse_args.return_value = mock_args

        mock_exists.return_value = True
        mock_fetch_df.side_effect = FileNotFoundError("File not found")

        fetch_gmail_data.fetch_gmail_data()

        mock_exit.assert_called_once_with(1)
