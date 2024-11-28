import csv
import time
from kafka import KafkaConsumer
import os

batch_size = 100
output_dir = "batch_data"
batch_fill = 0
batch_number = 1

if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'udp_input',
    bootstrap_servers=['172.31.252.214:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='syslog-group-' + str(int(time.time()))
)

print("Starting to consume messages from udp_input topic...")


batch_filename = f"batch_{batch_number}.csv"
batch_filepath = os.path.join(output_dir, batch_filename)

# Consume messages from the Kafka topic
for message in consumer:
    
    syslog_data = message.value.decode('utf-8')
    print(f"Received syslog data: {syslog_data}")
    
    batch_fill += 1
    print(f"----{batch_fill}----")
    if batch_fill == 1:
        # open a new file and write headers to it.
        outfile = open(batch_filepath, mode='w', newline='', encoding='utf-8')
        csv_writer = csv.DictWriter(outfile, fieldnames=['message'])
        
        # Write the header to the new CSV file
        csv_writer.writeheader()
        csv_writer.writerow({'message': syslog_data})
    
    # Check if batch size condition is met
    elif batch_fill < batch_size:
        # keep writing in the current file
        csv_writer.writerow({'message': syslog_data})
        
    else:    
        # close this file and make preparations to write to new file
        outfile.close()
        
        batch_number += 1
        batch_filename = f"batch_{batch_number}.csv"
        batch_filepath = os.path.join(output_dir, batch_filename)
        batch_fill = 0
