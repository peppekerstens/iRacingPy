import argparse, sys

parser=argparse.ArgumentParser()

parser.add_argument("--bar", help="Do the bar option")
parser.add_argument("--foo", help="Foo the program")

args=parser.parse_args()

print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
print(f"Dict format: {vars(args)}")



def get_team(df_result: pd) -> dict:
    teams = df_result['team_id'].unique()
    return teams

def get_team_drivers(df_result: pd, team_id: int) -> pd:
    team_drivers = df_result['team_id'] == team_id
    df_team_drivers = df_result[team_drivers]
    return df_team_drivers

def get_team_total_session_time(df_team_drivers: pd) -> int:
    total = df_team_drivers['time_valid'].sum()
    return total

"""
def get_total_session_time(result: json, ): #assumes all contenders (teams of drivers) within a session (race, qually etc), eg all memebers under ['session_results']
    total_time = 0
    for contender in result:
        if contender['finish_position'] == 0:
            contender_time = contender['laps_complete'] * contender['average_lap']
            total_time += contender_time
    total_time = total_time / 10000
    return total_time

def get_team_driver_results(result: json, ):
    new_list = []
    for team_results in result:
        team_display_name = team_results["display_name"]
        #if  session_results['simsession_type_name'] == type:
        for driver in team_results['driver_results']:
            driver['team_display_name'] = team_display_name
            new_list.append(driver)
    return new_list
"""
