# import requests
# import random
# from faker import Faker
# from collections import defaultdict
# from scipy.stats import norm
# import math
# import time
# import numpy as np
# import logging

# # # Configure logging
# # logging.basicConfig(level=logging.DEBUG)
# # logger = logging.getLogger(__name__)

# fake = Faker()
# BASE_URL = "http://127.0.0.1:5001"

# # Metric parameters per experiment
# METRIC_PARAMS = {
#     "Button Color Test": {
#         "type": "binary",
#         "variants": {
#             "Red Button": {"conversion_rate": 0.3},
#             "Blue Button": {"conversion_rate": 0.5}
#         }
#     },
#     "Checkout Flow Revenue": {
#         "type": "continuous",
#         "variants": {
#             "Single Page Checkout": {"mean": 50, "std": 10},
#             "Multi Page Checkout": {"mean": 45, "std": 10}
#         }
#     },
#     "Banner Ad Satisfaction": {
#         "type": "categorical",
#         "variants": {
#             "Static Banner": {"weights": [0.5, 0.3, 0.2]},  # Low, Medium, High
#             "Animated Banner": {"weights": [0.3, 0.4, 0.3]}
#         }
#     }
# }

# # Statistical parameters
# ALPHA = 0.05
# POWER = 0.80
# MDE = 0.1  # For binary
# EFFECT_SIZE = 5  # For continuous (difference in means)

# def calculate_sample_size(metric_type, baseline, mde=0.1, effect_size=5, alpha=0.05, power=0.80):
#     z_alpha = norm.ppf(1 - alpha / 2)
#     z_beta = norm.ppf(power)
#     if metric_type == "binary":
#         p1 = baseline
#         p2 = p1 + mde
#         pooled_var = p1 * (1 - p1) + p2 * (1 - p2)
#         n = (z_alpha + z_beta) ** 2 * pooled_var / (mde ** 2)
#     elif metric_type == "continuous":
#         std = 10  # Assumed standard deviation
#         n = (z_alpha + z_beta) ** 2 * 2 * std ** 2 / effect_size ** 2
#     else:  # categorical
#         n = 353  # Fallback to binary sample size
#     return math.ceil(n)

# def get_active_experiments():
#     try:
#         response = requests.get(f"{BASE_URL}/experiments")
#         if response.ok:
#             return response.json()
#         logger.error(f"Error fetching experiments: {response.text}")
#         return []
#     except requests.RequestException as e:
#         logger.error(f"Failed to connect to API: {e}")
#         return []

# def prompt_user_for_experiments(experiments):
#     if not experiments:
#         print("No active experiments available.")
#         return []
#     print("\nAvailable Experiments:")
#     for exp in experiments:
#         print(f"ID: {exp['experiment_id']}, Name: {exp['name']}, Variants: {exp['variants']}, Metric Type: {exp['metric_type']}")
#     selected_ids = []
#     while not selected_ids:
#         try:
#             user_input = input("\nEnter experiment IDs (comma-separated, e.g., 1,2,3) or 'all': ").strip()
#             if user_input.lower() == 'all':
#                 selected_ids = [exp['experiment_id'] for exp in experiments]
#             else:
#                 selected_ids = [int(id.strip()) for id in user_input.split(',')]
#                 valid_ids = {exp['experiment_id'] for exp in experiments}
#                 if not all(id in valid_ids for id in selected_ids):
#                     print("Invalid experiment ID(s).")
#                     selected_ids = []
#         except ValueError:
#             print("Invalid input. Enter numbers separated by commas or 'all'.")
#     return selected_ids

# def retry_request(func, url, max_attempts=3, delay=1, **kwargs):
#     for attempt in range(max_attempts):
#         try:
#             response = func(url, **kwargs)
#             if response.ok:
#                 return response
#             logger.error(f"Attempt {attempt+1} failed for {url}: {response.status_code} {response.text}")
#         except requests.RequestException as e:
#             logger.error(f"Attempt {attempt+1} failed for {url}: {e}")
#         time.sleep(delay)
#     logger.error(f"All {max_attempts} attempts failed for {url}")
#     return None

# # Fetch and prompt
# experiments = get_active_experiments()
# EXPERIMENT_IDS = prompt_user_for_experiments(experiments)
# if not EXPERIMENT_IDS:
#     print("No experiments selected. Exiting.")
#     exit()

# # Calculate sample sizes
# sample_sizes = {}
# for experiment_id in EXPERIMENT_IDS:
#     experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
#     if not experiment:
#         print(f"Experiment {experiment_id} not found.")
#         continue
#     experiment_name = experiment['name']
#     metric_type = experiment['metric_type']
#     params = METRIC_PARAMS.get(experiment_name, {})
#     baseline = list(params.get('variants', {}).values())[0].get('conversion_rate', 0.1) if metric_type == 'binary' else 50
#     sample_size = calculate_sample_size(metric_type, baseline, MDE, EFFECT_SIZE, ALPHA, POWER)
#     sample_sizes[experiment_id] = sample_size
#     print(f"Experiment {experiment_id} ({experiment_name}): {sample_size} users per variant")

# # Store assignments
# all_assignments = defaultdict(dict)
# sample_assignments = defaultdict(list)

# # Step 1: Assign all users
# for experiment_id in EXPERIMENT_IDS:
#     sample_size = sample_sizes[experiment_id]
#     experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
#     if not experiment:
#         continue
#     num_variants = len(experiment['variants'])
#     total_users = sample_size * num_variants * 2
#     for _ in range(total_users):
#         email = fake.email()
#         response = retry_request(requests.post, f"{BASE_URL}/assign_user", json={
#             "email": email,
#             "experiment_id": experiment_id
#         })
#         if response:
#             result = response.json()
#             assignment_id = result["assignment_id"]
#             user_id = result["user_id"]
#             variant = result["variant"]
#             all_assignments[email][experiment_id] = (user_id, assignment_id, variant)
#             print(f"{email} → Exp {experiment_id}: {variant} (ID={assignment_id})")
#         else:
#             print(f"Failed to assign {email} to Exp {experiment_id} after retries.")

# # Step 2: Select sample size users
# for experiment_id in EXPERIMENT_IDS:
#     sample_size = sample_sizes[experiment_id]
#     experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
#     if not experiment:
#         continue
#     num_variants = len(experiment['variants'])
#     variant_assignments = defaultdict(list)
#     for email, exps in all_assignments.items():
#         if experiment_id in exps:
#             user_id, assignment_id, variant = exps[experiment_id]
#             variant_assignments[variant].append((user_id, assignment_id))
#     for variant, assignments in variant_assignments.items():
#         selected = random.sample(assignments, min(sample_size, len(assignments)))
#         for user_id, assignment_id in selected:
#             sample_assignments[experiment_id].append((user_id, assignment_id, variant))
#             response = retry_request(requests.post, f"{BASE_URL}/add_sample_size_user", json={
#                 "user_id": user_id,
#                 "experiment_id": experiment_id,
#                 "assignment_id": assignment_id
#             })
#             if response:
#                 print(f"Added sample user {user_id} to Exp {experiment_id} ({variant})")
#             else:
#                 print(f"Failed to add sample user {user_id} to Exp {experiment_id} after retries.")

# # Step 3: Record metrics
# for experiment_id, assignments in sample_assignments.items():
#     experiment = next((e for e in get_active_experiments() if e['experiment_id'] == experiment_id), None)
#     if not experiment:
#         print(f"Experiment {experiment_id} not found.")
#         continue
#     experiment_name = experiment['name']
#     metric_type = experiment['metric_type']
#     params = METRIC_PARAMS.get(experiment_name, {})
#     for user_id, assignment_id, variant in assignments:
#         if metric_type == "binary":
#             conversion_rate = params['variants'][variant]['conversion_rate']
#             value = 1 if random.random() < conversion_rate else 0
#         elif metric_type == "continuous":
#             mean = params['variants'][variant]['mean']
#             std = params['variants'][variant]['std']
#             value = max(0, np.random.normal(mean, std))  # Non-negative revenue
#         else:  # categorical
#             weights = params['variants'][variant]['weights']
#             value = random.choices([1, 2, 3], weights=weights)[0]  # 1=Low, 2=Medium, 3=High
#         response = retry_request(requests.post, f"{BASE_URL}/record_metric", json={
#             "assignment_id": assignment_id,
#             "metric": experiment_name.lower().replace(" ", "_"),
#             "value": float(value),
#             "metric_type": metric_type
#         })
#         if response:
#             print(f"Recorded {metric_type} value={value} for user {user_id} (Exp {experiment_id}: {variant})")
#         else:
#             print(f"Failed to record for user {user_id} (Exp {experiment_id}) after retries.")

# # Step 4: Analyze
# for experiment_id in EXPERIMENT_IDS:
#     response = retry_request(requests.get, f"{BASE_URL}/analyze/{experiment_id}")
#     if response:
#         print(f"\nAnalysis for Experiment {experiment_id} (Sample Size: {sample_sizes[experiment_id]} per variant):")
#         print(response.json())
#     else:
#         print(f"Failed to analyze Exp {experiment_id} after retries.")


import requests
import random
from faker import Faker
from collections import defaultdict
from scipy.stats import norm
import math
import time
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

fake = Faker()
BASE_URL = "http://127.0.0.1:5001"

# Metric parameters per experiment
METRIC_PARAMS = {
    "Button Color Test": {
        "type": "binary",
        "variants": {
            "Red Button": {"conversion_rate": 0.3},
            "Blue Button": {"conversion_rate": 0.5}
        }
    },
    "Checkout Flow Revenue": {
        "type": "continuous",
        "variants": {
            "Single Page Checkout": {"mean": 50, "std": 10},
            "Multi Page Checkout": {"mean": 45, "std": 10}
        }
    },
    "Banner Ad Satisfaction": {
        "type": "categorical",
        "variants": {
            # Low, Medium, High weights
            "Static Banner": {"weights": [0.5, 0.3, 0.2]},
            "Animated Banner": {"weights": [0.3, 0.4, 0.3]}
        },
        # For categorical, we'll calculate sample size based on a 'success' category.
        # Let's consider 'High' satisfaction as success.
        # Baseline 'High' rate for Static Banner: 0.2
        "baseline_success_rate": 0.2,
        # Desired MDE for 'High' satisfaction rate (e.g., detect a 0.05 absolute increase)
        "mde_success_rate": 0.05
    }
}

# Statistical parameters (These will be used if not overridden by specific metric params)
ALPHA = 0.05
POWER = 0.80
# MDE for binary (if not specified per experiment)
DEFAULT_BINARY_MDE = 0.05 # Changed from 0.1 for more realistic sample sizes
# EFFECT_SIZE for continuous (difference in means, if not specified per experiment)
DEFAULT_CONTINUOUS_EFFECT_SIZE = 5

def calculate_sample_size(metric_type, experiment_name, alpha=ALPHA, power=POWER):
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)

    params = METRIC_PARAMS.get(experiment_name, {})

    if metric_type == "binary":
        baseline = list(params.get('variants', {}).values())[0].get('conversion_rate', 0.1)
        mde = DEFAULT_BINARY_MDE # Use default or retrieve from params if added
        p1 = baseline
        p2 = p1 + mde
        # Ensure p2 is within valid probability range
        p2 = min(max(0, p2), 1)

        if p1 == 0 and p2 == 0: # Avoid division by zero if no conversion expected
            logger.warning(f"Binary baseline and MDE result in p1=0, p2=0 for {experiment_name}. Returning a default large sample size.")
            return 10000 # Return a large default to avoid issues

        pooled_var = p1 * (1 - p1) + p2 * (1 - p2)
        if mde == 0: # Avoid division by zero
            logger.warning(f"MDE is zero for binary metric {experiment_name}. Returning a default large sample size.")
            return 10000
        n = (z_alpha + z_beta) ** 2 * pooled_var / (mde ** 2)
        logger.info(f"Binary sample size for {experiment_name}: Baseline={baseline}, MDE={mde}, Calculated N={math.ceil(n)}")
        return math.ceil(n)

    elif metric_type == "continuous":
        # Assumed standard deviation; ideally, this would come from historical data or params
        std = list(params.get('variants', {}).values())[0].get('std', 10)
        effect_size = DEFAULT_CONTINUOUS_EFFECT_SIZE # Use default or retrieve from params if added
        if effect_size == 0: # Avoid division by zero
            logger.warning(f"Effect size is zero for continuous metric {experiment_name}. Returning a default large sample size.")
            return 10000
        n = (z_alpha + z_beta) ** 2 * 2 * std ** 2 / effect_size ** 2
        logger.info(f"Continuous sample size for {experiment_name}: Std={std}, Effect Size={effect_size}, Calculated N={math.ceil(n)}")
        return math.ceil(n)

    elif metric_type == "categorical":
        # Treating 'High' satisfaction as a binary 'success' rate
        baseline_success = params.get('baseline_success_rate', 0.2) # Default to 0.2 if not found
        mde_success = params.get('mde_success_rate', 0.05) # Default to 0.05 if not found

        p1 = baseline_success
        p2 = p1 + mde_success
        # Ensure p2 is within valid probability range
        p2 = min(max(0, p2), 1)

        if p1 == 0 and p2 == 0: # Avoid division by zero if no success expected
            logger.warning(f"Categorical baseline_success_rate and MDE result in p1=0, p2=0 for {experiment_name}. Returning a default large sample size.")
            return 10000

        pooled_var = p1 * (1 - p1) + p2 * (1 - p2)
        if mde_success == 0: # Avoid division by zero
            logger.warning(f"MDE for success rate is zero for categorical metric {experiment_name}. Returning a default large sample size.")
            return 10000
        n = (z_alpha + z_beta) ** 2 * pooled_var / (mde_success ** 2)
        logger.info(f"Categorical (binary success) sample size for {experiment_name}: Baseline Success={baseline_success}, MDE Success={mde_success}, Calculated N={math.ceil(n)}")
        return math.ceil(n)
    else:
        logger.warning(f"Unknown metric type '{metric_type}' for {experiment_name}. Falling back to a default sample size of 500.")
        return 500 # Fallback for unhandled types


def get_active_experiments():
    try:
        response = requests.get(f"{BASE_URL}/experiments")
        if response.ok:
            return response.json()
        logger.error(f"Error fetching experiments: {response.text}")
        return []
    except requests.RequestException as e:
        logger.error(f"Failed to connect to API: {e}")
        return []

def prompt_user_for_experiments(experiments):
    if not experiments:
        print("No active experiments available.")
        return []
    print("\nAvailable Experiments:")
    for exp in experiments:
        print(f"ID: {exp['experiment_id']}, Name: {exp['name']}, Variants: {exp['variants']}, Metric Type: {exp['metric_type']}")
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

def retry_request(func, url, max_attempts=3, delay=1, **kwargs):
    for attempt in range(max_attempts):
        try:
            response = func(url, **kwargs)
            if response.ok:
                return response
            logger.error(f"Attempt {attempt+1} failed for {url}: {response.status_code} {response.text}")
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt+1} failed for {url}: {e}")
        time.sleep(delay)
    logger.error(f"All {max_attempts} attempts failed for {url}")
    return None

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
        print(f"Experiment {experiment_id} not found. Skipping.")
        continue
    experiment_name = experiment['name']
    metric_type = experiment['metric_type']
    sample_size = calculate_sample_size(metric_type, experiment_name, ALPHA, POWER)
    sample_sizes[experiment_id] = sample_size
    print(f"Calculated Sample Size for Experiment {experiment_id} ({experiment_name}): {sample_size} users per variant")

# Store assignments
all_assignments = defaultdict(dict) # Stores assignments for all users
sample_assignments = defaultdict(list) # Stores assignments for selected sample size users

# Step 1: Assign all users
# To ensure we have enough users for sample selection, we assign (sample_size * num_variants * some_buffer) users
# A buffer of 2-3x the desired sample size per variant is often good to ensure enough diversity and cover potential drop-offs.
ASSIGNMENT_BUFFER_MULTIPLIER = 2.5 # Assign 2.5 times the calculated sample size per variant
print("\n--- Step 1: Assigning users to experiments ---")
for experiment_id in EXPERIMENT_IDS:
    sample_size = sample_sizes[experiment_id]
    experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
    if not experiment:
        continue
    num_variants = len(experiment['variants'])
    # Total users to assign for this experiment to ensure enough for sample selection
    total_users_to_assign = math.ceil(sample_size * num_variants * ASSIGNMENT_BUFFER_MULTIPLIER)
    logger.info(f"Attempting to assign {total_users_to_assign} users for Experiment {experiment_id} to ensure sample size.")

    assigned_count = 0
    while assigned_count < total_users_to_assign:
        email = fake.email()
        if email in all_assignments and experiment_id in all_assignments[email]:
            continue # Skip if already assigned in this experiment

        response = retry_request(requests.post, f"{BASE_URL}/assign_user", json={
            "email": email,
            "experiment_id": experiment_id
        })
        if response:
            result = response.json()
            assignment_id = result["assignment_id"]
            user_id = result["user_id"]
            variant = result["variant"]
            all_assignments[email][experiment_id] = (user_id, assignment_id, variant)
            # print(f"Assigned {email} → Exp {experiment_id}: {variant} (ID={assignment_id})") # Too verbose
            assigned_count += 1
        else:
            logger.warning(f"Failed to assign {email} to Exp {experiment_id} after retries. Continuing to next user.")
            # Break if critical failure to avoid infinite loop
            if assigned_count < sample_size * num_variants: # If we can't even get minimum for one round, something is wrong
                logger.error(f"Critical failure to assign sufficient users for experiment {experiment_id}. Stopping assignments for this experiment.")
                break
    logger.info(f"Completed initial assignment phase for Experiment {experiment_id}. Assigned {assigned_count} users.")


# Step 2: Select sample size users for metric recording
print("\n--- Step 2: Selecting users for sample size and adding to AB test system ---")
for experiment_id in EXPERIMENT_IDS:
    sample_size = sample_sizes[experiment_id]
    experiment = next((e for e in experiments if e['experiment_id'] == experiment_id), None)
    if not experiment:
        continue
    num_variants = len(experiment['variants'])

    # Group all initial assignments by variant
    variant_pool = defaultdict(list)
    for email, exps in all_assignments.items():
        if experiment_id in exps:
            user_id, assignment_id, variant = exps[experiment_id]
            variant_pool[variant].append((user_id, assignment_id))

    for variant_name in experiment['variants']:
        assignments_for_variant = variant_pool[variant_name]
        # Select 'sample_size' users for this variant from the pool
        selected = random.sample(assignments_for_variant, min(sample_size, len(assignments_for_variant)))

        if len(selected) < sample_size:
            logger.warning(f"Could not select {sample_size} users for variant '{variant_name}' in Exp {experiment_id}. Only found {len(selected)} users in the pool.")

        for user_id, assignment_id in selected:
            sample_assignments[experiment_id].append((user_id, assignment_id, variant_name))
            response = retry_request(requests.post, f"{BASE_URL}/add_sample_size_user", json={
                "user_id": user_id,
                "experiment_id": experiment_id,
                "assignment_id": assignment_id
            })
            if response:
                pass # print(f"Added sample user {user_id} to Exp {experiment_id} ({variant_name})") # Too verbose
            else:
                logger.warning(f"Failed to add sample user {user_id} to Exp {experiment_id} after retries. This user won't be part of the final sample.")
    logger.info(f"Completed sample selection for Experiment {experiment_id}. Total sample users selected: {len(sample_assignments[experiment_id])}")

# Step 3: Record metrics for selected sample size users
print("\n--- Step 3: Recording metrics for selected sample users ---")
for experiment_id, assignments in sample_assignments.items():
    experiment = next((e for e in get_active_experiments() if e['experiment_id'] == experiment_id), None)
    if not experiment:
        logger.error(f"Experiment {experiment_id} not found during metric recording. Skipping.")
        continue
    experiment_name = experiment['name']
    metric_type = experiment['metric_type']
    params = METRIC_PARAMS.get(experiment_name, {})

    for user_id, assignment_id, variant in assignments:
        value = None
        if metric_type == "binary":
            conversion_rate = params['variants'][variant]['conversion_rate']
            value = 1 if random.random() < conversion_rate else 0
        elif metric_type == "continuous":
            mean = params['variants'][variant]['mean']
            std = params['variants'][variant]['std']
            value = max(0, np.random.normal(mean, std))  # Non-negative revenue
        elif metric_type == "categorical":
            weights = params['variants'][variant]['weights']
            # Values for categorical often map to internal IDs (e.g., 1, 2, 3)
            # Make sure these match what your backend expects for 'Low', 'Medium', 'High'
            value = random.choices([1, 2, 3], weights=weights)[0]  # 1=Low, 2=Medium, 3=High
        else:
            logger.warning(f"Unknown metric type '{metric_type}' for {experiment_name}. Cannot record metric for user {user_id}.")
            continue

        response = retry_request(requests.post, f"{BASE_URL}/record_metric", json={
            "assignment_id": assignment_id,
            "metric": experiment_name.lower().replace(" ", "_"), # Ensure metric name matches backend
            "value": float(value),
            "metric_type": metric_type
        })
        if response:
            pass # print(f"Recorded {metric_type} value={value} for user {user_id} (Exp {experiment_id}: {variant})") # Too verbose
        else:
            logger.warning(f"Failed to record metric for user {user_id} (Exp {experiment_id}: {variant}) after retries.")
    logger.info(f"Completed metric recording for Experiment {experiment_id}.")


# Step 4: Analyze
print("\n--- Step 4: Analyzing experiments ---")
for experiment_id in EXPERIMENT_IDS:
    response = retry_request(requests.get, f"{BASE_URL}/analyze/{experiment_id}")
    if response:
        print(f"\nAnalysis for Experiment {experiment_id} (Sample Size: {sample_sizes[experiment_id]} per variant):")
        analysis_data = response.json()
        if isinstance(analysis_data, dict) and 'message' in analysis_data and 'error' in analysis_data['message'].lower():
            print(f"Analysis Error: {analysis_data['message']}")
        else:
            print(analysis_data)
    else:
        logger.error(f"Failed to analyze Exp {experiment_id} after retries.")