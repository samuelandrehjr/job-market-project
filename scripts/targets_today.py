import pandas as pd
import urllib.parse

FEEDS = r"E:\job_market_project\data\feeds.csv"
OUT = r"E:\job_market_project\output\targets_today.csv"

ROLES = [
    "IT Support",
    "Help Desk",
    "Technical Support Engineer",
    "QA Tester",
    "Desktop Support",
]

def mk_google_site_search(company, role):
    q = f'site:{company} "{role}" careers'
    return "https://www.google.com/search?q=" + urllib.parse.quote(q)

def main():
    df = pd.read_csv(FEEDS)

    rows = []
    for _, r in df.iterrows():
        company = str(r["company"]).strip()
        url = str(r["feed_url"]).strip()

        for role in ROLES:
            rows.append({
                "company": company,
                "role": role,
                "career_page": url,
                "search_link": mk_google_site_search(url.replace("https://","").replace("http://","").split("/")[0], role),
                "status": "OPEN",
                "notes": ""
            })

        out = pd.DataFrame(rows)
        out.to_csv(OUT, index=False)
        print("Saved:", OUT)
        print(out.head(10).to_string(index=False))

if __name__ == "__main__":
    main()