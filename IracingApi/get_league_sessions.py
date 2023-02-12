import pwinput
from iracingdataapi.client import irDataClient
from tabulate import tabulate
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme
import pandas as pd
import re

league_id = 5606
season_id = 83043

"""
session_id': 186249222,
'private_session_id': 2993437,
'session_id': 186249222,
'qualify_length': 60, 'race_laps': 0, 'race_length': 600,
track_name': 'Road America', 'config_name': 'Full Course'
'time_limit': 300
"""

print('Going into interactive mode....')
username = input("Enter username: ")
password = pwinput.pwinput(prompt='Enter password: ')
csv_name = 'league_sessions.csv'

idc = irDataClient(username=username, password=password)
def get_league_sessions(idc: irDataClient, league_id: int, season_id: int, type = 'race', print = True) -> pd:
    #try:
        seasons = idc.league_seasons(league_id)  
        df_seasons = pd.DataFrame.from_dict(seasons['seasons'])
        league_season_sessions = idc.league_season_sessions(league_id, season_id)
        df_sessions = pd.DataFrame.from_dict(league_season_sessions['sessions'])
        #races = df_sessions['race_length'] != 0
        #df_races = df_sessions[races]
        #print(tabulate(df_sessions[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
    #except RuntimeError as e:
        #if "Site Maintenance" in e:
        #if re.match(r"*Site Maintenance*", e):
            #print (e.args[0]) 

        #raise #ImportError(e)
        #RuntimeError: {'error': 'Site Maintenance', 'note': 'The site is currently undergoing maintenance. Please try your request later.'} 

def get_session_results(race_result: json, type: str):
    new_list = []
    for session_results in race_result['session_results']:
        if session_results['simsession_type_name'] == type:
            new_list.append(session_results)
    return new_list

df_sessions = get_league_sessions(idc,league_id,season_id)
print(tabulate(df_sessions[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))
df_sessions.to_csv(csv_name,index=False,columns=['session_id','time_limit','qualify_length','race_length'])  