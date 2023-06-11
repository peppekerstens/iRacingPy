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


def update_team_indicator(df_team_indicator: pd, df_driver_indicator: pd, df_latest_session: pd) -> pd:
    # we only need drivers who attended the last race
    attending_drivers = df_driver_indicator['driven'] == True
    df_attending_drivers = df_driver_indicator[attending_drivers]
    
    # we only need the gold drivers
    gold_drivers = df_attending_drivers['new_classification'] == 'Gold'
    df_gold_drivers = df_attending_drivers[gold_drivers]

    #iterate through all the info an rebuild team_indicator 
    df_new_team_indicator = pd.DataFrame(columns=['team_id','display_name','race_count','percentage'])
    try:
        unique_teams = df_latest_session['team_id'].unique()
    except:
        return df_new_team_indicator #when there are no teams found...
    for team_id in unique_teams:
        #get driver results for this team
        drivers = df_latest_session['team_id'] == team_id
        df_drivers = df_latest_session[drivers]
        team_display_name = df_drivers.iloc[0]['team_display_name']
        percentage = 0
        # iterate through the drivers for this team
        for index, row in df_drivers.iterrows():
            #is it a gold driver? get the driver indicator
            indicator = df_gold_drivers['cust_id'] == row['cust_id']
            df_indicator = df_gold_drivers[indicator]
            if not df_indicator.empty: #if a result, driver is gold
                percentage += row['percentage']
        #check if there are previous team results in the team indicator file
        team = df_team_indicator['team_id'] == team_id
        df_team = df_team_indicator[team]
        if not df_team.empty:
            race_count = df_team.iloc[0]['race_count'] + 1
            running_percentage = round((df_team.iloc[0]['race_count'] * df_team.iloc[0]['percentage'] + percentage) /  race_count,2)   
        if df_team.empty:
            running_percentage = percentage
            race_count = 1            
        df_new_team_indicator.loc[index] = [team_id,team_display_name,race_count,running_percentage]

    #now combine any old values which may not have been updated with the new Dataframe
    df_not_in_common = df_team_indicator.loc[~df_team_indicator['team_id'].isin(df_new_team_indicator['team_id'])]
    frames = [df_not_in_common, df_new_team_indicator]
    result = pd.concat(frames)
    return result


if __name__ == '__main__': #only execute when called as script, skipped when loaded as module
    driver_indicator_file = 'pec_driver_indicator_GT3 Class.csv' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
    team_indicator_file = 'pec_team_indicator.csv' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
    latest_session_file = 'session_60222976.0_Race_GT3 Class.csv' #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv

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
        #while answer != "y":
        answer = input(f"Found {latest_session_file}, use that file and continue? y/n ")
        if answer == 'n':
            print('Error: no valid session file provided. please re-run and provide valid file!')
            quit() #https://www.scaler.com/topics/exit-in-python/

    try:
        df_latest_session = pd.read_csv(latest_session_file)
    except:
        print('Error: session file {latest_session_file} not found! Please re-run and provide valid file!')
        quit()

    print(tabulate(df_latest_session, headers = 'keys', tablefmt = 'psql'))

    # show indicator
    df_new_team_indicator = update_team_indicator(df_team_indicator, df_driver_indicator, df_latest_session)
    print(tabulate(df_new_team_indicator, headers = 'keys', tablefmt = 'psql'))

    # save indicator as file
    df_new_team_indicator.to_csv(team_indicator_file,index=False)