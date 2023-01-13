from  iracingdataapi.client import irDataClient
import json
#https://stackoverflow.com/questions/2733813/iterating-through-a-json-object

#could (should!) improve with List Comprehensions or Vectorization
#https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
def get_session_results(race_result: json, type: str):
    new_list = []
    for session_results in race_result['session_results']:
        if  session_results['simsession_type_name'] == type:
            new_list.append(session_results)
    return new_list

def get_driver_results(race_result: json):
    new_list = []
    for driver_results in race_result:
        #if  session_results['simsession_type_name'] == type:
        for driver in driver_results['driver_results']:
            new_list.append(driver)
    return new_list


#def get_total_laps(race_result: json, team_id: int):
#    result = 0
#    for item in race_result:
#        if  item['team_id'] == team_id:
#            result += item['laps_complete']
#    return result

import sys
import csv
import pandas as pd 
import numpy as np

def get_total_laps(result: pd, team_id: int):
    team_match = result['team_id'] == team_id
    team_result = result[team_match]
    return team_result['laps_complete'].sum()

if __name__ == '__main__':
   
    if len(sys.argv) < 4:
     print('Usage: py get_memberdata.py [username] [password] [session_id]')
     sys.exit()

    username = sys.argv[1] #first cmdline arg is acnt name
    password = sys.argv[2] #second cmdline arg is pwd
    session_id = sys.argv[3] #third cmdline arg is pwd
    
    idc = irDataClient(username=username, password=password)

    session_id = 43720351 #BMW 12.0 Challenge 
    session_id = 58362796 #PEC S2 5th race fuji
    # get results from a session server
    session_result = idc.result(subsession_id=session_id)
    team_race = False
    #if session_result['min_team_drivers'] == 1 and session_result['max_team_drivers'] == 1: team_race = False
    if session_result['min_team_drivers'] > 1 and session_result['max_team_drivers'] > 1: team_race = True

    track = session_result['track']
    #get info in all tracks present in iRacing. Needed for track length, which is needed to calculate avg driver speed.
    all_tracks = idc.tracks
    df_all_tracks = pd.json_normalize(all_tracks)
    #current_track = all_tracks['track_id'] == track['track_id']
    current_track = df_all_tracks['track_id'] == track['track_id']
    #current_track_detail = all_tracks[current_track]
    current_track_detail = df_all_tracks[current_track]
    current_track_detail[['track_name','config_name','track_config_length']]
    track_length = current_track_detail['track_config_length'] * 1.609344  #track_config_length is provided in miles

    #if team_race:
    race_result = get_session_results(session_result, 'Race')
    driver_result = get_driver_results(race_result[0]['results'])
    df_race_result = pd.json_normalize(race_result[0]['results'])
    df_driver_result = pd.json_normalize(driver_result)

    #some code to detect by class
    #https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
    #
    #Get the total time driven per team, to calculate percentage per driver later
    df_race_result['avg_lap'] = (df_race_result['average_lap'] / 10000)
    df_race_result['time'] = (df_race_result['avg_lap'] * df_race_result['laps_complete'])
    df_race_result[['team_id','display_name','avg_lap','laps_complete','time']] 
    #Get the team results per class - ToDo
    car_class = df_race_result['car_class_short_name'] == "GT3 Class"
    df_race_result_class = df_race_result[car_class]

    #Get the speed an total time driven per driver of each team
    #average_lap = 940294 
    #average_lap = 94.0294 => sec
    df_driver_result['avg_lap'] = (df_driver_result['average_lap'] / 10000)
    df_driver_result['speed'] = (track_length.iloc[0] / df_driver_result['avg_lap'] * 3600)
    df_driver_result['time'] = (df_driver_result['avg_lap'] * df_driver_result['laps_complete'])
    #https://datatofish.com/compare-values-dataframes/
    #not there yet....
    #df_driver_result['percentage'] = np.where(df_race_result['team_id'] == df_driver_result['team_id'], 0, df_driver_result['laps_complete'] / df_race_result['laps_complete'])
    #throws ValueError: Can only compare identically-labeled Series objects
    
    #so the long way round
    df_driver_result['percentage'] = round(df_driver_result['laps_complete'] / get_total_laps(df_driver_result, df_driver_result['team_id'].iloc[0]) * 100,0)
    #df_driver_result[['team_id','cust_id','display_name', 'finish_position','finish_position_in_class','average_lap','best_lap_time','laps_complete','car_class_name']]
    df_driver_result[['team_id','cust_id','display_name', 'avg_lap','laps_complete','speed','time', 'percentage']] 