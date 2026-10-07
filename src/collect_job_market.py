import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not APP_ID or not APP_KEY:
    raise ValueError(
        "Adzuna API credentials are missing from .env"
    )


BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def collect_jobs(
    role_category,
    search_query,
    country_code="gb",
    max_jobs=50,
    start_page=1,
    max_pages=10,
    pause_seconds=1,
):
    """
    Collect job postings from Adzuna.

    Parameters
    ----------
    role_category : str
        GradPath role classification.

    search_query : str
        Search query sent to Adzuna.

    country_code : str
        Adzuna country code.

    max_jobs : int
        Maximum number of jobs to collect for this query.

    start_page : int
        First Adzuna result page.

    max_pages : int
        Maximum number of pages to request.

    pause_seconds : float
        Pause between API requests.
    """

    jobs = []
    pages_collected = 0

    results_per_page = min(50, max_jobs)

    for page in range(start_page, start_page + max_pages):

        if len(jobs) >= max_jobs:
            break

        url = (
            f"{BASE_URL}/"
            f"{country_code}/search/{page}"
        )

        remaining = max_jobs - len(jobs)

        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": min(results_per_page, remaining),
            "what": search_query,
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            print(
                f"Request failed for "
                f"'{search_query}' page {page}: {exc}"
            )
            continue

        data = response.json()
        results = data.get("results", [])

        pages_collected += 1

        if not results:
            print(
                f"No results returned for "
                f"'{search_query}' page {page}."
            )
            break

        collected_date = (
            datetime.now(timezone.utc)
            .date()
            .isoformat()
        )

        for job in results:

            location = job.get("location") or {}
            company = job.get("company") or {}
            category = job.get("category") or {}

            jobs.append(
                {
                    "job_id": job.get("id"),
                    "role_category": role_category,
                    "job_title": job.get("title"),
                    "company": company.get(
                        "display_name"
                    ),
                    "location": location.get(
                        "display_name"
                    ),
                    "country": country_code,
                    "latitude": job.get("latitude"),
                    "longitude": job.get("longitude"),
                    "contract_type": job.get(
                        "contract_type"
                    ),
                    "salary_min": job.get(
                        "salary_min"
                    ),
                    "salary_max": job.get(
                        "salary_max"
                    ),
                    "salary_is_predicted": job.get(
                        "salary_is_predicted"
                    ),
                    "posting_date": job.get(
                        "created"
                    ),
                    "date_collected": collected_date,
                    "description": job.get(
                        "description"
                    ),
                    "category": category.get(
                        "label"
                    ),
                    "source": "Adzuna",
                    "source_url": job.get(
                        "redirect_url"
                    ),
                    "search_query": search_query,
                }
            )

        print(
            f"Query='{search_query}' | "
            f"Page={page} | "
            f"Retrieved={len(results)} | "
            f"Total={len(jobs)}"
        )

        if len(results) < results_per_page:
            break

        time.sleep(pause_seconds)

    print(
        f"Finished query '{search_query}'. "
        f"Jobs collected: {len(jobs)} | "
        f"Pages: {pages_collected}"
    )

    return jobs


def validate_jobs(df):
    """
    Perform basic data-quality validation.
    """

    required_columns = [
        "job_id",
        "job_title",
        "description",
        "source_url",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    before = len(df)

    df = df.dropna(
        subset=[
            "job_id",
            "job_title",
            "description",
            "source_url",
        ]
    ).copy()

    df["job_title"] = (
        df["job_title"]
        .astype(str)
        .str.strip()
    )

    df["description"] = (
        df["description"]
        .astype(str)
        .str.strip()
    )

    df = df[
        (df["job_title"] != "")
        & (df["description"] != "")
    ].copy()

    duplicates_removed = df["job_id"].duplicated().sum()

    df = df.drop_duplicates(
        subset=["job_id"]
    ).copy()

    after = len(df)

    validation_summary = {
        "records_before_validation": before,
        "duplicates_removed": int(
            duplicates_removed
        ),
        "records_after_validation": after,
    }

    return df, validation_summary


def collect_role(
    role_category,
    search_queries,
    target_jobs,
    country_code="gb",
):
    """
    Collect and validate jobs for one GradPath role.

    Jobs are distributed across multiple search queries
    to improve query diversity.
    """

    all_jobs = []

    # Collect extra jobs because duplicates may occur
    # across different search queries.
    jobs_per_query = (
        target_jobs // len(search_queries)
    ) + 10

    for query in search_queries:

        print("\n" + "=" * 60)
        print(
            f"Role: {role_category} | "
            f"Query: {query}"
        )
        print("=" * 60)

        jobs = collect_jobs(
            role_category=role_category,
            search_query=query,
            country_code=country_code,
            max_jobs=jobs_per_query,
        )

        all_jobs.extend(jobs)

    df = pd.DataFrame(all_jobs)

    if df.empty:
        return df, {
            "records_before_validation": 0,
            "duplicates_removed": 0,
            "records_after_validation": 0,
        }

    return validate_jobs(df)


if __name__ == "__main__":

    DATA_ANALYST_QUERIES = [
        "data analyst",
        "junior data analyst",
        "business data analyst",
        "BI analyst",
    ]

    DATA_SCIENTIST_QUERIES = [
        "data scientist",
        "junior data scientist",
        "applied data scientist",
        "machine learning data scientist",
    ]

    print("\nGradPath Job Market Collection")
    print("=" * 60)

    analyst_df, analyst_summary = collect_role(
        role_category="Data Analyst",
        search_queries=DATA_ANALYST_QUERIES,
        target_jobs=130,
    )

    scientist_df, scientist_summary = collect_role(
        role_category="Data Scientist",
        search_queries=DATA_SCIENTIST_QUERIES,
        target_jobs=130,
    )

    analyst_path = (
        "data/raw/"
        "data_analyst_market.csv"
    )

    scientist_path = (
        "data/raw/"
        "data_scientist_market.csv"
    )

    analyst_df.to_csv(
        analyst_path,
        index=False,
        encoding="utf-8",
    )

    scientist_df.to_csv(
        scientist_path,
        index=False,
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("COLLECTION SUMMARY")
    print("=" * 60)

    print("\nData Analyst:")
    print(analyst_summary)

    print("\nData Scientist:")
    print(scientist_summary)

    print("\nOutput files:")
    print(analyst_path)
    print(scientist_path)