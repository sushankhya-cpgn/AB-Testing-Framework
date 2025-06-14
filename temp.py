# import requests
# import random
# from faker import Faker

# fake = Faker()

# EXPERIMENT_ID = 1  
# BASE_URL = "http://127.0.0.1:5001"


# CONVERSION_RATES = {
#     "Red Button": 0.3,
#     "Blue Button": 0.5
# }

# assignment_map = {}  

# # Step 1: Generate and assign users
# for _ in range(500):
#     email = fake.email()
#     response = requests.post(f"{BASE_URL}/assign_user", json={
#         "email": email,
#         "experiment_id": EXPERIMENT_ID
#     })
    
#     if response.ok:
#         result = response.json()
#         assignment_id = result["assignment_id"]
#         variant = result["variant"]
#         assignment_map[email] = (assignment_id, variant)
#         print(f"{email} → {variant} (assignment_id={assignment_id})")
#     else:
#         print(f"Error assigning {email}")

# # Step 2: Simulate metric recording 
# record_metric = True
# if record_metric:
#     for email, (assignment_id, variant) in assignment_map.items():
#         converted = random.random() < CONVERSION_RATES[variant]
#         value = 1 if converted else 0

#         res = requests.post(f"{BASE_URL}/record_metric", json={
#             "assignment_id": assignment_id,
#             "metric": "conversion",
#             "value": value
#         })

#         print(f"Recorded conversion={value} for {email} ({variant})")

# import requests
# import random
# from faker import Faker

# fake = Faker()
# BASE_URL = "http://127.0.0.1:5001"

# # Variant-specific conversion rates per experiment
# EXPERIMENT_CONVERSION_RATES = {

#     1: {"Red Button": 0.3, "Blue Button": 0.5},
#     2: {"Standardization": 0.4, "Normalization": 0.6},
#     3: {"Logistic Regression": 0.5, "Decision Tree": 0.45},
#     4: {"Image Rotation": 0.55, "Image Flipping": 0.5},
#     5: {"Batch Inference": 0.35, "Real-time Inference": 0.65},
#     6: {"Pandas Pipeline": 0.4, "Dask Pipeline": 0.6}
# }

# NUM_USERS = 300
# record_metric = True

# for experiment_id, conversion_map in EXPERIMENT_CONVERSION_RATES.items():
#     print(f"\nSimulating experiment {experiment_id}...")
#     assignment_map = {}

#     for _ in range(NUM_USERS):
#         email = fake.email()
#         response = requests.post(f"{BASE_URL}/assign_user", json={
#             "email": email,
#             "experiment_id": experiment_id
#         })

#         if response.ok:
#             result = response.json()
#             assignment_id = result["assignment_id"]
#             variant = result["variant"]
#             assignment_map[email] = (assignment_id, variant)
#             print(f"{email} → {variant} (assignment_id={assignment_id})")
#         else:
#             print(f"Error assigning {email}: {response.text}")

#     if record_metric:
#         for email, (assignment_id, variant) in assignment_map.items():
#             conversion_rate = conversion_map.get(variant, 0.5)
#             converted = random.random() < conversion_rate
#             value = 1 if converted else 0

#             res = requests.post(f"{BASE_URL}/record_metric", json={
#                 "assignment_id": assignment_id,
#                 "metric": "conversion",
#                 "value": value
#             })

#             if res.ok:
#                 print(f"Recorded conversion={value} for {email} ({variant})")
#             else:
#                 print(f"Failed to record metric for {email}")


# import requests
# import random
# from faker import Faker

# fake = Faker()
# BASE_URL = "http://127.0.0.1:5001"

# # Conversion rates for each experiment variant
# EXPERIMENT_CONVERSION_RATES = {
#     1: {"Red Button": 0.3, "Blue Button": 0.5},
#     2: {"Standardization": 0.4, "Normalization": 0.6},
#     3: {"Logistic Regression": 0.5, "Decision Tree": 0.45},
#     4: {"Image Rotation": 0.55, "Image Flipping": 0.5},
#     5: {"Batch Inference": 0.35, "Real-time Inference": 0.65},
#     6: {"Pandas Pipeline": 0.4, "Dask Pipeline": 0.6}
# }

# # ------------------------------------------------------------------ #
# # Helper functions
# # ------------------------------------------------------------------ #

# def get_available_experiments():
#     try:
#         r = requests.get(f"{BASE_URL}/experiments", timeout=8)
#         return r.json() if r.ok else []
#     except requests.RequestException as e:
#         print("Connection error:", e)
#         return []

# def display_experiments(experiments):
#     if not experiments:
#         print("No experiments available."); return False
#     print("\nAvailable Experiments\n" + "-" * 60)
#     for i, exp in enumerate(experiments, 1):
#         print(f"{i}. {exp['name']} (ID: {exp['id']})")
#         print(f"   Start: {exp['start_date']} | End: {exp['end_date']}")
#         print(f"   Variants: {', '.join(exp.get('variants', []))}\n")
#     return True


# def simulate_users_for_experiment(experiment_id: int, num_users: int):
#     print(f"\nSimulating {num_users} users for experiment {experiment_id} …")
#     print("-" * 50)

#     assignment_map = {}
#     conversion_rates = EXPERIMENT_CONVERSION_RATES.get(experiment_id, {})
#     assigned = 0

#     # 1) Assign every generated user
#     for i in range(1, num_users + 1):
#         email = fake.email()
#         try:
#             res = requests.post(
#                 f"{BASE_URL}/assign_user",
#                 json={"email": email, "experiment_id": experiment_id},
#                 timeout=8
#             )
#             if res.ok:
#                 data = res.json()
#                 assignment_map[email] = (data["assignment_id"], data["variant"])
#                 assigned += 1
#                 print(f"User {i:3d}: {email} → {data['variant']} (ID: {data['assignment_id']})")
#             else:
#                 print(f"User {i:3d}: ✖ Assign failed – {res.text}")
#         except requests.RequestException as e:
#             print(f"User {i:3d}: ✖ Connection error – {e}")

#     print(f"\n✅ Users assigned: {assigned}/{num_users}")

#     # 2) Simulate and record conversions
#     if not assignment_map:
#         print("No users assigned, stopping."); return

#     print("\nSimulating conversions …\n" + "-" * 30)
#     conversions_recorded = total_conversions = 0

#     for email, (aid, variant) in assignment_map.items():
#         converted = random.random() < conversion_rates.get(variant, 0.5)
#         value = int(converted)

#         try:
#             r = requests.post(
#                 f"{BASE_URL}/record_metric",
#                 json={"assignment_id": aid, "metric": "conversion", "value": value},
#                 timeout=8
#             )
#             if r.ok:
#                 conversions_recorded += 1
#                 total_conversions += value
#                 print(f"{email} ({variant}): {'✓ Converted' if converted else '○ No conversion'}")
#             else:
#                 print(f"✖ Metric record failed for {email}")
#         except requests.RequestException as e:
#             print(f"✖ Metric connection error for {email}: {e}")

#     cr = (total_conversions / conversions_recorded * 100) if conversions_recorded else 0
#     print("\n📊 Summary")
#     print(f"- Metrics recorded: {conversions_recorded}")
#     print(f"- Total conversions: {total_conversions}")
#     print(f"- Observed conversion rate: {cr:.2f}%")



# def main():
#     print("🧪 Interactive Experiment Simulator\n" + "=" * 50)
#     experiments = get_available_experiments()
#     if not display_experiments(experiments):
#         return

#     try:
#         idx = int(input("Select an experiment (number): ").strip())
#         if not 1 <= idx <= len(experiments):
#             print("Invalid selection."); return
#         exp = experiments[idx - 1]
#         n = input("How many users to simulate? (default 50): ").strip()
#         num_users = int(n) if n else 50
#         if num_users <= 0:
#             print("User count must be positive."); return
#         simulate_users_for_experiment(exp["id"], num_users)
#     except (ValueError, KeyboardInterrupt):
#         print("\nCancelled.")
#     except Exception as e:
#         print("Unexpected error:", e)

# if __name__ == "__main__":
#     main()


# import requests
# import random
# from faker import Faker

# fake = Faker()

# EXPERIMENT_ID = 1  
# BASE_URL = "http://127.0.0.1:5001"


# CONVERSION_RATES = {
#     "Red Button": 0.3,
#     "Blue Button": 0.5
# }

# assignment_map = {}  

# # Step 1: Generate and assign users
# for _ in range(500):
#     email = fake.email()
#     response = requests.post(f"{BASE_URL}/assign_user", json={
#         "email": email,
#         "experiment_id": EXPERIMENT_ID
#     })
    
#     if response.ok:
#         result = response.json()
#         assignment_id = result["assignment_id"]
#         variant = result["variant"]
#         assignment_map[email] = (assignment_id, variant)
#         print(f"{email} → {variant} (assignment_id={assignment_id})")
#     else:
#         print(f"Error assigning {email}")

# # Step 2: Simulate metric recording 
# record_metric = True
# if record_metric:
#     for email, (assignment_id, variant) in assignment_map.items():
#         converted = random.random() < CONVERSION_RATES[variant]
#         value = 1 if converted else 0

#         res = requests.post(f"{BASE_URL}/record_metric", json={
#             "assignment_id": assignment_id,
#             "metric": "conversion",
#             "value": value
#         })

#         print(f"Recorded conversion={value} for {email} ({variant})")


#original code
# import requests
# import random
# from faker import Faker
# from collections import defaultdict

# fake = Faker()
# BASE_URL = "http://127.0.0.1:5001"

# # Conversion rates per experiment (for simulation)
# CONVERSION_RATES = {
#     "Button Color Test": {"Red Button": 0.3, "Blue Button": 0.5},
#     "Checkout Flow Test": {"Single Page Checkout": 0.4, "Multi Page Checkout": 0.35},
#     "Banner Ad Test": {"Static Banner": 0.2, "Animated Banner": 0.25}
# }

# def get_active_experiments():
#     """Fetch active experiments from the API."""
#     try:
#         response = requests.get(f"{BASE_URL}/experiments")
#         if response.ok:
#             return response.json()
#         else:
#             print(f"Error fetching experiments: {response.text}")
#             return []
#     except requests.RequestException as e:
#         print(f"Failed to connect to API: {e}")
#         return []

# def prompt_user_for_experiments(experiments):
#     """Prompt user to select experiments by ID."""
#     if not experiments:
#         print("No active experiments available.")
#         return []

#     print("\nAvailable Experiments:")
#     for exp in experiments:
#         print(f"ID: {exp['experiment_id']}, Name: {exp['name']}, Variants: {exp['variants']}")

#     selected_ids = []
#     while not selected_ids:
#         try:
#             user_input = input("\nEnter experiment IDs to simulate (comma-separated, e.g., 1,2,3) or 'all' for all: ").strip()
#             if user_input.lower() == 'all':
#                 selected_ids = [exp['experiment_id'] for exp in experiments]
#             else:
#                 selected_ids = [int(id.strip()) for id in user_input.split(',')]
#                 # Validate IDs
#                 valid_ids = {exp['experiment_id'] for exp in experiments}
#                 if not all(id in valid_ids for id in selected_ids):
#                     print("Invalid experiment ID(s). Please try again.")
#                     selected_ids = []
#         except ValueError:
#             print("Invalid input. Please enter numbers separated by commas or 'all'.")
    
#     return selected_ids

# # Fetch and prompt for experiments
# experiments = get_active_experiments()
# EXPERIMENT_IDS = prompt_user_for_experiments(experiments)
# if not EXPERIMENT_IDS:
#     print("No experiments selected. Exiting.")
#     exit()

# # Store assignments: {email: {experiment_id: (assignment_id, variant)}}
# assignment_map = defaultdict(dict)

# # Step 1: Assign users to selected experiments
# NUM_USERS = 500
# for _ in range(NUM_USERS):
#     email = fake.email()
#     for experiment_id in EXPERIMENT_IDS:
#         response = requests.post(f"{BASE_URL}/assign_user", json={
#             "email": email,
#             "experiment_id": experiment_id
#         })
#         if response.ok:
#             result = response.json()
#             assignment_id = result["assignment_id"]
#             variant = result["variant"]
#             assignment_map[email][experiment_id] = (assignment_id, variant)
#             print(f"{email} → Exp {experiment_id}: {variant} (ID={assignment_id})")
#         else:
#             print(f"Error assigning {email} to Exp {experiment_id}: {response.text}")

# # Step 2: Record metrics
# for email, experiments in assignment_map.items():
#     for experiment_id, (assignment_id, variant) in experiments.items():
#         # Lookup experiment name
#         experiment = next((e for e in get_active_experiments() if e['experiment_id'] == experiment_id), None)
#         if not experiment:
#             print(f"Experiment {experiment_id} not found.")
#             continue
#         experiment_name = experiment['name']

#         # Simulate conversion
#         conversion_rate = CONVERSION_RATES.get(experiment_name, {}).get(variant, 0.1)
#         value = 1 if random.random() < conversion_rate else 0
#         response = requests.post(f"{BASE_URL}/record_metric", json={
#             "assignment_id": assignment_id,
#             "metric": "conversion",
#             "value": value
#         })
#         if response.ok:
#             print(f"Recorded conversion={value} for {email} (Exp {experiment_id}: {variant})")
#         else:
#             print(f"Error recording for {email} (Exp {experiment_id}): {response.text}")

# # Step 3: Analyze experiments
# for experiment_id in EXPERIMENT_IDS:
#     response = requests.get(f"{BASE_URL}/analyze/{experiment_id}")
#     if response.ok:
#         print(f"\nAnalysis for Experiment {experiment_id}:")
#         print(response.json())
#     else:
#         print(f"Failed to analyze Exp {experiment_id}: {response.text}")

import requests
import random
from faker import Faker
from collections import defaultdict
from scipy.stats import norm
import math

fake = Faker()
BASE_URL = "http://127.0.0.1:5001"

# Conversion rates per experiment
CONVERSION_RATES = {
    "Button Color Test": {"Red Button": 0.3, "Blue Button": 0.5},
    "Checkout Flow Test": {"Single Page Checkout": 0.4, "Multi Page Checkout": 0.35},
    "Banner Ad Test": {"Static Banner": 0.2, "Animated Banner": 0.25}
}

# Statistical parameters
ALPHA = 0.05
POWER = 0.80
MDE = 0.1

def calculate_sample_size(baseline_rate, mde=0.1, alpha=0.05, power=0.80):
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    p1 = baseline_rate
    p2 = p1 + mde
    pooled_var = p1 * (1 - p1) + p2 * (1 - p2)
    n = (z_alpha + z_beta) ** 2 * pooled_var / (mde ** 2)
    return math.ceil(n)

def get_active_experiments():
    try:
        response = requests.get(f"{BASE_URL}/experiments")
        if response.ok:
            return response.json()
        print(f"Error fetching experiments: {response.text}")
        return []
    except requests.RequestException as e:
        print(f"Failed to connect to API: {e}")
        return []

def prompt_user_for_experiments(experiments):
    if not experiments:
        print("No active experiments available.")
        return []
    print("\nAvailable Experiments:")
    for exp in experiments:
        print(f"ID: {exp['experiment_id']}, Name: {exp['name']}, Variants: {exp['variants']}")
    selected_ids = []
    while not selected_ids:
        try:
            user_input = input("\nEnter experiment IDs (comma-separated, e.g., 1,2,3) or 'all': ").strip()
            if user_input.lower() == 'all':
                selected_ids = [exp['experiment_id'] for exp in experiments]
            else:
                selected_ids = [int(id.strip()) for id in user_input.split(',')]
                valid_ids = {exp['experiment_id'] for exp in experiments}
                if not all(id in valid_ids for id in selected_ids):
                    print("Invalid experiment ID(s).")
                    selected_ids = []
        except ValueError:
            print("Invalid input. Enter numbers separated by commas or 'all'.")
    return selected_ids

# Fetch and prompt
experiments = get_active_experiments()
EXPERIMENT_IDS = prompt_user_for_experiments(experiments)
if not EXPERIMENT_IDS:
    print("No experiments selected. Exiting.")
    exit()

# Calculate sample sizes
sample_sizes = {}
for experiment_id in EXPERIMENT_IDS:
    experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
    if not experiment:
        print(f"Experiment {experiment_id} not found.")
        continue
    experiment_name = experiment['name']
    baseline_rate = list(CONVERSION_RATES.get(experiment_name, {}).values())[0] if CONVERSION_RATES.get(experiment_name) else 0.1
    sample_size = calculate_sample_size(baseline_rate, MDE, ALPHA, POWER)
    sample_sizes[experiment_id] = sample_size
    print(f"Experiment {experiment_id} ({experiment_name}): {sample_size} users per variant")

# Store assignments
all_assignments = defaultdict(dict)
sample_assignments = defaultdict(list)

# Step 1: Assign all users
for experiment_id in EXPERIMENT_IDS:
    sample_size = sample_sizes[experiment_id]
    experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
    if not experiment:
        continue
    num_variants = len(experiment['variants'])
    total_users = sample_size * num_variants * 2
    for _ in range(total_users):
        email = fake.email()
        response = requests.post(f"{BASE_URL}/assign_user", json={
            "email": email,
            "experiment_id": experiment_id
        })
        if response.ok:
            result = response.json()
            assignment_id = result["assignment_id"]
            user_id = result["user_id"]
            variant = result["variant"]
            all_assignments[email][experiment_id] = (user_id, assignment_id, variant)
            print(f"{email} → Exp {experiment_id}: {variant} (ID={assignment_id})")
        else:
            print(f"Error assigning {email} to Exp {experiment_id}: {response.text}")

# Step 2: Select sample size users
for experiment_id in EXPERIMENT_IDS:
    sample_size = sample_sizes[experiment_id]
    experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
    if not experiment:
        continue
    num_variants = len(experiment['variants'])
    variant_assignments = defaultdict(list)
    for email, exps in all_assignments.items():
        if experiment_id in exps:
            user_id, assignment_id, variant = exps[experiment_id]
            variant_assignments[variant].append((user_id, assignment_id))
    for variant, assignments in variant_assignments.items():
        selected = random.sample(assignments, min(sample_size, len(assignments)))
        for user_id, assignment_id in selected:
            sample_assignments[experiment_id].append((user_id, assignment_id, variant))
            response = requests.post(f"{BASE_URL}/add_sample_size_user", json={
                "user_id": user_id,
                "experiment_id": experiment_id,
                "assignment_id": assignment_id
            })
            if response.ok:
                print(f"Added sample user {user_id} to Exp {experiment_id} ({variant})")
            else:
                print(f"Error adding sample user {user_id} to Exp {experiment_id}: {response.text}")

# Step 3: Record metrics
for experiment_id, assignments in sample_assignments.items():
    experiment = next((e for e in get_active_experiments() if e['experiment_id'] == experiment_id), None)
    if not experiment:
        print(f"Experiment {experiment_id} not found.")
        continue
    experiment_name = experiment['name']
    for user_id, assignment_id, variant in assignments:
        conversion_rate = CONVERSION_RATES.get(experiment_name, {}).get(variant, 0.1)
        value = 1 if random.random() < conversion_rate else 0
        response = requests.post(f"{BASE_URL}/record_metric", json={
            "assignment_id": assignment_id,
            "metric": "conversion",
            "value": value
        })
        if response.ok:
            print(f"Recorded conversion={value} for user {user_id} (Exp {experiment_id}: {variant})")
        else:
            print(f"Error recording for user {user_id} (Exp {experiment_id}): {response.text}")

# Step 4: Analyze
for experiment_id in EXPERIMENT_IDS:
    response = requests.get(f"{BASE_URL}/analyze/{experiment_id}")
    if response.ok:
        print(f"\nAnalysis for Experiment {experiment_id} (Sample Size: {sample_sizes[experiment_id]} per variant):")
        print(response.json())
    else:
        print(f"Failed to analyze Exp {experiment_id}: {response.text}")