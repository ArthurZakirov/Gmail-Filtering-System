"""
Unit tests for filter_job_applications.py CLI entrypoint functions
"""

import os
import sys

# Add the project root to the path - must be before local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import tempfile
from unittest.mock import Mock, patch

import pandas as pd
import pytest

import filter_job_applications


class TestParseArguments:
    """Test argument parsing functionality"""

    def test_default_arguments(self):
        """Test that default arguments are parsed correctly"""
        with patch("sys.argv", ["filter_job_applications.py", "-i", "test.csv"]):
            args = filter_job_applications.parse_arguments()
            assert args.input == "test.csv"
            assert args.output == "filtered_applications.csv"
            assert args.columns == ["Subject", "Body"]
            assert args.keywords == ["application", "bewerbung"]
            assert args.exclude_keywords == ["github"]
            assert args.verbose is False
            assert args.dry_run is False

    def test_custom_output_argument(self):
        """Test custom output file argument"""
        with patch(
            "sys.argv",
            [
                "filter_job_applications.py",
                "-i",
                "input.csv",
                "-o",
                "custom_output.csv",
            ],
        ):
            args = filter_job_applications.parse_arguments()
            assert args.output == "custom_output.csv"

    def test_custom_columns_argument(self):
        """Test custom columns argument"""
        with patch(
            "sys.argv",
            [
                "filter_job_applications.py",
                "-i",
                "input.csv",
                "-c",
                "Subject",
                "Content",
                "Body",
            ],
        ):
            args = filter_job_applications.parse_arguments()
            assert args.columns == ["Subject", "Content", "Body"]

    def test_custom_keywords_argument(self):
        """Test custom keywords argument"""
        with patch(
            "sys.argv",
            [
                "filter_job_applications.py",
                "-i",
                "input.csv",
                "-k",
                "job",
                "career",
                "position",
            ],
        ):
            args = filter_job_applications.parse_arguments()
            assert args.keywords == ["job", "career", "position"]

    def test_custom_exclude_keywords_argument(self):
        """Test custom exclude keywords argument"""
        with patch(
            "sys.argv",
            [
                "filter_job_applications.py",
                "-i",
                "input.csv",
                "-e",
                "spam",
                "newsletter",
            ],
        ):
            args = filter_job_applications.parse_arguments()
            assert args.exclude_keywords == ["spam", "newsletter"]

    def test_verbose_flag(self):
        """Test verbose flag"""
        with patch("sys.argv", ["filter_job_applications.py", "-i", "input.csv", "-v"]):
            args = filter_job_applications.parse_arguments()
            assert args.verbose is True

    def test_dry_run_flag(self):
        """Test dry run flag"""
        with patch(
            "sys.argv", ["filter_job_applications.py", "-i", "input.csv", "--dry-run"]
        ):
            args = filter_job_applications.parse_arguments()
            assert args.dry_run is True

    def test_long_form_arguments(self):
        """Test long form arguments"""
        with patch(
            "sys.argv",
            [
                "filter_job_applications.py",
                "--input",
                "emails.csv",
                "--output",
                "jobs.csv",
                "--columns",
                "Subject",
                "Body",
                "--keywords",
                "application",
                "job",
                "--exclude-keywords",
                "github",
                "spam",
                "--verbose",
                "--dry-run",
            ],
        ):
            args = filter_job_applications.parse_arguments()
            assert args.input == "emails.csv"
            assert args.output == "jobs.csv"
            assert args.columns == ["Subject", "Body"]
            assert args.keywords == ["application", "job"]
            assert args.exclude_keywords == ["github", "spam"]
            assert args.verbose is True
            assert args.dry_run is True


class TestValidateInputFile:
    """Test input file validation functionality"""

    def test_file_not_found(self):
        """Test error when file doesn't exist"""
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            filter_job_applications.validate_input_file("nonexistent.csv")

    def test_non_csv_file(self):
        """Test error when file is not CSV"""
        with pytest.raises(ValueError, match="Input file must be a CSV file"):
            filter_job_applications.validate_input_file("test.txt")

    def test_valid_csv_file(self):
        """Test validation passes for valid CSV file"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_file.write(b"Subject,Body\nTest,Content")
            temp_file.flush()

            try:
                # Should not raise any exception
                filter_job_applications.validate_input_file(temp_file.name)
            finally:
                os.unlink(temp_file.name)


class TestLoadEmailData:
    """Test email data loading functionality"""

    def test_load_valid_csv(self):
        """Test loading valid CSV data"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(
                "Subject,Body\nJob Application,I am applying for the "
                "position\nOther,Random content"
            )
            temp_file.flush()

            try:
                df = filter_job_applications.load_email_data(temp_file.name)
                assert len(df) == 2
                assert list(df.columns) == ["Subject", "Body"]
                assert df.iloc[0]["Subject"] == "Job Application"
            finally:
                os.unlink(temp_file.name)

    def test_load_invalid_csv(self):
        """Test error when loading invalid CSV"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write("Invalid CSV content without proper structure")
            temp_file.flush()

            try:
                with pytest.raises(Exception, match="Error loading CSV file"):
                    filter_job_applications.load_email_data(temp_file.name)
            finally:
                os.unlink(temp_file.name)


class TestFilterJobApplicationsFunction:
    """Test the main filter_job_applications function"""

    @patch("filter_job_applications.parse_arguments")
    @patch("filter_job_applications.validate_input_file")
    @patch("filter_job_applications.load_email_data")
    @patch("filter_job_applications.extract_job_application_rows")
    def test_successful_filtering(
        self, mock_extract, mock_load, mock_validate, mock_parse
    ):
        """Test successful filtering workflow"""
        # Setup mocks
        mock_args = Mock()
        mock_args.input = "input.csv"
        mock_args.output = "output.csv"
        mock_args.columns = ["Subject", "Body"]
        mock_args.keywords = ["application"]
        mock_args.exclude_keywords = ["github"]
        mock_args.verbose = False
        mock_args.dry_run = False
        mock_parse.return_value = mock_args

        mock_df = pd.DataFrame(
            {
                "Subject": ["Job Application", "Newsletter"],
                "Body": ["I am applying", "News content"],
            }
        )
        mock_load.return_value = mock_df

        mock_filtered_df = pd.DataFrame(
            {"Subject": ["Job Application"], "Body": ["I am applying"]}
        )
        mock_extract.return_value = mock_filtered_df

        # Mock to_csv method
        with patch.object(mock_filtered_df, "to_csv") as mock_to_csv:
            filter_job_applications.filter_job_applications()

            # Verify function calls
            mock_validate.assert_called_once_with("input.csv")
            mock_load.assert_called_once_with("input.csv")
            mock_extract.assert_called_once_with(
                df=mock_df,
                columns=["Subject", "Body"],
                keywords=["application"],
                exclude_keywords=["github"],
            )
            mock_to_csv.assert_called_once_with("output.csv", index=False)

    @patch("filter_job_applications.parse_arguments")
    @patch("filter_job_applications.validate_input_file")
    @patch("filter_job_applications.load_email_data")
    @patch("filter_job_applications.extract_job_application_rows")
    @patch("builtins.print")
    def test_dry_run_mode(
        self, mock_print, mock_extract, mock_load, mock_validate, mock_parse
    ):
        """Test dry run mode doesn't save file"""
        # Setup mocks
        mock_args = Mock()
        mock_args.input = "input.csv"
        mock_args.output = "output.csv"
        mock_args.columns = ["Subject", "Body"]
        mock_args.keywords = ["application"]
        mock_args.exclude_keywords = ["github"]
        mock_args.verbose = False
        mock_args.dry_run = True
        mock_parse.return_value = mock_args

        mock_df = pd.DataFrame(
            {
                "Subject": ["Job Application", "Newsletter"],
                "Body": ["I am applying", "News content"],
            }
        )
        mock_load.return_value = mock_df

        mock_filtered_df = pd.DataFrame(
            {"Subject": ["Job Application"], "Body": ["I am applying"]}
        )
        mock_extract.return_value = mock_filtered_df

        # Mock to_csv method to ensure it's not called
        with patch.object(mock_filtered_df, "to_csv") as mock_to_csv:
            filter_job_applications.filter_job_applications()

            # Verify to_csv is not called in dry run mode
            mock_to_csv.assert_not_called()

            # Verify print was called for dry run output
            mock_print.assert_called()
