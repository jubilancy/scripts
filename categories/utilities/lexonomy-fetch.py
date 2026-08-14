# /// script
# dependencies = [
#   "requests",
# ]
# ///

import requests
import os

# --- Configuration ---
API_KEY = "NTWG7OE3H5IYH2CDGRVHP4B7IYWYZDP4"
BASE_URL = "https://www.lexonomy.eu/api"
OUTPUT_DIR = "lexonomy_exports"

# --- Extracted Dictionary IDs ---
DICTIONARY_IDS = [
    "ysa2p5ii", "px2hg65f", "asdfj", "j6j3t5ta", "7recj7bb",
    "y3ph5riw", "4spu8pvk", "xpa3mw79", "ddu5f2ce", "2wmupiys",
    "9wciquad", "74qm3htn", "g63n7idw"
]

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created folder: {OUTPUT_DIR}")

    for dict_id in DICTIONARY_IDS:
        print(f"📥 Downloading: {dict_id}...")
        
        # Lexonomy API endpoint for full entry export
        export_url = f"{BASE_URL}/getEntries?key={API_KEY}&dict={dict_id}"
        
        try:
            res = requests.get(export_url)
            res.raise_for_status()
            
            # Save to XML file
            save_path = os.path.join(OUTPUT_DIR, f"{dict_id}.xml")
            with open(save_path, "wb") as f:
                f.write(res.content)
            print(f"✅ Saved to {save_path}")
            
        except requests.exceptions.HTTPError as e:
            if res.status_code == 403:
                print(f"❌ Access Denied for {dict_id}. Check API key permissions.")
            elif res.status_code == 404:
                print(f"❌ Dictionary {dict_id} not found (404).")
            else:
                print(f"⚠️ HTTP Error for {dict_id}: {e}")
        except Exception as e:
            print(f"⚠️ Failed {dict_id}: {e}")

if __name__ == "__main__":
    main()