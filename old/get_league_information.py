import csv
import sys
import pwinput
from tabulate import tabulate
import json
from iracingdataapi.client import irDataClient
import pandas as pd
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme
import argparse

def dump_json(information: dict, filename: 'str') -> None:
    with open(filename + ".json", "w") as write_file:
        json.dump(information, write_file, indent=4, sort_keys=True)

def dump_csv_league_pending_requests(league_information, filename: 'str') -> None:
    df_league_pending_requests = pd.json_normalize(league_information['pending_requests'])
    #print(tabulate(df_league_pending_requests[['cust_id','display_name','initiated','revoked']], headers = 'keys', tablefmt = 'psql'))
    df_league_pending_requests.to_csv(filename + ".csv",index=False,columns=['cust_id','display_name','initiated','revoked'])  

def dump_csv_league_roster(league_information, filename: 'str') -> None:
    df_league_roster = pd.json_normalize(league_information['roster'])
    #print(tabulate(df_league_roster[['cust_id','display_name','league_member_since','admin']], headers = 'keys', tablefmt = 'psql'))
    df_league_roster.to_csv(filename + ".csv",index=False,columns=['cust_id','display_name','league_member_since','admin'])  

def dump_csv_league_seasons(league_seasons, filename: 'str') -> None:
    #df_league_seasons = pd.DataFrame.from_dict(league_seasons['seasons'])
    df_league_seasons = pd.json_normalize(league_seasons['seasons'])
    #print(tabulate(df_league_seasons[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
    df_league_seasons.to_csv(filename + ".csv",index=False) 

def dump_csv_league_seasons_sessions(league_seasons_sessions, filename: 'str') -> None:
    #df_league_seasons = pd.DataFrame.from_dict(league_seasons['seasons'])
    df_league_seasons = pd.json_normalize(league_seasons_sessions['sessions'])
    #print(tabulate(df_league_seasons[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
    df_league_seasons.to_csv(filename + ".csv",index=False)  

""""
    def extract_cust_id(data):
        cust_ids = []
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'cust_id':
                    cust_ids.append(value)
                elif isinstance(value, (dict, list)):
                    cust_ids.extend(extract_cust_id(value))
        elif isinstance(data, list):
            for item in data:
                cust_ids.extend(extract_cust_id(item))
        return cust_ids

    cust_ids = extract_cust_id(league_information)
    print("Customer IDs exported to iracingid.csv")
    with open('iracingid.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['cust_id'])
        for cust_id in cust_ids:
            writer.writerow([cust_id])
"""


if __name__ == '__main__': 
    league_information_file = 'league_information'
    league_roster_file = 'league_roster'
    league_pending_requests_file = 'league_pending_requests'
    league_seasons_file = 'league_seasons'
    league_season_sessions_file = 'league_season_sessions'

    #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults
    parser=argparse.ArgumentParser()
    parser.add_argument("--username", help="", default='', type=str)
    parser.add_argument("--password", help="", default='', type=str)
    parser.add_argument("--league_id", help="", default=5606, type=int) #PEC league
    parser.add_argument("--season_id", help="", default=110644, type=int) #season 6
    parser.add_argument("--csv", help="", default=True, type=bool)
    parser.add_argument("--json", help="", default=True, type=bool)

    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")
    
    username = args.username
    password = args.password
    league_id = args.league_id
    season_id = args.season_id
    jsondump = args.json
    csvdump = args.csv

    if username == "":
        username = input("Enter username: ")

    if password == "":
        password = pwinput.pwinput(prompt='Enter password: ')

    if league_id == "":
        league_id = input("Enter league_id: ")

    if season_id == "":
        season_id = input("Enter season_id: ")

    idc = irDataClient(username=username, password=password)

    # Get generic league information
    league_information = idc.league_get(league_id)

    #league_membership = idc.league_membership(self, include_league=False):

    #idc.league_roster(self, league_id, include_licenses=False)
    
    # Get all league seasons
    league_seasons = idc.league_seasons(league_id)

    # Get all league seasons sessions
    league_season_sessions = idc.league_season_sessions(league_id, season_id)
    

    if jsondump == True:
        dump_json(league_information, league_information_file)
        dump_json(league_seasons, league_seasons_file)
        dump_json(league_season_sessions, league_season_sessions_file)

    if csvdump == True:
        dump_csv_league_pending_requests(league_information, league_pending_requests_file)
        dump_csv_league_roster(league_information, league_roster_file)
        dump_csv_league_seasons(league_seasons, league_seasons_file)
        dump_csv_league_seasons_sessions(league_season_sessions, league_season_sessions_file)
