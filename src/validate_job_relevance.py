import re
from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

ANALYST_PATH = Path(
    "data/raw/data_analyst_market.csv"
)

SCIENTIST_PATH = Path(
    "data/raw/data_scientist_market.csv"
)

OUTPUT_PATH = Path(
    "data/processed/jobs_role_validated.csv"
)


# -------------------------------------------------------------------
# Data Analyst classification rules
# -------------------------------------------------------------------

# Strong direct Data Analyst / BI / data-analysis signals.
ANALYST_RELEVANT_PATTERNS = [
    r"\bdata analyst\b",
    r"\bdata business analyst\b",
    r"\bdata & business analyst\b",
    r"\bbusiness & data analyst\b",
    r"\bbi analyst\b",
    r"\bbi/data analyst\b",
    r"\bdata management analyst\b",
    r"\bdigital data analyst\b",
    r"\breporting analyst\b",
    r"\bpower bi analyst\b",
    r"\banalytics & insights analyst\b",
    r"\banalytics analyst\b",
    r"\bdata analytics analyst\b",
    r"\bbi support analyst\b",
    r"\bbi systems analyst\b",
    r"\bbi / systems analyst\b",
    r"\bbi ba\b",
    r"\bbusiness intelligence analyst\b",
    r"\bproduct bi\b",
    r"\bbi and engineering analyst\b",
    r"\bbi/gcp analyst\b",
]


# Adjacent roles that can contain relevant skills but are not
# automatically treated as Data Analyst roles.
ANALYST_UNCERTAIN_PATTERNS = [
    r"\bbusiness analyst\b",
    r"\btechnical business analyst\b",
    r"\bdata governance analyst\b",
    r"\bgrowth analyst\b",
    r"\bgrowth\b.*\banalyst\b",
    r"\bdata science manager\b",
    r"\banalytics & ai\b",
    r"\banalytics\b.*\bstrategist\b",
    r"\bstrategist\b.*\banalytics\b",
    r"\bsystem engineer\b.*\banalytics\b",
    r"\banalytics\b.*\bsystem engineer\b",
]


# Clearly outside the target Data Analyst role.
ANALYST_IRRELEVANT_PATTERNS = [
    r"\bdata scientist\b",
    r"\bdata engineer\b",
    r"\bmachine learning engineer\b",
    r"\bsoftware engineer\b",
    r"\bsoftware developer\b",
    r"\bandroid developer\b",
    r"\bc\+\+ developer\b",
    r"\bc# developer\b",
    r"\bdeveloper\b",
    r"\belectronics engineer\b",
    r"\bproject engineer\b",
    r"\binfrastructure engineer\b",
    r"\bquality administrator\b",
    r"\bfinance business partner\b",
]


# -------------------------------------------------------------------
# Data Scientist classification rules
# -------------------------------------------------------------------

# Strong Data Science / Applied Science / ML research signals.
SCIENTIST_RELEVANT_PATTERNS = [
    r"\bdata scientist\b",
    r"\bdata science trainee\b",
    r"\bapplied data scientist\b",
    r"\bprincipal data scientist\b",
    r"\bmachine learning scientist\b",
    r"\bapplied scientist\b",
    r"\bapplied ai scientist\b",
    r"\bmachine learning quant researcher\b",
    r"\bmachine learning researcher\b",
    r"\bdata science researcher\b",
    r"\bdata science\b.*\bresearcher\b",
    r"\bresearcher\b.*\bdata science\b",
    r"\bmachine learning\b.*\bresearcher\b",
    r"\bapplied ai ml\b",
]


# Adjacent AI/ML engineering roles.
SCIENTIST_UNCERTAIN_PATTERNS = [
    r"\bmachine learning engineer\b",
    r"\bml engineer\b",
    r"\bai engineer\b",
    r"\bai scientist\b",
    r"\bai developer\b",
    r"\bai consultant\b",
    r"\bdata science engineer\b",
    r"\bai/ml engineer\b",
    r"\bai ml engineer\b",
    r"\bmachine learning developer\b",
    r"\bmachine learning\b.*\bengineer\b",
    r"\bengineer\b.*\bmachine learning\b",
]


# Clearly outside the target Data Scientist role.
SCIENTIST_IRRELEVANT_PATTERNS = [
    r"\bdata engineer\b",
    r"\bandroid developer\b",
    r"\bc\+\+ developer\b",
    r"\bc# developer\b",
    r"\bsoftware developer\b",
    r"\bsoftware engineer\b",
    r"\binfrastructure engineer\b",
    r"\belectronics engineer\b",
    r"\bproject engineer\b",
    r"\bsenior developer\b",
    r"\bgraduate developer\b",
    r"\bpep screening\b",
    r"\bstrategy lead\b",
    r"\bsystems engineer\b",
    r"\btechnology officer\b",
]


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def normalize_title_for_matching(title):
    """
    Prepare a job title for rule-based matching.

    This is only used internally for classification.
    The original job_title is never modified.
    """

    if pd.isna(title):
        return ""

    title = str(title).lower().strip()

    # Normalize different dash characters.
    title = (
        title.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )

    # Add spaces around separators where useful.
    title = title.replace("/", " / ")

    # Handle titles where words were joined together.
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


def matches_any_pattern(title, patterns):
    """
    Return True if the title matches at least one pattern.
    """

    for pattern in patterns:
        if re.search(pattern, title):
            return True

    return False


# -------------------------------------------------------------------
# Data Analyst classifier
# -------------------------------------------------------------------

def classify_analyst_title(title):
    """
    Classify a Data Analyst candidate title.

    Priority:
        1. Relevant
        2. Irrelevant
        3. Uncertain

    Specific relevant patterns are checked first so that titles such
    as 'Data Business Analyst' are not incorrectly captured by the
    broader 'Business Analyst' rule.
    """

    normalized_title = normalize_title_for_matching(title)

    # ---------------------------------------------------------------
    # 1. Strong relevant signals
    # ---------------------------------------------------------------

    if matches_any_pattern(
        normalized_title,
        ANALYST_RELEVANT_PATTERNS,
    ):
        return (
            "relevant",
            "Title contains a strong Data Analyst, BI, or data-analysis signal.",
        )

    # ---------------------------------------------------------------
    # 2. Clearly irrelevant signals
    # ---------------------------------------------------------------

    if matches_any_pattern(
        normalized_title,
        ANALYST_IRRELEVANT_PATTERNS,
    ):
        return (
            "irrelevant",
            "Title matches a non-Data-Analyst role.",
        )

    # ---------------------------------------------------------------
    # 3. Adjacent roles
    # ---------------------------------------------------------------

    if matches_any_pattern(
        normalized_title,
        ANALYST_UNCERTAIN_PATTERNS,
    ):
        return (
            "uncertain",
            "Title is an adjacent analytics, business, or technical role.",
        )

    # ---------------------------------------------------------------
    # 4. Unknown
    # ---------------------------------------------------------------

    return (
        "uncertain",
        "Title does not provide enough evidence for automatic classification.",
    )


# -------------------------------------------------------------------
# Data Scientist classifier
# -------------------------------------------------------------------

def classify_scientist_title(title):
    """
    Classify a Data Scientist candidate title.

    Priority:
        1. Relevant
        2. Irrelevant
        3. Uncertain

    Specific Data Science / Applied Science patterns are checked
    before broader AI/ML engineering patterns.
    """

    normalized_title = normalize_title_for_matching(title)

    # ---------------------------------------------------------------
    # 1. Strong relevant signals
    # ---------------------------------------------------------------

    if matches_any_pattern(
        normalized_title,
        SCIENTIST_RELEVANT_PATTERNS,
    ):
        return (
            "relevant",
            "Title contains a strong Data Science, Applied Science, or ML research signal.",
        )

    # ---------------------------------------------------------------
    # 2. Clearly irrelevant signals
    # ---------------------------------------------------------------

    if matches_any_pattern(
        normalized_title,
        SCIENTIST_IRRELEVANT_PATTERNS,
    ):
        return (
            "irrelevant",
            "Title matches a non-Data-Scientist role.",
        )

    # ---------------------------------------------------------------
    # 3. Adjacent AI/ML roles
    # ---------------------------------------------------------------

    if matches_any_pattern(
        normalized_title,
        SCIENTIST_UNCERTAIN_PATTERNS,
    ):
        return (
            "uncertain",
            "Title is an adjacent AI/ML engineering or consulting role.",
        )

    # ---------------------------------------------------------------
    # 4. Unknown
    # ---------------------------------------------------------------

    return (
        "uncertain",
        "Title does not provide enough evidence for automatic classification.",
    )


# -------------------------------------------------------------------
# Dataset validation
# -------------------------------------------------------------------

def validate_dataset(df, expected_role):
    """
    Validate required columns before classification.
    """

    required_columns = [
        "job_id",
        "job_title",
        "role_category",
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

    unexpected_roles = set(
        df["role_category"].dropna().unique()
    ) - {expected_role}

    if unexpected_roles:
        raise ValueError(
            f"Unexpected role_category values found in "
            f"{expected_role} dataset: {unexpected_roles}"
        )


# -------------------------------------------------------------------
# Process one role dataset
# -------------------------------------------------------------------

def process_role_dataset(df, expected_role):
    """
    Apply role relevance classification to one role dataset.
    """

    validate_dataset(
        df,
        expected_role,
    )

    df = df.copy()

    if expected_role == "Data Analyst":

        classifications = df["job_title"].apply(
            classify_analyst_title
        )

    elif expected_role == "Data Scientist":

        classifications = df["job_title"].apply(
            classify_scientist_title
        )

    else:
        raise ValueError(
            f"Unsupported role: {expected_role}"
        )

    df["role_relevance"] = classifications.apply(
        lambda result: result[0]
    )

    df["relevance_reason"] = classifications.apply(
        lambda result: result[1]
    )

    return df


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():

    print("\nGradPath Role Relevance Validation")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Load raw datasets
    # ---------------------------------------------------------------

    analyst_df = pd.read_csv(
        ANALYST_PATH
    )

    scientist_df = pd.read_csv(
        SCIENTIST_PATH
    )

    print(
        f"\nLoaded Data Analyst jobs: "
        f"{len(analyst_df)}"
    )

    print(
        f"Loaded Data Scientist jobs: "
        f"{len(scientist_df)}"
    )

    # ---------------------------------------------------------------
    # Classify each role
    # ---------------------------------------------------------------

    analyst_df = process_role_dataset(
        analyst_df,
        expected_role="Data Analyst",
    )

    scientist_df = process_role_dataset(
        scientist_df,
        expected_role="Data Scientist",
    )

    # ---------------------------------------------------------------
    # Combine datasets
    # ---------------------------------------------------------------

    validated_df = pd.concat(
        [
            analyst_df,
            scientist_df,
        ],
        ignore_index=True,
    )

    # ---------------------------------------------------------------
    # Save processed dataset
    # ---------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    validated_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    print("\n" + "=" * 60)
    print("ROLE RELEVANCE SUMMARY")
    print("=" * 60)

    print("\nOverall:")

    print(
        validated_df["role_relevance"]
        .value_counts()
    )

    print("\nBy Role:")

    summary = pd.crosstab(
        validated_df["role_category"],
        validated_df["role_relevance"],
    )

    print(summary)

    print("\nOutput:")
    print(OUTPUT_PATH)

    print("\nValidation complete.")


if __name__ == "__main__":
    main()

