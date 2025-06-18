"""
Email filtering functions for Gmail data processing.

This module contains functions to filter email data based on various criteria,
particularly for identifying application-related emails.
"""

import re
from email.utils import parseaddr

import pandas as pd


def extract_application_status_col(
    df: pd.DataFrame,
    label_name: str = "JOBS",
) -> pd.DataFrame:
    return df["Labels"].apply(
        lambda x: re.search(rf"{label_name}/(?P<status>[^/']+)", x).group("status")
    )


def extract_email_and_name(df: pd.DataFrame) -> pd.DataFrame:
    name = df["From"].apply(lambda x: parseaddr(x)[0])
    email = df["From"].apply(lambda x: parseaddr(x)[1])
    return name, email


def filter_out_sent(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["From"].str.startswith("Arthur Zakirov")]


def filter_df_by_label(
    df: pd.DataFrame,
    label_name: str = "JOBS",
) -> pd.DataFrame:
    df = df[df["Labels"].str.contains(label_name)]
    return df


def transform_dataframe(
    df: pd.DataFrame,
    label_name: str = "JOBS",
) -> pd.DataFrame:
    df = filter_df_by_label(df=df, label_name=label_name)
    df = filter_out_sent(df=df)
    df["ApplicationStatus"] = extract_application_status_col(df=df)
    df["Name"], df["Email"] = extract_email_and_name(df=df)
    df = df.drop(columns=["From", "Labels", "Body", "ID", "To"])
    return df


def extract_job_application_rows(
    df,
    columns=["Subject", "Body"],
    keywords=["application", "bewerbung"],
    exclude_keywords=["github"],
):
    """
    Filter DataFrame to get application-related rows.

    Args:
        df (pd.DataFrame): The DataFrame containing email data
        columns (list): List of column names to search in (default: ["Subject", "Body"])
        keywords (list): Keywords to search for (default: ["application", "bewerbung"])
        exclude_keywords (list): Keywords to exclude (default: ["github"])

    Returns:
        pd.DataFrame: Filtered DataFrame containing only application-related rows
                     that don't contain exclude keywords
    """
    pattern = "|".join(map(re.escape, keywords))
    exclude_pattern = "|".join(map(re.escape, exclude_keywords))

    combined_filter = pd.Series(False, index=df.index)
    exclude_filter = pd.Series(False, index=df.index)

    for col in columns:
        if col in df.columns:
            match = (
                df[col]
                .astype(str)
                .str.contains(pattern, case=False, regex=True, na=False)
            )
            combined_filter |= match

            exclude = (
                df[col]
                .astype(str)
                .str.contains(exclude_pattern, case=False, regex=True, na=False)
            )
            exclude_filter |= exclude

    final_filter = combined_filter & (~exclude_filter)
    return df[final_filter]
