from  iracingdataapi.client import irDataClient
import yaml
import argparse
import os

#maybe use this?
#https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5
#https://realpython.com/python-yaml/

config_file = 'iracingpy.config.yaml'

def get_config(config_file: str): #improve to path?
    try:
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        return config
    except:
        return None

def set_config(config_file: str): #improve to path?
    with open(config_file, "w") as f:
        config = yaml.dump(
            config, stream=f, default_flow_style=False, sort_keys=False
        )

def get_member_data(idc: irDataClient, cust_id):
    member_data = None
    try:
        member_data = idc.member(cust_id=cust_id)
        #df_member_data = pd.DataFrame.from_dict(member_data['members'])
        #return df_member_data
    except:
        return member_data
    return member_data 

if __name__ == '__main__': #only execute when called as script, skipped when loaded as module
    config = get_config(config_file)
    print(f"Dict format: {config['league_id']}")

    #league_information_path = config['base_path']+config['league_path']+config['league_information_file'] + ".json"

    idc = irDataClient(username=username, password=password)

    # Get the list of drivers in the league
    league_information = idc.league_get(league_id)
    league_roster = league_information['roster']
    members = [] 
    for member in league_roster:
        member_data = get_member_data(idc, member['cust_id'])
        if member_data != None:
            members += member_data['members']
    
    