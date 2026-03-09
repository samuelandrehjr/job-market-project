import os
import requests
import pandas as pd

OUT_PATH = r"E:\job_market_project\output\usajobs_full.csv"

URL = "https://data.usajobs.gov/api/search"

# ---- Filters you can edit anytime ----
KEYWORD = "IT Support"    # try: "Help Desk", "Cybersecurity", "SysAdmin"
LOCATION = ""            # try: "Boston, Massachusetts" or "Remote" or "Washington, DC" 
RESULTS_PER_PAGE = 25    # USAjobs cap per page
MAX_PAGES = 5            # 5 pages = up to 125 jobs

HEADERS = {
    "User-Agent": "job-market-project/1.0",
    "From": "samuelandrehjr@gmail.com",
    "Host": "data.usajobs.gov",
    "Authorization-Key": os.getenv("USAJOBS_API_KEY", "")
}

print("Has key?", bool(HEADERS.get("Authorization-Key")))

def safe_num(x):
    try:
        return float(x)
    except Exception:
        return None
    
def first_remuneration(d):
    # PositionRemuneration is usually a list
    rem = d.get("PositionRemuneration", [])
    if isinstance(rem, list) and rem:
        return rem[0]
    return {}

def extract_job(item):
    d = item.get("MatchedObjectDescriptor", {}) or {}

    # ID: prefer PositionID, else MatchedObjectId, else apply link
    job_id = d.get("PositionID") or item.get("MatchedObjectedId") or d.get("PositionURI") or ""

    rem = first_remuneration(d)
    salary_min = safe_num(rem.get("MinimumRange"))
    salary_max = safe_num(rem.get("MaximumRange"))
    salary_rate = rem.get("RateIntervalCode", "") # e.g., "PA" (per annum)

    # Some fields vary by posting; we keep safe fallbacks
    telework = d.get("TeleworkEligible") or d.get("TeleworkEligibleFlag") or ""

    # Job grade can be a list (JobGrade) or a single string in some responses
    grade = d.get("JobGrade", "")
    if isinstance(grade, list):
        cleaned = []
        for g in grade:
            if isinstance(g, dict):
                cleaned.append(str(g.get("Code") or g.get("Name") or ""))
            else:
                cleaned.append(str(g))
        grade = ";".join([x for x in cleaned if x])
    elif isinstance(grade, dict):
        grade = str(grade.get("Code") or grade.get("Name") or "")
    else:
        grade = str(grade or "")

    # Job series often appears under JobCategory (list of dicts) or similar
    series = ""
    jc = d.get("JobCategory", [])
    if isinstance(jc, list) and jc:
        # sometimes dict keys differ; try common ones
        series = jc[0].get("Code") or jc[0].get("Name") or ""

    return {
        "job_id": job_id,
        "title": d.get("PositionTitle", ""),
        "organization": d.get("OrganizationName", ""),
        "department": d.get("DepartmentName", ""),
        "location": d.get("PositionLocationDisplay", ""),
        "posting_date": d.get("PublicationStartDate", ""),
        "closing_date": d.get("ApplicationCloseDate", ""),
        "telework": telework,
        "grade": grade,
        "job_series": series,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_rate": salary_rate,
        "apply_url": d.get("PositionURI", ""),
    }
    

def main():
    if not HEADERS.get("Authorization-Key"):
        print("Missing USAJOBS_API_KEY. In PowerShell: $env:USAJOBS_API_KEY='...'")
        return
    
    all_rows = []

    for page in range(1, MAX_PAGES + 1):
        params = {
            "keyword": KEYWORD,
            "ResultsPerPage": RESULTS_PER_PAGE,
            "Page": page 
        }
        if LOCATION.strip():
            params["LocationName"] = LOCATION.strip()

        r = requests.get(URL, params=params, headers=HEADERS, timeout=30)

        if r.status_code != 200:
            print("HTTP", r.status_code, "on page", page)
            print(r.text[:800])
            return
        
        data = r.json()
        search = data.get("SearchResult")
        if not search:
            print("No SearchResult on page", page)
            print("Top-level keys:", list(data.keys())[:20])
            return
        
        items = search.get("SearchResultItems", [])
        if not items:
            print("No items on page", page, "(done).")
            break

        for item in items:
            all_rows.append(extract_job(item))

        print(f"Fetched page {page}: +{len(items)} rows (total {len(all_rows)})")

    if not all_rows:
        print("No rows found.")
        return
    
    df = pd.DataFrame(all_rows)

    # Deduplicate
    before = len(df)
    df = df.drop_duplicates(subset=["job_id"], keep="first")
    after = len(df)
    print(f"Deduped: {before} -> {after}")

    df.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(df)} jobs to {OUT_PATH}")
    print(df.head(10).to_string(index=False))

if __name__ == "__main__": 
    main()