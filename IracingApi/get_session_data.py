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
    if len(sys.argv) < 4:
        #raise BaseException('bla')  #does not work; processing is stopped see: https://docs.python.org/3/library/exceptions.html#Exception
        print('Error: to few arguments!')
        print('Usage: py get_session_data.py [username] [password] [session_id]')
        print('Going into interactive mode....')
        username = input("Enter username: ")
        #password = getpass.getpass('Enter password:') # hard in practise, does not show any input hint
        password = pwinput.pwinput(prompt='Enter password: ')
        session_id = input("Enter session_id: ")

    if len(sys.argv) > 4:
        print('Error: to many arguments!')
        print('Usage: py get_session_data.py [username] [password] [session_id]')
        sys.exit()

    if len(sys.argv) == 4:
        username = sys.argv[1] #first cmdline arg is acnt name
        password = sys.argv[2] #second cmdline arg is pwd
        session_id = sys.argv[3] #third cmdline arg is pwd
    
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
    
    print(tabulate(df_current_track_detail[['track_name','config_name','track_config_length_km']], headers = 'keys', tablefmt = 'psql'))

    #if team_race:
    race_result = get_session_results(session_result, 'Race')
    driver_result = get_driver_results(race_result[0]['results'])
    print('Receiving al laps..')
    new_list = []
    for dr in driver_result:
        new_list.append(get_valid_avg_laps(dr, idc, session_id))
    df_race_result = pd.json_normalize(race_result[0]['results'])
    df_driver_result = pd.json_normalize(driver_result)

    #some code to detect by class
    #https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
    #
    #Get the total time driven per team, to calculate percentage per driver later
    df_race_result['avg_lap'] = (df_race_result['average_lap'] / 10000)
    df_race_result['time'] = (df_race_result['avg_lap'] * df_race_result['laps_complete'])
    
    #df_race_result[['team_id','display_name','avg_lap','laps_complete','time']]
    print(tabulate(df_race_result[['team_id','display_name','avg_lap','laps_complete','time']], headers = 'keys', tablefmt = 'psql'))

    #Get the team results per class - ToDo
    car_class = df_race_result['car_class_short_name'] == "GT3 Class"
    df_race_result_class = df_race_result[car_class]

    #Get the speed an total time driven per driver of each team, expressed as a percentage of the laps of winning team
    track_length = df_current_track_detail['track_config_length_km'].iloc[0]
    total_race_laps = df_race_result['laps_complete'].max()

    #get the valid avg_lap_times only
    #df_driver_result['average_lap_valid'] = get_valid_avg_laps(idc, session_id, df_driver_result['team_id'],df_driver_result['cust_id'])
    """
    df_driver_result['average_lap_valid'] = 0 #add another column (for lack of better way)
    for index, row in df_driver_result.iterrows():
        #lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=466944, team_id=203387)
        lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=row['cust_id'], team_id=row['team_id'])
        df_lap_data = pd.json_normalize(lap_data) 
        #df_lap_data[['group_id','cust_id','name','display_name', 'lap_number','flags','session_time', 'session_start_time', 'lap_time', 'team_fastest_lap', 'personal_best_lap','lap_events']]
        #df_lap_data[['lap_number','flags','session_time', 'session_start_time', 'lap_time', 'team_fastest_lap', 'personal_best_lap','lap_events']]
        #print(tabulate(df_lap_data[['lap_number','flags','session_time', 'session_start_time', 'lap_time', 'team_fastest_lap', 'personal_best_lap','lap_events']], headers = 'keys', tablefmt = 'psql'))

        array = [0, 4] #clean lap or offtrack lap
        clean_laps = df_lap_data['flags'].isin(array) 
        df_clean_lap_data = df_lap_data[clean_laps]

        valid_laps = df_lap_data['lap_time'] != -1
        df_valid_lap_data = df_clean_lap_data[valid_laps]
        #df_valid_lap_data[['lap_number','flags','session_time', 'session_start_time', 'lap_time', 'team_fastest_lap', 'personal_best_lap','lap_events']]
        avg_lap_time = df_valid_lap_data['lap_time'].mean()
        row['average_lap_valid'] = avg_lap_time
    """

    #total_race_laps = df_race_result.loc[df_race_result['laps_complete'].idxmax()]
    df_driver_result['avg_lap'] = (df_driver_result['average_lap'] / 10000)
    df_driver_result['avg_lap_valid'] = (df_driver_result['average_lap_valid'] / 10000)
    #df_driver_result['speed'] = (track_length.iloc[0] / df_driver_result['avg_lap'] * 3600)
    df_driver_result['speed'] = (track_length / df_driver_result['avg_lap_valid'] * 3600)
    df_driver_result['time'] = (df_driver_result['avg_lap_valid'] * df_driver_result['laps_complete'])
    
   
    
    #not there yet....
    #df_driver_result['percentage'] = np.where(df_race_result['team_id'] == df_driver_result['team_id'], 0, df_driver_result['laps_complete'] / df_race_result['laps_complete'])
    #throws ValueError: Can only compare identically-labeled Series objects
    #so the long way round
    df_driver_result['percentage'] = round(df_driver_result['laps_complete'] / total_race_laps * 100,0)
    #df_driver_result['percentage'] = round(df_driver_result['laps_complete'] / get_total_laps(df_driver_result, df_driver_result['team_id'].iloc[0]) * 100,0)
    
    #df_driver_result[['team_id','cust_id','display_name', 'avg_lap','laps_complete','speed','time', 'percentage']] 
    print(tabulate(df_driver_result[['team_id','cust_id','display_name', 'avg_lap','avg_lap_valid','laps_complete','speed','time', 'percentage']], headers = 'keys', tablefmt = 'psql'))


