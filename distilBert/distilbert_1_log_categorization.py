# -*- coding: utf-8 -*-
"""distilbert_1_log_categorization.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ySICnWzUoAHGiofg8knZNZwVYidwMZRR
"""

import os
import pandas as pd
from syslog_processing import Processing
from transformers import DistilBertTokenizer, DistilBertModel
import torch

obj = Processing()

input_csv_name = "GPN_Syslog_10000.csv"
input_csv_path = "data/GPN_Syslog_10000.csv"

"""STEP 1: Preprocess the Log Data for a particular router."""

desc = obj.get_specific_descriptions(input_csv_path= input_csv_path,physical_site_id='0001', geolocation_code='TLK', device_role='CR', device_model_number='M14', device_importance='01')

# Load log messages into a pandas DataFrame

df = pd.DataFrame(desc, columns=['log'])

"""STEP 2: Generate Embeddings with DistilBERT

Instead of classifying into rigid categories, we'll use DistilBERT to generate embeddings for each log message. These embeddings represent the semantics of each log message in a vector space.


"""

# Load the tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

# Tokenize the log messages
inputs = tokenizer(df['log'].tolist(), return_tensors='pt', padding=True, truncation=True)

# Generate embeddings using DistilBERT
with torch.no_grad():
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling to get sentence-level embeddings

"""Step 3: Clustering the Embeddings
Now that we have vector representations (embeddings) of each log message, we can apply clustering algorithms like K-Means, DBSCAN, or Agglomerative Clustering to group similar log messages together.
"""

"""
3.1 K-Means clustering
"""

# from sklearn.cluster import KMeans

# # Define the number of clusters (you can experiment with this number)
# num_clusters = 5

# # Apply K-Means clustering
# kmeans = KMeans(n_clusters=num_clusters, random_state=0)
# df['cluster'] = kmeans.fit_predict(embeddings.numpy())

"""3.2 DBSCAN (if you dont know how many clusters)"""

from sklearn.cluster import DBSCAN

# Apply DBSCAN clustering
dbscan = DBSCAN(eps=0.5, min_samples=5)
df['cluster'] = dbscan.fit_predict(embeddings.numpy())

"""Step 4: Visualizing and Analyzing the Clusters

Once you've clustered the log messages, you can inspect each cluster and identify potential patterns.
"""

# Group by cluster and inspect log messages
for cluster in df['cluster'].unique():
    print(f"Cluster {cluster}:")
    print(df[df['cluster'] == cluster]['log'].tolist())
    print("\n")

"""The clusters above tell us the seven major types of messages we are receiving in these logs. it will be helpful to deduplicate events and the unmber of clusters give an approximate idea of the distinct type of log messages."""

