import schedule
import time
import subprocess
import json

with open('config.json', 'r') as f:
    config = json.load(f)
    
time_interval = config["ingest_interval"]   

def job():
    print("Running the scheduled job...")
    subprocess.run(["python", "stage2_process_batch_data.py"])

# Schedule the job every 5 minutes 3 seconds
schedule.every(3).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
