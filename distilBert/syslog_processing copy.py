import csv
import json
import re
import os
import pandas as pd
from datetime import datetime
import time


class Processing:
    
    pattern1 = r"(?P<vendor>[A-Z]+)-(?P<physical_site_id>\d+)_(?P<geolocation_code>[A-Z\d]+)-(?P<device_role>[A-Z\d]+)_(?P<device_model_number>[A-Z\d]+)-(?P<device_importance>[A-Z\d]+) %%(?P<version_number>\d+)(?P<module_name>[A-Z]+)/(?P<severity>\d+)/(?P<log_type>[A-Z_]+)(?P<log_status>[\(\)a-z]+):CID=(?P<cid>[0-9a-zA-Z]+);(?P<description>.+)"
    pattern2 = r"(?P<vendor>[A-Z]+)-(?P<physical_site_id>\d+)_(?P<geolocation_code>[A-Z\d]+)-(?P<device_role>[A-Z\d]+)_(?P<device_model_number>[A-Z\d]+)-(?P<device_importance>[A-Z\d]+) %%(?P<version_number>\d+)(?P<module_name>[A-Z]+)/(?P<severity>\d+)/(?P<log_type>[A-Z_]+)(?P<log_status>[\(\)a-z]+)\[(?P<sequence_number>\d+)\]:(?P<description>.+)"
    pattern3 = r"(?P<vendor>[A-Z]+)-(?P<physical_site_id>\d+)_(?P<geolocation_code>[A-Z\d]+)-(?P<device_role>[A-Z\d]+)_(?P<device_model_number>[A-Z\d]+)-(?P<device_importance>[A-Z\d]+) %%\/(?P<severity>\d+)\/(?P<log_type>[A-Z_]+):OID (?P<oid>[A-Z\d\s.]+) (?P<description>.+)"
    pattern4 = r"(?P<vendor>[A-Z]+)-(?P<physical_site_id>\d+)_(?P<geolocation_code>[A-Z\d]+)-(?P<device_role>[A-Z\d]+)-(?P<device_function>[A-Z\d]+)_(?P<device_model_number>[A-Z\d]+)-(?P<device_importance>[A-Z\d]+) %%(?P<version_number>\d+)(?P<module_name>[A-Z]+)/(?P<severity>\d+)/(?P<log_type>[A-Z_]+)(?P<log_status>[\(\)a-z]+)\[(?P<sequence_number>\d+)\]:(?P<description>.+)"
    unhappy_list = ['error','fail','fails','failed','failure','deny','block','blocked', 'conflict']
    extracted_row_count = 0
    total_row_count = 0
    all_descriptions = []
    # Define headers for the new CSV file
    headers = [
        'timestamp_of_received_log',
        'timestamp_of_message',
        'year',
        'month',
        'day_of_month',
        'hour',
        'minute',
        'second',
        'millisecond',
        'day_of_week',
        'day_of_year',
        'week_of_year',
        'is_weekend',
        'seconds_since_midnight',
        'time_of_day_bucket',
        'device_identifier',
        'vendor', 
        'physical_site_id', 
        'geolocation_code', 
        'device_role', 
        'device_function',
        'device_model_number',
        'device_importance', 
        'version_number', 
        'module_name', 
        'severity',
        'log_type', 
        'log_status', 
        'cid',
        'oid',
        'sequence_number', 
        'description', 
        'device_with_description',
        'metadata',
        'is_unhappy']


    def extract_time_info(self,message):
        # Extract timestamp
        split_message = message.split(' ')
        if split_message[1] == '':
            split_message.remove('')
        timestamp_str = split_message[0:4]    
        timestamp_str = ' '.join(timestamp_str)
        dt = datetime.strptime(timestamp_str, "%b %d %Y %H:%M:%S")
        year = dt.year
        month = dt.month
        day_of_month = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second
        millisecond = dt.microsecond // 1000
        day_of_week = dt.weekday()  # Monday = 0, Sunday = 6
        day_of_year = dt.timetuple().tm_yday
        week_of_year = dt.isocalendar()[1]
        is_weekend = int(dt.weekday() >= 5)
        seconds_since_midnight = hour * 3600 + minute * 60 + second
        time_of_day_bucket = 'Morning' if hour < 12 else 'Afternoon' if hour < 18 else 'Evening' if hour < 21 else 'Night'
        time_dict = {
            'timestamp': timestamp_str,
            'year': year,
            'month': month,
            'day_of_month': day_of_month,
            'hour': hour,
            'minute': minute,
            'second': second,
            'millisecond': millisecond,
            'day_of_week': day_of_week,
            'day_of_year': day_of_year,
            'week_of_year': week_of_year,
            'is_weekend': is_weekend,
            'seconds_since_midnight': seconds_since_midnight,
            'time_of_day_bucket': time_of_day_bucket
        }
        return time_dict


    def remove_time_info_from_message(self,message):
        # Find the position of the first colon
        first_colon_pos = message.find(':')

        # Find the position of the second colon by starting the search after the first colon
        second_colon_pos = message.find(':', first_colon_pos + 1)

        # Slice the string two characters after the second colon
        truncated_message = message[second_colon_pos + 4:]

        # Print the truncated message
        return truncated_message


    def extract_metadata_from_description(self,description):
        if description:
            opening_bracket_pos = description.find('(')
            if opening_bracket_pos >= 0:
                
                # Slice the string and separate metadata
                metadata = description[opening_bracket_pos + 1:-1]
                
            else:
                # print("no metadata available inside the description")
                metadata = "" 
        else:
            # print("no description and hence no metadata")
            metadata = ""
            
        return metadata    


    def remove_metadata_from_description(self,description):
        if description:
            opening_bracket_pos = description.find('(')
            if opening_bracket_pos >= 0:
                
                # Slice the string and separate metadata
                new_desc = description[:opening_bracket_pos]
                
            else:
                new_desc = description
        else:
            new_desc = ""
            
        return new_desc 
    
    
    def get_all_device_with_descriptions(self, input_csv_path):
        
        if self.all_descriptions != []:
            return self.all_descriptions
        
        else:
            with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
                # Create CSV reader
                csv_reader = csv.reader(infile)
                next(csv_reader) # skipping the header row
                
                # Process each row in the input CSV
                for row in csv_reader:
                    self.total_row_count += 1
                    # print(row)
                    if len(row) < 3:
                        continue
                    
                    timestamp_of_received_log = row[0]
                    # Extract the message from the third column
                    message = row[2]
                    time_dict = self.extract_time_info(message=message)
                    final_time_dict = {"timestamp_of_received_log": timestamp_of_received_log} | time_dict
                    truncated_message = self.remove_time_info_from_message(message=message)
                    network_info_dict = self.extract_network_info(pattern=[self.pattern1,self.pattern2, self.pattern3, self.pattern4], message=truncated_message)
                    extracted_data = final_time_dict | network_info_dict

                    # storing all descriptions in a variable
                    
                    self.all_descriptions.append(extracted_data.get('device_with_description', '').lower().strip())   
        
            return self.all_descriptions
    

    def get_all_descriptions(self, input_csv_path):
        
        if self.all_descriptions != []:
            return self.all_descriptions
        
        else:
            with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
                # Create CSV reader
                csv_reader = csv.reader(infile)
                next(csv_reader) # skipping the header row
                
                # Process each row in the input CSV
                for row in csv_reader:
                    self.total_row_count += 1
                    # print(row)
                    if len(row) < 3:
                        continue
                    
                    timestamp_of_received_log = row[0]
                    # Extract the message from the third column
                    message = row[2]
                    time_dict = self.extract_time_info(message=message)
                    final_time_dict = {"timestamp_of_received_log": timestamp_of_received_log} | time_dict
                    truncated_message = self.remove_time_info_from_message(message=message)
                    network_info_dict = self.extract_network_info(pattern=[self.pattern1,self.pattern2, self.pattern3, self.pattern4], message=truncated_message)
                    extracted_data = final_time_dict | network_info_dict

                    # storing all descriptions in a variable
                    
                    self.all_descriptions.append(extracted_data.get('description', '').lower().strip())   
        
            return self.all_descriptions
    
    
    def get_specific_device_with_descriptions(self, input_csv_path, physical_site_id, geolocation_code, device_role, device_model_number, device_importance):
        
        filtered_desc = []
        with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
            # Create CSV reader
            csv_reader = csv.reader(infile)
            next(csv_reader) # skipping the header row
            
            # Process each row in the input CSV
            for row in csv_reader:
                self.total_row_count += 1
                # print(row)
                if len(row) < 3:
                    continue
                
                timestamp_of_received_log = row[0]
                # Extract the message from the third column
                message = row[2]
                time_dict = self.extract_time_info(message=message)
                final_time_dict = {"timestamp_of_received_log": timestamp_of_received_log} | time_dict
                truncated_message = self.remove_time_info_from_message(message=message)
                network_info_dict = self.extract_network_info(pattern=[self.pattern1,self.pattern2, self.pattern3, self.pattern4], message=truncated_message)
                extracted_data = final_time_dict | network_info_dict
                if extracted_data['physical_site_id'] == physical_site_id and extracted_data['geolocation_code'] == geolocation_code and extracted_data['device_role'] == device_role and extracted_data['device_model_number'] == device_model_number and extracted_data['device_importance'] == device_importance:  
                    # storing all specific descriptions in a variable
                    formatted_disc = extracted_data.get('device_with_description', '').lower().strip()
                    filtered_desc.append(formatted_disc)   
        
        return filtered_desc


    def get_specific_descriptions(self, input_csv_path, physical_site_id, geolocation_code, device_role, device_model_number, device_importance):
        
        filtered_desc = []
        with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
            # Create CSV reader
            csv_reader = csv.reader(infile)
            next(csv_reader) # skipping the header row
            
            # Process each row in the input CSV
            for row in csv_reader:
                self.total_row_count += 1
                # print(row)
                if len(row) < 3:
                    continue
                
                timestamp_of_received_log = row[0]
                # Extract the message from the third column
                message = row[2]
                time_dict = self.extract_time_info(message=message)
                final_time_dict = {"timestamp_of_received_log": timestamp_of_received_log} | time_dict
                truncated_message = self.remove_time_info_from_message(message=message)
                network_info_dict = self.extract_network_info(pattern=[self.pattern1,self.pattern2, self.pattern3, self.pattern4], message=truncated_message)
                extracted_data = final_time_dict | network_info_dict
                if extracted_data['physical_site_id'] == physical_site_id and extracted_data['geolocation_code'] == geolocation_code and extracted_data['device_role'] == device_role and extracted_data['device_model_number'] == device_model_number and extracted_data['device_importance'] == device_importance:  
                    # storing all specific descriptions in a variable
                    formatted_disc = extracted_data.get('description', '').lower().strip()
                    filtered_desc.append(formatted_disc)   
        
        return filtered_desc


    def extract_network_info(self,pattern,message):
        matching = None
        for ptn in pattern:
            match = re.search(ptn, message)
            matching = matching or match
        if matching:
            self.extracted_row_count+=1
            extracted_info = matching.groupdict()
            description = extracted_info.get("description")
            metadata = self.extract_metadata_from_description(description=description)
            description = self.remove_metadata_from_description(description)
            extracted_info["metadata"] = metadata
            extracted_info['description'] = description
            extracted_info['device_identifier'] = extracted_info.get('vendor', '') + "-" + extracted_info.get('physical_site_id', '') + "-" + extracted_info.get('geolocation_code', '') + "-" + extracted_info.get('device_role', '') + "-" + extracted_info.get('device_function', '') + "-" + extracted_info.get('device_model_number', '') + "-" + extracted_info.get('device_importance', '')
            extracted_info['device_with_description'] = extracted_info.get('vendor', '') + "-" + extracted_info.get('physical_site_id', '') + "-" + extracted_info.get('geolocation_code', '') + "-" + extracted_info.get('device_role', '') + "-" + extracted_info.get('device_function', '') + "-" + extracted_info.get('device_model_number', '') + "-" + extracted_info.get('device_importance', '') + " -> " + extracted_info.get('description', '')
            return extracted_info
        else:
            # Return empty strings for all expected fields if pattern does not match
            return {
                "device_identifier": "",
                "vendor": "",
                "physical_site_id": "",
                "geolocation_code": "",
                "device_role": "",
                "device_function": "",
                "device_model_number": "",
                "device_importance": "",
                "version_number": "",
                "module_name": "",
                "severity": "",
                "log_type": "",
                "log_status": "",
                "cid": "",
                "oid": "",
                "sequence_number": "",
                "description": "",
                "device_with_description": "",
                "metadata": "",
                "is_unhappy": ""
            }   


    def extract_unhappy_status_from_description(self,description):
        description = description.lower()
        if description == '':
            return "0"
        for elem in self.unhappy_list:
            if elem in description:
                return "1"
        return "0"
        

    def end_to_end_processing(self, input_csv_path, output_csv_path):

        # Open the input CSV file for reading and the output CSV file for writing
        with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile, \
            open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:

            # Create CSV reader and writer
            csv_reader = csv.reader(infile)
            next(csv_reader) # skipping the header row
            csv_writer = csv.DictWriter(outfile, fieldnames=self.headers)

            # Write the header to the new CSV file
            csv_writer.writeheader()

            # Process each row in the input CSV
            for row in csv_reader:
                self.total_row_count += 1
                # print(row)
                if len(row) < 3:
                    continue
                
                timestamp_of_received_log = row[0]
                # Extract the message from the third column
                message = row[2]
                time_dict = self.extract_time_info(message=message)
                final_time_dict = {"timestamp_of_received_log": timestamp_of_received_log} | time_dict
                truncated_message = self.remove_time_info_from_message(message=message)
                network_info_dict = self.extract_network_info(pattern=[self.pattern1,self.pattern2, self.pattern3, self.pattern4], message=truncated_message)
                extracted_data = final_time_dict | network_info_dict

                # storing all descriptions in a variable
                
                self.all_descriptions.append(extracted_data.get('description', ''))

                # Write the extracted data to the new CSV file
                
                data_to_write = {
                    'timestamp_of_received_log': extracted_data.get('timestamp_of_received_log', ''),
                    'timestamp_of_message': extracted_data.get('timestamp', ''),
                    'year': extracted_data.get('year', ''),
                    'month': extracted_data.get('month', ''),
                    'day_of_month': extracted_data.get('day_of_month', ''),
                    'hour': extracted_data.get('hour', ''),
                    'minute': extracted_data.get('minute', ''),
                    'second': extracted_data.get('second', ''),
                    'millisecond': extracted_data.get('millisecond', ''),
                    'day_of_week': extracted_data.get('day_of_week', ''),
                    'day_of_year': extracted_data.get('day_of_year', ''),
                    'week_of_year': extracted_data.get('week_of_year', ''),
                    'is_weekend': extracted_data.get('is_weekend', ''),
                    'seconds_since_midnight': extracted_data.get('seconds_since_midnight', ''),
                    'time_of_day_bucket': extracted_data.get('time_of_day_bucket', ''),
                    'device_identifier': extracted_data.get('device_identifier', ''),
                    'vendor': extracted_data.get('vendor', ''),
                    'physical_site_id': extracted_data.get('physical_site_id', ''),
                    'geolocation_code': extracted_data.get('geolocation_code', ''),
                    'device_role': extracted_data.get('device_role', ''),
                    'device_function': extracted_data.get('device_function', ''),
                    'device_model_number': extracted_data.get('device_model_number', ''),
                    'device_importance': extracted_data.get('device_importance', ''),
                    'version_number': extracted_data.get('version_number', ''),
                    'module_name': extracted_data.get('module_name', ''),
                    'severity': extracted_data.get('severity', ''),
                    'log_type': extracted_data.get('log_type', ''),
                    'log_status': extracted_data.get('log_status', ''),
                    'cid': extracted_data.get('cid', ''),
                    'oid': extracted_data.get('oid', ''),
                    'sequence_number': extracted_data.get('sequence_number', ''),
                    'description': extracted_data.get('description', ''),
                    'device_with_description': extracted_data.get('device_with_description', ''),
                    'metadata': extracted_data.get('metadata', ''),
                    'is_unhappy': self.extract_unhappy_status_from_description(extracted_data.get('description', ''))
                }
                csv_writer.writerow(data_to_write)
        # the two CSVs are automatically closed after the execution of the with block

        print("CSV processing complete. Data written to:", output_csv_path)
        return


    @staticmethod
    def standardising_live_message(message):
        message_dict = json.loads(message)
        raw_msg = message_dict.get('payload','')
        if raw_msg != '':
            index = raw_msg.find('>')
            msg_str = raw_msg[index+1:]
            return msg_str
        else:
            return ''   


    def end_to_end_processing_single_live_message(self, receiving_time, json_string_live_message):
        standard_live_message = self.standardising_live_message(json_string_live_message)
        if standard_live_message:
            time_dict = self.extract_time_info(message=standard_live_message)
            final_time_dict = {"timestamp_of_received_log": str(receiving_time)} | time_dict
            truncated_message = self.remove_time_info_from_message(message=standard_live_message)
            network_info_dict = self.extract_network_info(pattern=[self.pattern1,self.pattern2, self.pattern3, self.pattern4], message=truncated_message)
            extracted_data = final_time_dict | network_info_dict
            
        return_dict = {
                'timestamp_of_received_log': extracted_data.get('timestamp_of_received_log', ''),
                'timestamp_of_message': extracted_data.get('timestamp', ''),
                'year': extracted_data.get('year', ''),
                'month': extracted_data.get('month', ''),
                'day_of_month': extracted_data.get('day_of_month', ''),
                'hour': extracted_data.get('hour', ''),
                'minute': extracted_data.get('minute', ''),
                'second': extracted_data.get('second', ''),
                'millisecond': extracted_data.get('millisecond', ''),
                'day_of_week': extracted_data.get('day_of_week', ''),
                'day_of_year': extracted_data.get('day_of_year', ''),
                'week_of_year': extracted_data.get('week_of_year', ''),
                'is_weekend': extracted_data.get('is_weekend', ''),
                'seconds_since_midnight': extracted_data.get('seconds_since_midnight', ''),
                'time_of_day_bucket': extracted_data.get('time_of_day_bucket', ''),
                'device_identifier': extracted_data.get('device_identifier', ''),
                'vendor': extracted_data.get('vendor', ''),
                'physical_site_id': extracted_data.get('physical_site_id', ''),
                'geolocation_code': extracted_data.get('geolocation_code', ''),
                'device_role': extracted_data.get('device_role', ''),
                'device_function': extracted_data.get('device_function', ''),
                'device_model_number': extracted_data.get('device_model_number', ''),
                'device_importance': extracted_data.get('device_importance', ''),
                'version_number': extracted_data.get('version_number', ''),
                'module_name': extracted_data.get('module_name', ''),
                'severity': extracted_data.get('severity', ''),
                'log_type': extracted_data.get('log_type', ''),
                'log_status': extracted_data.get('log_status', ''),
                'cid': extracted_data.get('cid', ''),
                'description': extracted_data.get('description', ''),
                'device_with_description': extracted_data.get('device_with_description', ''),
                'metadata': extracted_data.get('metadata', ''),
                'is_unhappy': extracted_data.get('is_unhappy', '')
            }
        
        return return_dict        
            
        
if __name__ == "__main__":
    start_time = time.time()
    # Define the input and output CSV file paths
    input_csv_name = "GPN_Syslog_10000.csv"
    input_dir = "data"
    output_dir = "processed_data"

    if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
            
    output_csv_name = input_csv_name[:-4] + "_output" + ".csv"
    input_csv_path = os.path.join(input_dir,input_csv_name)
    output_csv_path = os.path.join(output_dir,output_csv_name)
    
    
    object = Processing()
    object.end_to_end_processing(input_csv_path=input_csv_path, output_csv_path=output_csv_path)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Processing time: {execution_time} seconds")
    print(f"{object.extracted_row_count} rows successfully processed out of {object.total_row_count} rows")

    # Open the file in append mode
    with open('descriptions.txt', 'w') as file:
        file.write('\n'.join(object.get_all_descriptions(input_csv_path=input_csv_path)))
    
    
    
    