import pytelemetry
import csv

def ibt_to_csv(ibt_file, csv_file):
    # Load the telemetry data from the .ibt file
    telemetry = pytelemetry.Telemetry(ibt_file)
    
    # Open the CSV file for writing
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the headers (column names)
        headers = ['Timestamp'] + telemetry.variables
        writer.writerow(headers)
        
        # Write the telemetry data
        for row in telemetry.rows:
            writer.writerow(row)
    
    print(f"Data successfully written to {csv_file}")

# Example usage
ibt_file = './telemetry/telemetry/acuraarx06gtp_sebring international 2024-04-27 13-13-33.ibt'
csv_file = './telemetry/telemetry/acuraarx06gtp_sebring international 2024-04-27 13-13-33.csv'
ibt_to_csv(ibt_file, csv_file)
