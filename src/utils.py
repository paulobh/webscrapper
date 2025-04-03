# src/utils.py
import requests
import csv
import json
import os
from src.config import TARGET_URL, OUTPUT_FILE, DOWNLOAD_DIR


def save_data(data, filename):
    if filename.endswith('.csv'):
        _save_as_csv(data, filename)
    elif filename.endswith('.json'):
        _save_as_json(data, filename)
    else: # Save as a simple text
        _save_as_txt(data,filename)

def _save_as_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys() if data else []
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def _save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4) # Use indent for pretty printing

def _save_as_txt(data, filename):
     with open(filename, 'w', encoding='utf-8') as textfile:
        for item in data:
            url = item.get('url')
            if url:
                textfile.write(url + '\n')

def download_file(url, filepath):
    """Downloads a file from a URL and saves it to a local file."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True) 
    try:
        response = requests.get(url, stream=True)  # stream=True for large files
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(filepath, 'wb') as f:  # Open in binary write mode ('wb')
            for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                f.write(chunk)
        return True  # Return True if download was successful

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"Error saving file {filepath}: {e}")
        return False