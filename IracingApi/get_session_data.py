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

    #subsession_id = 43720351 #BMW 12.0 Challenge 
    #subsession_id = 58362796 #PEC S2 5th race fuji

    #subsession_id = 50813237 #1st FP S2

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
def get_session_result_types(result: json):
    new_list = []
    for session_results in result['session_results']:
        session_result_type = session_results['simsession_type_name']
        new_list.append(session_result_type)
    return new_list

def get_session_result_classes_json(result: json):
    unique_car_classes = set()
    for session_results in result['session_results']:
        for item in session_results['results']:
            unique_car_classes.add(item["car_class_short_name"])
    return unique_car_classes

def get_session_result_classes(df_result: pd):
    #assumes a converted json to Dataframe with the data subset session_results\results from a iRacing session result file   
    return df_result["car_class_short_name"].unique()

def get_session_results(result: json, result_type: str):
    new_list = []
    for session_results in result['session_results']:
        if session_results['simsession_type_name'] == result_type:
            new_list.append(session_results)
    return new_list

def get_team_driver_results(result: json):
    new_list = []
    for driver_results in result:
        #if  session_results['simsession_type_name'] == type:
        for driver in driver_results['driver_results']:
            new_list.append(driver)
    return new_list

def get_personal_driver_results(result: json):
    new_list = []
    for driver in result['driver_results']:
        new_list.append(driver)
    return new_list

def get_team_name(result: json, team_id: int) -> str:
    for item in result:
        if item['team_id'] == team_id:
            return item['display_name']
    return ''

def get_valid_laps(driver_result: json, idc: irDataClient, session_id: int):
    cust_id = driver_result['cust_id']
    team_id = driver_result['team_id']
    lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=cust_id, team_id=team_id)
    new_list = []
    for lap in lap_data:
        #array = [0, 4] #clean lap or invalid lap (slow down penalty)
        if lap['flags'] in [0, 4] and lap['lap_time'] != -1:
            new_list.append(lap)
    avg_lap_time = 0
    laps_complete = 0
    if new_list != []:
        df_lap_data = pd.json_normalize(new_list)
        #df_valid_lap_data[['lap_number','flags','session_time', 'session_start_time', 'lap_time', 'team_fastest_lap', 'personal_best_lap','lap_events']] 
        avg_lap_time = df_lap_data['lap_time'].mean()
        laps_complete = len(df_lap_data)
    driver_result['average_lap_valid'] = avg_lap_time
    driver_result['laps_complete_valid'] = laps_complete
    return driver_result

def get_total_laps(result: pd, team_id: int):
    team_match = result['team_id'] == team_id
    team_result = result[team_match]
    return team_result['laps_complete'].sum()

def get_track_detail(df_all_tracks: pd, track_id) -> pd:
    #add the lentgh in KM to all records. If we do this after filtering the track we want, we get an 'bad practise' error
    df_all_tracks['track_config_length_km'] = df_all_tracks['track_config_length'] * 1.609344  #track_config_length is provided in miles
    #we want info from a specific track
    current_track = df_all_tracks['track_id'] == track_id
    df_current_track_detail = df_all_tracks[current_track]
    return df_current_track_detail

def get_total_racelaps_class(df_result:pd, car_class) -> int:
    #get the total race laps per class
    current_car_class = df_result['car_class_short_name'] == car_class
    df_result_class = df_result[current_car_class]
    total_race_laps = df_result_class['laps_complete'].max()
    return total_race_laps

def get_session_driver_result_class(idc, subsession_id, result, track_length, result_type, car_class) -> pd:
    print()
    print(f"Getting information for {result_type}")
    print()
    session_result = get_session_results(result,result_type)
    #practice_result = get_session_results(session_result, 'Open Practice')
    #race_result = get_session_results(session_result, 'Race')
    team_race = False
    if result['max_team_drivers'] > 1: team_race = True
    #if result['min_team_drivers'] > 1 and result['max_team_drivers'] > 1: team_race = True
    #for item in session_result['results']:
    #
    if team_race == True:
        item = session_result[0]['results'] #improve: hard coding on first race!
        driver_result = get_team_driver_results(item)
    if team_race == False:
        item = session_result['results'][0] #improve: hard coding on first race!
        driver_result = get_personal_driver_results(item)
    df_result = pd.json_normalize(item)  
    print()
    print('Receiving all laps')
    print()
    driver_count = len(driver_result)
    new_list = []
    with tqdm(total=driver_count) as pbar:
        for dr in driver_result:
            new_list.append(get_valid_laps(dr, idc, subsession_id))
            pbar.update(1)
            #print(end=".")
    df_driver_result = pd.json_normalize(driver_result)
    #some code to detect by class
    #https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
    #
    #Get the total time driven per team, to calculate percentage per driver later
    df_result['avg_lap'] = (df_result['average_lap'] / 10000)
    df_result['time'] = (df_result['avg_lap'] * df_result['laps_complete'])    
    #Get the team results for the GT3 class
    current_car_class = df_result['car_class_short_name'] == car_class
    df_result_class = df_result[current_car_class]
    total_race_laps = df_result_class['laps_complete'].max()
    #Get the speed an total time driven per driver of each team
    #average_lap = 940294 = 94.0294 sec
    df_driver_result['avg_lap'] = (df_driver_result['average_lap'] / 10000)
    df_driver_result['avg_lap_valid'] = (df_driver_result['average_lap_valid'] / 10000)
    #df_driver_result['speed'] = (track_length.iloc[0] / df_driver_result['avg_lap'] * 3600)    
    df_driver_result['speed'] = (track_length / df_driver_result['avg_lap_valid'] * 3600)
    df_driver_result['time_valid'] = (df_driver_result['avg_lap_valid'] * df_driver_result['laps_complete_valid'])
    df_driver_result['time'] = (df_driver_result['avg_lap'] * df_driver_result['laps_complete'])
    df_driver_result['percentage'] = round(df_driver_result['laps_complete'] / total_race_laps * 100,0)
    #get the team name from the race_result - not working yet, so empty for now
    #df_driver_result['team_display_name'] = get_team_name(first_race_result, df_driver_result['team_id'])
    df_driver_result['team_display_name'] = ''
    car_class = df_driver_result['car_class_short_name'] == car_class
    df_driver_result_class = df_driver_result[car_class]
    return df_driver_result_class
      

def process_session_result(username, password, subsession_id):
    print('Processing...')
    idc = irDataClient(username=username, password=password)
    # get results from a session server
    result = idc.result(subsession_id=subsession_id)
    track = result['track']
    #get info in all tracks present in iRacing. Needed for track length, which is needed to calculate avg driver speed.
    all_tracks = idc.tracks
    #if all_tracks is not None:
    #    print('Received all_tracks')
    df_all_tracks = pd.json_normalize(all_tracks)
    df_current_track_detail = get_track_detail(df_all_tracks, track['track_id'])
    print()
    print('Track information')
    print()
    print(tabulate(df_current_track_detail[['track_name','config_name','track_config_length_km']], headers = 'keys', tablefmt = 'psql'))
    track_length = df_current_track_detail['track_config_length_km'].iloc[-1]

    session_result_types = get_session_result_types(result)
    car_classes = get_session_result_classes_json(result)
    for result_type in session_result_types:
        for car_class in car_classes:
            #car_classes = df_result['car_class_short_name'].unique()
            #car_class = "GT3 Class"
            df_driver_result = get_session_driver_result_class(idc, subsession_id, result, track_length, result_type, car_class)

            csv_name = 'session_' + subsession_id + '_' + result_type + '_' + car_class + '.csv'

            print()
            print(f"driver result {subsession_id} {result_type} {car_class}")
            print()
            print(tabulate(df_driver_result[['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','laps_complete','avg_lap_valid','laps_complete_valid','speed','time','time_valid','percentage']], headers = 'keys', tablefmt = 'psql'))

            #csv_name = 'session_' + session_id + '_' + session_result['simsession_type_name'] + 'csv'

            #from pathlib import Path  
            #filepath = Path('folder/subfolder/out.csv')  
            #filepath.parent.mkdir(parents=True, exist_ok=True)
            df_driver_result.to_csv(csv_name,index=False,columns=['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','laps_complete','avg_lap_valid','laps_complete_valid','speed','time','time_valid','percentage'])
    return

if __name__ == '__main__':
    if len(sys.argv) < 4:
        #raise BaseException('bla')  #does not work; processing is stopped see: https://docs.python.org/3/library/exceptions.html#Exception
        print('Error: to few arguments!')
        print('Usage: py get_session_data.py [username] [password] [session_id] [csv name]')
        print('Going into interactive mode....')
        username = input("Enter username: ")
        #password = getpass.getpass('Enter password:') # hard in practise, does not show any input hint
        password = pwinput.pwinput(prompt='Enter password: ')
        subsession_id = input("Enter subsession_id: ")

    if len(sys.argv) > 4:
        print('Error: to many arguments!')
        print('Usage: py get_session_data.py [username] [password] [session_id] [csv name]')
        sys.exit()

    if len(sys.argv) == 4:
        username = sys.argv[1] #first cmdline arg is acnt name
        password = sys.argv[2] #second cmdline arg is pwd
        subsession_id = sys.argv[3] #third cmdline arg is session_id
    
    process_session_result(username, password, subsession_id)

 