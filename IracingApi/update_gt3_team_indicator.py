# This script updates the indicator being used in the Platinum Endurance Championship for GT3 AM Class
# It is beyond this script to explain all intentions and rules for GT3 AM competition class. 
# In its most basic form:
# On entry, a driver Gold when iRating >= 2750
# On entry, a driver is Silver when iRating <2750
# A GT3 team may not have Gold drivers attending which have an iRating >3750 for more than 3 times
# comment rest of rules here for script/rule clarity


# at minimum, indicator file must contain, 
#
# team_id,races_attended,pro_driven
#
# but may be wise to keep some history as well for reference and proof (nice to have)

import sys
import os
import csv
import pandas as pd 
from tabulate import tabulate
import glob

league_attendees = 'pec_league_attendees.csv' #refence file for valid league attendees
member_data = 'member_data.csv' #up-to-date info on members irating and validation (only needed for first race)
team_indicator_file = 'pec_s3_team_indicator.csv' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
latest_session_file = None #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv

#(generic) functions
def import_csv(path: str) -> dict:
    try:
        file = open(path, "r")
        data = list(csv.reader(file, delimiter=","))
        file.close()
    except:
        data = None
    return data

# get previous indicator
# must either be result of previous race -or if first race- result from iRating analysis
previous_state = import_csv(team_indicator_file)

if previous_state == None:
    df_indicator = pd.DataFrame(columns=['team_id','races_attended','pro_driven'])
else:
    df_indicator = pd.DataFrame.from_dict(previous_state)

# get result from current race
if latest_session_file == None:
    sessionsFilenamesList = glob.glob('session_*.csv')
    latest_session_file = max(sessionsFilenamesList, key=os.path.getmtime)
    answer = None
    while answer != 'y' or answer != 'n':
        answer = input(f"Found {latest_session_file}, use that file and continue? y/n")

if answer == 'n':
    print('Error: no valid session file provided. please re-run and provide valid file!')
    quit() #https://www.scaler.com/topics/exit-in-python/

latest_session = import_csv(latest_session_file)
df_latest_session = pd.DataFrame.from_dict(latest_session)

# add the driver percentages to the teams percentages

#scenario first race
if previous_state == None:
    pass

#scenario other races
if previous_state != None:
    for index, row in df_indicator.iterrows():
        team_id = row['team_id']
        #lookup pro results
        current_team = df_latest_session['team_id'] == row['team_id']
        df_latest_session_team = df_latest_session[current_team]



# show indicator

# save indicator as file


