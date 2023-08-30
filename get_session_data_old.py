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

def extract_value(data,keyName):
    result = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == keyName:
                result.append(value)
            elif isinstance(value, (dict, list)):
                result.extend(extract_value(value,keyName))
    elif isinstance(data, list):
        for item in data:
            result.extend(extract_value(item,keyName))
    return result

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

def get_total_session_time(result: json): #assumes all contenders (teams of drivers) within a session (race, qually etc), eg all memebers under ['session_results']
    total_time = 0
    for contender in result:
        if contender['finish_position'] == 0:
            contender_time = contender['laps_complete'] * contender['average_lap']
            total_time += contender_time
    return total_time



#def get_session_results(result: json):
#    new_list = []
#    for session_results in result['session_results']:
#        if session_results['simsession_type_name'] == result_type:
#            new_list.append(session_results)
#    return new_list


#def get_drivers(result: json):
#    new_list = []
#    team_race = False
#    if result['max_team_drivers'] > 1: team_race = True
#    for session_results in result['session_results']:
#        for driver_results in result:
#            #if  session_results['simsession_type_name'] == type:
#            for driver in driver_results['driver_results']:
#                new_list.append(driver)
#    
#            if team_race == True:
#                item = session_result[0]['results'] #improve: hard coding on first race!
#                driver_result = get_team_driver_results(item)
#            if team_race == False:
#                item = session_result[0]['results'] #improve: hard coding on first race!
#                driver_result = item # no more processing needed
#
#    return new_list

def get_team_driver_results(result: json):
    new_list = []
    for team_results in result:
        team_display_name = team_results["display_name"]
        #if  session_results['simsession_type_name'] == type:
        for driver in team_results['driver_results']:
            driver['team_display_name'] = team_display_name
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

def get_valid_laps_old(driver_result: json, idc: irDataClient, session_id: int, result_type: str) -> json:
    cust_id = driver_result['cust_id']
    team_id_str = ''
    try:
        team_id = driver_result['team_id']
        team_id_str = '_' + str(team_id)
        lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=cust_id, team_id=team_id)
    except:
        lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=cust_id)
    
    raw_lap_data_file = './lap_data/raw_lap_data_' + str(subsession_id) + '_' + result_type + '_' + str(cust_id) + team_id_str + '.json'
    with open(raw_lap_data_file, "w") as lap_data_file:
        json.dump(lap_data, lap_data_file, indent=4, sort_keys=True)

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
    #print()
    #print('Track information')
    #print()
    #print(tabulate(df_current_track_detail[['track_name','config_name','track_config_length_km']], headers = 'keys', tablefmt = 'psql'))
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
        item = session_result[0]['results'] #improve: hard coding on first race!
        driver_result = item # no more processing needed
        #driver_result = get_personal_driver_results(item)
    total_session_time = get_total_session_time(item)
    df_result = pd.json_normalize(item)


    print()
    print('Receiving all laps')
    print()
    driver_count = len(driver_result)
    new_list = []
    with tqdm(total=driver_count) as pbar:
        for dr in driver_result:
            new_list.append(get_valid_laps_old(dr, idc, subsession_id, result_type))
            pbar.update(1)
            #print(end=".")
    df_driver_result = pd.json_normalize(driver_result)

    #some code to detect by class
    #https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
    #
    #Get the total time driven per team, to calculate percentage per driver later
    df_result['avg_lap'] = (df_result['average_lap'] / 10000)
    df_result['time'] = (df_result['avg_lap'] * df_result['laps_complete'])
    df_result_file = './results/df_result_' + str(subsession_id) + '_' + result_type + '_' + car_class + '.csv'
    df_result.to_csv(df_result_file,index=False)
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
    df_driver_result['total_session_time'] = total_session_time
    #get the team name from the race_result - not working yet, so empty for now
    #df_driver_result['team_display_name'] = get_team_name(first_race_result, df_driver_result['team_id'])
    #df_driver_result['team_display_name'] = df_result[]
    df_driver_result_file = './results/df_driver_result_' + str(subsession_id) + '_' + result_type + '_' + car_class + '.csv'
    df_driver_result.to_csv(df_driver_result_file,index=False)
    car_class = df_driver_result['car_class_short_name'] == car_class
    df_driver_result_class = df_driver_result[car_class]
    return df_driver_result_class
      

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


#def get_session_lap_data(idc: irDataClient , subsession_id: int, simsession_number: int, driver_result: json) -> json:
#    driver_count = len(driver_result)
#    df = pd.DataFrame()
#    with tqdm(total=driver_count) as pbar:
#        for dr in driver_result:
#            df_lap_data = get_lap_data(idc, subsession_id, simsession_number, dr)
#            frames = [df, df_lap_data]
#            df = pd.concat(frames)
#            pbar.update(1)
#    return df

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

#def get_valid_laps(df_lap_data: pd, cust_id: int) -> pd:
#    driver_laps = df_lap_data['cust_id'] == cust_id
#    df_driver_laps = df_lap_data[driver_laps]
#    lap_invalidation_events = ['pitted','invalid']
#    #for invalidation_event in lap_invalidation_events:
#    valid_laps = ~np.isin(df_driver_laps['lap_events'], lap_invalidation_events)
#    #valid_laps = df_driver_laps['lap_events'] #.isin(lap_invalidation_events) #and ~df_lap_data['lap_time'] == 0
#    df_valid_laps = df_driver_laps[valid_laps]
#    return df_valid_laps

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

def get_lap_avg(df_lap_data: pd, cust_id: int) -> int:
    driver_laps = df_lap_data['cust_id'] == cust_id
    df_driver_laps = df_lap_data[driver_laps]
    avg_lap_time = df_driver_laps['lap_time'].mean()
    return avg_lap_time

def get_laps_total(df_lap_data: pd, cust_id: int) -> int:
    driver_laps = df_lap_data['cust_id'] == cust_id
    df_driver_laps = df_lap_data[driver_laps]
    laps_total = len(df_driver_laps)
    return laps_total

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

def get_session_drivers_unique(df_result: pd):
    unique_drivers = df_result["cust_id"].unique()
    return unique_drivers

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
        driver['average_lap_valid'] = lap_avg
        if lap_avg != 0:
            driver['speed_valid'] = (track_length / lap_avg * 3600)
        if lap_avg == 0:
            driver['speed_valid'] = 0
        driver['time_valid'] = lap_avg * laps_total
    return driver_result

def process_session_result(username, password, subsession_id, session_type = None, car_class = None):
    idc = irDataClient(username=username, password=password)
    # get results from a session server
    result = idc.result(subsession_id=subsession_id)
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
            df_result['avg_lap'] = (df_result['average_lap'] / 10000)
            df_result['time'] = (df_result['avg_lap'] * df_result['laps_complete'])
            df_result['speed'] = (track_length / (df_result['average_lap'] / 10000)) * 3600
            df_result['total_session_time'] = total_session_time
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


def process_session_result_old(username, password, subsession_id):
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
            print(tabulate(df_driver_result[['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','laps_complete','avg_lap_valid','laps_complete_valid','speed','time','time_valid','percentage','total_session_time']], headers = 'keys', tablefmt = 'psql'))

            #csv_name = 'session_' + session_id + '_' + session_result['simsession_type_name'] + 'csv'

            #from pathlib import Path  
            #filepath = Path('folder/subfolder/out.csv')  
            #filepath.parent.mkdir(parents=True, exist_ok=True)
            df_driver_result.to_csv(csv_name,index=False,columns=['team_id','team_display_name','cust_id','display_name','oldi_rating','avg_lap','laps_complete','avg_lap_valid','laps_complete_valid','speed','time','time_valid','percentage','total_session_time'])
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

 