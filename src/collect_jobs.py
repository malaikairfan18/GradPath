import os
from datetime import datetime, timezone

import pandas as pd
import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not APP_ID or not APP_KEY:
    raise ValueError("Adzuna API credentials are missing from .env")


def collect_jobs(role_category, search_query, country_code="gb", max_jobs=10):
    """
    Collect job postings from Adzuna.

    Parameters:
        role_category: GradPath role classification.
        search_query: Adzuna search query.
        country_code: Adzuna country code.
        max_jobs: Maximum number of jobs to collect.
    """

    url = (
        f"https://api.adzuna.com/v1/api/jobs/"
        f"{country_code}/search/1"
    )

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": max_jobs,
        "what": search_query,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    collected_date = datetime.now(timezone.utc).date().isoformat()

    jobs = []

    for job in data.get("results", []):
        location = job.get("location", {})
        category = job.get("category", {})

        jobs.append(
            {
                "job_id": job.get("id"),
                "role_category": role_category,
                "job_title": job.get("title"),
                "company": job.get("company", {}).get("display_name"),
                "location": location.get("display_name"),
                "country": country_code,
                "latitude": job.get("latitude"),
                "longitude": job.get("longitude"),
                "contract_type": job.get("contract_type"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "salary_is_predicted": job.get("salary_is_predicted"),
                "posting_date": job.get("created"),
                "date_collected": collected_date,
                "description": job.get("description"),
                "category": category.get("label"),
                "source": "Adzuna",
                "source_url": job.get("redirect_url"),
            }
        )

    return jobs


if __name__ == "__main__":

    jobs = collect_jobs(
        role_category="Data Analyst",
        search_query="data analyst",
        country_code="gb",
        max_jobs=10,
    )

    df = pd.DataFrame(jobs)

    output_path = "data/raw/data_analyst_test.csv"

    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Jobs collected: {len(df)}")
    print(f"Saved to: {output_path}")
    print("\nColumns:")
    print(df.columns.tolist())