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
import argparse

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

def get_total_session_time(result: json): #assumes all contenders (teams of drivers) within a session (race, qually etc), eg all memebers under ['session_results']
    total_time = 0
    for contender in result:
        if contender['finish_position'] == 0:
            contender_time = contender['laps_complete'] * contender['average_lap']
            total_time += contender_time
    total_time = total_time / 10000
    return total_time

def get_session_class_result(result: json, car_class: str):
    #assumes all contenders (teams of drivers) within a session (race, qually etc), eg all memebers under ['session_results']
    class_result = []
    for item in result:
        if item["car_class_short_name"] == car_class:
            class_result.append(item)
    return class_result

def get_total_session_time_class(result: json, car_class: str): 
    #assumes all contenders (teams of drivers) within a session (race, qually etc), eg all memebers under ['session_results']
    total_time = 0
    class_result = get_session_class_result(result,car_class)
    for contender in class_result:
        if contender['finish_position_in_class'] == 0:
            contender_time = contender['laps_complete'] * contender['average_lap']
            total_time += contender_time
    total_time = total_time / 10000
    return total_time

def get_team_driver_results(result: json):
    new_list = []
    for team_results in result:
        team_display_name = team_results["display_name"]
        #if  session_results['simsession_type_name'] == type:
        for driver in team_results['driver_results']:
            driver['team_display_name'] = team_display_name
            new_list.append(driver)
    return new_list

def get_track_detail(df_all_tracks: pd, track_id) -> pd:
    #add the lentgh in KM to all records. If we do this after filtering the track we want, we get an 'bad practise' error
    df_all_tracks['track_config_length_km'] = df_all_tracks['track_config_length'] * 1.609344  #track_config_length is provided in miles
    #we want info from a specific track
    current_track = df_all_tracks['track_id'] == track_id
    df_current_track_detail = df_all_tracks[current_track]
    #print()
    #print('Track information')
    #print()
    #print(tabulate(df_current_track_detail[['track_name','config_name','track_config_length_km']], headers = 'keys', tablefmt = 'psql'))
    return df_current_track_detail

def get_lap_data(idc: irDataClient, subsession_id: int, simsession_number: int, driver: json) -> json:
    lap_data = json.loads('{}')
    cust_id = driver['cust_id']
    try:
        team_id = driver['team_id']
        lap_data = idc.result_lap_data(subsession_id=subsession_id,simsession_number=simsession_number, cust_id=cust_id, team_id=team_id)
    except:
        lap_data = idc.result_lap_data(subsession_id=subsession_id,simsession_number=simsession_number, cust_id=cust_id)
    #print(f"get_lap_data: {len(lap_data)}")
    return lap_data

def get_session_lap_data(idc: irDataClient , subsession_id: int, simsession_number: int, driver_result: json) -> json:
    driver_count = len(driver_result)
    lap_data = []
    with tqdm(total=driver_count) as pbar:
        for driver in driver_result:
            driver_lap_data = get_lap_data(idc, subsession_id, simsession_number, driver)
            lap_data.extend(driver_lap_data)
            pbar.update(1)
    #print(f"get_session_lap_data: {len(lap_data)}")
    return lap_data

def get_valid_laps(lap_data: json, cust_id: int) -> json:
    driver_valid_lap_data = []
    lap_invalidation_events = ['pitted','invalid']
    for lap in lap_data:
        if lap['cust_id'] == cust_id:
            lap_valid = False
            for invalidation_event in lap_invalidation_events:
                if invalidation_event not in lap['lap_events']:
                    lap_valid = True
            if lap['lap_time'] == -1:
                lap_valid = False
            if lap_valid == True:
                driver_valid_lap_data.append(lap)
    return driver_valid_lap_data

def get_track_length(idc: irDataClient, track_id: int):
    all_tracks = idc.tracks
    df_all_tracks = pd.json_normalize(all_tracks)
    df_current_track_detail = get_track_detail(df_all_tracks, track_id)
    track_length = df_current_track_detail['track_config_length_km'].iloc[-1]
    return track_length

def get_session_drivers(session_result: json, team_race: bool = False) -> json:
    #gets the session_result part from the iRacing session result. 
    #assumes input is already filtered on certain subssesion (Race, Free Practice etc)
    if team_race == True:
        #item = session_result[0]['results'] #improve: hard coding on first race!
        item = session_result['results'] #improve: hard coding on first race!
        driver_result = get_team_driver_results(item)
    if team_race == False:
        #item = session_result[0]['results'] #improve: hard coding on first race!
        item = session_result['results'] #improve: hard coding on first race!
        driver_result = item # no more processing needed
    return driver_result

def add_valid_lap_report(driver_result: json, lap_data: json, track_length) -> json:
    # adds extra info to provided driver_result
    for driver in driver_result:
        #filter driver specific lap data and create the lap report
        #driver_lap_data = df_lap_data['cust_id'] == driver['cust_id']
        #df_driver_lap_data = df_lap_data[driver_lap_data]
        #df_valid_driver_laps = get_valid_laps(df_driver_lap_data,driver['cust_id'])
        valid_driver_laps = get_valid_laps(lap_data,driver['cust_id'])

        #laps_total = get_laps_total(valid_driver_laps,driver['cust_id']) 
        laps_total = len(valid_driver_laps)

        #lap_avg = get_lap_avg(valid_driver_laps,driver['cust_id']) / 10000
        new_list = []
        for lap in valid_driver_laps:
            new_list.append(int(lap['lap_time']))
        lap_avg = 0    
        if new_list != []:
            lap_avg = np.average(new_list) / 10000
        
        driver['laps_complete_valid'] = laps_total
        driver['average_lap_valid'] = round(lap_avg)
        if lap_avg != 0:
            driver['speed_valid'] = round(track_length / lap_avg * 3600)
        if lap_avg == 0:
            driver['speed_valid'] = 0
        driver['time_valid'] = round(lap_avg * laps_total)
    return driver_result

def process_session_result(username, password, subsession_id, session_type = None, car_class = None):
    idc = irDataClient(username=username, password=password)
    # get results from a session server
    result = idc.result(subsession_id=subsession_id)
    result_file = './iracing_result/iracing-result-' + str(subsession_id) + '.json'
    # save for future reference
    with open(result_file, "w") as write_file:
        json.dump(result, write_file, indent=4, sort_keys=True)
    # get track info
    track = result['track']
    track_length = get_track_length(idc,track['track_id'])
    # check if team race
    team_race = False
    if result['max_team_drivers'] > 1: team_race = True
    # check simsession types (Practice, Race....)
    session_types = get_session_result_types(result)
    # check car_classes (LMP2, GT3...)
    car_classes = get_session_result_classes_json(result)
    # iterate each session_result
    for session_result in result['session_results']:
        if None == session_type or session_type == session_result['simsession_type_name']:
            drivers = get_session_drivers(session_result,team_race)
            # add session info to drivers list
            for driver in drivers:
                driver['simsession_number'] = session_result['simsession_number']
                driver['simsession_type'] = session_result['simsession_type']
                driver['simsession_type_name'] = session_result['simsession_type_name']
                driver['simsession_subtype'] = session_result['simsession_subtype']
                driver['simsession_name'] = session_result['simsession_name']
            # get the total session time of this one (Practice, Race....)
            total_session_time = get_total_session_time(drivers)
            # get the lap data of each driver for further analysis
            lap_data = get_session_lap_data(idc=idc,subsession_id=subsession_id,simsession_number=session_result['simsession_number'],driver_result=drivers)
            #print(f"lap data count {len(lap_data)}")
            # save the lap data if further checks are needed
            df_lap_data = pd.json_normalize(lap_data)
            # drop unneeded columns
            columns_to_drop = ['ai',
                                'helmet.pattern',
                                'helmet.color1',
                                'helmet.color2',
                                'helmet.color3',
                                'helmet.face_type',
                                'helmet.helmet_type']
            df_lap_data.drop(columns=columns_to_drop,inplace=True)
            df_lap_data_file = './lap_data/lap_data_' + str(subsession_id) + '_' + session_result['simsession_type_name'] + '.csv'
            df_lap_data.to_csv(df_lap_data_file,index=False) 
            # get the validated laps 
            driver_report = add_valid_lap_report(drivers,lap_data,track_length)
            df_result = pd.json_normalize(driver_report)
            #TODO the total time driven per team, to calculate percentage per driver later
            df_result['avg_lap'] = round(df_result['average_lap'] / 10000)
            df_result['time'] = round(df_result['avg_lap'] * df_result['laps_complete'])
            df_result['speed'] = round((track_length / (df_result['average_lap'] / 10000)) * 3600)
            df_result['total_session_time'] = round(total_session_time)
            #df_result['total_session_time_class'] = get_total_session_time_class(drivers,df_result["car_class_short_name"])
            # drop unneeded columns
            columns_to_drop = ['livery.car_id',
                                'livery.pattern',
                                'livery.color1',
                                'livery.color2',
                                'livery.color3',
                                'livery.number_font',
                                'livery.number_color1',
                                'livery.number_color2',
                                'livery.number_color3',
                                'livery.number_slant',
                                'livery.sponsor1',
                                'livery.sponsor2',
                                'livery.car_number',
                                'livery.wheel_color',
                                'livery.rim_type',
                                'suit.pattern',
                                'suit.color1',
                                'suit.color2',
                                'suit.color3',
                                'helmet.pattern',
                                'helmet.color1',
                                'helmet.color2',
                                'helmet.color3',
                                'helmet.face_type',
                                'helmet.helmet_type']
            df_result.drop(columns=columns_to_drop,inplace=True)

            columns_to_drop = ['division',
                                'old_license_level',
                                'old_sub_level',
                                'old_cpi',
                                'oldi_rating',
                                'old_ttrating', 
                                'new_license_level',
                                'new_sub_level',
                                'new_cpi',
                                'newi_rating',
                                'new_ttrating',
                                'multiplier',
                                'license_change_oval',
                                'license_change_road',
                                'max_pct_fuel_fill',
                                'weight_penalty_kg',
                                'league_points',
                                'league_agg_points']
            df_result.drop(columns=columns_to_drop,inplace=True)

            columns_to_drop = ['best_nlaps_num',
                                'best_nlaps_time',
                                'best_qual_lap_at',
                                'best_qual_lap_num',
                                'best_qual_lap_time',
                                'reason_out_id',
                                'reason_out',
                                'champ_points',
                                'drop_race',
                                'club_points',
                                'qual_lap_time',
                                'aggregate_champ_points',
                                'watched',
                                'friend',
                                'ai']
            df_result.drop(columns=columns_to_drop,inplace=True)
            # save the session data 
            df_result_file = './sessions/session_' + str(subsession_id) + '_' + session_result['simsession_type_name'] + '.csv'
            df_result.to_csv(df_result_file,index=False)
    return


if __name__ == '__main__':
        #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults
    parser=argparse.ArgumentParser()
    parser.add_argument("--username", help="",  default='', type=str)
    parser.add_argument("--password", help="",  default='', type=str)
    parser.add_argument("--sessionid", help="")
    parser.add_argument("--type", help="")
    
    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")
    
    username = args.username
    password = args.password
    subsession_id = args.sessionid
    session_type = args.type

    if username == "":
        username = input("Enter username: ")

    if password == "":
        password = pwinput.pwinput(prompt='Enter password: ')

    if subsession_id == "":
        subsession_id = input("Enter subsession_id: ")
    
    if session_type == "":
        session_type = None

    process_session_result(username, password, subsession_id, session_type)

    #process_session_result_old(username, password, subsession_id)

 