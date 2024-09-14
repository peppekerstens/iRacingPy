from  iracingdataapi.client import irDataClient
import json

team_id = 147029

idc = irDataClient(username=username, password=password)

"""
    result_file = './iracing_result/iracing-result-' + str(subsession_id) + '.json'
    # save for future reference
    with open(result_file, "w") as write_file:
        json.dump(result, write_file, indent=4, sort_keys=True)
"""

def get_team_members(team: json) -> json:
    new_list = []
    for member in team['roster']:
        del member['helmet']
        member['team_id'] = team_id
        new_list.append(member)
    return new_list

def get_team_info(team: json) -> json:
    #strip unwanted keys, from https://stackoverflow.com/questions/3420122/filter-dict-to-contain-only-certain-keys
    my_keys = ['team_id','team_name','about','created']
    new_dict = {key: team[key] for key in my_keys}
    """ 
    new_dict = {
        'team_id': team['team_id'],

        'about': team['about'],
        'created': team['created'],
    }
    new_dict['team_id'] = team['team_id']

    }
    new_list['team_id'] = team['team_id']
    new_list['team_id'] = 

    for member in team['roster']:
        del member['helmet']
        
        new_list.append(member)
    """
    return new_dict

def get_team(idc, team_id) -> json:
    team = idc.team(team_id)
    return team

team = get_team(idc,team_id)
team_info = get_team_info(team)
team_members = get_team_members(team)

result_file = './teams/team_members-' + str(team_id) + '.json'
# save for future reference
with open(result_file, "w") as write_file:
    json.dump(team_members, write_file, indent=4, sort_keys=True)

result_file = './teams/team_info-' + str(team_id) + '.json'
# save for future reference
with open(result_file, "w") as write_file:
    json.dump(team_info, write_file, indent=4, sort_keys=True)

result_file = './teams/team-' + str(team_id) + '.json'
# save for future reference
with open(result_file, "w") as write_file:
    json.dump(team, write_file, indent=4, sort_keys=True)