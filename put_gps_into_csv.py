import csv

# Read the first CSV file
with open('thursday_friday_gps.csv', 'r') as file1:
    csv_reader1 = csv.reader(file1)
    data1 = list(csv_reader1)

# Read the second CSV file
with open('wifi_data_ts.csv', 'r') as file2:
    csv_reader2 = csv.reader(file2)
    data2 = list(csv_reader2)

# Iterate through rows of the first file
for row1 in data1:
    if row1:  # Check if row is not empty
        for row2 in data2:
            if row2:  # Check if row is not empty
                if row1[0] == row2[0]:  # Match first column
                    # Copy second, third, and fourth columns
                    row2[3], row2[4], row2[5] = row1[1], row1[2], row1[3]

# Write the modified data to a new CSV file
with open('completed.csv', 'w', newline='') as outfile:
    csv_writer = csv.writer(outfile)
    csv_writer.writerows(data2)
