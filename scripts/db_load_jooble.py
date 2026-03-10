import os
import re
import sqlite3
import requests

DB_PATH = r"E:\job_market_project\data\jobs.db"

API_KEY = os.getenv("JOOBLE_API_KEY", "").strip()
URL = f"https://jooble.org/api/{API_KEY}"

# Start broad enough to be useful, but still relevant to your board
KEYWORDS = "information technology OR IT OR help desk OR cybersecurity OR systems administrator"
LOCATION = "USA"
RESULTS_PER_PAGE = 20
PAGES = 3 # 3 pages x 20 = up to 60 rows before dedupe

def parse_salary_range(salary_text):
    if not salary_text:
        return None, None
    
    nums = re.findall(r"[\d,]+(?:\.d+)?", str(salary_text))
    cleaned = []

    for n in nums:
        try:
            cleaned.append(float(n.replace(",", "")))
        except:
            pass

    if len(cleaned) >= 2:
        return cleaned[0], cleaned[1]
    elif len(cleaned) == 1:
        return None, None
    
def normalize_telework_flag(location_text, title_text="", snippet_text=""):
    blob = f"{location_text} {title_text} {snippet_text}".lower()

    if "remote" in blob or "work from home" in blob or "worldwide" in blob:
        return "remote"
    return "unknown"

def main():
    if not API_KEY:
        print("Missing JOOBLE_API_KEY in environment.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0

    for page in range(1, PAGES + 1):
        payload = {
            "keywords": KEYWORDS,
            "location": LOCATION, 
            "page": str(page),
            "ResultOnPage": str(RESULTS_PER_PAGE)
        }

        r = requests.post(URL, json=payload, timeout=30)
        r.raise_for_status()

        data = r.json()
        jobs = data.get("jobs", [])

        if not jobs:
            print(f"No Jooble jobs on page {page}.")
            break

        for job in jobs:
            salary_min, salary_max = parse_salary_range(job.get("salary", ""))
            telework_flag = normalize_telework_flag(
                job.get("location", ""),
                job.get("title", ""),
                job.get("snippet", "")
            )

            row = (
                f"jooble_{job.get('id', '')}",  # job_id
                "jooble",                       # source
                job.get("title", ""),
                job.get("company", ""),
                "",                             # department
                job.get("location", ""),
                job.get("updated", ""),         # posting_date
                "",                             # closing_date
                job.get("type", ""),            # telework raw-ish / job type
                telework_flag,                  # telework_flag
                "",                             # grade
                "",                             # job_series
                salary_min,
                salary_max,
                "",                             # salary_rate
                job.get("link", "")
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

        print(f"Loaded Jooble page {page}: +{len(jobs)} rows")

    conn.commit()
    conn.close()

    print("Loaded Jooble rows into SQLite:", inserted)

if __name__ == "__main__":
    main()