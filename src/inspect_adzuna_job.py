import os

import requests
from dotenv import load_dotenv


load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


JOB_ID = "5904201286"


def main():

    url = (
        f"{BASE_URL}/gb/"
        f"search/1"
    )

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 50,
        "what": "data analyst",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    jobs = data.get("results", [])

    matching_job = None

    for job in jobs:

        if str(job.get("id")) == JOB_ID:
            matching_job = job
            break

    if matching_job is None:

        print(
            f"Job {JOB_ID} was not found "
            "in this API response."
        )

        return

    print("\n" + "=" * 70)
    print("JOB INFORMATION")
    print("=" * 70)

    print(
        f"\nID: {matching_job.get('id')}"
    )

    print(
        f"Title: {matching_job.get('title')}"
    )

    print(
        f"Company: "
        f"{(matching_job.get('company') or {}).get('display_name')}"
    )

    print(
        f"Redirect URL: "
        f"{matching_job.get('redirect_url')}"
    )

    description = matching_job.get(
        "description"
    )

    print(
        f"\nDescription length: "
        f"{len(description or '')}"
    )

    print("\nDESCRIPTION:")
    print("-" * 70)
    print(description)
    print("-" * 70)

    print("\nAVAILABLE API FIELDS:")

    for key in matching_job.keys():
        print(f"- {key}")


if __name__ == "__main__":
    main()