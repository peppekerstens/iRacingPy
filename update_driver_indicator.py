import argparse
import sys
import os
import csv
import pandas as pd 
from tabulate import tabulate
import glob

#driver_indicator_columns = ['team_id','team_display_name','cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified','driven','gold_race_count','gold_total_drive_time','gold_total_sesion_time','gold_total_percentage','index','total_index','total_session_time']
driver_indicator_columns = ['team_id','team_display_name','cust_id','display_name','classification','percentage','avg_speed','total_time','total_session_time']

def generate_member_data_driver_indicator(df_member_data: pd, cust_id: int) -> pd:
    #scenario first time driver. use downloaded member_data (which should contain classification based on iRating) as a reference
    df_indicator = pd.DataFrame(columns=driver_indicator_columns)
    driver = df_member_data['cust_id'] == cust_id
    df_driver = df_member_data[driver]
    #print(tabulate(df_driver, headers = 'keys', tablefmt = 'psql'))
    if not df_driver.empty:
        #classification = df_driver.iloc[0]['gt3am']
        #print(df_row['driver_classification'])
        #if classification == 'Gold':
        #                        ['team_id','cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified','driven','gold_race_count','gold_total_drive_time','gold_total_sesion_time','index','total_index']
        df_indicator.loc[0] = [0,'',df_driver.iloc[0]['cust_id'] ,df_driver.iloc[0]['display_name'],df_driver.iloc[0]['gt3am'],0,0,0,0]
    return df_indicator


def update_driver_info(df_latest_session: pd,df_member_data: pd) -> pd:
    #build dataframe based on current results
    df_driver_info = pd.DataFrame(columns=driver_indicator_columns)
    for index, df_row in df_latest_session.iterrows():
        cust_id = df_row['cust_id']
        df_indicator_driver = generate_member_data_driver_indicator(df_member_data,cust_id)
        if not df_indicator_driver.empty:
            try:
                team_id = df_row['team_id']
            except:
                team_id = None
            cust_id = df_row['cust_id']
            display_name = df_row['display_name']
            team_display_name = df_row['team_display_name']
            classification = df_indicator_driver.iloc[0]['classification']
            total_session_time = round(df_row['total_session_time'])
            total_time = round(df_row['time_valid'])
            percentage = round(total_time/total_session_time * 100,0)
            avg_speed = round(df_row['speed_valid'])
            #print(f"cust_id: {df_row['cust_id']}")
            #print(f"total_time: {total_time}")
            #print(f"total_session_time: {total_session_time}")
            #print(f"percentage: {percentage}")
            #total_time = round(df_indicator_driver.iloc[0]['total_time'] + df_row['time_valid'],2)
            # ['team_id','team_display_name','cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified','driven','gold_race_count','gold_total_drive_time','gold_total_sesion_time','gold_total_percentage','index','total_index','total_session_time']
            df_driver_info.loc[index] = [team_id,team_display_name,cust_id,display_name,classification,percentage,avg_speed,total_time,total_session_time]
            #driver_indicator_columns = ['team_id','team_display_name','cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified','driven','gold_race_count','gold_total_drive_time','gold_total_sesion_time','gold_total_percentage','index','total_index','total_session_time']
            #driver_indicator_columns = ['team_id','team_display_name','cust_id','display_name','classification','percentage','total_time','total_session_time']

        if df_indicator_driver.empty:    
            print(f"WARNING: could not find indicator information for driver {df_row['display_name']} ({df_row['cust_id']}) skipping!")
    return df_driver_info

if __name__ == '__main__': #only execute when called as script, skipped when loaded as module
    #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults
    parser=argparse.ArgumentParser()
    parser.add_argument("--member_data", help="location of member data file. if only name is supplied, script location is used",  default='./member_data.csv', type=str)
    parser.add_argument("--session", help="location of the session file to process. if only name is supplied, script location is used")
    
    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")

    member_data_file= args.member_data #up-to-date info on members irating and validation (only needed for first race)
    #cust_id,display_name,latest_iRating,driver_classification,driver_qualification
    latest_session_file = args.session #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv

    #load the member data
    try:
        df_member_data = pd.read_csv(member_data_file)
    except:
        print('Error: member_data file {member_data_file} not found! Please re-run and provide valid file!')
        quit()

    try:
        df_latest_session = pd.read_csv(latest_session_file)
    except:
        print('Error: session file {latest_session_file} not found! Please re-run and provide valid file!')
        quit()

    #print(tabulate(df_latest_session, headers = 'keys', tablefmt = 'psql'))

    #we only need to process the GT3 car_class
    car_classes = ['IMSA23']
    for car_class in car_classes:
        latest_session_class = df_latest_session["car_class_short_name"] == car_class
        df_latest_session_class = df_latest_session[latest_session_class]

        df_driver_info = update_driver_info(df_latest_session_class,df_member_data)

        driver_indicator_file = './indicators/driver_indicator.csv'
        df_driver_info.to_csv(driver_indicator_file,index=False)
        """
        print(tabulate(df_driver_info))
        df_new_indicator = update_driver_indicator(df_driver_info, df_member_data)
        print(tabulate(df_new_indicator[['cust_id','display_name','race_count','old_classification','total_time','avg_speed','percentage','new_classification','deadzone','reclassified']], headers = 'keys', tablefmt = 'psql'))
        
        #parser.add_argument("--driver_indicator", help="location of the driver indicator file. if only name is supplied, script location is used",  default='./indicators/driver_indicator.csv', type=str)
        driver_indicator_file = './indicators/driver_indicator.csv'
        df_new_indicator.to_csv(driver_indicator_file,index=False)
        """