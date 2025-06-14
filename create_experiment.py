import requests

BASE_URL = "http://127.0.0.1:5001"

# Define experiments with different metric types
experiments = [
    {
        "name": "Button Color Test",
        "start_date": "2025-06-01",
        "end_date": "2025-07-01",
        "variants": ["Red Button", "Blue Button"],
        "metric_type": "binary"
    },
    {
        "name": "Checkout Flow Revenue",
        "start_date": "2025-06-15",
        "end_date": "2025-07-15",
        "variants": ["Single Page Checkout", "Multi Page Checkout"],
        "metric_type": "continuous"
    },
    {
        "name": "Banner Ad Satisfaction",
        "start_date": "2025-06-20",
        "end_date": "2025-07-20",
        "variants": ["Static Banner", "Animated Banner"],
        "metric_type": "categorical"
    }
]

# Create experimentsC
experiment_ids = []
for exp_data in experiments:
    response = requests.post(f"{BASE_URL}/create_experiment", json=exp_data)
    if response.ok:
        result = response.json()
        experiment_ids.append(result["experiment_id"])
        print(f"Created '{exp_data['name']}': {result}")
    else:
        print(f"Failed to create '{exp_data['name']}': {response.text}")

print("Experiment IDs:", experiment_ids)