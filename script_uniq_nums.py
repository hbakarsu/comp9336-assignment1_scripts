import csv
from collections import OrderedDict

unique_numbers = OrderedDict()

with open('wifi_data_ts.csv', 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        if row:  
            try:
                number = int(row[0])  
                unique_numbers[number] = None
            except ValueError:
                pass  

# Export unique numbers to a new CSV file
with open('data_unique_numbers.csv', 'w', newline='') as file:
    csv_writer = csv.writer(file)
    for number in unique_numbers.keys():
        csv_writer.writerow([number])
