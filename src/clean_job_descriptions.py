import html
import re
import unicodedata
from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

INPUT_PATH = Path(
    "data/processed/jobs_title_normalized.csv"
)

OUTPUT_PATH = Path(
    "data/processed/jobs_text_cleaned.csv"
)


# -------------------------------------------------------------------
# Text cleaning
# -------------------------------------------------------------------

def clean_description(text):
    """
    Clean a job description while preserving useful information
    for later skill extraction.

    The original description is never modified.
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # ---------------------------------------------------------------
    # 1. Decode HTML entities
    # ---------------------------------------------------------------

    text = html.unescape(text)

    # ---------------------------------------------------------------
    # 2. Remove HTML tags
    # ---------------------------------------------------------------

    text = re.sub(
        r"<[^>]+>",
        " ",
        text,
    )

    # ---------------------------------------------------------------
    # 3. Normalize Unicode
    # ---------------------------------------------------------------

    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    # ---------------------------------------------------------------
    # 4. Normalize common dash characters
    # ---------------------------------------------------------------

    text = (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )

    # ---------------------------------------------------------------
    # 5. Replace line breaks / tabs with spaces
    # ---------------------------------------------------------------

    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text,
    )

    # ---------------------------------------------------------------
    # 6. Normalize repeated whitespace
    # ---------------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    # ---------------------------------------------------------------
    # 7. Remove leading/trailing whitespace
    # ---------------------------------------------------------------

    text = text.strip()

    return text


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

def validate_input(df):

    required_columns = [
        "job_id",
        "job_title",
        "normalized_title",
        "title_family",
        "role_category",
        "role_relevance",
        "description",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():

    print("\nGradPath Job Description Cleaning")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------------

    df = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"\nLoaded jobs: {len(df)}"
    )

    validate_input(df)

    # ---------------------------------------------------------------
    # Missing values before cleaning
    # ---------------------------------------------------------------

    missing_before = (
        df["description"]
        .isna()
        .sum()
    )

    # ---------------------------------------------------------------
    # Clean descriptions
    # ---------------------------------------------------------------

    df["description_clean"] = (
        df["description"]
        .apply(clean_description)
    )

    # ---------------------------------------------------------------
    # Missing / empty values after cleaning
    # ---------------------------------------------------------------

    missing_after = (
        df["description_clean"]
        .isna()
        .sum()
    )

    empty_after = (
        df["description_clean"]
        .str.strip()
        .eq("")
        .sum()
    )

    # ---------------------------------------------------------------
    # Length statistics
    # ---------------------------------------------------------------

    original_lengths = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.len()
    )

    clean_lengths = (
        df["description_clean"]
        .str.len()
    )

    # ---------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    print("\n" + "=" * 60)
    print("CLEANING SUMMARY")
    print("=" * 60)

    print(
        f"\nRows processed: "
        f"{len(df)}"
    )

    print(
        f"Missing descriptions before: "
        f"{missing_before}"
    )

    print(
        f"Missing descriptions after: "
        f"{missing_after}"
    )

    print(
        f"Empty descriptions after: "
        f"{empty_after}"
    )

    print("\nOriginal description length:")

    print(
        f"Min:    {original_lengths.min()}"
    )

    print(
        f"Max:    {original_lengths.max()}"
    )

    print(
        f"Mean:   {original_lengths.mean():.2f}"
    )

    print(
        f"Median: {original_lengths.median():.2f}"
    )

    print("\nClean description length:")

    print(
        f"Min:    {clean_lengths.min()}"
    )

    print(
        f"Max:    {clean_lengths.max()}"
    )

    print(
        f"Mean:   {clean_lengths.mean():.2f}"
    )

    print(
        f"Median: {clean_lengths.median():.2f}"
    )

    print("\nOutput:")
    print(OUTPUT_PATH)

    print("\nDescription cleaning complete.")


if __name__ == "__main__":
    main()