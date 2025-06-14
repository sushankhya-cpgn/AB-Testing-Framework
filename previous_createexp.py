
# import requests

# BASE_URL = "http://127.0.0.1:5001"

# experiments = [
#     {
#     "name": "Button Color Test",
#     "start_date": "2025-06-01",
#     "end_date": "2025-07-01",
#     "variants": ["Red Button", "Blue Button"]
#     },

#     {
#         "name": "Data Preprocessing Test",
#         "start_date": "2025-06-01",
#         "end_date": "2025-06-15",
#         "variants": ["Standardization", "Normalization"]
#     },

#     {
#         "name": "Model Comparison Test",
#         "start_date": "2025-06-15",
#         "end_date": "2025-07-01",
#         "variants": ["Logistic Regression", "Decision Tree"]
#     },

#     {
#         "name": "Data Augmentation Test",
#         "start_date": "2025-07-01",
#         "end_date": "2025-07-15",
#         "variants": ["Image Rotation", "Image Flipping"]
#     },
  
#     {
#         "name": "Model Deployment Test",
#         "start_date": "2025-07-20",
#         "end_date": "2025-08-05",
#         "variants": ["Batch Inference", "Real-time Inference"]
#     },

#     {
#         "name": "Data Pipeline Efficiency Test",
#         "start_date": "2025-08-01",
#         "end_date": "2025-08-15",
#         "variants": ["Pandas Pipeline", "Dask Pipeline"]
#     }
# ]

# # Loop through the experiments and send POST requests
# for experiment in experiments:
#     response = requests.post(f"{BASE_URL}/create_experiment", json=experiment)
#     if response.ok:
#         print(f"Experiment '{experiment['name']}' created:", response.json())
#     else:
#         print(f"Failed to create experiment '{experiment['name']}':", response.text)



# import requests

# BASE_URL = "http://127.0.0.1:5001"

# experiment_data = {
#     "name": "Button Color Test",
#     "start_date": "2025-06-01",
#     "end_date": "2025-07-01",
#     "variants": ["Red Button", "Blue Button"]
# }

# response = requests.post(f"{BASE_URL}/create_experiment", json=experiment_data)
# if response.ok:
#     print("Experiment created:", response.json())
# else:
#     print("Failed to create experiment:", response.text)

# import requests

# BASE_URL = "http://127.0.0.1:5001"

# experiment_data = {
#     "name": "Button Color Test",
#     "start_date": "2025-06-01",
#     "end_date": "2025-07-01",
#     "variants": ["Red Button", "Blue Button"]
# }

# response = requests.post(f"{BASE_URL}/create_experiment", json=experiment_data)
# if response.ok:
#     print("Experiment created:", response.json())
# else:
#     print("Failed to create experiment:", response.text)

import requests

BASE_URL = "http://127.0.0.1:5001"

# Define multiple experiments
experiments = [
    {
        "name": "Button Color Test",
        "start_date": "2025-06-01",
        "end_date": "2025-07-01",
        "variants": ["Red Button", "Blue Button"]
    },
    {
        "name": "Checkout Flow Test",
        "start_date": "2025-06-15",
        "end_date": "2025-07-15",
        "variants": ["Single Page Checkout", "Multi Page Checkout"]
    },
    {
        "name": "Banner Ad Test",
        "start_date": "2025-06-20",
        "end_date": "2025-07-20",
        "variants": ["Static Banner", "Animated Banner"]
    }
]

# Create experiments and store IDs
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