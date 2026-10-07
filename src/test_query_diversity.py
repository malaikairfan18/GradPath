import os

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


QUERIES = [
    "data analyst",
    "junior data analyst",
    "business data analyst",
    "BI analyst",
]


def search_jobs(query, results_per_page=10):

    url = f"{BASE_URL}/gb/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json().get("results", [])


def main():

    all_results = []

    for query in QUERIES:

        print("\n" + "=" * 60)
        print(f"QUERY: {query}")
        print("=" * 60)

        results = search_jobs(query)

        print(f"Results returned: {len(results)}")

        for job in results:

            all_results.append(
                {
                    "query": query,
                    "job_id": job.get("id"),
                    "title": job.get("title"),
                    "company": (
                        job.get("company") or {}
                    ).get("display_name"),
                }
            )

            print(
                f"{job.get('id')} | "
                f"{job.get('title')} | "
                f"{(job.get('company') or {}).get('display_name')}"
            )

    df = pd.DataFrame(all_results)

    print("\n" + "=" * 60)
    print("QUERY DIVERSITY SUMMARY")
    print("=" * 60)

    print(f"\nTotal retrieved records: {len(df)}")
    print(
        f"Unique job IDs: "
        f"{df['job_id'].nunique()}"
    )

    print(
        f"Duplicate records across queries: "
        f"{df['job_id'].duplicated().sum()}"
    )

    print("\nJobs appearing in multiple queries:")

    counts = (
        df.groupby("job_id")["query"]
        .nunique()
        .sort_values(ascending=False)
    )

    repeated_ids = counts[counts > 1]

    if repeated_ids.empty:
        print("None")

    else:
        print(repeated_ids.to_string())


if __name__ == "__main__":
    main()