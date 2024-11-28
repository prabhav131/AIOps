import pandas as pd

# Define the input and output file names
input_csv = 'your_input_file.csv'  # Replace with your actual input file
output_csv = 'latest_unique_rows_output.csv'  # Output file

# Define the fields that determine uniqueness
unique_fields = ['field1', 'field2', 'field3']  # Replace with your actual field names

# Read the CSV file into a DataFrame
df = pd.read_csv(input_csv)

# Create a dictionary to store the latest rows based on unique combinations
latest_rows = {}

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Create a tuple of the unique fields
    unique_key = tuple(row[field] for field in unique_fields)
    
    # If the unique key is not in the dictionary, or if it is, update it with the latest row
    latest_rows[unique_key] = row  # This will replace with the latest occurrence

# Convert the dictionary values (latest rows) back to a DataFrame
latest_unique_df = pd.DataFrame(latest_rows.values())

# Save the latest unique rows to a new CSV file
latest_unique_df.to_csv(output_csv, index=False)

print(f"Latest unique rows saved to {output_csv}")
