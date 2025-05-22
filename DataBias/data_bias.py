import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import binomtest
from scipy.stats import chisquare


#initial table read
tables = pd.read_html("./trimet_stopevents_2022-12-07.html") 
df = pd.concat(tables, ignore_index=True)
print(f"number of rows: {df.shape[0]}")

#datetime
base_date = datetime(2022, 12, 7)
df['tstamp'] = df['arrive_time'].apply(
    lambda x: (base_date + timedelta(seconds=x)).strftime("%Y:%m:%d:%H:%M:%S")
)

#filter dataframes
df = df[['trip_number', 'vehicle_number', 'tstamp', 'location_id', 'ons', 'offs']]

print(f"columns: {df.columns}")
print()

num_vehicles = df['vehicle_number'].nunique()
print(f"Number of vehicles: {num_vehicles}")

num_locations = df['location_id'].nunique()
print(f"Number of unique stop locations: {num_locations}")

min_tstamp = df['tstamp'].min()
max_tstamp = df['tstamp'].max()
print(f"Min tstamp: {min_tstamp}")
print(f"Max tstamp: {max_tstamp}")

num_boarding_events = df[df['ons'] >= 1].shape[0]
print(f"Stop events with at least one boarding: {num_boarding_events}")

total_events = df.shape[0]
boarding_percentage = (num_boarding_events / total_events) * 100
print(f"Percentage of stop events with boarding: {boarding_percentage:.2f}%")

print()
#6913
loc_df = df[df['location_id'] == 6913]

num_stops_at_location = loc_df.shape[0]

unique_vehicles_at_location = loc_df['vehicle_number'].nunique()

boarding_events_at_location = loc_df[loc_df['ons'] >= 1].shape[0]
boarding_pct_location = (boarding_events_at_location / num_stops_at_location) * 100 if num_stops_at_location > 0 else 0

print(f"[Location 6913]")
print(f"Stops made: {num_stops_at_location}")
print(f"Different buses stopped: {unique_vehicles_at_location}")
print(f"Percentage of stops with at least one boarding: {boarding_pct_location:.2f}%")

print()
# Filter rows for vehicle_number == 4062
veh_df = df[df['vehicle_number'] == 4062]

stops_by_vehicle = veh_df.shape[0]

total_boarded = veh_df['ons'].sum()

total_deboarded = veh_df['offs'].sum()

boarding_events_vehicle = veh_df[veh_df['ons'] >= 1].shape[0]
boarding_pct_vehicle = (boarding_events_vehicle / stops_by_vehicle) * 100 if stops_by_vehicle > 0 else 0

print(f"\n[Vehicle 4062]")
print(f"Stops made: {stops_by_vehicle}")
print(f"Total passengers boarded: {total_boarded}")
print(f"Total passengers deboarded: {total_deboarded}")
print(f"Percentage of stops with at least one boarding: {boarding_pct_vehicle:.2f}%")

#Part 4
print()
print("---PART 4---")
total_stops = df.shape[0]
print(f"Total stop events: {total_stops}")

boarding_stops = df[df['ons'] >= 1].shape[0]
print(f"Stop events with at least one boarding: {boarding_stops}")

observed_pct = (boarding_stops / total_stops) * 100
print(f"Percentage of stop events with boardings: {observed_pct:.2f}%")

p_system = (df["ons"] >= 1).mean()

vehicle_stats = df.groupby("vehicle_number").agg(
    total_stops=('vehicle_number', 'count'),
    stops_with_boards=('ons', lambda x: (x >= 1).sum())
).reset_index()

vehicle_stats["p_value"] = vehicle_stats.apply(
    lambda row: binomtest(
        k=row["stops_with_boards"],
        n=row["total_stops"],
        p=p_system,
        alternative="two-sided"
    ).pvalue,
    axis=1
)

alpha = 0.05
biased_vehicles = vehicle_stats[vehicle_stats["p_value"] < alpha]

# Display results
print("\nVehicles with potential bias (p < 0.05):")
print(biased_vehicles[["vehicle_number", "p_value"]])

# Graduate Part - offs

vehicle_offs_stats = df.groupby("vehicle_number").agg(
    total_stops=('vehicle_number', 'count'),
    stops_with_offs=('offs', lambda x: (x >= 1).sum())
).reset_index()

p_system_offs = (df['offs'] >= 1).mean()

vehicle_offs_stats['p_value'] = vehicle_offs_stats.apply(
    lambda row: binomtest(
        k=row['stops_with_offs'],
        n=row['total_stops'],
        p=p_system_offs,
        alternative='two-sided'
    ).pvalue,
    axis=1
)
alpha_offs = 0.05
biased_vehicles_offs = vehicle_offs_stats[vehicle_offs_stats['p_value'] < alpha_offs]

print("---Graduate Part---")
print("\nVehicles with potential bias in offs data (p < 0.05):")
print(biased_vehicles_offs[['vehicle_number', 'p_value']])

#Graduate Part B
total_offs = df['offs'].sum()
total_ons = df['ons'].sum()

print()
print("---Grad Part B---")
print(f"Total number of offs: {total_offs}")
print(f"Total number of ons: {total_ons}")

#Graduate Part C
overall_offs_ons_ratio = total_offs / total_ons if total_ons > 0 else float('nan')

print()
print("---Grad Part C")
print(f"Overall offs: {total_offs}, ons: {total_ons}, offs/ons ratio: {overall_offs_ons_ratio:.4f}")

vehicle_stats = df.groupby('vehicle_number').agg(
    total_offs=('offs', 'sum'),
    total_ons=('ons', 'sum')
).reset_index()

overall_ratio = total_offs / total_ons if total_ons > 0 else float('nan')

def vehicle_chisquare(row):
    observed = [row['total_offs'], row['total_ons']]
    total = sum(observed)
    if total == 0:
        return float('nan')  # no data, skip

    expected_offs = total * (overall_ratio / (1 + overall_ratio))
    expected_ons = total * (1 / (1 + overall_ratio))
    expected = [expected_offs, expected_ons]

    chi2_result = chisquare(f_obs=observed, f_exp=expected)
    return chi2_result.pvalue

vehicle_stats['p_value'] = vehicle_stats.apply(vehicle_chisquare, axis=1)

#Grad Part D

alpha = 0.05
biased_vehicles = vehicle_stats[vehicle_stats['p_value'] < alpha]

print()
print("---Grad PArt D---")
print("Vehicles with significant bias (p < 0.05):")
print(biased_vehicles[['vehicle_number', 'p_value']])





print()