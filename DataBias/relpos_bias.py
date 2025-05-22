import pandas as pd
import numpy as np
from scipy.stats import ttest_1samp
import numpy as np

#Part A
relpos_df = pd.read_csv("trimet_relpos_2022-12-07.csv")
relpos_df = relpos_df.dropna(subset=["RELPOS"])

relpos_array = relpos_df["RELPOS"].to_numpy()

print(f"Total RELPOS values: {len(relpos_array)}")
print(f"Sample values: {relpos_array[:5]}")

#Part B
vehicle_results = []

for vehicle_id, group in relpos_df.groupby("VEHICLE_NUMBER"):
    vehicle_relpos = group["RELPOS"].to_numpy()
    
    if len(vehicle_relpos) < 2:
        continue

    t_stat, p_val = ttest_1samp(vehicle_relpos, popmean=0.0)
    
    vehicle_results.append({
        "vehicle_number": vehicle_id,
        "n_values": len(vehicle_relpos),
        "mean_relpos": np.mean(vehicle_relpos),
        "p_value": p_val
    })

relpos_bias_df = pd.DataFrame(vehicle_results)

alpha = 0.05
biased_vehicles_relpos = relpos_bias_df[relpos_bias_df["p_value"] < alpha]

print("\nVehicles with statistically significant RELPOS bias (p < 0.05):")
print(biased_vehicles_relpos.sort_values("p_value"))

#Part C
very_biased_vehicles = relpos_bias_df[relpos_bias_df["p_value"] < 0.005]

print("\nVehicles with strong RELPOS bias (p < 0.005):")
print(very_biased_vehicles[["vehicle_number", "p_value"]].sort_values("p_value"))