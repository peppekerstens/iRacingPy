# This script updates the team indicator being used in the Platinum Endurance Championship for GT3 AM Class
#
# It is beyond this script to explain all intentions and rules for GT3 AM competition class. 
# This script is the last step in a chain of calculations. It updates the team_indicator_file, 
# based the outcome of the script which update the indicator of each separate driver
#
# Global order of actions 
# 1. Read the driver_indicator_file, if exists, if not; stop
# 2. Read the team_indicator_file, if exists
# 3. Get the latest_session_file 
# 4. Iterate through the driver_indicator_file.
# 5. If a team has one or more Gold drivers, sum their percentage
# 6. Recalculate the running percentage for that team
# 7. Save the updated result in team_indicator_file


# at minimum, indicator file must contain, 
#
# 'team_id','display_name','race_count','percentage'
#
# but may be wise to keep some history as well for reference and proof (nice to have)

import sys
import os
import pandas as pd 
from tabulate import tabulate
import glob

driver_indicator_file = 'pec_s3_driver_indicator.csv' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
team_indicator_file = 'pec_s3_team_indicator.csv' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
latest_session_file = None #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv

def generate_team_indicator(df_member_data: pd, cust_id: int) -> pd:
    df_indicator = pd.DataFrame(columns=['cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified'])
    driver = df_member_data['cust_id'] == cust_id
    df_driver = df_member_data[driver]
    #print(tabulate(df_driver, headers = 'keys', tablefmt = 'psql'))
    if not df_driver.empty:
        classification = df_driver.iloc[0]['driver_classification']
        #print(df_row['driver_classification'])
        if classification == 'Not allowed':
            #print(df_row['driver_classification'])
            classification = 'Gold'
        df_indicator.loc[0] = [df_row['cust_id'] ,df_row['display_name'],0,classification,0,0,0,classification,False,False]
    return df_indicator

def get_df_indicator_team(df_indicator: pd, df_member_data: pd, cust_id: int) -> pd:
    if df_indicator.empty:
        df_indicator_driver = generate_member_data_driver_indicator(df_member_data,cust_id)
    else:
        driver_indicator = df_indicator['cust_id'] == cust_id
        df_indicator_driver = df_indicator[driver_indicator]
    return df_indicator_driver

# Read the driver_indicator_file, if exists, if not; stop
try:
    df_driver_indicator = pd.read_csv(driver_indicator_file)
except:
    print(f"ERROR: could not find file {driver_indicator_file}. Quitting...")
    quit()

print(tabulate(df_driver_indicator, headers = 'keys', tablefmt = 'psql'))

# Read the team_indicator_file, if exists
try:
    df_team_indicator = pd.read_csv(team_indicator_file)
except:
    #scenario first race
    print(f"WARNING: could not find file {team_indicator_file}. Is this the first race?")
    df_team_indicator = pd.DataFrame(columns=['team_id','display_name','race_count','percentage'])

print(tabulate(df_team_indicator, headers = 'keys', tablefmt = 'psql'))

# Get the latest_session_file - result from current race
if latest_session_file == None:
    sessionsFilenamesList = glob.glob('session_*.csv')
    latest_session_file = max(sessionsFilenamesList, key=os.path.getmtime)
    answer = None
    #while answer != "y" or answer != "n":
    while answer != "y":
        answer = input(f"Found {latest_session_file}, use that file and continue? y/n ")
        print (answer)

if answer == 'n':
    print('Error: no valid session file provided. please re-run and provide valid file!')
    quit() #https://www.scaler.com/topics/exit-in-python/

try:
    df_latest_session = pd.read_csv(latest_session_file)
except:
    print('Error: session file {latest_session_file} not found! Please re-run and provide valid file!')
    quit()

print(tabulate(df_latest_session, headers = 'keys', tablefmt = 'psql'))

# we only need the gold drivers
gold_drivers = df_driver_indicator['new_classification'] == 'Gold'
df_gold_drivers = df_driver_indicator[gold_drivers]

#we want the drivers, grouped by team
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html
df_latest_session_grouped_team = df_latest_session.groupby('team_id', group_keys=True).apply(lambda x: x) 

# rebuild team_indicator by iterating through the driver_indicator_file, 

df_new_team_indicator = pd.DataFrame(columns=['team_id','display_name','race_count','percentage'])






for index, row in df_driver_indicator.iterrows():
    team_id = row['team_id']
    team = df_team_indicator['cust_id'] == team_id
    df_team = df_team_indicator[team]
     

    df_team = get_team(df_team_indicator,team_id)
    if not df_team.empty:
        #print(tabulate(df_indicator_driver, headers = 'keys', tablefmt = 'psql'))
        old_classification = df_indicator_driver.iloc[0]['old_classification']
        cust_id = df_row['cust_id'] 
        display_name = df_row['display_name']
        percentage = df_row['percentage']
        new_classification = df_indicator_driver.iloc[0]['new_classification']
        race_count = df_indicator_driver.iloc[0]['race_count'] + 1 # https://stackoverflow.com/questions/16729574/how-can-i-get-a-value-from-a-cell-of-a-dataframe
        total_time = round(df_indicator_driver.iloc[0]['total_time'] + df_row['time'],2)
        avg_speed = round((df_indicator_driver.iloc[0]['total_time'] * df_indicator_driver.iloc[0]['avg_speed'] + df_row['time'] * df_row['speed']) / total_time,2)
        df_pec_driver_info.loc[index] = [cust_id,display_name,race_count,old_classification,total_time,avg_speed,percentage,new_classification]
    if df_indicator_driver.empty:    
        print(f"WARNING: could not find indicator information for driver {df_row['display_name']} ({df_row['cust_id']}) skipping!")



    #lookup pro results
    current_team = df_latest_session['team_id'] == row['team_id']
    df_latest_session_team = df_latest_session[current_team]



# show indicator

# save indicator as file


