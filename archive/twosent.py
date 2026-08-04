import requests
from bs4 import BeautifulSoup
import re
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://old.reddit.com/r/TwoSentenceHorror/"

def extract_two_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    return sentences[:2] if len(sentences) >= 2 else None

def is_valid_post(title, flair):
    if flair and any(bad in flair.lower() for bad in ["announcement", "meta", "shitpost"]):
        return False
    return True

def scrape_real_horror_posts(limit=20):
    posts_collected = []
    url = BASE_URL
    print("scraping")
    while url and len(posts_collected) < limit:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        post_divs = soup.find_all("div", class_="thing")

        for post in post_divs:
            if "stickied" in post.get("class", []):
                continue

            title_tag = post.find("a", class_="title")
            flair_tag = post.find("span", class_="linkflairlabel")
            if not title_tag:
                continue

            title = title_tag.text.strip()
            flair = flair_tag.text if flair_tag else ""
            if not is_valid_post(title, flair):
                continue

            sentences = extract_two_sentences(title)
            if sentences and len(sentences) == 2:
                posts_collected.append(sentences)

            if len(posts_collected) >= limit:
                break

        next_button = soup.find("span", class_="next-button")
        url = next_button.a["href"] if next_button else None
        time.sleep(1)

    return posts_collected

# Print the final results
if __name__ == "__main__":
    results = scrape_real_horror_posts(limit=20)
    for i, (s1, s2) in enumerate(results, 1):
        print(f"{i}. {s1}\n   {s2}\n")

    input("...")
