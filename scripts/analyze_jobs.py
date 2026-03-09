import os
import pandas as pd

IN_PATH = r"E:\job_market_project\output\usajobs_full.csv"
OUT_DIR = r"E:\job_market_project\output"
OUT_SUMMARY = r"E:\job_market_project\output\summary_metrics.csv"
OUT_TOP_AGENCIES = r"E:\job_market_project\output\top_agencies.csv"
OUT_TOP_LOCATIONS = r"E:\job_market_project\output\top_locations.csv"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(IN_PATH)

    # salary columns
    for col in ["salary_min", "salary_max"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["salary_mid"] = (df["salary_min"] + df["salary_max"]) / 2

    # telework normalize
    df["telework_norm"] = df["telework"].astype(str).str.strip().str.upper()
    df["telework_flag"] = df["telework_norm"].isin(["YES", "TRUE", "Y", "1"])

    top_agencies = df["organization"].value_counts().head(20).reset_index()
    top_agencies.columns = ["organization", "job_count"]

    top_locations = df["location"].value_counts().head(20).reset_index()
    top_locations.columns = ["location", "job_count"]

    avg_salary = df["salary_mid"].mean()

    telework_counts = df["telework_flag"].value_counts(dropna=False).to_dict()
    telework_yes = int(telework_counts.get(True, 0))
    telework_no = int(telework_counts.get(False, 0))

    summary = pd.DataFrame([{
        "total_jobs": len(df),
        "avg_salary_mid": avg_salary, 
        "telework_yes": telework_yes,
        "telework_no": telework_no 
    }])

    summary.to_csv(OUT_SUMMARY, index=False)
    top_agencies.to_csv(OUT_TOP_AGENCIES, index=False)
    top_locations.to_csv(OUT_TOP_LOCATIONS, index=False)

    print("Saved:")
    print(" ", OUT_SUMMARY)
    print(" ", OUT_TOP_AGENCIES)
    print(" ", OUT_TOP_LOCATIONS)
    print("\nTop agencies:\n", top_agencies.head(10).to_string(index=False))
    print("\nTop locations:\n", top_locations.head(10).to_string(index=False))
    print("\nAvg salary midpoint:", avg_salary)

if __name__ == "__main__":
    main()