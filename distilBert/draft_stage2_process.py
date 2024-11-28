import os
import time
import pandas as pd
import csv

batch_data_dir = "batch_data" # raw data
processed_data_dir = "processed_data" # final processed data

# Create processed data directory if it doesn't exist
if not os.path.isdir(processed_data_dir):
    os.makedirs(processed_data_dir)

def preprocess_data(messages):
    """Basic preprocessing on the raw data (customize as needed)."""
    return [message.strip() for message in messages]  # Example: strip whitespace

def process_csv_file(file_path):
    """Load CSV file, preprocess it, process it through LLM, and save the insights."""
    batch_data = pd.read_csv(file_path)
    messages = batch_data['message'].tolist()

    # Preprocess the data
    preprocessed_messages = preprocess_data(messages)

    # Extract insights using the LLM
    insights = llm.extract_insights(preprocessed_messages)

    # Save insights to a new CSV
    insight_filename = f"insights_{os.path.basename(file_path)}"
    insight_filepath = os.path.join(processed_data_dir, insight_filename)

    with open(insight_filepath, mode='w', newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(['insight'])  # Header for insights

        for insight in insights:
            csv_writer.writerow([insight])

    print(f"Processed and saved insights to {insight_filepath}")

# Monitor the batch_data directory for new files
processed_files = set()

while True:
    # Get the list of CSV files in the batch_data directory
    batch_files = [f for f in os.listdir(batch_data_dir) if f.endswith('.csv')]

    # Process each new file
    for batch_file in batch_files:
        batch_file_path = os.path.join(batch_data_dir, batch_file)

        if batch_file_path not in processed_files:
            print(f"Processing {batch_file}...")
            process_csv_file(batch_file_path)
            processed_files.add(batch_file_path)

    # Sleep for a few seconds before checking again
    time.sleep(5)  # Adjust the frequency as needed
