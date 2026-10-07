import re
from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

INPUT_PATH = Path(
    "data/processed/jobs_role_validated.csv"
)

OUTPUT_PATH = Path(
    "data/processed/jobs_title_normalized.csv"
)


# -------------------------------------------------------------------
# Title normalization
# -------------------------------------------------------------------

def clean_title_for_matching(title):
    """
    Prepare a job title for rule-based matching.

    The original job_title is never modified.
    """

    if pd.isna(title):
        return ""

    title = str(title).lower().strip()

    # Normalize dash characters.
    title = (
        title.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )

    # Add spaces around slashes.
    title = title.replace("/", " / ")

    # Separate accidentally joined words.
    title = re.sub(
        r"(?<=[a-z])(?=[A-Z])",
        " ",
        title,
    )

    # Normalize whitespace.
    title = re.sub(
        r"\s+",
        " ",
        title,
    )

    return title.strip()


def normalize_title(title, role_category, role_relevance):
    """
    Convert a job title into a standardized GradPath role title.

    Only clearly relevant jobs are normalized automatically.

    Uncertain and irrelevant jobs are preserved as their cleaned
    original title so that information is not lost.
    """

    original_clean = clean_title_for_matching(title)

    if not original_clean:
        return None

    # ---------------------------------------------------------------
    # Data Analyst
    # ---------------------------------------------------------------

    if role_category == "Data Analyst":

        if role_relevance == "relevant":

            # Direct Data Analyst titles.
            if re.search(
                r"\bdata analyst\b",
                original_clean,
            ):
                return "Data Analyst"

            # Business/Data Analyst variants.
            if (
                re.search(r"\bdata business analyst\b", original_clean)
                or re.search(r"\bdata & business analyst\b", original_clean)
                or re.search(r"\bbusiness & data analyst\b", original_clean)
            ):
                return "Data Analyst"

            # BI Analyst variants.
            if (
                re.search(r"\bbi analyst\b", original_clean)
                or re.search(r"\bbi / data analyst\b", original_clean)
                or re.search(r"\bbi / systems analyst\b", original_clean)
                or re.search(r"\bbusiness intelligence analyst\b", original_clean)
                or re.search(r"\bbi support analyst\b", original_clean)
                or re.search(r"\bbi systems analyst\b", original_clean)
                or re.search(r"\bbi ba\b", original_clean)
                or re.search(r"\bbi/gcp analyst\b", original_clean)
                or re.search(r"\bbi and engineering analyst\b", original_clean)
            ):
                return "BI Analyst"

            # Reporting roles.
            if re.search(
                r"\breporting analyst\b",
                original_clean,
            ):
                return "Reporting Analyst"

            # Data management roles.
            if re.search(
                r"\bdata management analyst\b",
                original_clean,
            ):
                return "Data Management Analyst"

            # Digital data roles.
            if re.search(
                r"\bdigital data analyst\b",
                original_clean,
            ):
                return "Data Analyst"

            # Power BI.
            if re.search(
                r"\bpower bi analyst\b",
                original_clean,
            ):
                return "BI Analyst"

            # Analytics analyst.
            if re.search(
                r"\banalytics analyst\b",
                original_clean,
            ):
                return "Analytics Analyst"

    # ---------------------------------------------------------------
    # Data Scientist
    # ---------------------------------------------------------------

    if role_category == "Data Scientist":

        if role_relevance == "relevant":

            # Direct Data Scientist titles.
            if re.search(
                r"\bdata scientist\b",
                original_clean,
            ):
                return "Data Scientist"

            # Data Science trainee roles.
            if re.search(
                r"\bdata science trainee\b",
                original_clean,
            ):
                return "Data Scientist"

            # Applied Data Scientist.
            if re.search(
                r"\bapplied data scientist\b",
                original_clean,
            ):
                return "Data Scientist"

            # Principal Data Scientist.
            if re.search(
                r"\bprincipal data scientist\b",
                original_clean,
            ):
                return "Data Scientist"

            # Applied Scientist.
            if re.search(
                r"\bapplied scientist\b",
                original_clean,
            ):
                return "Data Scientist"

            # Applied AI Scientist.
            if re.search(
                r"\bapplied ai scientist\b",
                original_clean,
            ):
                return "Data Scientist"

            # ML research / quantitative research.
            if (
                re.search(
                    r"\bmachine learning researcher\b",
                    original_clean,
                )
                or re.search(
                    r"\bmachine learning quant researcher\b",
                    original_clean,
                )
                or re.search(
                    r"\bdata science researcher\b",
                    original_clean,
                )
                or re.search(
                    r"\bmachine learning scientist\b",
                    original_clean,
                )
            ):
                return "Data Scientist"

            # Applied AI/ML roles classified as relevant.
            if re.search(
                r"\bapplied ai ml\b",
                original_clean,
            ):
                return "Data Scientist"

    # ---------------------------------------------------------------
    # Fallback
    # ---------------------------------------------------------------

    # For uncertain/irrelevant roles, keep a cleaned version of the
    # original title rather than forcing a target-role label.
    return original_clean.title()


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():

    print("\nGradPath Job Title Normalization")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Load validated dataset
    # ---------------------------------------------------------------

    df = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"\nLoaded jobs: {len(df)}"
    )

    # ---------------------------------------------------------------
    # Validate required columns
    # ---------------------------------------------------------------

    required_columns = [
        "job_id",
        "job_title",
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
    # Normalize titles
    # ---------------------------------------------------------------

    df["normalized_title"] = df.apply(
        lambda row: normalize_title(
            title=row["job_title"],
            role_category=row["role_category"],
            role_relevance=row["role_relevance"],
        ),
        axis=1,
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
    print("NORMALIZATION SUMMARY")
    print("=" * 60)

    print(
        f"\nOriginal titles: "
        f"{df['job_title'].nunique()}"
    )

    print(
        f"Normalized titles: "
        f"{df['normalized_title'].nunique()}"
    )

    print("\nNormalized titles by role:")

    print(
        df.groupby(
            [
                "role_category",
                "normalized_title",
            ]
        )
        .size()
        .sort_values(
            ascending=False
        )
        .head(20)
    )

    print("\nOutput:")
    print(OUTPUT_PATH)

    print("\nTitle normalization complete.")


if __name__ == "__main__":
    main()

