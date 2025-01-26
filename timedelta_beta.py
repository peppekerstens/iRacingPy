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

# Load json file for preprocessing
with open(file1_path, mode="r", encoding="utf-8") as read_file:
    result_data = json.load(read_file)
# Filter race results

df = pd.read_json(file1_path) 

print(df.to_string()) 

