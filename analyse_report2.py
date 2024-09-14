#https://www.datacamp.com/tutorial/fuzzy-string-python

import pandas as pd
from thefuzz import fuzz
from thefuzz import process


# Rename the misspelled columns
exported_data["country"] = exported_data["country"].apply(
  lambda x: process.extractOne(x, existing_data["country"], scorer=fuzz.partial_ratio)[0]
)
​
# Attempt to join the two dataframe
data = pd.merge(existing_data, exported_data, on="country", how="left")
print(data.head())

# Check the similarity score
name = "Kurtis Pykes"
full_name = "Kurtis K D Pykes"

print(f"Similarity score: {fuzz.partial_ratio(name, full_name)}")

# Load data from source1
source1_url = "https://docs.google.com/spreadsheets/d/11rHcrDMEom-pqpMqTj0hLMIhU1nN9ZQS2VyUv2x0k84/export?format=csv"
df1 = pd.read_csv(source1_url)

# Load data from source2
source2_url = "https://docs.google.com/spreadsheets/d/18gNaDQS-HLvxTPXJfSZ0x-Wj57w3lKlA8nhWoQmcnKQ/export?format=csv"
df2 = pd.read_csv(source2_url)

# Extract team names from source1 and source2
team_names_source1 = df1['Team name'].str.lower().unique()
team_names_source2 = df2['What is your team name (please include the race number)'].str.lower().unique()

# Check if names in source2 look like names used in source1
similar_names = []
for name in team_names_source2:
    if any(name in source1_name for source1_name in team_names_source1):
        similar_names.append(name)

# Print similar names
print("Names in source2 that look like names used in source1:")
for name in similar_names:
    print(name)
