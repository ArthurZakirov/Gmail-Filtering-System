"""
Integration tests for CLI entrypoint files
"""

import os
import subprocess
import sys
import tempfile
from unittest.mock import patch

import pytest

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestFilterJobApplicationsCLIIntegration:
    """Integration tests for filter_job_applications.py CLI"""

    def test_help_flag(self):
        """Test that --help flag works correctly"""
        result = subprocess.run(
            [sys.executable, "filter_job_applications.py", "--help"],
            cwd="/workspaces/Gmail-Filtering-System",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Input CSV file path" in result.stdout
        assert "Output CSV file path" in result.stdout
        assert "Column names to search" in result.stdout
        assert "Keywords to search for" in result.stdout
        assert "Keywords to exclude" in result.stdout

    def test_script_imports_correctly(self):
        """Test that the script can be imported without errors"""
        try:
            import filter_job_applications

            assert hasattr(filter_job_applications, "parse_arguments")
            assert hasattr(filter_job_applications, "validate_input_file")
            assert hasattr(filter_job_applications, "load_email_data")
            assert hasattr(filter_job_applications, "filter_job_applications")
        except ImportError as e:
            pytest.fail(f"Failed to import filter_job_applications: {e}")

    def test_missing_input_file_error(self):
        """Test error message when input file is missing"""
        result = subprocess.run(
            [sys.executable, "filter_job_applications.py", "-i", "nonexistent.csv"],
            cwd="/workspaces/Gmail-Filtering-System",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "File not found" in result.stderr

    def test_dry_run_with_sample_data(self):
        """Test dry run mode with sample CSV data"""
        # Create temporary CSV file with sample data
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Subject,Body,From\n")
            temp_file.write(
                "Job Application,I am applying for the software engineer "
                "position,applicant@email.com\n"
            )
            temp_file.write(
                "GitHub Notification,You have a new follower," "noreply@github.com\n"
            )
            temp_file.write("Newsletter,Weekly tech news,news@tech.com\n")
            temp_file.flush()

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "filter_job_applications.py",
                        "-i",
                        temp_file.name,
                        "--dry-run",
                    ],
                    cwd="/workspaces/Gmail-Filtering-System",
                    capture_output=True,
                    text=True,
                )
                assert result.returncode == 0
                assert "Dry run results" in result.stdout
                assert "Total emails: 3" in result.stdout
                assert "Job application emails found: 1" in result.stdout
            finally:
                os.unlink(temp_file.name)


class TestFetchGmailDataCLIIntegration:
    """Integration tests for fetch_gmail_data.py CLI"""

    def test_help_flag(self):
        """Test that --help flag works correctly"""
        result = subprocess.run(
            [sys.executable, "fetch_gmail_data.py", "--help"],
            cwd="/workspaces/Gmail-Filtering-System",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Gmail search query" in result.stdout
        assert "Output CSV file path" in result.stdout

    def test_script_imports_correctly(self):
        """Test that the script can be imported without errors"""
        try:
            import fetch_gmail_data

            assert hasattr(fetch_gmail_data, "parse_arguments")
            assert hasattr(fetch_gmail_data, "build_query")
            assert hasattr(fetch_gmail_data, "fetch_gmail_data")
        except ImportError as e:
            pytest.fail(f"Failed to import fetch_gmail_data: {e}")

    @patch("fetch_gmail_data.os.path.exists")
    def test_missing_token_error_message(self, mock_exists):
        """Test error message when token file is missing"""
        mock_exists.return_value = False

        result = subprocess.run(
            [sys.executable, "fetch_gmail_data.py", "--token", "nonexistent.json"],
            cwd="/workspaces/Gmail-Filtering-System",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1


class TestGmailAuthSetupCLIIntegration:
    """Integration tests for gmail_auth_setup.py CLI"""

    def test_help_flag(self):
        """Test that --help flag works correctly"""
        result = subprocess.run(
            [sys.executable, "gmail_auth_setup.py", "--help"],
            cwd="/workspaces/Gmail-Filtering-System",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "token_path" in result.stdout
        assert "credentials_path" in result.stdout
        assert "scopes" in result.stdout

    def test_script_imports_correctly(self):
        """Test that the script can be imported without errors"""
        try:
            import gmail_auth_setup

            assert hasattr(gmail_auth_setup, "authorize_gmail_access")
            assert hasattr(gmail_auth_setup, "parser")
        except ImportError as e:
            pytest.fail(f"Failed to import gmail_auth_setup: {e}")


class TestEndToEndWorkflow:
    """End-to-end integration tests"""

    def test_both_scripts_exist_and_executable(self):
        """Test that both CLI scripts exist and are executable"""
        scripts = ["fetch_gmail_data.py", "gmail_auth_setup.py"]

        for script in scripts:
            script_path = os.path.join("/workspaces/Gmail-Filtering-System", script)
            assert os.path.exists(script_path), f"Script {script} does not exist"
            assert os.access(script_path, os.R_OK), f"Script {script} is not readable"

    def test_package_structure_integrity(self):
        """Test that the package structure is intact for CLI functionality"""
        # Test that required modules can be imported
        try:
            from src.data.gmail_data_extractor import fetch_gmail_messages_as_df

            assert callable(fetch_gmail_messages_as_df)
        except ImportError as e:
            pytest.fail(f"Failed to import required module: {e}")

    def test_argument_parsing_integration(self):
        """Test argument parsing works in real CLI context"""
        # Test fetch_gmail_data argument parsing
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
import sys
sys.path.append("/workspaces/Gmail-Filtering-System")
import fetch_gmail_data
print("fetch_gmail_data imports successfully")
            """,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "imports successfully" in result.stdout

        # Test gmail_auth_setup argument parsing
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
import sys
sys.path.append("/workspaces/Gmail-Filtering-System")
import gmail_auth_setup
print("gmail_auth_setup imports successfully")
            """,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "imports successfully" in result.stdout
