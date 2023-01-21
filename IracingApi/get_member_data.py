
from  iracingdataapi.client import irDataClient

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

import numpy
import pandas as pd 
import pwinput
from tabulate import tabulate

def get_member_irating(idc: irDataClient, custid: int):
    iracing_member_data =  get_iracing_member_data(idc, custid)
    member_data = iracing_member_data['member']

    #get the last registered iRating from member
    member_chart_data = iracing_member_data['chart']
    mcd = pd.DataFrame.from_dict(member_chart_data['data'])

    latest_iRating = mcd.iloc[-1]['value']
    
    if latest_iRating > 3750:
        driver_classification = 'Gold'
    else:
        driver_classification = 'Silver'
    
    if latest_iRating > 2500:
        driver_qualification = 'lmdh approved'
    elif latest_iRating > 2000:
        driver_qualification = 'lmp2 approved'
    elif latest_iRating > 1500:
        driver_qualification = 'gt3 approved'
    else:
        driver_qualification = 'not qualified' 

    display_name = member_data['members']
    display_name2 = display_name[0]['display_name']
    #table = [['iRacing Customer ID', 'Driver Name', 'iRating', 'Driver Classifictaion'], 
                #custid[0], display_name2, latest_iRating, driver_classification]
    #print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
    print(f"{custid[0]},{display_name2},{latest_iRating},{driver_classification},{driver_qualification}")
    #print(tabulate([['custid[0]','display_name2','latest_iRating', 'driver_classification']], headers = 'keys', tablefmt = 'psql'))

import sys
import csv

if __name__ == '__main__':
   
    if len(sys.argv) == 4:
        username = sys.argv[1] #first cmdline arg is acnt name
        password = sys.argv[2] #second cmdline arg is pwd
        cust_id_csv = sys.argv[3] #third cmdline arg is csv with one table cust_ids (iRacing id)

    else:
        #raise BaseException('bla')  #does not work; processing is stopped see: https://docs.python.org/3/library/exceptions.html#Exception
        #print('Error: to few arguments!')
        #print('Usage: py get_session_data.py [username] [password] [session_id]')
        print('Going into interactive mode....')
        username = input("Enter username: ")
        #password = getpass.getpass('Enter password:') # hard in practise, does not show any input hint
        password = pwinput.pwinput(prompt='Enter password: ')
        cust_id_csv = input("Enter Customer ID CSV: ")
    
    idc = irDataClient(username=username, password=password)

    with open(cust_id_csv, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in csvreader:
            get_member_irating(idc,row)

    #for iRacing_cust_id in cust_id:
    #    get_member_irating(idc,iRacing_cust_id)

