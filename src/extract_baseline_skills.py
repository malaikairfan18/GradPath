import re
from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

INPUT_PATH = Path(
    "data/processed/jobs_text_cleaned.csv"
)

VOCAB_PATH = Path(
    "data/processed/initial_skill_vocabulary.csv"
)

OUTPUT_PATH = Path(
    "data/processed/job_skill_matches_baseline.csv"
)


# -------------------------------------------------------------------
# Text normalization
# -------------------------------------------------------------------

def normalize_text(text):
    """
    Normalize text for skill matching.

    This does not modify the original job description.
    """

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Normalize common separators.
    text = (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
    )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# -------------------------------------------------------------------
# Build safe regex pattern
# -------------------------------------------------------------------

def build_skill_pattern(alias):
    """
    Convert a skill alias into a safe regex pattern.

    Word boundaries help prevent false matches such as:
        R → matching every occurrence of the letter 'r'

    Special handling is included for very short aliases.
    """

    alias = normalize_text(alias)

    if not alias:
        return None

    # ---------------------------------------------------------------
    # Very short aliases
    # ---------------------------------------------------------------

    if len(alias) <= 2:

        # Avoid extracting single-letter skills from arbitrary words.
        if alias == "r":
            return r"(?<![a-z])r(?![a-z])"

        return (
            rf"(?<![a-z0-9])"
            rf"{re.escape(alias)}"
            rf"(?![a-z0-9])"
        )

    # ---------------------------------------------------------------
    # Normal aliases
    # ---------------------------------------------------------------

    escaped = re.escape(alias)

    return (
        rf"(?<![a-z0-9])"
        rf"{escaped}"
        rf"(?![a-z0-9])"
    )


# -------------------------------------------------------------------
# Prepare vocabulary
# -------------------------------------------------------------------

def prepare_vocabulary(vocabulary):

    vocabulary = vocabulary.copy()

    vocabulary["aliases"] = (
        vocabulary["aliases"]
        .fillna("")
        .astype(str)
    )

    vocabulary["alias_list"] = (
        vocabulary["aliases"]
        .str.split(";")
    )

    return vocabulary


# -------------------------------------------------------------------
# Extract skills from one description
# -------------------------------------------------------------------

def extract_skills(text, vocabulary):

    normalized_text = normalize_text(text)

    matches = []

    for _, skill in vocabulary.iterrows():

        aliases = skill["alias_list"]

        for alias in aliases:

            alias = normalize_text(alias)

            if not alias:
                continue

            pattern = build_skill_pattern(alias)

            if pattern is None:
                continue

            if re.search(
                pattern,
                normalized_text,
            ):

                if alias == normalize_text(
                    skill["skill_name"]
                ):
                    match_type = "canonical"
                else:
                    match_type = "alias"

                matches.append(
                    {
                        "skill_id": skill["skill_id"],
                        "skill_name": skill["skill_name"],
                        "skill_category": skill[
                            "skill_category"
                        ],
                        "role": skill["role"],
                        "source": skill["source"],
                        "matched_alias": alias,
                        "match_type": match_type,
                    }
                )

                # ---------------------------------------------------
                # Stop after the first matching alias for this skill.
                # ---------------------------------------------------

                break

    return matches


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():

    print("\nGradPath Baseline Skill Extraction")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Load jobs
    # ---------------------------------------------------------------

    jobs = pd.read_csv(
        INPUT_PATH
    )

    vocabulary = pd.read_csv(
        VOCAB_PATH
    )

    print(
        f"\nJobs loaded: {len(jobs)}"
    )

    print(
        f"Skills in vocabulary: {len(vocabulary)}"
    )

    # ---------------------------------------------------------------
    # Validate required columns
    # ---------------------------------------------------------------

    required_job_columns = [
        "job_id",
        "job_title",
        "normalized_title",
        "title_family",
        "role_category",
        "role_relevance",
        "description",
        "description_clean",
    ]

    required_skill_columns = [
        "skill_id",
        "skill_name",
        "skill_category",
        "role",
        "source",
        "aliases",
    ]

    missing_job_columns = [
        column
        for column in required_job_columns
        if column not in jobs.columns
    ]

    missing_skill_columns = [
        column
        for column in required_skill_columns
        if column not in vocabulary.columns
    ]

    if missing_job_columns:
        raise ValueError(
            f"Missing job columns: {missing_job_columns}"
        )

    if missing_skill_columns:
        raise ValueError(
            f"Missing vocabulary columns: {missing_skill_columns}"
        )

    # ---------------------------------------------------------------
    # Prepare vocabulary
    # ---------------------------------------------------------------

    vocabulary = prepare_vocabulary(
        vocabulary
    )

    # ---------------------------------------------------------------
    # Extract matches
    # ---------------------------------------------------------------

    matches = []

    for index, job in jobs.iterrows():

        job_matches = extract_skills(
            job["description_clean"],
            vocabulary,
        )

        for match in job_matches:

            matches.append(
                {
                    "job_id": job["job_id"],
                    "job_title": job["job_title"],
                    "normalized_title": job[
                        "normalized_title"
                    ],
                    "title_family": job[
                        "title_family"
                    ],
                    "role_category": job[
                        "role_category"
                    ],
                    "role_relevance": job[
                        "role_relevance"
                    ],
                    "skill_id": match["skill_id"],
                    "skill_name": match["skill_name"],
                    "skill_category": match[
                        "skill_category"
                    ],
                    "skill_role": match["role"],
                    "skill_source": match["source"],
                    "matched_alias": match[
                        "matched_alias"
                    ],
                    "match_type": match[
                        "match_type"
                    ],
                }
            )

        # -----------------------------------------------------------
        # Progress indicator
        # -----------------------------------------------------------

        if (index + 1) % 50 == 0:
            print(
                f"Processed {index + 1}/{len(jobs)} jobs..."
            )

    # ---------------------------------------------------------------
    # Create match dataframe
    # ---------------------------------------------------------------

    matches_df = pd.DataFrame(
        matches
    )

    # ---------------------------------------------------------------
    # Handle zero-match case
    # ---------------------------------------------------------------

    if matches_df.empty:

        print(
            "\nNo skill matches were found."
        )

        matches_df = pd.DataFrame(
            columns=[
                "job_id",
                "job_title",
                "normalized_title",
                "title_family",
                "role_category",
                "role_relevance",
                "skill_id",
                "skill_name",
                "skill_category",
                "skill_role",
                "skill_source",
                "matched_alias",
                "match_type",
            ]
        )

    # ---------------------------------------------------------------
    # Remove accidental duplicate matches
    # ---------------------------------------------------------------

    before_dedup = len(matches_df)

    if not matches_df.empty:

        matches_df = matches_df.drop_duplicates(
            subset=[
                "job_id",
                "skill_id",
            ]
        ).copy()

    duplicates_removed = (
        before_dedup - len(matches_df)
    )

    # ---------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    matches_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8",
    )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    print("\n" + "=" * 60)
    print("BASELINE EXTRACTION SUMMARY")
    print("=" * 60)

    print(
        f"\nJobs processed: "
        f"{len(jobs)}"
    )

    print(
        f"Jobs with at least one skill: "
        f"{matches_df['job_id'].nunique() if not matches_df.empty else 0}"
    )

    print(
        f"Jobs with no matched skills: "
        f"{len(jobs) - matches_df['job_id'].nunique() if not matches_df.empty else len(jobs)}"
    )

    print(
        f"Skill matches: "
        f"{len(matches_df)}"
    )

    print(
        f"Duplicate matches removed: "
        f"{duplicates_removed}"
    )

    if not matches_df.empty:

        print("\nMatches by role:")

        print(
            matches_df["role_category"]
            .value_counts()
        )

        print("\nTop matched skills:")

        print(
            matches_df["skill_name"]
            .value_counts()
            .head(20)
        )

        print("\nMatches by skill category:")

        print(
            matches_df["skill_category"]
            .value_counts()
        )

    print("\nOutput:")
    print(OUTPUT_PATH)

    print("\nBaseline skill extraction complete.")


if __name__ == "__main__":
    main()