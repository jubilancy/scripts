import csv
import time
from pathlib import Path

import requests
from requests.exceptions import RequestException
from tqdm import tqdm

INPUT_CSV = Path("goodreads_import_split_2026-05-24.csv")
OUTPUT_CSV = Path("goodreads_import_normalized_2026-05-24.csv")

SAVE_EVERY = 5
GOOGLE_DELAY = 0.15
OPENLIB_DELAY = 0.35
TIMEOUT = (3, 12)

FIELDNAMES = ["title", "author", "category", "genre", "tag"]

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "eliana-book-normalizer/1.0 (contact: elianatamrat@gmail.com)"
    }
)


def norm(s: str) -> str:
    return "".join(ch.lower() for ch in str(s) if ch.isalnum() or ch.isspace()).strip()


def load_rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_rows(rows, path: Path):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "title": row.get("title", ""),
                    "author": row.get("author", ""),
                    "category": row.get("category", ""),
                    "genre": row.get("genre", ""),
                    "tag": row.get("tag", ""),
                }
            )


def is_done(row):
    return bool(row.get("genre", "").strip())


def score_match(input_title, input_author, cand_title, cand_authors):
    score = 0
    it = norm(input_title)
    ia = norm(input_author)
    ct = norm(cand_title)
    ca = " ".join(norm(a) for a in cand_authors)

    if it and ct == it:
        score += 6
    elif it and (ct.startswith(it[: min(len(it), 12)]) or it.startswith(ct[: min(len(ct), 12)])):
        score += 3

    if ia:
        parts = ia.split()
        if parts:
            surname = parts[-1]
            if surname and surname in ca:
                score += 4

    return score


def google_books_lookup(title, author):
    params = {
        "q": f'intitle:{title} inauthor:{author}',
        "maxResults": 5,
        "printType": "books",
    }

    try:
        r = session.get(
            "https://www.googleapis.com/books/v1/volumes",
            params=params,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
    except RequestException:
        return None

    items = data.get("items", [])
    if not items:
        return None

    best = None
    best_score = -1

    for item in items:
        vi = item.get("volumeInfo", {})
        cand_title = vi.get("title", "")
        cand_authors = vi.get("authors", []) or []
        score = score_match(title, author, cand_title, cand_authors)
        if score > best_score:
            best_score = score
            best = vi

    if not best:
        return None

    out_title = best.get("title", title)
    out_authors = best.get("authors", [author]) or [author]
    categories = best.get("categories", []) or []

    return {
        "title": out_title,
        "author": out_authors[0],
        "genre": "; ".join(categories[:3]),
        "source": "google",
    }


def openlibrary_lookup(title, author):
    params = {"title": title, "author": author, "limit": 5}

    try:
        r = session.get(
            "https://openlibrary.org/search.json",
            params=params,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
    except RequestException:
        return None

    docs = data.get("docs", [])
    if not docs:
        return None

    best = None
    best_score = -1

    for doc in docs:
        cand_title = doc.get("title", "")
        cand_authors = doc.get("author_name", []) or []
        score = score_match(title, author, cand_title, cand_authors)
        if score > best_score:
            best_score = score
            best = doc

    if not best:
        return None

    out_title = best.get("title", title)
    out_authors = best.get("author_name", [author]) or [author]
    subjects = best.get("subject_facet") or best.get("subject") or []

    if isinstance(subjects, list):
        genre = "; ".join(subjects[:3])
    else:
        genre = str(subjects)

    return {
        "title": out_title,
        "author": out_authors[0],
        "genre": genre,
        "source": "openlibrary",
    }


def normalize_row(row):
    original_title = row.get("title", "").strip()
    original_author = row.get("author", "").strip()

    result = google_books_lookup(original_title, original_author)
    time.sleep(GOOGLE_DELAY)

    if result:
        row["title"] = result["title"]
        row["author"] = result["author"]
        row["genre"] = result["genre"]
        return result["source"]

    result = openlibrary_lookup(original_title, original_author)
    time.sleep(OPENLIB_DELAY)

    if result:
        row["title"] = result["title"]
        row["author"] = result["author"]
        row["genre"] = result["genre"]
        return result["source"]

    row["genre"] = ""
    return "no_match"


def main():
    rows = load_rows(OUTPUT_CSV) if OUTPUT_CSV.exists() else load_rows(INPUT_CSV)

    total = len(rows)
    completed = sum(1 for row in rows if is_done(row))

    google_hits = 0
    openlibrary_hits = 0
    no_match_hits = 0
    changed_since_save = 0

    pbar = tqdm(
        total=total,
        initial=completed,
        desc="Normalizing books",
        unit="book",
    )

    try:
        for idx, row in enumerate(rows, start=1):
            if is_done(row):
                continue

            source = normalize_row(row)

            if source == "google":
                google_hits += 1
            elif source == "openlibrary":
                openlibrary_hits += 1
            else:
                no_match_hits += 1

            changed_since_save += 1
            pbar.update(1)
            pbar.set_postfix(
                google=google_hits,
                openlib=openlibrary_hits,
                no_match=no_match_hits,
                saved_every=SAVE_EVERY,
            )

            if changed_since_save >= SAVE_EVERY:
                save_rows(rows, OUTPUT_CSV)
                changed_since_save = 0

        save_rows(rows, OUTPUT_CSV)

    except KeyboardInterrupt:
        save_rows(rows, OUTPUT_CSV)
        pbar.close()
        print("\\nStopped by user. Progress saved.")
        return

    pbar.close()
    print(f"Done. Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()