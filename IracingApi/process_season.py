import os
import sys
import csv
import pwinput

league_sessions_file = 'league_sessions.csv'

if len(sys.argv) < 3:
    print('Going into interactive mode....')
    username = input("Enter username: ")
    password = pwinput.pwinput(prompt='Enter password: ')

def import_csv(path: str) -> dict:
    file = open(path, "r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return data

league_sessions = import_csv(league_sessions_file)
for session in league_sessions:
    print(f"Processing {session[0]}")
    session_id = session[0]
    csv_name = 'session_' + session_id + '.csv'
    mystring = "get_session_data.py " + username + " " + password + " " +  session_id + " " +  csv_name
    os.system(mystring)

