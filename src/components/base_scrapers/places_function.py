import requests


def get_place_id(name, api_key):
    # Base URL
    base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

    # Parameters in a dictionary
    params = {
        "input": name,
        "inputtype": "textquery",
        "fields": "place_id,formatted_address,geometry,name",
        "key": api_key
    }

    # Send request and capture response
    response = requests.get(base_url, params=params)
    # Check if the request is successful
    if response.status_code == 200:
        return response.json()
    else:
        return None