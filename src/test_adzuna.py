import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 5,
    "what": "data analyst",
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("Total results:", data.get("count"))
    print("Jobs returned:", len(data.get("results", [])))

    import json

    jobs = data.get("results", [])

    if jobs:
        print("\nFirst job - full API response:")
        print(json.dumps(jobs[0], indent=2))

else:
    print("Request failed")
    print(response.text)