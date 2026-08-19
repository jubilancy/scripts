import math
from googleapiclient.discovery import build

def get_max_google_results(search_term: str, api_key: str, cse_id: str) -> list:
    """
    Fetches the maximum possible results (100) from Google Custom Search API
    by paginating through 10 requests of 10 results each.
    """
    service = build("customsearch", "v1", developerKey=api_key)
    all_items = []
    
    # Maximum 100 total items allowed by Google API (10 loops * 10 results)
    max_results = 100 
    results_per_page = 10
    start_index = 1

    while start_index <= max_results:
        try:
            # Execute search query
            response = service.cse().list(
                q=search_term,
                cx=cse_id,
                num=results_per_page,
                start=start_index
            ).execute()
            
            # Extract items from response payload
            items = response.get("items", [])
            if not items:
                break
                
            all_items.extend(items)
            
            # Increment start index to fetch the next page block
            start_index += results_per_page
            
        except Exception as e:
            print(f"API Error at start index {start_index}: {e}")
            break

    return all_items

# Example Usage:
# API_KEY = "YOUR_GOOGLE_API_KEY"
# CSE_ID = "YOUR_CUSTOM_SEARCH_ENGINE_ID"
# results = get_max_google_results("quantum computing developments", API_KEY, CSE_ID)
# print(f"Retrieved {len(results)} total search results.")