import pandas as pd

# Load the Google Sheets document
url = "https://docs.google.com/spreadsheets/d/18gNaDQS-HLvxTPXJfSZ0x-Wj57w3lKlA8nhWoQmcnKQ/export?format=csv"
df = pd.read_csv(url)

# Extract unique names from the specified columns
team_names = df['What is your team name (please include the race number)'].unique()
involving_team_names = df['Who is the involving team (name + race number)'].unique()

# Print the unique names
print("Unique Team Names:")
for name in team_names:
    print(name)

print("\nUnique Involving Team Names:")
for name in involving_team_names:
    print(name)