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

def get_all_tracks(idc: irDataClient) -> pd:
    #get info in all tracks present in iRacing. Needed for track length, which is needed to calculate avg driver speed.
    all_tracks = idc.tracks
    df_all_tracks = pd.json_normalize(all_tracks)
    #add the lentgh in KM to all records. If we do this after filtering the track we want, we get an 'bad practise' error
    df_all_tracks['track_config_length_km'] = df_all_tracks['track_config_length'] * 1.609344  #track_config_length is provided in miles
    return df_all_tracks

def get_track_detail(df_all_tracks: pd, track_id) -> pd:
    #gets information from a sepcific track
    current_track = df_all_tracks['track_id'] == track_id
    df_current_track_detail = df_all_tracks[current_track]
    return df_current_track_detail

def convert_result(result: json) -> pd:
    

def get_lap_data(idc: irDataClient, result: pd) -> pd:
    cust_id = driver_result['cust_id']
    team_id = driver_result['team_id']
    lap_data = idc.result_lap_data(subsession_id=session_id,simsession_number=0, cust_id=cust_id, team_id=team_id)
    df_lap_data = pd.json_normalize(new_list)
    return df_lap_data

def process_session_result(idc: irDataClient, df_all_tracks, subsession_id):
    print('Processing...')
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
    
    idc = irDataClient(username=username, password=password)

    # get results from a session server
    result = idc.result(subsession_id=subsession_id)
    track = result['track']
    # get track detail information (track length)
    df_all_tracks = get_all_tracks(idc)
    df_track_detail = get_track_detail(df_all_tracks, track['track_id'])
    print()
    print('Track information')
    print()
    print(tabulate(df_track_detail[['track_name','config_name','track_config_length_km']], headers = 'keys', tablefmt = 'psql'))
    track_length = df_track_detail['track_config_length_km'].iloc[-1]

    get_lap_data

    process_session_result(idc,df_all_tracks, subsession_id)