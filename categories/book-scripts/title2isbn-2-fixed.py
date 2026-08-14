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
import sys
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
INPUT_FILE  = "books.csv"
OUTPUT_FILE = "books_with_isbn.csv"
TITLE_COL   = "title"
AUTHOR_COL  = "author"
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


def print_progress(current: int, total: int, found: int, not_found: int, skipped: int, title: str):
    pct     = current / total * 100
    bar_len = 28
    filled  = int(bar_len * current / total)
    bar     = "█" * filled + "░" * (bar_len - filled)
    remaining = total - current
    eta_secs  = int(remaining * DELAY * 1.2)
    eta_str   = f"{eta_secs // 60}m {eta_secs % 60}s" if eta_secs >= 60 else f"{eta_secs}s"
    t = (title[:34] + "…") if len(title) > 34 else title.ljust(35)
    print(
        f"\r[{bar}] {current:>4}/{total} {pct:>5.1f}%  "
        f"✓{found} ✗{not_found} ⏭{skipped}  ETA {eta_str}  {t}",
        end="", flush=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    csv_path = Path(INPUT_FILE)
    if not csv_path.exists():
        print(f"ERROR: '{INPUT_FILE}' not found.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path, dtype=str).fillna("")
    total = len(df)
    print(f"Loaded {total} rows from {INPUT_FILE}")
    print(f"Columns: {list(df.columns)}\n")

    if TITLE_COL not in df.columns:
        print(f"ERROR: Column '{TITLE_COL}' not found.", file=sys.stderr)
        sys.exit(1)

    has_author = AUTHOR_COL in df.columns

    # ── Resume logic ─────────────────────────────────────────────────────────
    out_path = Path(OUTPUT_FILE)
    already_done: set[str] = set()

    if out_path.exists():
        try:
            done_df = pd.read_csv(out_path, dtype=str).fillna("")
            already_done = set(done_df[TITLE_COL].tolist())
            print(f"Resuming — {len(already_done)} rows already in {OUTPUT_FILE}, skipping them.\n")
        except Exception as e:
            print(f"Warning: could not read existing output ({e}). Starting fresh.\n")

    write_header = not out_path.exists() or len(already_done) == 0

    # ── Process ──────────────────────────────────────────────────────────────
    found     = 0
    not_found = 0
    skipped   = 0

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        title  = str(row.get(TITLE_COL, "")).strip()
        author = str(row.get(AUTHOR_COL, "")).strip() if has_author else ""

        # Skip already-processed rows
        if title in already_done:
            skipped += 1
            print_progress(i, total, found, not_found, skipped, title)
            continue

        # If the input row already has an ISBN (pre-existing data), carry it forward
        existing_isbn13 = str(row.get("isbn13", "")).strip()
        existing_isbn10 = str(row.get("isbn10", "")).strip()
        if existing_isbn13 and existing_isbn13 not in ("", "nan", "None"):
            result = {
                "isbn13":    existing_isbn13,
                "isbn10":    existing_isbn10,
                "ol_title":  str(row.get("ol_title", "")),
                "ol_author": str(row.get("ol_author", "")),
                "source":    "pre-existing",
            }
            found += 1
        else:
            result = openlibrary_search(title, author)
            if result.get("isbn13") or result.get("isbn10"):
                found += 1
            else:
                not_found += 1
            time.sleep(DELAY)

        # Build output row: original columns + result columns (result wins on overlap)
        row_dict = row.to_dict()
        row_dict.update(result)

        # Write one row at a time so a Ctrl+C never loses progress
        pd.DataFrame([row_dict]).to_csv(
            out_path,
            mode="a",
            header=write_header,
            index=False,
        )
        write_header = False  # only write header once

        print_progress(i, total, found, not_found, skipped, title)

    print()  # newline after progress bar

    # ── Summary ───────────────────────────────────────────────────────────────
    processed = found + not_found
    match_rate = (found / processed * 100) if processed else 0
    print(f"\n{'─' * 55}")
    print(f"  Total rows      : {total}")
    print(f"  Skipped (done)  : {skipped}")
    print(f"  Newly processed : {processed}")
    print(f"  ISBNs found     : {found} ({match_rate:.1f}%)")
    print(f"  Not found       : {not_found} ({100 - match_rate:.1f}%)")
    print(f"  Output file     : {OUTPUT_FILE}")
    print(f"{'─' * 55}")


if __name__ == "__main__":
    main()
