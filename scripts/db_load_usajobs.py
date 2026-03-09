import sqlite3
import pandas as pd

DB_PATH = r"E:\job_market_project\data\jobs.db"
CSV_PATH = r"E:\job_market_project\output\usajobs_full.csv"

def main():
    df = pd.read_csv(CSV_PATH)

    df["source"] = "usajobs"

    needed = [
        "job_id", "source", "title", "organization", "department", "location",
        "posting_date", "closing_date", "telework", "grade", "job_series",
        "salary_min", "salary_max", "salary_rate", "apply_url"
    ]

    for col in needed:
        if col not in df.columns:
            df[col] = ""

    df = df[needed]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0

    for _, row in df.iterrows():
        cur.execute("""
        INSERT OR REPLACE INTO jobs (
            job_id, source, title, organization, department, location,
            posting_date, closing_date, telework, grade, job_series,
            salary_min, salary_max, salary_rate, apply_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))

        inserted += 1

    conn.commit()
    conn.close()

    print("Loaded rows into SQLite:", inserted)

if __name__ == "__main__":
    main()