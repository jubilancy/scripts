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
INPUT_FILE  = "books.csv"
TITLE_COL   = "title"
AUTHOR_COL  = "author"
OUTPUT_FILE = "books_with_isbn.csv"
DELAY       = 0.5

# ── Helpers ──────────────────────────────────────────────────────────────────

def openlibrary_search(title: str, author: str = "") -> dict:
    """Search Open Library by title + author, fall back to title only."""
    def _query(params):
        try:
            r = requests.get(
                "https://openlibrary.org/search.json",
                params={**params, "limit": 1, "fields": "isbn,title,author_name"},
                timeout=10,
            )
            r.raise_for_status()
            docs = r.json().get("docs", [])
            if docs:
                doc = docs[0]
                isbns = doc.get("isbn", [])
                isbn13 = next((i for i in isbns if len(i) == 13), None)
                isbn10 = next((i for i in isbns if len(i) == 10), None)
                if isbn13 or isbn10:
                    return {
                        "isbn13":    isbn13 or "",
                        "isbn10":    isbn10 or "",
                        "ol_title":  doc.get("title", ""),
                        "ol_author": ", ".join(doc.get("author_name", [])),
                    }
        except Exception as e:
            print(f"\n  [API error] {title!r}: {e}", file=sys.stderr)
        return {}

    # Pass 1: title + author (most accurate)
    if author:
        result = _query({"title": title, "author": author})
        if result:
            return {**result, "source": "title+author"}
        time.sleep(DELAY)

    # Pass 2: title only (fallback)
    result = _query({"title": title})
    if result:
        return {**result, "source": "title-only"}

    return {"isbn13": "", "isbn10": "", "ol_title": "", "ol_author": "", "source": "not found"}


def print_progress(current: int, total: int, found: int, not_found: int, title: str):
    pct      = current / total * 100
    bar_len  = 28
    filled   = int(bar_len * current / total)
    bar      = "█" * filled + "░" * (bar_len - filled)
    eta_secs = int((total - current) * DELAY * 1.2)
    eta_str  = f"{eta_secs // 60}m {eta_secs % 60}s" if eta_secs >= 60 else f"{eta_secs}s"
    t        = title[:34] + "…" if len(title) > 34 else title.ljust(35)
    print(
        f"\r[{bar}] {current:>4}/{total}  {pct:>5.1f}%  "
        f"✓{found} ✗{not_found}  ETA {eta_str}  {t}",
        end="", flush=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    csv_path = Path(INPUT_FILE)
    if not csv_path.exists():
        print(f"ERROR: '{INPUT_FILE}' not found. Place your CSV here and re-run.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path, dtype=str).fillna("")
    total = len(df)
    print(f"Loaded {total} rows from {INPUT_FILE}")
    print(f"Columns: {list(df.columns)}\n")

    if TITLE_COL not in df.columns:
        print(f"ERROR: Column '{TITLE_COL}' not found. Update TITLE_COL at the top of the script.", file=sys.stderr)
        sys.exit(1)

    has_author = AUTHOR_COL in df.columns
    if not has_author:
        print(f"Note: No '{AUTHOR_COL}' column found — searching by title only.\n")

    results   = []
    found     = 0
    not_found = 0

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        title  = str(row.get(TITLE_COL,  "")).strip()
        author = str(row.get(AUTHOR_COL, "")).strip() if has_author else ""

        # Skip rows that already have an ISBN
        existing = str(row.get("isbn13", "") or row.get("isbn", "")).strip()
        if existing and existing not in ("", "nan", "None"):
            results.append({"isbn13": existing, "isbn10": "", "ol_title": "", "ol_author": "", "source": "pre-existing"})
            found += 1
            print_progress(i, total, found, not_found, title)
            continue

        result = openlibrary_search(title, author)
        if result.get("isbn13") or result.get("isbn10"):
            found += 1
        else:
            not_found += 1

        results.append(result)
        time.sleep(DELAY)
        print_progress(i, total, found, not_found, title)

    print()  # newline after bar

    out_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    out_df.to_csv(OUTPUT_FILE, index=False)

    match_rate = found / total * 100
    print(f"\n{'─'*55}")
    print(f"  Total rows    : {total}")
    print(f"  ISBNs found   : {found}  ({match_rate:.1f}%)")
    print(f"  Not found     : {not_found}  ({100 - match_rate:.1f}%)")
    print(f"  Output file   : {OUTPUT_FILE}")
    print(f"{'─'*55}")


if __name__ == "__main__":
    main()
