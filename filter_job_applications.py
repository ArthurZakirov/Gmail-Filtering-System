#!/usr/bin/env python3
"""
Job Application Email Filter

This script filters email data to extract job application-related emails
based on keywords.
"""

import argparse
import logging
import os
import sys

# Add the src directory to the path to import the filter function
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Also add current directory to path for relative imports during git hooks
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import pandas as pd

try:
    from filters.email_filters import extract_job_application_rows
except ImportError:
    # Fallback for git hook execution
    from src.filters.email_filters import extract_job_application_rows


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Filter email data to extract job application-related emails"
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input CSV file path containing email data",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="filtered_applications.csv",
        help="Output CSV file path for filtered results "
        "(default: filtered_applications.csv)",
    )

    parser.add_argument(
        "-c",
        "--columns",
        nargs="+",
        default=["Subject", "Body"],
        help="Column names to search in (default: Subject Body)",
    )

    parser.add_argument(
        "-k",
        "--keywords",
        nargs="+",
        default=["application", "bewerbung"],
        help="Keywords to search for (default: application bewerbung)",
    )

    parser.add_argument(
        "-e",
        "--exclude-keywords",
        nargs="+",
        default=["github"],
        help="Keywords to exclude (default: github)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be filtered without saving to file",
    )

    return parser.parse_args()


def validate_input_file(file_path):
    """Validate that the input file exists and is a CSV file."""
    if not file_path.lower().endswith(".csv"):
        raise ValueError(f"Input file must be a CSV file: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")


def load_email_data(file_path):
    """Load email data from CSV file."""
    try:
        df = pd.read_csv(file_path)
        if df.empty or len(df.columns) == 0:
            raise ValueError("CSV file is empty or has no columns")
        logging.info(f"Loaded {len(df)} emails from {file_path}")
        logging.debug(f"Columns in dataset: {list(df.columns)}")
        return df
    except Exception as e:
        raise Exception(f"Error loading CSV file: {e}")


def filter_job_applications():
    """Main function to filter job application emails."""
    args = parse_arguments()

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        # Validate input file
        validate_input_file(args.input)

        # Load email data
        df = load_email_data(args.input)

        # Check if required columns exist
        missing_columns = [col for col in args.columns if col not in df.columns]
        if missing_columns:
            logging.warning(f"Missing columns in dataset: {missing_columns}")
            available_columns = [col for col in args.columns if col in df.columns]
            if not available_columns:
                raise ValueError(
                    f"None of the specified columns exist in the dataset. "
                    f"Available columns: {list(df.columns)}"
                )
            args.columns = available_columns
            logging.info(f"Using available columns: {args.columns}")

        # Log filtering parameters
        logging.info(f"Filtering with keywords: {args.keywords}")
        logging.info(f"Excluding keywords: {args.exclude_keywords}")
        logging.info(f"Searching in columns: {args.columns}")

        # Filter job applications
        filtered_df = extract_job_application_rows(
            df=df,
            columns=args.columns,
            keywords=args.keywords,
            exclude_keywords=args.exclude_keywords,
        )

        logging.info(
            f"Found {len(filtered_df)} job application emails out of "
            f"{len(df)} total emails"
        )

        if args.dry_run:
            print("\nDry run results:")
            print(f"Total emails: {len(df)}")
            print(f"Job application emails found: {len(filtered_df)}")
            print(f"Percentage: {len(filtered_df)/len(df)*100:.2f}%")

            if args.verbose and len(filtered_df) > 0:
                print("\nSample results (first 5):")
                # Show sample of filtered results
                sample_columns = [
                    col
                    for col in ["Subject", "From", "Date"]
                    if col in filtered_df.columns
                ]
                if sample_columns:
                    print(filtered_df[sample_columns].head().to_string(index=False))
                else:
                    print("No standard email columns found for preview")
        else:
            # Save filtered results
            filtered_df.to_csv(args.output, index=False)
            logging.info(
                f"Successfully saved {len(filtered_df)} filtered emails to "
                f"{args.output}"
            )

            print("Filtering complete!")
            print(f"Input: {args.input} ({len(df)} emails)")
            print(f"Output: {args.output} ({len(filtered_df)} job application emails)")
            print(f"Filter rate: {len(filtered_df)/len(df)*100:.2f}%")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error filtering job applications: {e}")
        sys.exit(1)


if __name__ == "__main__":
    filter_job_applications()
