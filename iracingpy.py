import yaml
import os

#maybe use this?
#https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5

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


if __name__ == '__main__': #only execute when called as script, skipped when loaded as module
    #https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    #https://stackoverflow.com/questions/15301147/python-argparse-default-value-or-specified-value
    #expand later to use a config file instead of defaults
    parser=argparse.ArgumentParser()
    parser.add_argument("--member_data", help="location of member data file. if only name is supplied, script location is used",  default='member_data.csv', type=str)
    parser.add_argument("--driver_indicator", help="location of the driver indicator file. if only name is supplied, script location is used",  default='pec_s3_driver_indicator.csv', type=str)
    parser.add_argument("--session", help="location of the session file to process. if only name is supplied, script location is used")
    
    args=parser.parse_args()
    #print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
    #print(f"Dict format: {vars(args)}")

    member_data_file = args.member_data #up-to-date info on members irating and validation (only needed for first race)
    #cust_id,display_name,latest_iRating,driver_classification,driver_qualification
    driver_indicator_file = args.driver_indicator #server both as reference data set from previous race(s) as well as file to save latest status to after processing
    latest_session_file = args.session #results from current race. maybe an agrument for this script? currently being detected as latest file within directory with name session_*.csv

