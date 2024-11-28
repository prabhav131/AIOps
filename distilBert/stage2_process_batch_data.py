import os
import time
import pandas as pd
import csv
from syslog_processing import Processing

batch_data_dir = "batch_data" # raw data
processed_data_dir = "processed_data" # final processed data
object_processing = Processing()
if not os.path.isdir(processed_data_dir):
        os.makedirs(processed_data_dir)


batch_number = 1
batch_fill = 0
batch_size = 10000
batch_filename = f"output_batch_{batch_number}.csv"
output_filepath = os.path.join(processed_data_dir, batch_filename)
# Define the directory where the CSV files are stored
current_directory = os.getcwd()
print(current_directory)
directory_path = os.path.join(current_directory,batch_data_dir)

with open(output_filepath, mode= 'w', newline='', encoding='utf-8') as outfile:
    csv_writer = csv.DictWriter(outfile, fieldnames=object_processing.headers)

    # Write the header to the new CSV file
    csv_writer.writeheader()

# Iterate over files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):  # Check if the file is a CSV
        
        input_filepath = os.path.join(directory_path, filename)
        print(f"-----------{input_filepath}")

        with open(input_filepath, mode='r', newline='', encoding='utf-8') as infile, \
            open(output_filepath, mode= 'a', newline='', encoding='utf-8') as outfile:
                
            # Create CSV reader
            csv_reader = csv.reader(infile)
            next(csv_reader) # skipping the header row
            csv_writer = csv.DictWriter(outfile, fieldnames=object_processing.headers)
            
            for row in csv_reader:
                print(row[0])
                print(type(row[0]))
                message_dict = object_processing.end_to_end_processing_single_live_message(json_string_live_message=row[0])
                print("-------")
                print(message_dict)
                
                # Write the extracted data to the output CSV file
                    
                data_to_write = {
                    'timestamp_of_message': message_dict.get('timestamp_of_message', ''),
                    'year': message_dict.get('year', ''),
                    'month': message_dict.get('month', ''),
                    'day_of_month': message_dict.get('day_of_month', ''),
                    'hour': message_dict.get('hour', ''),
                    'minute': message_dict.get('minute', ''),
                    'second': message_dict.get('second', ''),
                    'millisecond': message_dict.get('millisecond', ''),
                    'day_of_week': message_dict.get('day_of_week', ''),
                    'day_of_year': message_dict.get('day_of_year', ''),
                    'week_of_year': message_dict.get('week_of_year', ''),
                    'is_weekend': message_dict.get('is_weekend', ''),
                    'seconds_since_midnight': message_dict.get('seconds_since_midnight', ''),
                    'time_of_day_bucket': message_dict.get('time_of_day_bucket', ''),
                    'device_identifier': message_dict.get('device_identifier', ''),
                    'vendor': message_dict.get('vendor', ''),
                    'physical_site_id': message_dict.get('physical_site_id', ''),
                    'geolocation_code': message_dict.get('geolocation_code', ''),
                    'device_role': message_dict.get('device_role', ''),
                    'device_function': message_dict.get('device_function', ''),
                    'device_model_number': message_dict.get('device_model_number', ''),
                    'device_importance': message_dict.get('device_importance', ''),
                    'version_number': message_dict.get('version_number', ''),
                    'module_name': message_dict.get('module_name', ''),
                    'severity': message_dict.get('severity', ''),
                    'log_type': message_dict.get('log_type', ''),
                    'log_status': message_dict.get('log_status', ''),
                    'cid': message_dict.get('cid', ''),
                    'oid': message_dict.get('oid', ''),
                    'sequence_number': message_dict.get('sequence_number', ''),
                    'description': message_dict.get('description', ''),
                    'device_with_description': message_dict.get('device_with_description', ''),
                    'metadata': message_dict.get('metadata', ''),
                    'is_unhappy': message_dict.get('is_unhappy', '')
                }
                csv_writer.writerow(data_to_write)
                

print("Processing completed for all files.")

