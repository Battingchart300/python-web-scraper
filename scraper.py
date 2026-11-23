"""Simple Python web scraper — download pages, extract data, save to CSV or JSON.

Example site: https://quotes.toscrape.com (a page made for practising scraping).

Rules:
- Only public pages, no login, no personal data.
- Respects robots.txt (checked before every run).
- Waits between requests (default 1 second) so the server is not hammered.

Usage:
    python scraper.py
    python scraper.py --url https://quotes.toscrape.com --pages 2 --output quotes.csv
    python scraper.py --url https://quotes.toscrape.com --pages 1 --format json --output quotes.json
"""

import argparse
import csv
import json
import time
import urllib.robotparser
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "python-web-scraper (learning project; +https://github.com/Battingchart300/python-web-scraper)"}


def robots_allows(url: str) -> bool:
    """Return True if robots.txt allows scraping this URL.

    If the site has no robots.txt (quotes.toscrape.com returns 404 for it,
    checked 17.11.2026), RobotFileParser treats everything as allowed.
    """
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(urljoin(url, "/robots.txt"))
    try:
        parser.read()
    except Exception:
        # robots.txt unreadable -> play safe and do not scrape
        return False
    return parser.can_fetch(HEADERS["User-Agent"], url)


def fetch_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def parse_quotes(html: str) -> list[dict]:
    """Extract quote text, author and tags from one page of quotes.toscrape.com."""
    soup = BeautifulSoup(html, "html.parser")
    quotes = []
    for block in soup.select("div.quote"):
        text = block.select_one("span.text")
        author = block.select_one("small.author")
        tags = [tag.get_text(strip=True) for tag in block.select("div.tags a.tag")]
        quotes.append(
            {
                "text": text.get_text(strip=True) if text else "",
                "author": author.get_text(strip=True) if author else "",
                "tags": ", ".join(tags),
            }
        )
    return quotes


def next_page_url(html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    nxt = soup.select_one("li.next a")
    if nxt and nxt.get("href"):
        return urljoin(current_url, nxt["href"])
    return None


def scrape_quotes(start_url: str, max_pages: int = 1, delay: float = 1.0) -> list[dict]:
    if not robots_allows(start_url):
        raise SystemExit(f"robots.txt does not allow scraping {start_url}")
    all_quotes: list[dict] = []
    url: str | None = start_url
    page = 0
    while url and page < max_pages:
        page += 1
        print(f"Page {page}: {url}")
        html = fetch_page(url)
        all_quotes.extend(parse_quotes(html))
        url = next_page_url(html, url)
        if url and page < max_pages:
            time.sleep(delay)
    return all_quotes


def save_csv(quotes: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        writer.writerows(quotes)


def save_json(quotes: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape quotes into CSV or JSON.")
    parser.add_argument("--url", default="https://quotes.toscrape.com",
                        help="Page to scrape (default: quotes.toscrape.com)")
    parser.add_argument("--pages", type=int, default=1,
                        help="How many pages to follow (default: 1)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Seconds to wait between requests (default: 1)")
    parser.add_argument("--format", choices=["csv", "json"], default="csv",
                        help="Output format (default: csv)")
    parser.add_argument("--output", default="quotes.csv",
                        help="Output file (default: quotes.csv)")
    args = parser.parse_args()

    quotes = scrape_quotes(args.url, args.pages, args.delay)
    if args.format == "json":
        save_json(quotes, args.output)
    else:
        save_csv(quotes, args.output)
    print(f"Saved {len(quotes)} quotes to {args.output}")


if __name__ == "__main__":
    main()
