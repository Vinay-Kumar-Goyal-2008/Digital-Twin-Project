import urllib.parse
import urllib.request
import feedparser
import json
import time
import os

TARGET_PAPERS = 500   # reduce for stability first
BATCH_SIZE = 10       # smaller batch = faster response
SLEEP_TIME = 3        # slower = more stable

QUERIES = [
    'all:"Richard Feynman"',
    'all:"Feynman lecture"',
    'all:"Feynman lectures on physics"',
    'all:"Feynman interview"',
    'all:"Feynman talk"',
    'all:"Feynman QED"',
    'all:"quantum electrodynamics"',
    'all:"QED"',
    'all:"Feynman diagrams"',
    'all:"path integral formulation"',
    'all:"path integral"',
    'all:"sum over histories"',
    'all:"quantum mechanics lecture"',
    'all:"physics intuition Feynman"',
    'all:"Feynman explanation"',
    'all:"Feynman teaches"',
    'all:"Feynman messenger lectures"',
    'all:"Cornell lectures physics"',
    'all:"Feynman problem solving"',
    'all:"Feynman curiosity"',
    'all:"Feynman surely youre joking"',
    'all:"Surely You’re Joking Mr Feynman"',
    'all:"Feynman philosophy science"',
    'all:"what is understanding Feynman"',
    'all:"Feynman atomic theory"',
    'all:"Feynman quantum physics explanation"',
]

papers = []
seen = set()

def safe_request(url):
    for attempt in range(3):  # retry system
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            time.sleep(5)
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception as e:
            print(f"Retry {attempt+1} failed:", e)
            time.sleep(3)
    return None


for query in QUERIES:

    start = 0

    while len(papers) < TARGET_PAPERS:

        print(f"Collected: {len(papers)} | Query: {query}")

        url = (
            "https://export.arxiv.org/api/query?"
            f"search_query={urllib.parse.quote(query)}"
            f"&start={start}"
            f"&max_results={BATCH_SIZE}"
            f"&sortBy=submittedDate"
            f"&sortOrder=descending"
        )

        data = safe_request(url)

        if not data:
            print("Skipping batch due to timeout")
            start += BATCH_SIZE
            continue

        feed = feedparser.parse(data)

        if not feed.entries:
            break

        for e in feed.entries:

            if e.id in seen:
                continue

            title = e.title.strip()
            abstract = e.summary.strip()

            if "feynman" not in (title + abstract).lower() and "quantum" not in (title + abstract).lower():
                continue

            seen.add(e.id)

            papers.append({
                "title": title,
                "abstract": abstract,
                "text": title + "\n" + abstract,
                "arxiv_id": e.id
            })

            if len(papers) >= TARGET_PAPERS:
                break

        start += BATCH_SIZE
        time.sleep(SLEEP_TIME)


os.makedirs("feynman_data/raw_json", exist_ok=True)

with open("feynman_data/raw_json/feynman_papers.json", "w", encoding="utf-8") as f:
    json.dump(papers, f, indent=2, ensure_ascii=False)

print("DONE:", len(papers))