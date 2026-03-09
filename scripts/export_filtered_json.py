import pandas as pd
import json

IN_PATH = r"E:\job_market_project\output\filtered_jobs.csv"
OUT_PATH = r"E:\job_market_project\web\jobs.json"

def main():
    df = pd.read_csv(IN_PATH)
    records = df.fillna("").to_dict(orient="records")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print("Saved:", OUT_PATH)
    print("Rows:", len(records))

if __name__ == "__main__":
    main()