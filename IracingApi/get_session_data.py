# This script requests server host session data via the iRacing API. 
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

    #session_id = 43720351 #BMW 12.0 Challenge 
    #session_id = 58362796 #PEC S2 5th race fuji

from  iracingdataapi.client import irDataClient
import json
import sys
import csv
import pandas as pd 
from tabulate import tabulate
import numpy as np
#https://stackoverflow.com/questions/9202224/getting-a-hidden-password-input
#import getpass
import pwinput
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme

#https://stackoverflow.com/questions/2733813/iterating-through-a-json-object
#could (should!) improve with List Comprehensions or Vectorization
#https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
def get_session_results(race_result: json, type: str):
    new_list = []
    for session_results in race_result['session_results']:
        if session_results['simsession_type_name'] == type:
            new_list.append(session_results)
    return new_list

def get_driver_results(race_result: json):
    new_list = []
    for driver_results in race_result:
        #if  session_results['simsession_type_name'] == type:
        for driver in driver_results['driver_results']:
            new_list.append(driver)
    return new_list

def get_team_name(race_result: json, team_id: int) -> str:
    for item in race_result:
        if item['team_id'] == team_id:
            return item['display_name']
    return ''

def get_valid_avg_laps(driver_result: json, idc: irDataClient, session_id: int):
    cust_id = driver_result['cust_id']
    team_id = driver_result['team_id']
    lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=cust_id, team_id=team_id)
    new_list = []
    for lap in lap_data:
        #array = [0, 4] #clean lap or offtrack lap
        if lap['flags'] in [0, 4] and lap['lap_time'] != -1:
            new_list.append(lap) 
    df_lap_data = pd.json_normalize(new_list)
    #df_valid_lap_data[['lap_number','flags','session_time', 'session_start_time', 'lap_time', 'team_fastest_lap', 'personal_best_lap','lap_events']]
    avg_lap_time = df_lap_data['lap_time'].mean()
    driver_result['average_lap_valid'] = avg_lap_time
    return driver_result

"""
def get_valid_avg_laps(idc: irDataClient, session_id: int, team_id = None, cust_id = None):
    lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=cust_id, team_id=team_id)
    df_lap_data = pd.json_normalize(lap_data) 
    array = [0, 4] #clean lap or offtrack lap
    clean_laps = df_lap_data['flags'].isin(array) 
    df_clean_lap_data = df_lap_data[clean_laps]
    valid_laps = df_lap_data['lap_time'] != -1
    df_valid_lap_data = df_clean_lap_data[valid_laps]
    #df_valid_lap_data[['lap_number','flags','session_time', 'session_start_time', 'lap_time', 'team_fastest_lap', 'personal_best_lap','lap_events']]
    avg_lap_time = df_valid_lap_data['lap_time'].mean()
    return avg_lap_time
"""

def get_total_laps(result: pd, team_id: int):
    team_match = result['team_id'] == team_id
    team_result = result[team_match]
    return team_result['laps_complete'].sum()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        #raise BaseException('bla')  #does not work; processing is stopped see: https://docs.python.org/3/library/exceptions.html#Exception
        print('Error: to few arguments!')
        print('Usage: py get_session_data.py [username] [password] [session_id] [csv name]')
        print('Going into interactive mode....')
        username = input("Enter username: ")
        #password = getpass.getpass('Enter password:') # hard in practise, does not show any input hint
        password = pwinput.pwinput(prompt='Enter password: ')
        session_id = input("Enter session_id: ")
        csv_name = input(f"Enter CSV name (<enter> for session_{session_id}.csv): ")
        if csv_name == '':
            csv_name = 'session_' + session_id + '.csv'

    if len(sys.argv) > 5:
        print('Error: to many arguments!')
        print('Usage: py get_session_data.py [username] [password] [session_id] [csv name]')
        sys.exit()

    if len(sys.argv) == 5:
        username = sys.argv[1] #first cmdline arg is acnt name
        password = sys.argv[2] #second cmdline arg is pwd
        session_id = sys.argv[3] #third cmdline arg is session_id
        csv_name = sys.argv[4] #third cmdline arg is csv_name

    if csv_name == None:
        csv_name = 'session_' + session_id + '.csv'
    
    print('Processing...')
    idc = irDataClient(username=username, password=password)

    # get results from a session server
    session_result = idc.result(subsession_id=session_id)
    if session_result is not None:
        print('Received session_result')

    team_race = False
    #if session_result['min_team_drivers'] == 1 and session_result['max_team_drivers'] == 1: team_race = False
    if session_result['min_team_drivers'] > 1 and session_result['max_team_drivers'] > 1: team_race = True

    track = session_result['track']
    #get info in all tracks present in iRacing. Needed for track length, which is needed to calculate avg driver speed.
    all_tracks = idc.tracks
    if all_tracks is not None:
        print('Received all_tracks')
    df_all_tracks = pd.json_normalize(all_tracks)
    #add the lentgh in KM to all records. If we do this after filtering the track we want, we get an 'bad practise' error
    df_all_tracks['track_config_length_km'] = df_all_tracks['track_config_length'] * 1.609344  #track_config_length is provided in miles
    #we want info from a specific track
    current_track = df_all_tracks['track_id'] == track['track_id']
    df_current_track_detail = df_all_tracks[current_track]
    
    print()
    print('Track information')
    print()
    print(tabulate(df_current_track_detail[['track_name','config_name','track_config_length_km']], headers = 'keys', tablefmt = 'psql'))

    #if team_race:
    race_result = get_session_results(session_result, 'Race')
    first_race_result = race_result[0]['results'] #improve: hard coding on first race!
    driver_result = get_driver_results(first_race_result) 
    driver_count = len(driver_result)

    print()
    print('Receiving all laps')
    print()
    new_list = []
    with tqdm(total=driver_count) as pbar:
        for dr in driver_result:
            new_list.append(get_valid_avg_laps(dr, idc, session_id))
            pbar.update(1)
            #print(end=".")
    df_race_result = pd.json_normalize(first_race_result)
    df_driver_result = pd.json_normalize(driver_result)

    #some code to detect by class
    #https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
    #
    #Get the total time driven per team, to calculate percentage per driver later
    df_race_result['avg_lap'] = (df_race_result['average_lap'] / 10000)
    df_race_result['time'] = (df_race_result['avg_lap'] * df_race_result['laps_complete'])
    
    print()
    print('Overall race result')
    print()
    #df_race_result[['team_id','display_name','avg_lap','laps_complete','time']]
    print(tabulate(df_race_result[['team_id','display_name','avg_lap','laps_complete','time']], headers = 'keys', tablefmt = 'psql'))

    #Get the team results for the GT3 class
    car_class = df_race_result['car_class_short_name'] == "GT3 Class"
    df_race_result_class = df_race_result[car_class]
    total_race_laps = df_race_result_class['laps_complete'].max()
    #Get the speed an total time driven per driver of each team
    #average_lap = 940294 
    #average_lap = 94.0294 => sec
    df_driver_result['avg_lap'] = (df_driver_result['average_lap'] / 10000)
    df_driver_result['avg_lap_valid'] = (df_driver_result['average_lap_valid'] / 10000)
    #df_driver_result['speed'] = (track_length.iloc[0] / df_driver_result['avg_lap'] * 3600)
    df_current_track_detail['track_config_length_km'].iloc[-1]
    df_driver_result['speed'] = (df_current_track_detail['track_config_length_km'].iloc[-1] / df_driver_result['avg_lap_valid'] * 3600)
    df_driver_result['time'] = (df_driver_result['avg_lap_valid'] * df_driver_result['laps_complete'])
    df_driver_result['percentage'] = round(df_driver_result['laps_complete'] / total_race_laps * 100,0)
    #get the team name from the race_result - not working yet, so empty for now
    #df_driver_result['team_display_name'] = get_team_name(first_race_result, df_driver_result['team_id'])
    df_driver_result['team_display_name'] = ''
    car_class = df_driver_result['car_class_short_name'] == "GT3 Class"
    df_driver_result_class = df_driver_result[car_class]
    print()
    print('GT3 Class driver result')
    print()
    print(tabulate(df_driver_result_class[['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','avg_lap_valid','laps_complete','speed','time', 'percentage']], headers = 'keys', tablefmt = 'psql'))


    #from pathlib import Path  
    #filepath = Path('folder/subfolder/out.csv')  
    #filepath.parent.mkdir(parents=True, exist_ok=True)  
    df_driver_result_class.to_csv(csv_name,index=False,columns=['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','avg_lap_valid','laps_complete','speed','time', 'percentage'])  
