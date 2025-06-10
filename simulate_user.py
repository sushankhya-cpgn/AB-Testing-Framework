import requests
import random
from faker import Faker

fake = Faker()

EXPERIMENT_ID = 1  
BASE_URL = "http://127.0.0.1:5001"


CONVERSION_RATES = {
    "Red Button": 0.3,
    "Blue Button": 0.5
}

assignment_map = {}  

# Step 1: Generate and assign users
for _ in range(500):
    email = fake.email()
    response = requests.post(f"{BASE_URL}/assign_user", json={
        "email": email,
        "experiment_id": EXPERIMENT_ID
    })
    
    if response.ok:
        result = response.json()
        assignment_id = result["assignment_id"]
        variant = result["variant"]
        assignment_map[email] = (assignment_id, variant)
        print(f"{email} → {variant} (assignment_id={assignment_id})")
    else:
        print(f"Error assigning {email}")

# Step 2: Simulate metric recording 
record_metric = True
if record_metric:
    for email, (assignment_id, variant) in assignment_map.items():
        converted = random.random() < CONVERSION_RATES[variant]
        value = 1 if converted else 0

        res = requests.post(f"{BASE_URL}/record_metric", json={
            "assignment_id": assignment_id,
            "metric": "conversion",
            "value": value
        })

        print(f"Recorded conversion={value} for {email} ({variant})")
