import re
import sqlite3
import requests

DB_PATH = r"E:\job_market_project\data\jobs.db"
URL = "https://remotive.com/api/remote-jobs"

def parse_salary_range(salary_text):
    if not salary_text:
        return None, None
    
    nums = re.findall(r"[\d,]+(?:\.\d+)?", str(salary_text))
    cleaned = []

    for n in nums:
        try:
            cleaned.append(float(n.replace(",", "")))
        except:
            pass

    if len(cleaned) >= 2:
        return cleaned[0], cleaned[1]
    elif len(cleaned) == 1:
        return cleaned[0], cleaned[0]
    else:
        return None, None
    
def main():
    r = requests.get(URL, timeout=30)
    r.raise_for_status()

    data = r.json()
    jobs = data.get("jobs", [])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0

    for job in jobs:
        salary_min, salary_max = parse_salary_range(job.get("salary", ""))

        row = (
            f"remotive_{job.get('id', '')}",    # job_id
            "remotive",                          # source
            job.get("title", ""),
            job.get("company_name", ""),
            "",                                 # department
            job.get("candidate_required_location", ""),
            job.get("publication_date", ""),
            "",                                 # closing_date
            "remote",                           # telework
            "",                                 # grade
            job.get("category", ""),
            salary_min,
            salary_max,
            "",                                 # salary_rate
            job.get("url", "")
        )

        cur.execute("""
        INSERT OR REPLACE INTO jobs (
            job_id, source, title, organization, department, location,
            posting_date, closing_date, telework, grade, job_series,
            salary_min, salary_max, salary_rate, apply_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

        inserted += 1

    conn.commit()
    conn.close()

    print("Loaded remotive rows into SQLite:", inserted)

if __name__ == "__main__":
    main()