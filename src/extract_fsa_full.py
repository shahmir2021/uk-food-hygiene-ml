import requests
import time
import json
from pathlib import Path


# FSA establishments endpoint
URL = "https://api.ratings.food.gov.uk/Establishments"

# API version
HEADERS = {
    "x-api-version": "2"
}

# Where the scaled raw data will eventually be saved
OUTPUT_FILE = Path(
    "data/raw/fsa_establishments_full.json"
)

print("Stage 10 FSA extractor ready")

# --------------------------------
# 1. Test the FSA API
# --------------------------------

params = {
    "pageNumber": 1,
    "pageSize": 100
}

response = requests.get(
    URL,
    headers=HEADERS,
    params=params,
    timeout=30
)

# Stop immediately if the API request failed
response.raise_for_status()

data = response.json()

print("Status:", response.status_code)
print("Records on page:", len(data["establishments"]))
print("Metadata:")
print(data["meta"])