# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import sqlite3
import os
import pathlib

SQL_FILE = 'export.sql'
# Change this to your Quartz content directory if needed
OUTPUT_DIR = './content' 

def export_to_quartz():
    conn = sqlite3.connect(':memory:')
    
    if not os.path.exists(SQL_FILE):
        print(f"Error: {SQL_FILE} not found.")
        return
    
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    cursor.execute("SELECT title, content, slug, category, created_at FROM notes")
    notes = cursor.fetchall()

    for title, content, slug, category, created_at in notes:
        # Quartz uses tags for categorization
        tag = category.strip() if category else 'uncategorized'
        
        # Format date to YYYY-MM-DD for Quartz compatibility
        clean_date = created_at.split(' ')[0] if created_at else ""
        
        md_content = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"date: {clean_date}\n"
            f"tags:\n"
            f"  - {tag}\n"
            f"---\n\n"
            f"{content}"
        )
        
        # Save files directly into folders (Quartz handles this as folders/subfolders)
        save_path = os.path.join(OUTPUT_DIR, tag)
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)
        
        file_name = f"{slug or title.lower().replace(' ', '-')}.md"
        with open(os.path.join(save_path, file_name), 'w', encoding='utf-8') as f:
            f.write(md_content)

    print(f"Success: {len(notes)} posts ready for Quartz in {OUTPUT_DIR}/")
    conn.close()

if __name__ == "__main__":
    export_to_quartz()