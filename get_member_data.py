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

def get_pec_driver_qualification(iRating: int) -> str:
    if iRating >= 2500:
        return 'lmdh'
    elif iRating >= 2000:
        return 'lmp2'
    elif iRating >= 1500:
        return 'gt3'
    else:
        return None 

def get_pec_driver_classification(iRating: int) -> str:
    if iRating > 3500:
        return 'Not allowed'
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

def get_pec_driver_information(idc: irDataClient, df_member_data: pd) -> pd:
    member_count = len(df_member_data)
    df_pec_driver_info = pd.DataFrame(columns=['cust_id','display_name','latest_iRating', 'driver_classification','driver_qualification'])
    print('Getting driver chart data')
    print()
    #df_pec_driver_info = None
    with tqdm(total=member_count) as pbar:
        for index, df_row in df_member_data.iterrows():
            cust_id = df_row['cust_id'] #no need to do something like df_row.iloc[0]['cust_id'] as it already is a single row
            try:
                df_member_chart_data = get_member_chart_data(idc,cust_id)
                display_name = df_row['display_name']
                latest_iRating = get_member_latest_iRating(df_member_chart_data)
                driver_qualification = get_pec_driver_qualification(latest_iRating)
                driver_classification = get_pec_driver_classification(latest_iRating)
                df_pec_driver_info.loc[index] = [cust_id,display_name,latest_iRating,driver_classification,driver_qualification]
            except:
                print(f"WARNING: Could not find info for cust_id: {cust_id}")
            pbar.update(1)
    print()
    return df_pec_driver_info

def get_member_chart_data(idc: irDataClient, custid: int) -> pd:
    member_chart_data = idc.member_chart_data(cust_id=custid)
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
    if len(sys.argv) == 5:
        username = sys.argv[1] #first cmdline arg is acnt name
        password = sys.argv[2] #second cmdline arg is pwd
        cust_id_csv = sys.argv[3] #third cmdline arg is csv with one table cust_ids (iRacing id)
        csv_name = sys.argv[3] #csv file to save results

    else:
        #raise BaseException('bla')  #does not work; processing is stopped see: https://docs.python.org/3/library/exceptions.html#Exception
        #print('Error: to few arguments!')
        #print('Usage: py get_session_data.py [username] [password] [session_id]')
        print('Going into interactive mode....')
        username = input("Enter username: ")
        #password = getpass.getpass('Enter password:') # hard in practise, does not show any input hint
        password = pwinput.pwinput(prompt='Enter password: ')
        cust_id_csv = input("Enter Customer ID CSV (press <enter> for league_roster.csv): ")
        if cust_id_csv == '':
            cust_id_csv = 'league_roster.csv'
            #cust_id_csv = 'iracingid.csv'
        csv_name = input("Enter CSV name for result (press <enter> for member_data.csv): ")
        if csv_name == '':
            csv_name = 'member_data.csv'

    idc = irDataClient(username=username, password=password)

    #pd.Series(states_df.name.values).to_dict()
    #https://cmdlinetips.com/2021/04/convert-two-column-values-from-pandas-dataframe-to-a-dictionary/
    #https://sparkbyexamples.com/pandas/convert-pandas-dataframe-to-series/#:~:text=Convert%20DataFrame%20Column%20to%20Series,selected%20column%20as%20a%20Series.
    #member_data = get_member_data(idc, cust_id) -> cust_id should be series of type {'12233','112333'}

    df_league_roster = pd.read_csv(cust_id_csv)
    #csvdata = import_csv(cust_id_csv)
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
    df_pec_driver_info = get_pec_driver_information(idc,df_member_data)

    #print(f"{custid[0]},{display_name2},{latest_iRating},{driver_classification},{driver_qualification}")
    print(tabulate(df_pec_driver_info[['cust_id','display_name','latest_iRating', 'driver_classification','driver_qualification']], headers = 'keys', tablefmt = 'psql'))

    df_pec_driver_info.to_csv(csv_name,index=False,columns=['cust_id','display_name','latest_iRating', 'driver_classification','driver_qualification'])  
