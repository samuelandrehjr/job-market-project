import sqlite3
import pandas as pd
import json

DB_PATH = r"E:\job_market_project\data\jobs.db"
OUT_JSON = r"E:\job_market_project\web\jobs.json"

def main():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT *
    FROM jobs
    ORDER BY salary_max DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    records = df.fillna("").to_dict(orient="records")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print("Saved:", OUT_JSON)
    print("Rows:", len(records))

if __name__ == "__main__":
    main()