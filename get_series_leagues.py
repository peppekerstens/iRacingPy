import sys
import csv
from iracingdataapi.client import irDataClient
import pandas as pd 
import pwinput
from tabulate import tabulate
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme
import json
import argparse

def write_json(uri, payload):
    with open(uri, "w") as write_file:
        json.dump(payload, write_file, indent=4, sort_keys=True)

def get_series_result(series_result: json, event_type = 'race') -> json:
    new_list = []
    for result in series_result:
        if result['event_type_name'] == event_type:
            new_list.append(series_result)
    return new_list

"""def process_series_result(series_result: json):
    for result in series_result:
        result["season_quarter"]
        result["season_year"]
        result["series_id"]
        result["series_name"]
"""

if __name__ == '__main__':
        #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults



    parser=argparse.ArgumentParser()

    #parser.add_argument("--member_data", help="location of member data file. if only name is supplied, script location is used",  default='./league_data/member_data.csv', type=str)
    #parser.add_argument("--driver_indicator", help="location of the driver indicator file. if only name is supplied, script location is used",  default='./indicators/pec_s3_driver_indicator.csv', type=str)
    #parser.add_argument("--session", help="location of the session file to process. if only name is supplied, script location is used")

    parser.add_argument("--username", help="",  default='', type=str)
    parser.add_argument("--password", help="",  default='', type=str)
    #parser.add_argument("--sessionid", help="")
    #parser.add_argument("--type", help="")
    
    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")
    
    username = args.username
    password = args.password
    #subsession_id = args.sessionid
    #session_type = args.type

    if username == "":
        username = input("Enter username: ")

    if password == "":
        password = pwinput.pwinput(prompt='Enter password: ')

    #if subsession_id == "":
    #    subsession_id = input("Enter subsession_id: ")
    
    #if session_type == "":
    #    session_type = None

    idc = irDataClient(username=username, password=password)
    """
        series = idc.get_series()
        series_file = './series/series.json'
        write_json(series_file, series)

        season_id = 4316 (this season)
        results = idc.result_search_series(2023,2,None,None,None,None,None,419)
        results_file = './results/series_419_results.json'
        write_json(results_file, results)
    """

    """
    result = idc.result(60348749)
    result_file = './results/series_447_s2_60348749.json'
    write_json(result_file, result)
    """

    #season_id = 4316 (this season)
    results = idc.result_search_series(2023,3,None,None,None,None,None,419)
    results_file = './results/series_419_s3_results.json'
    write_json(results_file, results)
    
    """
    drivers = idc.lookup_drivers("c")
    drivers_file = './drivers/drivers_c.json'
    write_json(drivers_file, drivers)
    """

    #my_league_directory = idc.league_directory()
    #league_directory_file = './league_directory/league_directory.json'
    #write_json(league_directory_file, my_league_directory)