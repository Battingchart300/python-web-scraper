# python-web-scraper

Simple Python web scraper — download pages, extract data and save it to CSV or JSON.

Built with `requests` + `BeautifulSoup`. Example site is [quotes.toscrape.com](https://quotes.toscrape.com), a page made for practising scraping: 10 quotes per page, each with text, author and tags.

## How to run

```bash
pip install -r requirements.txt
python scraper.py
```

That scrapes 1 page (10 quotes) into `quotes.csv`.

More options:

```bash
python scraper.py --pages 2 --output quotes.csv
python scraper.py --pages 1 --format json --output quotes.json
```

## Output

CSV / JSON with 3 columns:

| text | author | tags |
| --- | --- | --- |
| "The world as we have created it..." | Albert Einstein | change, deep-thoughts, thinking, world |

## Rules

- Only public pages, no login, no personal data.
- Respects `robots.txt` — checked before every run (quotes.toscrape.com has none, checked 17.11.2026, so scraping it is allowed).
- Waits 1 second between requests by default, so the server is not hammered.

## License

MIT — see [LICENSE](LICENSE).
