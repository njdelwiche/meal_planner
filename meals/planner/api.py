import requests
import os

# Source: https://www.geeksforgeeks.org/get-post-requests-using-python/
url = "https://trackapi.nutritionix.com/v2/natural/nutrients/"
API_key = os.environ["nutrix_key"]
API_id = os.environ["nutrix_id"]
API_user_id = "Beta Testing"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    # Set environment variables
    "x-app-id": API_id,
    "x-app-key": API_key,
    "x-remote-user-id": API_user_id
  }


def get_info(search):
    '''
    Gets food item names and weights by querying
    Nutrionix natural language API. Ideally, searches should
    represent a long list of items to reduce API calls.
    '''
    data = []
    # Submit a post request to the API
    hits = requests.post(url=url, headers=headers, json={"query": search})
    results = hits.json().get("foods")
    # Store name and weight for each item
    for food_item in results:
        weight = food_item.get('serving_weight_grams')
        item = food_item.get('tags').get('item')
        data.append((item.lower(), weight))
    return data
