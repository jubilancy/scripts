# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "pandas",
# ]
# ///

import requests
import pandas as pd
import time
import re
import sys
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
INPUT_FILE  = "books.csv"          # Your CSV file (change if needed)
TITLE_COL   = "title"              # Column name for titles
URL_COL     = "url"                # Column name for Goodreads URLs
OUTPUT_FILE = "books_with_isbn.csv"
DELAY       = 0.5                  # Seconds between API requests (be polite)

# ── Helpers ──────────────────────────────────────────────────────────────────

def extract_goodreads_id(url: str) -> str | None:
    """Pull the numeric Goodreads book ID out of a URL."""
    if not isinstance(url, str):
        return None
    match = re.search(r'/book/show/(\d+)', url)
    return match.group(1) if match else None


def openlibrary_by_title(title: str, author: str = "") -> dict:
    """Search Open Library by title (+ optional author) and return best match."""
    params = {"title": title, "limit": 1, "fields": "isbn,title,author_name"}
    if author:
        params["author"] = author
    try:
        r = requests.get("https://openlibrary.org/search.json", params=params, timeout=10)
        r.raise_for_status()
        docs = r.json().get("docs", [])
        if docs:
            doc = docs[0]
            isbns = doc.get("isbn", [])
            # Prefer 13-digit ISBNs
            isbn13 = next((i for i in isbns if len(i) == 13), None)
            isbn10 = next((i for i in isbns if len(i) == 10), None)
            return {
                "isbn13": isbn13 or "",
                "isbn10": isbn10 or "",
                "ol_title": doc.get("title", ""),
                "ol_author": ", ".join(doc.get("author_name", [])),
                "source": "openlibrary",
            }
    except Exception as e:
        print(f"  [OpenLibrary error] {title!r}: {e}", file=sys.stderr)
    return {}


def lookup_isbn(row: pd.Series) -> pd.Series:
    title  = str(row.get(TITLE_COL, "")).strip()
    url    = str(row.get(URL_COL,   "")).strip()
    author = str(row.get("author",  "")).strip() if "author" in row.index else ""

    # Skip if ISBN already filled
    existing_isbn = str(row.get("isbn", "")).strip()
    if existing_isbn and existing_isbn not in ("", "nan", "None"):
        return pd.Series({
            "isbn13": existing_isbn if len(existing_isbn) == 13 else "",
            "isbn10": existing_isbn if len(existing_isbn) == 10 else "",
            "ol_title": "",
            "ol_author": "",
            "source": "pre-existing",
        })

    print(f"Looking up: {title[:60]}")
    result = openlibrary_by_title(title, author)
    time.sleep(DELAY)
    return pd.Series(result)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    csv_path = Path(INPUT_FILE)
    if not csv_path.exists():
        print(f"ERROR: '{INPUT_FILE}' not found.\n"
              f"Place your CSV in the same folder as this script and re-run.",
              file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path, dtype=str)
    print(f"Loaded {len(df)} rows from {INPUT_FILE}")
    print(f"Columns: {list(df.columns)}\n")

    # Make sure required columns exist
    if TITLE_COL not in df.columns:
        print(f"ERROR: Column '{TITLE_COL}' not found. "
              f"Set TITLE_COL at the top of the script to match your CSV.", file=sys.stderr)
        sys.exit(1)

    # Add Goodreads ID column from URL
    if URL_COL in df.columns:
        df["goodreads_id"] = df[URL_COL].apply(extract_goodreads_id)
    else:
        df["goodreads_id"] = ""

    # Look up ISBNs
    results = df.apply(lookup_isbn, axis=1)
    df = pd.concat([df, results], axis=1)

    df.to_csv(OUTPUT_FILE, index=False)
    found    = (df["isbn13"].notna() & (df["isbn13"] != "")).sum()
    not_found = len(df) - found
    print(f"\n✓ Done — {found} ISBNs found, {not_found} not found.")
    print(f"✓ Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
