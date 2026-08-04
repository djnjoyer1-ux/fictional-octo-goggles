import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.nbabox.me/"

def get_navbar_links(base_url):
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to get base page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    # Find the navbar div by its class (based on your snippet)
    navbar_div = soup.find("div", class_="collapse navbar-collapse")
    if not navbar_div:
        print("Navbar not found.")
        return []

    links = []
    for a_tag in navbar_div.find_all("a", href=True):
        href = a_tag['href']
        # If relative URL, convert to absolute
        if href.startswith("/"):
            full_url = requests.compat.urljoin(base_url, href)
        else:
            full_url = href
        sport = a_tag.get_text(strip=True)
        links.append((sport, full_url))
    return links

def scrape_matches(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    date_headers = soup.find_all("div", class_="btn btn-dark text-light")
    matches = []

    for date_header in date_headers:
        match_date = date_header.text.strip()

        for sibling in date_header.find_next_siblings():
            if sibling.name == "div" and "btn btn-dark text-light" in sibling.get("class", []):
                break
            if sibling.name == "a" and "btn btn-secondary" in sibling.get("class", []):
                match_time_elem = sibling.find("span", class_="w4e1k4j1c3")
                match_time = match_time_elem.text.strip() if match_time_elem else "Unknown"
                match_title = sibling.get("title", "").strip()
                matches.append({
                    "date": match_date,
                    "time": match_time,
                    "title": match_title
                })
    return matches

def main():
    sport_links = get_navbar_links(BASE_URL)

    for sport, url in sport_links:
        print(f"\n=== {sport} ===")
        match_data = scrape_matches(url)
        if match_data:
            for match in match_data:
                print(f"{match['date']} at {match['time']} — {match['title']}")
        else:
            print("No match data found.")

if __name__ == "__main__":
    main()
