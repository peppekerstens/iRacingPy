import csv
import sys
import pwinput
from iracingdataapi.client import irDataClient

def extract_cust_id(data):
    cust_ids = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'cust_id':
                cust_ids.append(value)
            elif isinstance(value, (dict, list)):
                cust_ids.extend(extract_cust_id(value))
    elif isinstance(data, list):
        for item in data:
            cust_ids.extend(extract_cust_id(item))
    return cust_ids

print('Going into interactive mode....')
username = input("Enter username: ")
password = pwinput.pwinput(prompt='Enter password: ')

league_id = 5606

idc = irDataClient(username=username, password=password)

# Get the list of drivers in the league
drivers = idc.league_get(league_id)
cust_ids = extract_cust_id(drivers)

with open('iracingid.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['cust_id'])
    for cust_id in cust_ids:
        writer.writerow([cust_id])

print("Customer IDs exported to iracingid.csv")
