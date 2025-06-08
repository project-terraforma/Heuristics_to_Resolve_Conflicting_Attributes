# import requests

API_KEY = "YOUR_YELP_API_KEY"  # Replace with your Yelp API Key

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

SEARCH_ENDPOINT = "https://api.yelp.com/v3/businesses/search"

def search_yelp_businesses(location="New York, NY", term="restaurants", limit=50):
    params = {
        "location": location,
        "term": term,
        "limit": limit,  # max 50 per request
        "sort_by": "best_match"  # or rating, review_count, distance
    }
    
    response = requests.get(SEARCH_ENDPOINT, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    data = response.json()
    return data.get("businesses", [])

# Example usage:
if __name__ == "__main__":
    businesses = search_yelp_businesses()
    for biz in businesses:
        print(f"{biz['name']} - Rating: {biz['rating']} - Address: {' '.join(biz['location']['display_address'])}")

