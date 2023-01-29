
import sys
import csv
from iracingdataapi.client import irDataClient
import pandas as pd 
import pwinput
from tabulate import tabulate
from tqdm import tqdm #https://github.com/tqdm/tqdm/#readme

"""
def get_iracing_member_data(idc: irDataClient, custid: int):
    # get generic member information
    member_data = idc.member(cust_id=custid)

    # get generic member information
    member_chart_data = idc.member_chart_data(cust_id=custid)

    # get the summary data of a member
    member_summary = idc.stats_member_summary(cust_id=custid)

    # get latest race results of a member
    member_recent_races = idc.stats_member_recent_races(cust_id=custid)

    return {
        "member": member_data ,
        "summary": member_summary ,
        "chart": member_chart_data ,
        "recent": member_recent_races
    }
"""

def get_pec_driver_qualification(iRating: int) -> str:
    if iRating >= 2500:
        return 'lmdh'
    elif iRating >= 2200:
        return 'lmp2'
    elif iRating >= 1500:
        return 'gt3'
    else:
        return None 

def get_pec_driver_classification(iRating: int) -> str:
    if iRating > 3750:
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
    #df_member_data['latest_iRating'] = None
    #df_member_data['driver_qualification'] = '' #just add a column with empty string
    #df_member_data['driver_classification'] = '' #just add a column with empty string
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
                #df_member_chart_data['display_name'] = df_row['display_name']
                #df_member_chart_data['driver_qualification'] = '' #just add a column with empty string
                #df_member_chart_data['driver_classification'] = '' #just add a column with empty string
                #df_latest = df_member_chart_data.iloc[-1] #get the latest iRating (last row)
                #df_member_chart_data['driver_qualification'] = get_pec_driver_qualification(df_member_chart_data['value'])
                #df_member_chart_data['driver_classification'] = get_pec_driver_classification(df_member_chart_data['value'])
                #df_pec_driver_info += df_latest
            except:
                print(f"WARNING: Could not find info for cust_id: {cust_id}")
            pbar.update(1)
    print()
    return df_pec_driver_info

def get_member_chart_data(idc: irDataClient, custid: int) -> pd:
    member_chart_data = idc.member_chart_data(cust_id=custid)
    df_member_chart_data = pd.DataFrame.from_dict(member_chart_data['data'])
    return df_member_chart_data

def get_member_data(idc: irDataClient, custid: dict) -> pd:
    member_data = idc.member(cust_id=custid)
    df_member_data = pd.DataFrame.from_dict(member_data['members'])
    return df_member_data

def import_csv(path: str) -> dict:
    file = open(path, "r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return data

"""
def get_member_irating(idc: irDataClient, custid: int) -> pd:
    iracing_member_data =  get_iracing_member_data(idc, custid)
    member_data = iracing_member_data['member']

    #get the last registered iRating from member
    member_chart_data = iracing_member_data['chart']
    mcd = pd.DataFrame.from_dict(member_chart_data['data'])
    
    latest_iRating = mcd.iloc[-1]['value']
    
    display_name = member_data['members']
    display_name2 = display_name[0]['display_name']
    #table = [['iRacing Customer ID', 'Driver Name', 'iRating', 'Driver Classifictaion'], 
                #custid[0], display_name2, latest_iRating, driver_classification]
    #print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
    print(f"{custid[0]},{display_name2},{latest_iRating},{driver_classification},{driver_qualification}")
    #print(tabulate([['custid[0]','display_name2','latest_iRating', 'driver_classification']], headers = 'keys', tablefmt = 'psql'))
"""

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
        cust_id_csv = input("Enter Customer ID CSV (press <enter> for iracingid.csv): ")
        if cust_id_csv == '':
            cust_id_csv = 'iracingid.csv'
        csv_name = input("Enter CSV name for result (press <enter> for member_data.csv): ")
        if csv_name == '':
            csv_name = 'member_data.csv'
    
    idc = irDataClient(username=username, password=password)

    csvdata = import_csv(cust_id_csv)
    df_member_data = get_member_data(idc,csvdata)
    df_pec_driver_info = get_pec_driver_information(idc,df_member_data)

    #print(f"{custid[0]},{display_name2},{latest_iRating},{driver_classification},{driver_qualification}")
    print(tabulate(df_pec_driver_info[['cust_id','display_name','latest_iRating', 'driver_classification','driver_qualification']], headers = 'keys', tablefmt = 'psql'))

    df_pec_driver_info.to_csv(csv_name,index=False,columns=['cust_id','display_name','latest_iRating', 'driver_classification','driver_qualification'])  
