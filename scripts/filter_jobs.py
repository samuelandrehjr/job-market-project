import argparse
import pandas as pd

IN_PATH = r"E:\job_market_project\output\usajobs_full.csv"
OUT_PATH = r"E:\job_market_project\output\filtered_jobs.csv"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", default="")
    parser.add_argument("--loc", default="")
    parser.add_argument("--min", type=float, default=0)
    parser.add_argument("--keyword", default="")
    parser.add_argument("--maxrows", type=int, default=200)
    args = parser.parse_args()

    df = pd.read_csv(IN_PATH)

    if "salary_max" in df.columns:
        df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")

    for col in ["organization", "location", "title"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    out = df.copy()

    if args.org.strip():
        out = out[out["organization"].str.contains(args.org, case=False, na=False)]

    if args.loc.strip():
        out = out[out["location"].str.contains(args.loc, case=False, na=False)]

    if args.keyword.strip():
        out = out[out["title"].str.contains(args.keyword, case=False, na=False)]

    if args.min > 0:
        out = out[out["salary_max"].fillna(0) >= args.min]

    if "salary_max" in out.columns:
        out = out.sort_values(by="salary_max", ascending=False)

    out = out.head(args.maxrows)
    out.to_csv(OUT_PATH, index=False)

    print("Saved:", OUT_PATH)
    print("Rows:", len(out))

if __name__ == "__main__":
    main()