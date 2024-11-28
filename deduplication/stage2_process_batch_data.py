import os
import csv
import glob
import json
from kafka import KafkaProducer
from dotenv import load_dotenv
from syslog_processing import Processing

# Load environment variables from the .env file
load_dotenv()

class LogProcessor:
    def __init__(self):
        # Configuration
        self.bootstrap_servers = os.getenv("KAFKA_BROKER")
        self.topic_name = os.getenv("TOPIC_NAME_PUBLISH")
        self.batch_data_dir = os.getenv("RAW_DATA_DIRECTORY")
        self.object_processing = Processing()  # object of syslog_processing class
        
        self.latest_rows = {}
        self.count = 0
        self.directory_path = self.get_directory_path()
        
    def get_directory_path(self):
        """Constructs the directory path for raw data."""
        current_directory = os.getcwd()
        return os.path.join(current_directory, self.batch_data_dir)

    def get_unique_records(self):
        """Extracts unique records from CSV files in the specified directory."""
        csv_files = self.get_sorted_csv_files()
        if len(csv_files) < 2:
            print("Not enough CSV files in the directory.")
            return
        
        second_latest_csv = csv_files[1]
        print(f"Second latest CSV file: {second_latest_csv}")

        with open(second_latest_csv, mode='r', newline='', encoding='utf-8') as infile:
            csv_reader = csv.reader(infile)
            next(csv_reader)  # Skip the header row
            
            for row in csv_reader:
                self.count += 1
                message_dict = self.object_processing.end_to_end_processing_single_live_message(json_string_live_message=row[0])
                # make a tuple for the 3 unique fields. store the tuple in dict to store only unique tuples
                unique_key = (message_dict.get('device_identifier', ''), 
                              message_dict.get('module_name', ''), 
                              message_dict.get('log_type', ''))
                # Store the latest row for the unique key
                self.latest_rows[unique_key] = row  

        print("Processing completed for all files.")
        print(f"{len(self.latest_rows)} rows are unique out of {self.count}")
        return self.latest_rows

    def get_sorted_csv_files(self):
        """Retrieves and sorts CSV files in the specified directory by modification time."""
        csv_files = glob.glob(os.path.join(self.directory_path, '*.csv'))
        csv_files.sort(key=os.path.getmtime, reverse=True)
        if not csv_files:
            print("No CSV files found in the directory.")
        return csv_files

    def publish_message(self, producer, message, message_count):
        """Sends a message to Kafka."""
        message = {
            'id': message_count,
            'content': message
        }
        producer.send(self.topic_name, value=message)
        print(f"Sent: {message}")

    def publish_to_kafka(self):
        """Publishes unique records to Kafka."""
        message_count = 0
        producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize messages to JSON
        )
        try:
            for key, value in self.latest_rows.items():
                message_count += 1
                key_str = str(key)
                value_str = str(value)
                combined_str = f"{key_str} -> {value_str}"
                self.publish_message(producer, combined_str, message_count)
        except KeyboardInterrupt:
            print("Publishing stopped.")
        finally:
            producer.close()  # Close the producer when done

    def store_unique_records(self):
        """Stores unique records in a CSV file."""
        output_csv = os.getenv("UNIQUE_OUTPUT_FILENAME")
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Key (Tuple)", "Value (List)"])
            for key, value in self.latest_rows.items():
                writer.writerow([str(key), str(value)])
        print(f"Dictionary saved to {output_csv}")

    def deduplicate(self):
        """Main method to deduplicate log entries."""
        unique_dict = self.get_unique_records()
        if unique_dict:
            self.publish_to_kafka()
            self.store_unique_records()

if __name__ == "__main__":
    log_processor = LogProcessor()
    log_processor.deduplicate()
    