# do we really need this?
# the race result action (get_session_data.py) seem to contain following info for attending drivers;
# 'finish_position': 15, 'finish_position_in_class': 5,
# 'old_cpi': 17.439022,'oldi_rating': 5655, 'old_ttrating': 1384,
# 'new_cpi': 17.439022, 'newi_rating': 5655, 'new_ttrating': 1384,
# the new parts are not updated when results are not an offcial
# .... as well as team info
# 'team_id': -286631, 'display_name': 'PGZ Motorsport #119', 'finish_position': 38,

import sys
import csv
from iracingdataapi.client import irDataClient
import pandas as pd 
import pwinput
from tabulate import tabulate
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme
import json
import argparse

def is_allowed_gtp(iRating: int) -> bool:
    if iRating >= 2750:
        return True
    else:
        return False 

def is_allowed_gt3(iRating: int) -> bool:
    if iRating >= 1700:
        return True
    else:
        return False 

def is_allowed_lmp2(iRating: int) -> bool:
    if iRating >= 2000:
        return True
    else:
        return False
           
def get_driver_qualification(iRating: int) -> str:
    if iRating >= 2750:
        return 'gtp'
    #elif iRating >= 2000:
    #    return 'lmp2'
    elif iRating >= 1700:
        return 'gt3'
    else:
        return None 

def get_gt3_AM_classification(iRating: int) -> str:
    if iRating > 3750:
        return 'No'
    elif iRating >= 2750:
        return 'Gold'
    else:
        return 'Silver'

def get_member_latest_iRating(df_member_chart_data: pd) -> int:
    #df_latest = df_member_chart_data.iloc[-1] #get the latest iRating (last row)
    #last_value = df_latest['value'] 
    if 'value' in df_member_chart_data.columns:
        last_value = df_member_chart_data['value'].iat[-1]
    else:
        last_value = 0
    return last_value 

def get_driver_information(idc: irDataClient, df_member_data: pd) -> pd:
    member_count = len(df_member_data)
    df_pec_driver_info = pd.DataFrame(columns=['cust_id','display_name','latest_iRating', 'gtp','lmp2','gt3pro','gt3am'])
    print('Getting driver chart data')
    print()
    #df_pec_driver_info = None
    with tqdm(total=member_count) as pbar:
        for index, df_row in df_member_data.iterrows():
            cust_id = df_row['cust_id'] #no need to do something like df_row.iloc[0]['cust_id'] as it already is a single row
            try:
                #df_member_chart_data = get_member_chart_data(idc,cust_id)
                #display_name = df_row['display_name']
                #latest_iRating = get_member_latest_iRating(df_member_chart_data)
                display_name = df_row['display_name']
                latest_iRating = get_member_irating(idc,cust_id)
                gtp = is_allowed_gtp(latest_iRating)
                lmp2 = is_allowed_lmp2(latest_iRating)
                gt3 = is_allowed_gt3(latest_iRating)
                gt3_class = get_gt3_AM_classification(latest_iRating)
                df_pec_driver_info.loc[index] = [cust_id,display_name,latest_iRating,gtp,lmp2,gt3,gt3_class]
            except:
                print(f"WARNING: Could not find info for cust_id: {cust_id}")
            pbar.update(1)
    print()
    return df_pec_driver_info

def get_member_chart_data(idc: irDataClient, custid: int) -> pd:
    member_chart_data = idc.member_chart_data(cust_id=custid, category_id=5)
    df_member_chart_data = pd.DataFrame.from_dict(member_chart_data['data'])
    return df_member_chart_data


def get_member_irating(idc: irDataClient, cust_id: int, category_id=5) -> int:
    member_profile = idc.member_profile(cust_id=cust_id)
    for license_history in member_profile['license_history']:
        if  license_history['category_id'] == category_id:
            return license_history['irating']
    return None

    df_member_chart_data = pd.DataFrame.from_dict(member_chart_data['data'])
    return df_member_chart_data

"""
def get_member_data(idc: irDataClient, df_league_roster:pd) -> pd:
    custid = dict(df_league_roster['cust_id'])
    custid_list = list(custid.values())
    custid_json = json.dumps(custid_list)
    member_data = idc.member(cust_id=custid_list)
    df_member_data = pd.DataFrame.from_dict(member_data['members'])
    return df_member_data
"""

def get_member_data(idc: irDataClient, cust_id) -> pd:
    member_data = None
    try:
        member_data = idc.member(cust_id=cust_id)
        #df_member_data = pd.DataFrame.from_dict(member_data['members'])
        #return df_member_data
    except:
        return member_data
    return member_data 

def import_csv(path: str) -> dict:
    file = open(path, "r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return data

if __name__ == '__main__':
    #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults
    parser=argparse.ArgumentParser()
    parser.add_argument("--username", help="", default='', type=str)
    parser.add_argument("--password", help="", default='', type=str)
    parser.add_argument("--league_id", help="", default=5606, type=int) #PEC league
    parser.add_argument("--roster", help="", type=str)#default='league_roster.csv', 
    parser.add_argument("--data", help="", default='member_data.csv', type=str)
    #parser.add_argument("--csv", help="", default=True, type=bool)
    #parser.add_argument("--json", help="", default=True, type=bool)

    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")
    
    username = args.username
    password = args.password
    roster = args.roster 
    data = args.data
    league_id = args.league_id
    #jsondump = args.json
    #csvdump = args.csv

    if username == "":
        username = input("Enter username: ")

    if password == "":
        password = pwinput.pwinput(prompt='Enter password: ')

    idc = irDataClient(username=username, password=password)

    # Get generic league information
    if roster == None:
        league_information = idc.league_get(league_id)
        df_league_roster = pd.json_normalize(league_information['roster'])
    else:
        df_league_roster = pd.read_csv(roster)
    
    #
    #try to make following code simpler?
    #check if one call can be made with all cust_id at once to idc.member instead of one by one
    #
    df_league_roster_count = len(df_league_roster)
    cust_id_array = df_league_roster['cust_id'].values
    #should be of type {}
    members = []  
    #new_list = []
    with tqdm(total=df_league_roster_count) as pbar:
        for cust_id in cust_id_array:
        #for index, df_row in df_league_roster.iterrows():
            #cust_id = df_row['cust_id']
            member_data = get_member_data(idc, cust_id)
            if member_data != None:
                members += member_data['members']
                #new_list.append(member_data['members'])
            pbar.update(1)
    #df_member_data = get_member_data(idc,df_league_roster)
    #df_member_data = get_member_data(idc, csvdata)
    df_member_data = pd.DataFrame.from_dict(members)
    df_pec_driver_info = get_driver_information(idc,df_member_data)

    #print(f"{custid[0]},{display_name2},{latest_iRating},{driver_classification},{driver_qualification}")
    print(tabulate(df_pec_driver_info, headers = 'keys', tablefmt = 'psql'))

    #df_pec_driver_info.to_csv(csv_name,index=False,columns=['cust_id','display_name','latest_iRating', 'driver_classification','driver_qualification'])
    df_pec_driver_info.to_csv(data,index=False)   

