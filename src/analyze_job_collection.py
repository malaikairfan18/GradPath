import pandas as pd


ANALYST_PATH = "data/raw/data_analyst_market.csv"
SCIENTIST_PATH = "data/raw/data_scientist_market.csv"


def load_jobs(path):
    """Load a collected job dataset."""
    return pd.read_csv(path)


def analyze_dataset(df, role_name):
    """Analyze basic quality and distribution of a job dataset."""

    print("\n" + "=" * 70)
    print(f"{role_name.upper()} JOB DATASET")
    print("=" * 70)

    print(f"\nTotal records: {len(df)}")

    # ---------------------------------------------------------
    # Basic quality checks
    # ---------------------------------------------------------

    print("\n--- DATA QUALITY ---")

    print(
        f"Unique job IDs: "
        f"{df['job_id'].nunique()}"
    )

    print(
        f"Duplicate job IDs: "
        f"{df['job_id'].duplicated().sum()}"
    )

    print(
        f"Missing job titles: "
        f"{df['job_title'].isna().sum()}"
    )

    print(
        f"Missing descriptions: "
        f"{df['description'].isna().sum()}"
    )

    print(
        f"Missing source URLs: "
        f"{df['source_url'].isna().sum()}"
    )

    print(
        f"Duplicate title + company combinations: "
        f"{df.duplicated(subset=['job_title', 'company']).sum()}"
    )

    # ---------------------------------------------------------
    # Title distribution
    # ---------------------------------------------------------

    print("\n--- JOB TITLES ---")

    title_counts = (
        df["job_title"]
        .value_counts()
    )

    print(title_counts.to_string())

    # ---------------------------------------------------------
    # Company distribution
    # ---------------------------------------------------------

    print("\n--- TOP COMPANIES ---")

    company_counts = (
        df["company"]
        .value_counts()
        .head(10)
    )

    print(company_counts.to_string())

    # ---------------------------------------------------------
    # Location distribution
    # ---------------------------------------------------------

    print("\n--- TOP LOCATIONS ---")

    location_counts = (
        df["location"]
        .value_counts()
        .head(10)
    )

    print(location_counts.to_string())

    # ---------------------------------------------------------
    # Search query distribution
    # ---------------------------------------------------------

    if "search_query" in df.columns:

        print("\n--- SEARCH QUERY DISTRIBUTION ---")

        query_counts = (
            df["search_query"]
            .value_counts()
        )

        print(query_counts.to_string())

    # ---------------------------------------------------------
    # Description length
    # ---------------------------------------------------------

    print("\n--- DESCRIPTION LENGTH ---")

    description_lengths = (
        df["description"]
        .astype(str)
        .str.len()
    )

    print(
        f"Minimum: {description_lengths.min()}"
    )

    print(
        f"Maximum: {description_lengths.max()}"
    )

    print(
        f"Mean: {description_lengths.mean():.1f}"
    )

    print(
        f"Median: {description_lengths.median():.1f}"
    )


def main():

    analyst_df = load_jobs(ANALYST_PATH)
    scientist_df = load_jobs(SCIENTIST_PATH)

    analyze_dataset(
        analyst_df,
        "Data Analyst",
    )

    analyze_dataset(
        scientist_df,
        "Data Scientist",
    )


if __name__ == "__main__":
    main()