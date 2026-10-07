import re
from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

INPUT_PATH = Path(
    "data/processed/jobs_title_normalized.csv"
)

OUTPUT_PATH = Path(
    "data/processed/jobs_title_normalized.csv"
)


# -------------------------------------------------------------------
# Pattern groups
# -------------------------------------------------------------------

DATA_ANALYST_PATTERNS = [
    r"\bdata analyst\b",
    r"\bbi analyst\b",
    r"\breporting analyst\b",
    r"\bpower bi\b.*\banalyst\b",
    r"\banalyst\b.*\bpower bi\b",
    r"\bdata management analyst\b",
    r"\banalytics analyst\b",
    r"\bbusiness intelligence analyst\b",
]


DATA_SCIENTIST_PATTERNS = [
    r"\bdata scientist\b",
    r"\bdata science\b",
    r"\bapplied scientist\b",
    r"\bmachine learning scientist\b",
    r"\bdata science researcher\b",
]


ADJACENT_AI_ML_PATTERNS = [
    r"\bmachine learning engineer\b",
    r"\bml engineer\b",
    r"\bai engineer\b",
    r"\bai developer\b",
    r"\bsenior ai developer\b",
    r"\bmachine learning developer\b",
    r"\bai/ml\b",
    r"\bmachine learning\b.*\bengineer\b",
    r"\bengineer\b.*\bmachine learning\b",
]


ADJACENT_DATA_ENGINEERING_PATTERNS = [
    r"\bdata engineer\b",
    r"\bdata engineering\b",
    r"\betl\b.*\bdeveloper\b",
    r"\bdata platform\b",
]


ADJACENT_ANALYTICS_PATTERNS = [
    r"\bbusiness analyst\b",
    r"\btechnical business analyst\b",
    r"\bgrowth analyst\b",
    r"\banalytics\b",
    r"\banalytics\b.*\banalyst\b",
    r"\banalyst\b.*\banalytics\b",
    r"\bdata governance\b",
]


# -------------------------------------------------------------------
# Helper
# -------------------------------------------------------------------

def normalize_for_matching(title):
    """
    Prepare title for pattern matching.
    """

    if pd.isna(title):
        return ""

    title = str(title).lower().strip()

    title = (
        title.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )

    title = re.sub(
        r"\s+",
        " ",
        title,
    )

    return title


def matches_any(title, patterns):
    """
    Return True when title matches any pattern.
    """

    return any(
        re.search(pattern, title)
        for pattern in patterns
    )


# -------------------------------------------------------------------
# Title family classification
# -------------------------------------------------------------------

def classify_title_family(title):

    title = normalize_for_matching(title)

    # ---------------------------------------------------------------
    # Target role families first
    # ---------------------------------------------------------------

    if matches_any(
        title,
        DATA_ANALYST_PATTERNS,
    ):
        return "Data Analyst"

    if matches_any(
        title,
        DATA_SCIENTIST_PATTERNS,
    ):
        return "Data Scientist"

    # ---------------------------------------------------------------
    # Adjacent families
    # ---------------------------------------------------------------

    if matches_any(
        title,
        ADJACENT_AI_ML_PATTERNS,
    ):
        return "Adjacent AI/ML"

    if matches_any(
        title,
        ADJACENT_DATA_ENGINEERING_PATTERNS,
    ):
        return "Adjacent Data Engineering"

    if matches_any(
        title,
        ADJACENT_ANALYTICS_PATTERNS,
    ):
        return "Adjacent Analytics"

    # ---------------------------------------------------------------
    # Everything else
    # ---------------------------------------------------------------

    return "Other"


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():

    print("\nGradPath Title Family Classification")
    print("=" * 60)

    df = pd.read_csv(INPUT_PATH)

    print(f"\nLoaded jobs: {len(df)}")

    required_columns = [
        "job_id",
        "job_title",
        "normalized_title",
        "role_category",
        "role_relevance",
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

    # ---------------------------------------------------------------
    # Create title family
    # ---------------------------------------------------------------

    df["title_family"] = df[
        "normalized_title"
    ].apply(classify_title_family)

    # ---------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    print("\n" + "=" * 60)
    print("TITLE FAMILY SUMMARY")
    print("=" * 60)

    print(
        df["title_family"]
        .value_counts()
    )

    print("\nBy role:")

    print(
        pd.crosstab(
            df["role_category"],
            df["title_family"],
        )
    )

    print("\nOutput:")
    print(OUTPUT_PATH)

    print("\nTitle family classification complete.")


if __name__ == "__main__":
    main()