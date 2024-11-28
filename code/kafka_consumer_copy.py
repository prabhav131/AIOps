import csv
from kafka import KafkaConsumer
from syslog_processing import Processing
import time
import os


start = time.time()

# processing = Processing() # creating object

# output_dir = "processed_data"

# if not os.path.isdir(output_dir):
#         os.makedirs(output_dir)
        
# output_csv_name = "live_kafka_processed_data.csv"
# output_csv_path = os.path.join(output_dir,output_csv_name)
# outfile = open(output_csv_path, mode='w', newline='', encoding='utf-8')

# csv_writer = csv.DictWriter(outfile, fieldnames=processing.headers)

# # Write the header to the new CSV file
# csv_writer.writeheader()

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
# Process messages from the Kafka topic

for message in consumer:
    
    # if count == 100:
    #     break
    syslog_data = message.value.decode('utf-8')
    print(f"Received syslog data: {syslog_data}")
    time_of_log_receiving = time.time()
    
    data_collection.append(syslog_data)
    count+=1
    # Add your processing logic here
    # processed_syslog_data_dict = processing.end_to_end_processing_single_live_message(time.time(),syslog_data)
    # print(processed_syslog_data_dict)
    # csv_writer.writerow(processed_syslog_data_dict)

# print(data_collection)

# outfile.close()
print(len(data_collection))
end = time.time()

print(f"time for execution is:  {end-start}")
