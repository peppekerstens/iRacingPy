import sys
import os
import csv
import pandas as pd 
from tabulate import tabulate
import glob

member_data_file= 'member_data.csv' #up-to-date info on members irating and validation (only needed for first race)
#cust_id,display_name,latest_iRating,driver_classification,driver_qualification
driver_indicator_file = 'pec_s3_driver_indicator.csv' #server both as reference data set from previous race(s) as well as file to save latest status to after processing
latest_session_file = None #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv

"""
#(generic) functions
def import_csv(path: str) -> dict:
    try:
        file = open(path, "r")
        data = list(csv.reader(file, delimiter=","))
        file.close()
    except:
        data = None
    return data
"""

# get previous indicator
# must either be result of previous race -or if first race- result from iRating analysis
try:
    df_indicator = pd.read_csv(driver_indicator_file)
except:
    #scenario first race - REWRITE: SHOULD ALWAYS LOAD TO ADD DRIVERS!!!! CALL IT DF_MEMBERS /DF_REF
    df_indicator = pd.DataFrame(columns=['cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification'])
    #add values from the member_data file as first reference
    #member_data = import_csv(member_data_file)
    df_member_data = pd.read_csv(member_data_file)
    for index, df_row in df_member_data.iterrows():
        classification = df_row['driver_classification']
        #print(df_row['driver_classification'])
        if df_row['driver_classification'] == 'Not allowed':
            #print(df_row['driver_classification'])
            classification = 'Gold'
        #else:
        #    classification = df_row['driver_classification']
        #df_indicator.loc[index] = [df_row['cust_id'] ,df_row['display_name'],0,classification,0,0,0,'None']
        df_indicator.loc[index] = [df_row['cust_id'] ,df_row['display_name'],0,classification,0,0,0,classification]

print(tabulate(df_indicator, headers = 'keys', tablefmt = 'psql'))

# get result from current race
if latest_session_file == None:
    sessionsFilenamesList = glob.glob('session_*.csv')
    latest_session_file = max(sessionsFilenamesList, key=os.path.getmtime)
    answer = None
    #while answer != "y" or answer != "n":
    while answer != "y":
        answer = input(f"Found {latest_session_file}, use that file and continue? y/n ")
        print (answer)

if answer == 'n':
    print('Error: no valid session file provided. please re-run and provide valid file!')
    quit() #https://www.scaler.com/topics/exit-in-python/

try:
    df_latest_session = pd.read_csv(latest_session_file)
except:
    print('Error: session file {latest_session_file} not found! Please re-run and provide valid file!')
    quit()

print(tabulate(df_latest_session, headers = 'keys', tablefmt = 'psql'))

#move the new_classification to old_classification
df_indicator['old_classification'] = df_indicator['new_classification']
#

#build intermediate dataframe based on current results
df_pec_driver_info = pd.DataFrame(columns=['cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification'])
for index, df_row in df_latest_session.iterrows():
    driver_indicator = df_indicator['cust_id'] == df_row['cust_id'] 
    df_indicator_driver = df_indicator[driver_indicator]
    if df_indicator_driver.empty:
        print(f"WARNING: could not find indicator information for driver {df_row['display_name']} ({df_row['cust_id']}) skipping!")
    else:
        #print(tabulate(df_indicator_driver, headers = 'keys', tablefmt = 'psql'))
        old_classification = df_indicator_driver.iloc[0]['old_classification']
        cust_id = df_row['cust_id'] 
        display_name = df_row['display_name']
        percentage = df_row['percentage']
        new_classification = 'None'
        race_count = df_indicator_driver.iloc[0]['race_count'] + 1 # https://stackoverflow.com/questions/16729574/how-can-i-get-a-value-from-a-cell-of-a-dataframe
        total_time = df_indicator_driver.iloc[0]['total_time'] + df_row['time']
        avg_speed = (df_indicator_driver.iloc[0]['total_time'] * df_indicator_driver.iloc[0]['avg_speed'] + df_row['time'] * df_row['speed']) / total_time
        df_pec_driver_info.loc[index] = [cust_id,display_name,race_count,old_classification,total_time,avg_speed,percentage,new_classification]

#print(df_pec_driver_info['avg_speed'])
print(tabulate(df_pec_driver_info, headers = 'keys', tablefmt = 'psql'))

df_new_indicator = pd.DataFrame(columns=['cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification'])
#how large is is the deadzone?
silver_deadzone_speed = 0
gold_deadzone_speed = 0
df_pec_driver_info_sorted = df_pec_driver_info.sort_values(by='avg_speed', ascending=False)
total_drivers = len(df_pec_driver_info_sorted)
gold_drivers = df_pec_driver_info_sorted['old_classification'] == 'Gold'
df_indicator_gold_drivers = df_pec_driver_info_sorted[gold_drivers]
gold_driver_count = len(df_indicator_gold_drivers)
silver_driver_count = total_drivers - gold_driver_count
gold_driver_deadzone = round(gold_driver_count * 0.3)
silver_driver_deadzone = round(silver_driver_count * 0.3)
if silver_driver_deadzone > 0 and gold_driver_deadzone >0:
    silver_deadzone_limit = gold_driver_count + silver_driver_deadzone
    gold_deadzone_limit = gold_driver_count - gold_driver_deadzone
    silver_deadzone_speed = df_pec_driver_info.iloc[silver_deadzone_limit]['avg_speed']
    gold_deadzone_speed = df_pec_driver_info.iloc[gold_deadzone_limit]['avg_speed']
    #review created list for new_classification
    for index, df_row in df_pec_driver_info_sorted.iterrows():
        if df_row['avg_speed'] > gold_deadzone_speed:
            new_classification = 'Gold'
        if df_row['avg_speed'] < silver_deadzone_speed:
            new_classification = 'Silver'
        if df_row['avg_speed'] <= gold_deadzone_speed and df_row['avg_speed'] >= silver_deadzone_speed:
            new_classification  = df_row['old_classification']
        if new_classification == 'Gold':
            driver_indicator = df_indicator['cust_id'] == df_row['cust_id'] 
            df_indicator_driver = df_indicator[driver_indicator]
            percentage = (df_indicator_driver.iloc[0]['race_count'] * df_indicator_driver.iloc[0]['percentage'] + df_row['percentage']) / df_row['race_count']
        else:
            percentage =  df_indicator_driver['percentage']
        df_new_indicator.loc[index] = [df_row['cust_id'] ,df_row['display_name'],df_row['race_count'],df_row['old_classification'],df_row['total_time'],df_row['avg_speed'],percentage,new_classification]
else:
    print(f"WARNING: detected deadzone too small to use!")
    #synthesise df_new_indicator

print(tabulate(df_new_indicator[['cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification']], headers = 'keys', tablefmt = 'psql'))

df_new_indicator.to_csv(driver_indicator_file,index=False)
