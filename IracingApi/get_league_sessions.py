import pwinput
from iracingdataapi.client import irDataClient
from tabulate import tabulate
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme
import pandas as pd

league_id = 5606
season_id = 83043

print('Going into interactive mode....')
username = input("Enter username: ")
password = pwinput.pwinput(prompt='Enter password: ')

idc = irDataClient(username=username, password=password)

seasons = idc.league_seasons(league_id)

df_seasons = pd.DataFrame.from_dict(seasons['seasons'])


league_season_sessions = idc.league_season_sessions(league_id, season_id)

df_sessions = pd.DataFrame.from_dict(league_season_sessions['sessions'])

"""
session_id': 186249222,
'private_session_id': 2993437,
'session_id': 186249222,
'qualify_length': 60, 'race_laps': 0, 'race_length': 600,
track_name': 'Road America', 'config_name': 'Full Course'
'time_limit': 300
"""

print(tabulate(df_sessions[['session_id','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))

#print(tabulate(df_sessions[['session_id','track_name','config_name','time_limit','qualify_length','race_length']], headers = 'keys', tablefmt = 'psql'))