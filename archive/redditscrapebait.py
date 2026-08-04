import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

# Set user-agent to mimic a real browser
HEADERS = {'User-Agent': 'Mozilla/5.0 (HeadlineAnalyzerBot)'}
URL = 'https://old.reddit.com/r/popular/'

# --- Expanded keyword lists ---

ragebait_keywords = [
    "furious", "outrage", "triggered", "nazi", "racist", "sexist", "homophobic",
    "transphobic", "bigot", "hater", "cancelled", "cheated", "lied", "broke up", "fight",
    "fired", "backlash", "brutal", "screamed", "exploded", "meltdown", "destroyed",
    "clapped back", "called out", "exposed", "drama", "abuse", "toxic", "weaponized",
    "harassed", "attacked", "punched", "beat up", "sued", "arrested", "charged",
    "violated", "hate", "violence", "controversy", "ban", "boycott", "doxxed"
]

useful_keywords = [
    "how to", "til", "explain", "guide", "lesson", "step by step", "science", "fact",
    "research", "study", "method", "tutorial", "summary", "infographic", "data",
    "learning", "knowledge", "insight", "mental model", "framework", "educational",
    "technology", "tips", "hack", "workflow", "process", "trick", "best practices",
    "experiment", "analysis", "case study", "deep dive", "report", "investigation",
    "discovery", "engineering", "mathematics", "physics", "biology", "ai", "algorithm"
]

# --- Scoring Functions ---
def score_keywords(title, keywords):
    title_lower = title.lower()
    return sum(1 for kw in keywords if kw in title_lower)

# --- Scrape and Analyze ---
def fetch_and_analyze(url):
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Failed to load Reddit page: HTTP {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    posts = soup.find_all('div', class_='thing', limit=25)

    results = []

    for post in posts:
        title_tag = post.find('a', class_='title')
        if title_tag:
            title = title_tag.text.strip()
            rage_score = score_keywords(title, ragebait_keywords)
            useful_score = score_keywords(title, useful_keywords)
            results.append([
                title[:80] + ('...' if len(title) > 80 else ''),
                rage_score,
                useful_score
            ])
    
    return results

# --- Run Script ---
if __name__ == '__main__':
    analyzed_data = fetch_and_analyze(URL)
    print(tabulate(analyzed_data, headers=["Title", "Ragebait Score", "Usefulness Score"]))
    input("...")
