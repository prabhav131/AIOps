import csv
from kafka import KafkaConsumer
from syslog_processing import Processing
import time
import os


start = time.time()

processing = Processing() # creating object

output_dir = "processed_data"

# are you processing line by line?
is_processing = False

if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
        
output_processed_csv_name = "live_kafka_processed_data.csv"
output_raw_csv_name = "live_kafka_raw_data.csv"

if is_processing:
    output_csv_path = os.path.join(output_dir,output_processed_csv_name)
else:
    output_csv_path = os.path.join(output_dir,output_raw_csv_name)    
# output_csv_path = os.path.join(output_dir,output_processed_csv_name)
outfile = open(output_csv_path, mode='w', newline='', encoding='utf-8')

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'udp_input',
    bootstrap_servers=['172.31.252.214:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='syslog-group-' + str(int(time.time()))
)

print("Starting to consume messages from udp_input topic...")
count = 0
data_collection = []


if is_processing:
    csv_writer = csv.DictWriter(outfile, fieldnames=processing.headers)
else:
    csv_writer = csv.DictWriter(outfile, fieldnames=['message'])


# Write the header to the new CSV file
csv_writer.writeheader()

# Consume messages from the Kafka topic
for message in consumer:
    
    if count == 100:
        break
    syslog_data = message.value.decode('utf-8')
    print(f"Received syslog data: {syslog_data}")
    time_of_log_receiving = time.time()
    
    data_collection.append(syslog_data)
    count+=1
    # Add your processing logic here: 
    # TO DO if processng takes time, it might skip ingesting some data.
    
    if is_processing:
        processed_syslog_data_dict = processing.end_to_end_processing_single_live_message(time.time(),syslog_data)
        # print(processed_syslog_data_dict)
        csv_writer.writerow(processed_syslog_data_dict)
    else:
        csv_writer.writerow({'message': syslog_data})    

# print(data_collection)

outfile.close()
print(len(data_collection))
end = time.time()

print(f"time for execution is:  {end-start}")