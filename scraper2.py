
import requests
import pandas as pd
import time
from tqdm import tqdm

# Wikipedia API endpoint
API_URL = "https://en.wikipedia.org/w/api.php"

# Configure HTTP session
session = requests.Session()

session.headers.update({
    "User-Agent": "WikipediaResearchScraper/1.0 (educational research project)"
})

# Number of articles to collect
TARGET_ARTICLES = 1000

# Store article titles
article_titles = []

print("Starting Wikipedia article collection...")

# STEP 1: Collect 1000 article titles
params = {
    "action": "query",
    "list": "allpages",
    "apnamespace": 0,
    "aplimit": "max",
    "format": "json",
    "maxlag": 5
}

while len(article_titles) < TARGET_ARTICLES:

    response = session.get(
        API_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    pages = data.get("query", {}).get("allpages", [])

    for page in pages:
        article_titles.append(page["title"])

        if len(article_titles) >= TARGET_ARTICLES:
            break

    # Handle Wikipedia pagination
    if "continue" not in data:
        break

    params.update(data["continue"])

print(f"Collected {len(article_titles)} article titles.")

# STEP 2: Extract article information
articles = []

# Wikipedia allows up to 50 titles per request
batch_size = 50

print("Extracting article information...")

for start in tqdm(range(0, len(article_titles), batch_size)):

    batch = article_titles[start:start + batch_size]

    extract_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|revisions",
        "titles": "|".join(batch),
        "explaintext": 1,
        "rvprop": "timestamp",
        "maxlag": 5
    }

    try:
        response = session.get(
            API_URL,
            params=extract_params,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print("API error:", data["error"])
            continue

        pages = data.get("query", {}).get("pages", {})

        # Organize returned pages by title
        page_lookup = {
            page["title"]: page
            for page in pages.values()
        }

        for title in batch:

            page = page_lookup.get(title)

            if not page:
                continue

            if "missing" in page:
                continue

            full_text = page.get("extract", "")

            revision = page.get("revisions", [{}])
            last_updated = revision[0].get("timestamp", "")

            article_id = page.get("pageid", "")

            article_url = (
                f"https://en.wikipedia.org/?curid={article_id}"
            )

            # Calculate word count
            word_count = len(full_text.split())

            # Store article information
            articles.append({
                "Article_ID": article_id,
                "Title": title,
                "URL": article_url,
                "Summary": full_text[:1000],
                "Full_Text": full_text,
                "Word_Count": word_count,
                "Last_Updated": last_updated
            })

        # Be considerate to Wikipedia servers
        time.sleep(0.2)

    except requests.exceptions.RequestException as error:
        print(f"Request failed for batch starting at {start}: {error}")

# STEP 3: Convert extracted data into DataFrame
df = pd.DataFrame(articles)

# STEP 4: Remove duplicate articles
df.drop_duplicates(subset=["Article_ID"], inplace=True)

# STEP 5: Save data into CSV
output_file = "wikipedia_articles.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

# STEP 6: Display final results
print("\nExtraction completed!")

print("Total articles extracted:", len(df))

print("CSV file saved as:", output_file)

print("\nFirst five articles:")
print(df[["Title", "Word_Count"]].head())

print("\nDataset information:")
print(df.info())
