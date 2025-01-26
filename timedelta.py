import json
import pandas as pd
import numpy as np
import os

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Define file names (files should be in the same directory as this script)
file1_name = 'iracing-result-72608683.json'

# Construct the full paths to the files
file1_path = os.path.join(script_directory, file1_name)

# Skip metadata rows and load the data https://www.w3schools.com/python/pandas/pandas_json.asp
df = pd.read_json(file1_path) 

print(df.to_string()) 
#basic op json https://realpython.com/python-json/
#with open("hello_frieda.json", mode="r", encoding="utf-8") as read_file:
#    frie_data = json.load(read_file)

# Filter out rows without an 'Average Lap Time' (crashes/disconnections)
df_filtered = df_combined[df_combined['Average Lap Time'].notna()]

# Keep only one entry per team, using 'Team ID' to filter duplicates
df_unique_teams = df_filtered.drop_duplicates(subset=['Team ID'])

# Define a function to convert 'mm:ss.sss' to total seconds
def convert_to_seconds(lap_time_str):
    try:
        minutes, seconds = lap_time_str.split(':')
        total_seconds = int(minutes) * 60 + float(seconds)
        return total_seconds
    except:
        return np.nan  # Handle invalid format

# Apply the conversion function to the 'Average Lap Time' column
df_unique_teams['Average Lap Time (s)'] = df_unique_teams['Average Lap Time'].apply(convert_to_seconds)

# Calculate total time driven in seconds (Laps Completed * Average Lap Time in seconds)
df_unique_teams['Total Time Driven (s)'] = df_unique_teams['Laps Comp'] * df_unique_teams['Average Lap Time (s)']

# Convert total time driven back to hh:mm:ss format
df_unique_teams['Total Time Driven'] = pd.to_datetime(df_unique_teams['Total Time Driven (s)'], unit='s').dt.strftime("%H:%M:%S")

# Calculate the maximum number of laps completed per car class
class_max_laps = df_unique_teams.groupby('Car Class')['Laps Comp'].transform('max')

# Add a column with the theoretical maximum total time driven for each class
# It assumes that the fastest car in each class completed the maximum laps
df_unique_teams['Max Total Time (s)'] = class_max_laps * df_unique_teams.groupby('Car Class')['Average Lap Time (s)'].transform('mean')

# Sort by Laps Completed, then by Average Lap Time, and then by Max Total Time (for theoretical sorting)
df_unique_teams_sorted = df_unique_teams.sort_values(by=['Laps Comp', 'Average Lap Time (s)', 'Max Total Time (s)'], ascending=[False, True, False])

# Re-adjust the positions after sorting
df_unique_teams_sorted['Fin Pos'] = range(1, len(df_unique_teams_sorted) + 1)

# Save the results to a new CSV file in the same directory
output_file_name = 'filtered_sorted_eventresult_ranked_by_laps.csv'
output_file_path = os.path.join(script_directory, output_file_name)

df_unique_teams_sorted.to_csv(output_file_path, index=False)

print(f"Results with total time driven and ranked by laps saved to {output_file_path}")
