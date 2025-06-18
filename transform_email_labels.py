#!/usr/bin/env python3
"""
Email Label Transformer

This script transforms email data by filtering based on labels and extracting
application status information.
"""

import argparse
import logging
import os
import sys

import pandas as pd

from src.filters.email_filters import transform_dataframe


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Transform email data by filtering labels and extracting"
        " application status"
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
        default="transformed_labels.csv",
        help="Output CSV file path for transformed results "
        "(default: transformed_labels.csv)",
    )

    parser.add_argument(
        "-l",
        "--label-name",
        type=str,
        default="JOB",
        help="Label name to filter by (default: JOB)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be transformed without saving to file",
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


def transform_labels():
    """Main function to transform email labels."""
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
        required_columns = ["Labels", "From"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Required columns {missing_columns} not found in dataset. "
                f"Available columns: {list(df.columns)}"
            )

        # Log transformation parameters
        logging.info(f"Label name to filter: {args.label_name}")
        logging.info(f"Required columns found: {required_columns}")

        # Transform dataframe
        transformed_df = transform_dataframe(
            df=df,
            label_name=args.label_name,
        )

        logging.info(
            f"Transformed {len(transformed_df)} emails out of "
            f"{len(df)} total emails"
        )

        if args.dry_run:
            print("\nDry run results:")
            print(f"Total emails: {len(df)}")
            print(f"Emails with label '{args.label_name}': {len(transformed_df)}")
            print(f"Percentage: {len(transformed_df)/len(df)*100:.2f}%")

            if args.verbose and len(transformed_df) > 0:
                print("\nSample results (first 5 with ApplicationStatus column):")
                # Show sample of transformed results
                sample_columns = [
                    col
                    for col in ["Subject", "Name", "Email", "Date", "ApplicationStatus"]
                    if col in transformed_df.columns
                ]
                if sample_columns:
                    print(transformed_df[sample_columns].head().to_string(index=False))
                else:
                    print("No standard email columns found for preview")
        else:
            # Save transformed results
            transformed_df.to_csv(args.output, index=False)
            logging.info(
                f"Successfully saved {len(transformed_df)} transformed emails to "
                f"{args.output}"
            )

            print("Transformation complete!")
            print(f"Input: {args.input} ({len(df)} emails)")
            print(
                f"Output: {args.output} ({len(transformed_df)} emails with "
                f"ApplicationStatus, Name, and Email columns)"
            )
            print(f"Filter rate: {len(transformed_df)/len(df)*100:.2f}%")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error transforming email labels: {e}")
        sys.exit(1)


if __name__ == "__main__":
    transform_labels()
