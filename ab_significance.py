import requests
from statsmodels.stats.proportion import proportions_ztest
from collections import defaultdict

BASE_URL = "http://127.0.0.1:5001"
Experiment_ID = 1 

res = requests.get(f"{BASE_URL}/results/{Experiment_ID}")
result = res.json()

print("Experiment Results:", result)

variants = list(result.keys())

variant_A = variants[0]
variant_B = variants[1]

assignments_A = result[variant_A]['assignments']
assignment_B = result[variant_B]['assignments']

avg_A = result[variant_A]['average_metric_value']
avg_B = result[variant_B]['average_metric_value']

conversion_A = round(avg_A * assignments_A)
conversion_B = round(avg_B * assignment_B)

# Running the Z-test for proportions

successes = [conversion_A, conversion_B]
totals = [assignments_A, assignment_B]
z_stat, p_value = proportions_ztest(successes, totals)
print(f"Z-statistic: {z_stat}, P-value: {p_value}")

if p_value < 0.05:
    winner = variant_A if conversion_A > conversion_B else variant_B
   
else:
    print("No significant difference found between variants.")
    winner = None
print(f"Winner: {winner}")
