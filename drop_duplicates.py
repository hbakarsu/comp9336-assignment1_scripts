import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('complete_collection_data.csv', low_memory=False)

# Remove duplicate rows
df_unique = df.drop_duplicates()

# Write the modified DataFrame to a new CSV file
df_unique.to_csv('completed.csv', index=False)