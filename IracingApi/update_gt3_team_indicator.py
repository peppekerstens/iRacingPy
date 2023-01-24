# This script updates the indicator being used in the Platinum Endurance Championship for GT3 AM Class
# It is beyond this script to explain all intentions and rules for GT3 AM competition class. 
# In its most basic form:
# On entry, a driver Gold when iRating >= 2750
# On entry, a driver is Silver when iRating <2750
# A GT3 team may not have Gold drivers attending which have an iRating >3750 for more than 3 times

# Silver drivers Drivers competing GT3 AM class drivers may not have an Irating beyond 3750
# This is processed, producing a table presenting 
#+----+-----------+-----------+---------------------------+-----------+-----------------+---------+-----------+--------------+
#|    |   team_id |   cust_id | display_name              |   avg_lap |   laps_complete |   speed |      time |   percentage |
#|----+-----------+-----------+---------------------------+-----------+-----------------+---------+-----------+--------------|
# in order of result (winning team first and so on)
#
#+---------------+--------------+
#|  column name  |  unit        |
#|---------------+--------------+
#| avg_lap       | seconds      |
#| laps_complete | int          |
#| speed         | km           |
#| time          | seconds      |
#| percentage    | percentage   |
#|---------------+--------------+
#
# Current limitations
# - Nu named arguments
# - Assumes only 1 race
# - Assumes team race 
#
# Links
# https://datatofish.com/compare-values-dataframes/



import sys
import os
import csv
import pandas as pd 
from tabulate import tabulate
import glob

team_indicator_file = 'pec_s3_team_indicator.csv'

# get previous indicator
# must either be result of previous race -or if first race- result from iRating analysis
def import_csv(path: str) -> dict:
    try:
        file = open(path, "r")
        data = list(csv.reader(file, delimiter=","))
        file.close()
    except:
        data = None
    return data

previous_state = import_csv(team_indicator_file)

if previous_state == None:
    df_indicator = pd.DataFrame(columns=['team_id','races_attended','am_driven'])
else:
    df_indicator = pd.DataFrame.from_dict(previous_state)

# get result from current race
latest_session = None
if latest_session == None:
    sessionsFilenamesList = glob.glob('session_*.csv')
    latest_session = max(sessionsFilenamesList, key=os.path.getmtime)
    answer = None
    while answer != 'y' or answer != 'n':
        answer = input(f"Found {latest_session}, use that file and continue? y/n")


# add the driver percentages to the teams percentages

# show indicator

# save indicator as file


#at minimum, indicator file must contain 
#team_id,races_attended,avg_percentage_am_driven