import csv
import sys
import pwinput
from tabulate import tabulate
import json
from iracingdataapi.client import irDataClient
import pandas as pd
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme

if __name__ == '__main__': 
    league_information_file = 'league_information'
    league_roster_file = 'league_roster'
    league_pending_requests_file = 'league_pending_requests'
    league_seasons_file = 'league_seasons'
    league_season_sessions_file = 'league_season_sessions'
    league_id = 5606
    season_id = 83043

    print('Going into interactive mode....')
    username = input("Enter username: ")
    password = pwinput.pwinput(prompt='Enter password: ')

    idc = irDataClient(username=username, password=password)

    # Get the list of drivers in the league
    league_information = idc.league_get(league_id)
    with open(league_information_file + ".json", "w") as write_file:
        json.dump(league_information, write_file, indent=4, sort_keys=True)

    df_league_pending_requests = pd.json_normalize(league_information['pending_requests'])
    #print(tabulate(df_league_pending_requests[['cust_id','display_name','initiated','revoked']], headers = 'keys', tablefmt = 'psql'))
    df_league_pending_requests.to_csv(league_pending_requests_file + ".csv",index=False,columns=['cust_id','display_name','initiated','revoked'])  

    df_league_roster = pd.json_normalize(league_information['roster'])
    #print(tabulate(df_league_roster[['cust_id','display_name','league_member_since','admin']], headers = 'keys', tablefmt = 'psql'))
    df_league_roster.to_csv(league_roster_file + ".csv",index=False,columns=['cust_id','display_name','league_member_since','admin'])  


    """
    session_id': 186249222,
    'private_session_id': 2993437,
    'session_id': 186249222,
    'qualify_length': 60, 'race_laps': 0, 'race_length': 600,
    track_name': 'Road America', 'config_name': 'Full Course'
    'time_limit': 300
    """

    league_seasons = idc.league_seasons(league_id)
    with open(league_seasons_file + ".json", "w") as write_file:
        json.dump(league_seasons, write_file, indent=4, sort_keys=True)
    df_league_seasons = pd.DataFrame.from_dict(league_seasons['seasons'])
    #print(tabulate(df_league_seasons[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
    df_league_seasons.to_csv(league_season_sessions_file + ".csv",index=False)  


    league_season_sessions = idc.league_season_sessions(league_id, season_id)
    with open(league_season_sessions_file + ".json", "w") as write_file:
        json.dump(league_season_sessions, write_file, indent=4, sort_keys=True)
    df_league_season_sessions = pd.DataFrame.from_dict(league_season_sessions['sessions'])
    #print(tabulate(df_league_season_sessions[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
    df_league_season_sessions.to_csv(league_season_sessions_file + ".csv",index=False,columns=['session_id','time_limit','qualify_length','race_length'])  


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




