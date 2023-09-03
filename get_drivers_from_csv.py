import csv
import pandas as pd

df = pd.read_csv(r'PECS4.csv')
print(tabulate(df)
#print(df)

#with open('PECS4.csv', newline='') as csvfile:
#    spamreader = csv.reader(csvfile, delimiter=',')
#    for row in spamreader:
#        print(', '.join(row))

#with open('PECS4.csv', newline='') as csvfile:
#    csv_reader = csv.reader(csvfile, delimiter=',')
#    line_count = 0
#    for row in csv_reader:
#        if line_count == 0:
#            print(f'Column names are {", ".join(row)}')
#            line_count += 1
#        else:
#            column  name
#            3       Team Name
#            4       Team IracingID
#            5       Car Number
#            6       Team Manager Name
#            7       Team Manager iRacingID
#            8       Team Manager = driver
#            9       Competition class
#            10      GTP Car Selection
#            11      LMP2 Car Selection
#            12      GT3 Car selection

#            print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
#            line_count += 1
#    print(f'Processed {line_count} lines.')