import sqlite3

DB_PATH = r"E:\job_market_project\data\jobs.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(jobs)")
    columns = [row[1] for row in cur.fetchall()]

    if "telework_flag" not in columns:
        cur.execute("ALTER TABLE jobs ADD COLUMN Telework_flag TEXT")
        conn.commit()
        print("Added telework_flag column.")
    else:
        print("telework_flag column already exists.")

    cur.execute("PRAGMA table_info(jobs)")
    updated_columns = [row[1] for row in cur.fetchall()]
    print("Current columns:", updated_columns)

    conn.close()

if __name__ == "__main__":
    main()
