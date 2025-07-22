import pandas as pd
import random

# Sample size logic by area & age bucket
sample_size_mapping = {
    "North": {"0-5": 3, "6-10": 2, "11-15": 1},
    "South": {"0-5": 2, "6-10": 3, "11-15": 2}
}

# Random garden data for demo
def load_garden_data():
    data = pd.DataFrame({
        "garden_id": range(1, 21),
        "area": [random.choice(["North", "South"]) for _ in range(20)],
        "age_bucket": [random.choice(["0-5", "6-10", "11-15"]) for _ in range(20)],
        "garden_area_ha": [round(random.uniform(1.0, 5.0), 2) for _ in range(20)]
    })
    return data

# Get filtered gardens
def get_gardens(area, age_bucket, df):
    return df[(df["area"] == area) & (df["age_bucket"] == age_bucket)]

# Determine how many gardens to sample
def get_sample_size(area, age_bucket):
    return sample_size_mapping.get(area, {}).get(age_bucket, 0)

# Estimate number of trees (example: 10 trees per hectare)
def get_tree_count(garden_area):
    return int(round(garden_area * 10))
