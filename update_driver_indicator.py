import argparse
import sys
import os
import csv
import pandas as pd 
from tabulate import tabulate
import glob

driver_indicator_columns = ['team_id','team_display_name','cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified','driven','gold_race_count','gold_total_drive_time','gold_total_sesion_time','gold_total_percentage','index','total_index','total_session_time']

def generate_member_data_driver_indicator(df_member_data: pd, cust_id: int) -> pd:
    #scenario first time driver. use downloaded member_data (which should contain classification based on iRating) as a reference
    df_indicator = pd.DataFrame(columns=driver_indicator_columns)
    driver = df_member_data['cust_id'] == cust_id
    df_driver = df_member_data[driver]
    #print(tabulate(df_driver, headers = 'keys', tablefmt = 'psql'))
    if not df_driver.empty:
        classification = df_driver.iloc[0]['driver_classification']
        #print(df_row['driver_classification'])
        if classification == 'Not allowed':
            #print(df_row['driver_classification'])
            classification = 'Gold'
        #                        ['team_id','cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified','driven','gold_race_count','gold_total_drive_time','gold_total_sesion_time','index','total_index']
        df_indicator.loc[0] = [0,'',df_driver.iloc[0]['cust_id'] ,df_driver.iloc[0]['display_name'],0,classification,0,0,0,classification,False,False,False,0,0,0,0,0,0,0]
    return df_indicator


def get_df_indicator_driver(df_indicator: pd, df_member_data: pd, cust_id: int) -> pd:
    driver_indicator = df_indicator['cust_id'] == cust_id
    df_indicator_driver = df_indicator[driver_indicator]
    if df_indicator_driver.empty:
        df_indicator_driver = generate_member_data_driver_indicator(df_member_data,cust_id)
    return df_indicator_driver


def update_driver_info(df_latest_session: pd,df_indicator: pd,df_member_data: pd) -> pd:
    #build intermediate dataframe based on current results
    df_driver_info = pd.DataFrame(columns=driver_indicator_columns)
    for index, df_row in df_latest_session.iterrows():
        cust_id = df_row['cust_id']
        df_indicator_driver = get_df_indicator_driver(df_indicator,df_member_data,cust_id)
        if not df_indicator_driver.empty:
            #print(tabulate(df_indicator_driver, headers = 'keys', tablefmt = 'psql'))
            old_classification = df_indicator_driver.iloc[0]['old_classification']
            try:
                team_id = df_row['team_id']
            except:
                team_id = None
            cust_id = df_row['cust_id']
            display_name = df_row['display_name']
            team_display_name = df_row['team_display_name']
            new_classification = df_indicator_driver.iloc[0]['new_classification']
            race_count = df_indicator_driver.iloc[0]['race_count'] + 1 # https://stackoverflow.com/questions/16729574/how-can-i-get-a-value-from-a-cell-of-a-dataframe
            avg_speed = df_row['speed_valid']
            total_time = df_row['time_valid']
            total_session_time = df_row['total_session_time']
            
            percentage = round(total_time/total_session_time * 100,0)
            #print(f"cust_id: {df_row['cust_id']}")
            #print(f"total_time: {total_time}")
            #print(f"total_session_time: {total_session_time}")
            #print(f"percentage: {percentage}")
            #total_time = round(df_indicator_driver.iloc[0]['total_time'] + df_row['time_valid'],2)
            # ['team_id','team_display_name','cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified','driven','gold_race_count','gold_total_drive_time','gold_total_sesion_time','gold_total_percentage','index','total_index','total_session_time']
            df_driver_info.loc[index] = [team_id,team_display_name,cust_id,display_name,race_count,old_classification,total_time,avg_speed,percentage,new_classification,False,False,False,0,0,0,0,0,0,total_session_time]
        if df_indicator_driver.empty:    
            print(f"WARNING: could not find indicator information for driver {df_row['display_name']} ({df_row['cust_id']}) skipping!")
    return df_driver_info

def update_driver_indicator(df_driver_info: pd, df_indicator: pd, df_member_data: pd ) -> pd:
    df_new_indicator = pd.DataFrame(columns=driver_indicator_columns)
    #how large is is the deadzone?
    silver_deadzone_speed = 0
    gold_deadzone_speed = 0
    df_driver_info_sorted = df_driver_info.sort_values(by='avg_speed', ascending=False)
    total_drivers = len(df_driver_info_sorted)
    gold_drivers = df_driver_info_sorted['old_classification'] == 'Gold'
    df_driver_info_gold_drivers = df_driver_info_sorted[gold_drivers]
    gold_driver_count = len(df_driver_info_gold_drivers)
    silver_driver_count = total_drivers - gold_driver_count
    gold_driver_deadzone = round(gold_driver_count * 0.3)
    silver_driver_deadzone = round(silver_driver_count * 0.3)
    if silver_driver_deadzone > 0 and gold_driver_deadzone > 0:
        silver_deadzone_limit = gold_driver_count + silver_driver_deadzone
        gold_deadzone_limit = gold_driver_count - gold_driver_deadzone
        silver_deadzone_speed = df_driver_info_sorted.iloc[silver_deadzone_limit]['avg_speed']
        gold_deadzone_speed = df_driver_info_sorted.iloc[gold_deadzone_limit]['avg_speed']
        #print(f"total_drivers: {total_drivers}")
        #print(f"gold_driver_count: {gold_driver_count}")
        #print(f"silver_driver_count: {silver_driver_count}")
        #print(f"silver_deadzone_limit: {silver_deadzone_limit}")
        #print(f"gold_deadzone_limit: {gold_deadzone_limit}")
        #print(f"silver_deadzone_speed: {silver_deadzone_speed}")
        #print(f"gold_deadzone_speed: {gold_deadzone_speed}")

        #review created list for new_classification
        for index, df_row in df_driver_info_sorted.iterrows():
            #get the old indicator info
            driver = df_indicator['cust_id'] == df_row['cust_id']
            df_indicator_driver = df_indicator[driver]

            if df_indicator_driver.empty:
                gold_race_count = 0
                gold_total_drive_time = 0
                gold_total_sesion_time = 0
                gold_total_percentage = 0

            if not df_indicator_driver.empty:
                gold_race_count = df_indicator_driver.iloc[0]['gold_race_count']
                gold_total_drive_time = df_indicator_driver.iloc[0]['gold_total_drive_time']
                gold_total_sesion_time = df_indicator_driver.iloc[0]['gold_total_sesion_time']
                gold_total_percentage = df_indicator_driver.iloc[0]['gold_total_percentage']

            deadzone = False
            if df_row['avg_speed'] > gold_deadzone_speed:
                new_classification = 'Gold'
            if df_row['avg_speed'] < silver_deadzone_speed:
                new_classification = 'Silver'
            if df_row['avg_speed'] <= gold_deadzone_speed and df_row['avg_speed'] >= silver_deadzone_speed:
                new_classification = df_row['old_classification']
                deadzone = True
            reclassified = False   
            if new_classification != df_row['old_classification']:
                reclassified = True
            #df_indicator_driver = get_df_indicator_driver(df_indicator,df_member_data, df_row['cust_id'])

            if new_classification == 'Gold':
                #'gold_race_count','gold_total_drive_time','gold_total_sesion_time',gold_total_percentage, 'index','total_index'
                gold_race_count += 1
                gold_total_drive_time = round(gold_total_drive_time + df_row['total_time'],2)
                gold_total_sesion_time = round(gold_total_sesion_time + df_row['total_session_time'],2)
                gold_total_percentage = round(gold_total_drive_time/gold_total_sesion_time * 100,0)
                #gold_total_time = round(df_indicator_driver.iloc[0]['total_time'] + df_row['time_valid'],2)

                #print(f"hoi {df_row['display_name']} {df_indicator_driver.iloc[0]['race_count']} {df_indicator_driver.iloc[0]['percentage']} {df_row['percentage']} {df_row['race_count']}")
                #percentage = (df_indicator_driver.iloc[0]['race_count'] * df_indicator_driver.iloc[0]['percentage'] + df_row['percentage']) / df_row['race_count']
            #else:
            #    percentage =  df_indicator_driver.iloc[0]['percentage']
                #print(f"hoi { df_row['display_name']} {df_indicator_driver.iloc[0]['percentage']}")
            #percentage =  df_indicator_driver.iloc[0]['percentage']
            driven = True
                                                                                                                                                                        #'gold_race_count','gold_total_drive_time','gold_total_sesion_time',gold_total_percentage, 'index','total_index'
            df_new_indicator.loc[index] = [df_row['team_id'],df_row['team_display_name'],df_row['cust_id'] ,df_row['display_name'],df_row['race_count'],df_row['old_classification'],df_row['total_time'],df_row['avg_speed'],df_row['percentage'],new_classification,deadzone,reclassified,driven,gold_race_count,gold_total_drive_time,gold_total_sesion_time,gold_total_percentage,0,0,df_row['total_session_time']]
    
        #now combine any old values which may not have been updated with the new Dataframe
        df_not_in_common = df_indicator.loc[~df_indicator['cust_id'].isin(df_new_indicator['cust_id'])]
        df_not_in_common['driven'] = False
        frames = [df_not_in_common, df_new_indicator]
        result = pd.concat(frames)
    else:
        print(f"WARNING: detected deadzone too small to use!")
        return df_indicator
    return result


if __name__ == '__main__': #only execute when called as script, skipped when loaded as module
    #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults
    parser=argparse.ArgumentParser()
    parser.add_argument("--member_data", help="location of member data file. if only name is supplied, script location is used",  default='./league_data/member_data.csv', type=str)
    parser.add_argument("--driver_indicator", help="location of the driver indicator file. if only name is supplied, script location is used",  default='./indicators/pec_s3_driver_indicator.csv', type=str)
    parser.add_argument("--session", help="location of the session file to process. if only name is supplied, script location is used")
    
    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")

    member_data_file= args.member_data #up-to-date info on members irating and validation (only needed for first race)
    #cust_id,display_name,latest_iRating,driver_classification,driver_qualification
    driver_indicator_file = args.driver_indicator #server both as reference data set from previous race(s) as well as file to save latest status to after processing
    latest_session_file = args.session #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv

    #always load the member data; use when data for driver does not exist in driver indicator file
    try:
        df_member_data = pd.read_csv(member_data_file)
    except:
        print('Error: member_data file {member_data_file} not found! Please re-run and provide valid file!')
        quit()

    # get previous indicator
    # must either be result of previous race -or if first race- result from iRating analysis
    try:
        df_indicator = pd.read_csv(driver_indicator_file)
    except:
        #scenario first race
        print(f"WARNING: could not find file {driver_indicator_file}. Is this the first race?")
        #scenario first race - REWRITE: SHOULD ALWAYS LOAD TO ADD DRIVERS!!!! CALL IT DF_MEMBERS /DF_REF
        df_indicator = pd.DataFrame(columns=driver_indicator_columns)
    #print(tabulate(df_indicator, headers = 'keys', tablefmt = 'psql'))

    try:
        df_latest_session = pd.read_csv(latest_session_file)
    except:
        print('Error: session file {latest_session_file} not found! Please re-run and provide valid file!')
        quit()

    #print(tabulate(df_latest_session, headers = 'keys', tablefmt = 'psql'))

    #we only need to process the GT3 car_class
    car_classes = ['GT3 Class']
    for car_class in car_classes:
        latest_session_class = df_latest_session["car_class_short_name"] == car_class
        df_latest_session_class = df_latest_session[latest_session_class]

        df_driver_info = update_driver_info(df_latest_session_class,df_indicator,df_member_data)

        #move the new_classification to old_classification
        df_driver_info['old_classification'] = df_driver_info['new_classification']

        df_new_indicator = update_driver_indicator(df_driver_info, df_indicator, df_member_data)
        print(tabulate(df_new_indicator[['cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified']], headers = 'keys', tablefmt = 'psql'))
        df_new_indicator.to_csv(driver_indicator_file,index=False)
