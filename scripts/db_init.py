import sqlite3

DB_PATH = r"E:\job_market_project\data\jobs.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        source TEXT,
        title TEXT,
        organization TEXT,
        department TEXT,
        location TEXT,
        posting_date TEXT,
        closing_date TEXT,
        telework TEXT,
        grade TEXT,
        job_series TEXT,
        salary_min REAL,
        salary_max REAL,
        salary_rate TEXT,
        apply_url TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Created database:", DB_PATH)

if __name__ == "__main__":
    main()