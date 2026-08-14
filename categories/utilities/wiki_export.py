# /// script
# dependencies = [
#   "wikipedia-api",
# ]
# ///

import wikipediaapi
import os
import time
from datetime import datetime

# 1. Initialize API
wiki = wikipediaapi.Wikipedia(
    user_agent='ResearchArchiveBot/1.0 (Contact: eliana.haile; personal-project; building-knowledge-base)',
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

VAULT_PATH = "/Users/eliana/Desktop/wiki"
os.makedirs(VAULT_PATH, exist_ok=True)

# 2. Process URLs
try:
    with open("wiki_links.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Error: 'wiki_links.txt' not found.")
    urls = []

for url in urls:
    title_slug = url.split('/')[-1]
    search_title = title_slug.replace('_', ' ')
    page = wiki.page(search_title)
    
    if page.exists():
        safe_name = "".join([c for c in page.title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        file_path = os.path.join(VAULT_PATH, f"{safe_name}.md")
        
        # Calculate word count for YAML
        words = page.text.split()
        word_count = len(words)
        
        # 3. Write with Enhanced YAML
        with open(file_path, "w", encoding="utf-8") as out:
            out.write("---\n")
            out.write(f"title: \"{page.title}\"\n")
            out.write(f"source: {url}\n")
            out.write(f"aliases: [\"{search_title}\", \"{title_slug}\"]\n")
            out.write(f"created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            out.write(f"word_count: {word_count}\n")
            out.write(f"type: research-entry\n")
            out.write(f"cssclasses: [scrapbook-style]\n") # Custom class for your aesthetic
            out.write("tags:\n  - wiki-import\n  - archive\n")
            out.write("---\n\n")
            
            out.write(f"# {page.title}\n\n")
            out.write(page.text)
            
        print(f"✓ Saved: {page.title} ({word_count} words)")
    else:
        print(f"✗ Not found: {search_title}")
    
    time.sleep(1)