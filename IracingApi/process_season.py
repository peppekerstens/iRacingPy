import os
import sys
import pwinput
from tabulate import tabulate
import json
from iracingdataapi.client import irDataClient
import pandas as pd
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme
import glob
from pathlib import Path

import get_league_information
import get_member_data
import get_session_data
import update_gt3_driver_indicator
import update_gt3_team_indicator

league_information_file = 'league_information'
league_roster_file = 'league_roster'
league_pending_requests_file = 'league_pending_requests'
league_seasons_file = 'league_seasons'
#league_season_sessions_file = 'league_season_sessions'
league_season_sessions_file = 's2'
member_data_file = 'member_data'
session_file_prefix = 'session_'
driver_indicator_file = 'pec_driver_indicator' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
team_indicator_file = 'pec_team_indicator' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
latest_session_file = None #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv
league_id = 5606
season_id = 83043 #s2
#season_id = 89417 #s3


def get_league_season(league_seasons: json, season_id: int):
    for season in league_seasons['seasons']:
        if  season['season_id'] == season_id:
            return season
    return None

def process_session_result(username, password, subsession_id):
    print('Processing...')
    idc = irDataClient(username=username, password=password)
    # get results from a session server
    result = idc.result(subsession_id=subsession_id)
    track = result['track']
    df_current_track_detail = get_session_data.get_track_detail(idc, track['track_id'])
    print()
    print('Track information')
    print()
    print(tabulate(df_current_track_detail[['track_name','config_name','track_config_length_km']], headers = 'keys', tablefmt = 'psql'))
    track_length = df_current_track_detail['track_config_length_km'].iloc[-1]

    session_result_types = get_session_data.get_session_result_types(result)
    car_classes = get_session_data.get_session_result_classes(result)
    for result_type in session_result_types:
        for car_class in car_classes:
            #car_classes = df_result['car_class_short_name'].unique()
            #car_class = "GT3 Class"
            df_driver_result = get_session_data.get_session_driver_result_class(idc, subsession_id, result, track_length, result_type, car_class)

            csv_name = 'session_' + subsession_id + '_' + result_type + '_' + car_class + '.csv'

            print()
            print(f"driver result {subsession_id} {result_type} {car_class}")
            print()
            print(tabulate(df_driver_result[['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','avg_lap_valid','laps_complete','speed','time', 'percentage']], headers = 'keys', tablefmt = 'psql'))

            #csv_name = 'session_' + session_id + '_' + session_result['simsession_type_name'] + 'csv'

            #from pathlib import Path  
            #filepath = Path('folder/subfolder/out.csv')  
            #filepath.parent.mkdir(parents=True, exist_ok=True)
            df_driver_result.to_csv(csv_name,index=False,columns=['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','avg_lap_valid','laps_complete','speed','time', 'percentage'])
    return


if len(sys.argv) < 3:
    print('Going into interactive mode....')
    username = input("Enter username: ")
    password = pwinput.pwinput(prompt='Enter password: ')

idc = irDataClient(username=username, password=password)

# Get the list of drivers in the league
league_information = idc.league_get(league_id)
print(f"Processing league {league_information['league_name']}")
df_league_roster = pd.json_normalize(league_information['roster'])
#print(tabulate(df_league_roster[['cust_id','display_name','league_member_since','admin']], headers = 'keys', tablefmt = 'psql'))
#df_league_roster.to_csv(league_roster_file + ".csv",index=False,columns=['cust_id','display_name','league_member_since','admin'])  

league_seasons = idc.league_seasons(league_id)
season = get_league_season(league_seasons, season_id)
if season is None:
    print(f"WARNING: Could not find season {season_id} in active seasons, trying retired seasons..")
    league_seasons = idc.league_seasons(league_id, retired=True)
    season = get_league_season(league_seasons, season_id)
if season is None:
    print(f"ERROR: Can not find a season match for {season_id} in league {league_information['league_name']}. Quitting.")
    quit()
df_current_season = pd.DataFrame.from_dict([season])
#df_league_seasons = pd.DataFrame.from_dict(league_seasons['seasons'])
#current_season = df_league_seasons['season_id'] == season_id
print(f"Processing season {df_current_season.iloc[0]['season_name']}")

#print(tabulate(df_league_seasons[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
#df_league_seasons.to_csv(league_season_sessions_file + ".csv",index=False)  

league_season_sessions_csv = league_season_sessions_file + '.csv'
df_league_season_sessions = pd.read_csv(league_season_sessions_csv)


league_season_sessions = idc.league_season_sessions(league_id, season_id)
df_league_season_sessions = pd.DataFrame.from_dict(league_season_sessions['sessions'])
print(tabulate(df_league_season_sessions[['session_id','subsession_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
#df_league_season_sessions.to_csv(league_s eason_sessions_file + ".csv",index=False,columns=['session_id','time_limit','qualify_length','race_length'])  

league_season_practise = df_league_season_sessions['race_length'] == 0
df_league_season_practise =  df_league_season_sessions[league_season_practise]

league_season_races = df_league_season_sessions['race_length'] != 0

#assumes a single subsession! does not work with multiple splits
for index, df_row in df_league_season_sessions.iterrows():
    subsession_id = df_row['subsession_id']
    print(f"Processing subsession {subsession_id}") 
    session_file = 'session_' + str(subsession_id) + '.csv'
    path = './' + session_file
    check_file = os.path.isfile(path)
    #sessionsFilenamesList = glob.glob(session_file)
    if check_file is True:
        #skip file
        print(f"{session_file} already exists, skipping..")
    if check_file is False:
        #process
        df_driver_result_class = get_session_data.get_session_driver_result(idc, subsession_id)
        #print(tabulate(df_driver_result_class[['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','avg_lap_valid','laps_complete','speed','time', 'percentage']], headers = 'keys', tablefmt = 'psql'))
        if df_driver_result_class is not None:
            df_driver_result_class.to_csv(session_file,index=False,columns=['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','avg_lap_valid','laps_complete','speed','time', 'percentage'])  

#report on all races
#for index, df_row in df_league_season_races.iterrows():
#    pass



