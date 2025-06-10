import requests

BASE_URL = "http://127.0.0.1:5001"

experiment_data = {
    "name": "Button Color Test",
    "start_date": "2025-06-01",
    "end_date": "2025-07-01",
    "variants": ["Red Button", "Blue Button"]
}

response = requests.post(f"{BASE_URL}/create_experiment", json=experiment_data)
if response.ok:
    print("Experiment created:", response.json())
else:
    print("Failed to create experiment:", response.text)
