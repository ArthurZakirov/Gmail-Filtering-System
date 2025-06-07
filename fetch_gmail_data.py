#!/usr/bin/env python3
"""
Gmail Data Fetcher

This script fetches Gmail data using the Gmail API and saves it to a CSV file.
"""

import argparse
import logging
import os
import pandas as pd
import urllib
import sys
from datetime import datetime, timedelta

sys.path.append("..")
from src.data.gmail_data_extractor import fetch_gmail_messages_as_df

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch Gmail data using Gmail API and save to CSV"
    )
    
    parser.add_argument(
        "-q", "--query",
        type=str,
        default="after:2025/03/01 before:2025/03/30",
        help="Gmail search query (default: after:2025/03/01 before:2025/03/30)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="data.csv",
        help="Output CSV file path (default: data.csv)"
    )
    
    parser.add_argument(
        "-t", "--token",
        type=str,
        default="config/token.json",
        help="Path to token.json file (default: config/token.json)"
    )
    
    parser.add_argument(
        "--after",
        type=str,
        help="Fetch emails after this date (format: YYYY/MM/DD). Overrides query if provided."
    )
    
    parser.add_argument(
        "--before",
        type=str,
        help="Fetch emails before this date (format: YYYY/MM/DD). Overrides query if provided."
    )
    
    parser.add_argument(
        "--last-days",
        type=int,
        help="Fetch emails from the last N days. Overrides other date options if provided."
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def build_query(args):
    """Build the Gmail search query based on arguments."""
    if args.last_days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.last_days)
        query = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"
        logging.info(f"Using last {args.last_days} days: {query}")
        return query
    
    if args.after or args.before:
        query_parts = []
        if args.after:
            query_parts.append(f"after:{args.after}")
        if args.before:
            query_parts.append(f"before:{args.before}")
        query = " ".join(query_parts)
        logging.info(f"Using date range: {query}")
        return query
    
    logging.info(f"Using query: {args.query}")
    return args.query


def fetch_gmail_data():
    """Main function to fetch Gmail data."""
    args = parse_arguments()
    
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if not os.path.exists(args.token):
        logging.error(f"Token file not found at {args.token}")
        logging.error("Please run gmail_auth_setup.py first to generate the token file.")
        sys.exit(1)
    
    logging.debug(f"Using token file: {args.token}")
    logging.debug(f"Output file: {args.output}")
    
    try:
        scope_access_keys = ["auth/gmail.readonly"]
        SCOPES_ROOT = "https://www.googleapis.com"
        SCOPES = [urllib.parse.urljoin(SCOPES_ROOT, access_key) for access_key in scope_access_keys]
        
        creds = Credentials.from_authorized_user_file(args.token, SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        
        logging.debug("Gmail service built successfully")
        
        query = build_query(args)

        logging.info(f"Fetching emails with query: {query}")
        
        df = fetch_gmail_messages_as_df(service, q=query)
        
        logging.info(f"Fetched {len(df)} emails")
        
        df.to_csv(args.output, index=False)
        
        logging.info(f"Successfully saved {len(df)} emails to {args.output}")
        
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error fetching Gmail data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    fetch_gmail_data()