# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import os
import pathlib

# Root directory for your Quartz content
TARGET_DIR = '/Users/eliana/Desktop/quartz'

def process_all_files():
    base_path = pathlib.Path(TARGET_DIR)
    processed_count = 0
    skipped_count = 0

    if not base_path.exists():
        print(f"Error: Directory '{TARGET_DIR}' not found.")
        return

    # .rglob("*") tells Python to look in every subfolder recursively
    for file_path in base_path.rglob("*.md"):
        # Skip index.md files
        if file_path.name == "index.md":
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip if frontmatter already exists
            if content.startswith("---"):
                skipped_count += 1
                continue

            # Generate title: "my-file-name" -> "my file name"
            clean_title = file_path.stem.replace("-", " ").replace("_", " ")
            
            frontmatter = f"---\ntitle: \"{clean_title}\"\n---\n\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)
            
            processed_count += 1
            print(f"Added title to: {file_path.relative_to(base_path)}")

        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

    print(f"\n--- Task Complete ---")
    print(f"Processed: {processed_count} files")
    print(f"Skipped:   {skipped_count} files (already had frontmatter)")

if __name__ == "__main__":
    process_all_files()