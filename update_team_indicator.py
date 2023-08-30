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

import argparse
import sys
import os
import pandas as pd 
from tabulate import tabulate
import glob

team_indicator_columns = ['team_id','team_display_name','race_count','percentage','gold_league_drive_time','gold_league_percentage','total_league_time']

def update_team_indicator(df_team_indicator: pd, df_driver_indicator: pd) -> pd:
    # we only need drivers who attended the last race
    attending_drivers = df_driver_indicator['driven'] == True
    df_attending_drivers = df_driver_indicator[attending_drivers]
    
    # we only need the gold drivers
    #gold_drivers = df_attending_drivers['new_classification'] == 'Gold'
    #df_gold_drivers = df_attending_drivers[gold_drivers]

    #iterate through all the info an rebuild team_indicator 
    df_new_team_indicator = pd.DataFrame(columns=team_indicator_columns)
    unique_teams = df_attending_drivers['team_id'].unique()
    print(f"found {len(unique_teams)} unique_teams")
    index = 0
    for team_id in unique_teams:
        #get driver results for this team
        drivers = df_attending_drivers['team_id'] == team_id
        df_drivers = df_attending_drivers[drivers]
        
        team_display_name = df_drivers.iloc[0]['team_display_name']
        print(f"processing team {team_display_name} with {len(df_drivers)} drivers")

        # check if there are previous records in the indicator file for same team
        indicator = df_team_indicator['team_id'] == team_id
        df_indicator = df_team_indicator[indicator]

        if df_indicator.empty:
            race_count = 1
            gold_league_drive_time = 0
            total_league_time = 0
        if not df_indicator.empty:
            # pre-populate values with previous records
            race_count = df_indicator.iloc[0]['race_count'] + 1
            gold_league_drive_time = df_indicator.iloc[0]['gold_league_drive_time']
            total_league_time = df_indicator.iloc[0]['total_league_time']

        percentage = 0
        gold_league_percentage = 0

        # we only need the gold drivers
        gold_drivers = df_drivers['new_classification'] == 'Gold'
        df_gold_drivers = df_drivers[gold_drivers]

        if not df_gold_drivers.empty:
            total_league_time += df_drivers.iloc[0]['total_session_time']
        # iterate through the drivers for this team
        for index2, row in df_gold_drivers.iterrows():
            gold_league_drive_time += row['gold_total_drive_time']
            #is it a gold driver? get the driver indicator
            #indicator = df_gold_drivers['cust_id'] == row['cust_id']
            #df_indicator = df_gold_drivers[indicator]
            #if not df_indicator.empty: #if a result, driver is gold
            percentage += row['percentage']
        if total_league_time > 0:
            gold_league_percentage = round(gold_league_drive_time/total_league_time * 100,0)
        #check if there are previous team results in the team indicator file
        #team = df_team_indicator['team_id'] == team_id
        #df_team = df_team_indicator[team]
        #if not df_team.empty:
        #    race_count = df_team.iloc[0]['race_count'] + 1
        #    running_percentage = round((df_team.iloc[0]['race_count'] * df_team.iloc[0]['percentage'] + percentage) /  race_count,2)   
        #if df_team.empty:
        #    running_percentage = percentage
        #    race_count = 1
        # ['team_id','team_display_name','race_count','percentage','gold_league_drive_time','gold_league_percentage','total_league_time']    
        index += 1
        df_new_team_indicator.loc[index] = [team_id,team_display_name,race_count,percentage,gold_league_drive_time,gold_league_percentage,total_league_time]

    #now combine any old values which may not have been updated with the new Dataframe
    df_not_in_common = df_team_indicator.loc[~df_team_indicator['team_id'].isin(df_new_team_indicator['team_id'])]
    frames = [df_not_in_common, df_new_team_indicator]
    result = pd.concat(frames)
    return result


if __name__ == '__main__': #only execute when called as script, skipped when loaded as module
    #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults
    parser=argparse.ArgumentParser()
    parser.add_argument("--team_indicator", help="location of the driver indicator file. if only name is supplied, script location is used",  default='./indicators/pec_s3_team_indicator.csv', type=str)
    parser.add_argument("--driver_indicator", help="location of the driver indicator file. if only name is supplied, script location is used",  default='./indicators/pec_s3_driver_indicator.csv', type=str)
       
    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")

    team_indicator_file = args.team_indicator 
    driver_indicator_file = args.driver_indicator #serves both as reference data set from previous race(s) as well as file to save latest status to after processing
    
    # Read the driver_indicator_file, if exists, if not; stop
    try:
        df_driver_indicator = pd.read_csv(driver_indicator_file)
    except:
        print(f"ERROR: could not find file {driver_indicator_file}. Quitting...")
        quit()

    #print(tabulate(df_driver_indicator, headers = 'keys', tablefmt = 'psql'))

    # Read the team_indicator_file, if exists
    try:
        df_team_indicator = pd.read_csv(team_indicator_file)
    except:
        #scenario first race
        print(f"WARNING: could not find file {team_indicator_file}. Is this the first race?")
        df_team_indicator = pd.DataFrame(columns=team_indicator_columns)

    #print(tabulate(df_team_indicator, headers = 'keys', tablefmt = 'psql'))

    # show indicator
    df_new_team_indicator = update_team_indicator(df_team_indicator, df_driver_indicator)
    print(tabulate(df_new_team_indicator, headers = 'keys', tablefmt = 'psql'))

    # save indicator as file
    df_new_team_indicator.to_csv(team_indicator_file,index=False)