import os
import re
import sqlite3
import requests

DB_PATH = r"E:\job_market_project\data\jobs.db"

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

COUNTRY = "us"
RESULTS_PER_PAGE = 20
PAGES = 3

WHAT = "information technology"
WHERE = ""
CATEGORY = "it-jobs"

def parse_salary_range(salary_min, salary_max):
    try:
        smin = float(salary_min) if salary_min else None
    except:
        smin = None
    try:
        smax = float(salary_max) if salary_max else None
    except:
        smax = None

    return smin, smax

def normalize_telework_flag(title, location, description=""):
    blob = f"{title} {location} {description}".lower()

    if "remote" in blob or "work from home" in blob:
        return "remote"
    
    return "unknown"

def main():
    if not APP_ID or not APP_KEY:
        print("Missing ADZUNA_APP_ID or ADZUNA_APP_KEY")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0

    for page in range(1, PAGES + 1):

        url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}"

        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": RESULTS_PER_PAGE,
            "what": WHAT,
            "where": WHERE,
            "category": CATEGORY,
            "content-type": "application/json"
        }

        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()

        print("Reques URL:", r.url)
        
        data = r.json()

        print("Top-level keys:", list(data.keys()))

        jobs = data.get("results", [])
      
        print("Count returned this page:", len(jobs))

        if not jobs:
            print("No Adzuna jobs returned.")
            break

        for job in jobs:

            salary_min, salary_max = parse_salary_range(
                job.get("salary_min"),
                job.get("salary_max")
            )

            telework_flag = normalize_telework_flag(
                job.get("title", ""),
                job.get("location", {}).get("display_name", ""),
                job.get("description", "")
            )

            row = (
                f"adzuna_{job.get('id', '')}",
                "adzuna",
                job.get("title", ""),
                job.get("company", {}).get("display_name", ""),
                "",
                job.get("location", {}).get("display_name", ""),
                job.get("created", ""),
                "",
                "",
                telework_flag,
                "",
                "",
                salary_min,
                salary_max,
                "",
                job.get("redirect_url", "")
            )

            cur.execute("""
            INSERT OR REPLACE INTO jobs (
                job_id, source, title, organization, department, location,
                posting_date, closing_date, telework, telework_flag, grade, job_series,
                salary_min, salary_max, salary_rate, apply_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)

            inserted += 1

        print(f"Loaded Adzuna page {page}: +{len(jobs)} rows")

    conn.commit()
    conn.close()

    print("Loaded Adzuna rows into SQLite:", inserted)

if __name__ == "__main__":
    main()