# /// script
# dependencies = ["requests"]
# ///

import requests
import csv
import time

def get_isbn(title):
    """Fetches ISBN_13 with a broader search and rate limiting."""
    try:
        url = "https://www.googleapis.com/books/v1/volumes"
        # Removed 'intitle:' to allow for broader matching
        params = {"q": title, "maxResults": 3} 
        response = requests.get(url, timeout=10)
        
        if response.status_code == 429:
            time.sleep(5)  # Back off if rate limited
            return "RATE LIMITED"
            
        data = response.json()
        
        if "items" in data:
            # Check the first few results for an ISBN_13
            for item in data["items"]:
                volume_info = item.get("volumeInfo", {})
                identifiers = volume_info.get("industryIdentifiers", [])
                for identifier in identifiers:
                    if identifier["type"] == "ISBN_13":
                        return identifier["identifier"]
        return "NOT FOUND"
    except Exception:
        return "NOT FOUND"

def process_titles(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            titles = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    results = []
    for title in titles:
        print(f"Searching for: {title}...")
        isbn = get_isbn(title)
        results.append({"Title": title, "ISBN": isbn})
        # Respectful delay for the API
        time.sleep(1) 

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "ISBN"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Done! Results saved to {output_file}")

if __name__ == "__main__":
    process_titles('titles.txt', 'isbns.csv')