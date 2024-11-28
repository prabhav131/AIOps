import csv
import time
import os
from kafka import KafkaConsumer
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class KafkaSyslogConsumer:
    def __init__(self):
        self.time_interval = int(os.getenv("INGEST_INTERVAL"))
        self.output_dir = os.getenv("RAW_DATA_DIRECTORY")
        self.batch_fill = 0
        self.batch_number = self.get_initial_batch_number()
        self.start_time = time.time()
        self.consumer = self.initialize_consumer()
        self.batch_filename = f"batch_{self.batch_number}.csv"
        self.batch_filepath = os.path.join(self.output_dir, self.batch_filename)
        self.csv_writer = None
        print("Starting to consume messages from udp_input topic...")

    def get_initial_batch_number(self):
        """Gets the starting batch number based on existing files."""
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
            return 1
        return len(os.listdir(self.output_dir)) + 1

    def initialize_consumer(self):
        """Initializes the Kafka consumer."""
        return KafkaConsumer(
            os.getenv("TOPIC_NAME_INGEST"),
            bootstrap_servers=[os.getenv("KAFKA_BROKER")],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='syslog-group-' + str(int(time.time()))
        )

    def write_message(self, message):
        """Writes a syslog message to the current CSV file."""
        syslog_data = message.value.decode('utf-8')
        print(f"Received syslog data: {syslog_data}")

        if self.batch_fill == 0:
            self.open_new_file()
            self.csv_writer.writerow({'message': syslog_data})
            self.batch_fill = -1  # Mark batch as filled for initial write
        elif time.time() - self.start_time < self.time_interval:
            # Write to the current batch file if within time interval
            self.csv_writer.writerow({'message': syslog_data})
        else:
            # Start a new batch
            self.close_current_file()
            self.prepare_new_batch()
            self.write_message(message)  # Write the current message to the new batch

    def open_new_file(self):
        """Opens a new CSV file for writing syslog data."""
        outfile = open(self.batch_filepath, mode='w', newline='', encoding='utf-8')
        self.csv_writer = csv.DictWriter(outfile, fieldnames=['message'])
        self.csv_writer.writeheader()

    def close_current_file(self):
        """Closes the current CSV file."""
        if self.csv_writer:
            self.csv_writer.writerows([])  # Ensure any remaining data is flushed before closing
            self.csv_writer = None

    def prepare_new_batch(self):
        """Prepares a new batch file and resets necessary parameters."""
        self.batch_number = len(os.listdir(self.output_dir)) + 1
        self.batch_filename = f"batch_{self.batch_number}.csv"
        self.batch_filepath = os.path.join(self.output_dir, self.batch_filename)
        self.batch_fill = 0
        self.start_time = time.time()
        print(f"writing in new file now: {self.batch_filename}")

    def consume_messages(self):
        """Starts consuming messages from the Kafka topic."""
        for message in self.consumer:
            self.write_message(message)

if __name__ == "__main__":
    kafka_consumer = KafkaSyslogConsumer()
    kafka_consumer.consume_messages()
