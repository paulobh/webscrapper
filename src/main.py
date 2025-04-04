# src/main.py
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

from urllib.parse import urljoin, unquote
import re

from pathlib import Path

import pandas as pd

import csv
import json
import os
from config import TARGET_URL, OUTPUT_FILE, DOWNLOAD_DIR, mapping_post_country
import utils

def get_html_content(url=TARGET_URL):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança uma exceção se a requisição falhar
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter a página: {e}")
    return html_content

def get_files_links(html_content, file_extension='.xlsx'):
    soup = BeautifulSoup(html_content, 'html.parser')  # 'lxml'

    file_links = []

    for a_tag in soup.find_all('a'):  # Find all <a> tags
        href = a_tag.get('href')
        if href and href.lower().endswith(file_extension):
            file_links.append(href)

    return file_links

def structure_data(file_links, base_url="https://travel.state.gov/", url=TARGET_URL):
    structured_data = {}

    for link in file_links:
        # 1. Remove the base URL and decode URL encoding
        absolute_url = urljoin(base_url, link)
        relative_path = absolute_url.replace(url, "").strip("/")  # Remove base and leading/trailing slashes
        relative_path = unquote(relative_path)  # Decode %20 to spaces, etc.
        

        # 2. Extract year, month, and type using regular expressions
        match = re.match(r'.*/FY(\d{4})/(\w+)\s*(\d{4}).*-\s*(.*?)\.xlsx', relative_path, re.IGNORECASE)

        if match:
            fiscal_year_str, month_str, year_str, report_type = match.groups()
            fiscal_year = int(fiscal_year_str)
            year = int(year_str)
            month = month_str.upper()
            date = f"{month} {year}"  # Combine month and year
            report_type = report_type.strip() # Remove extra spaces

            structured_data.setdefault(fiscal_year, {}).setdefault(date, {}).setdefault("reports", []).append(
            {
                "report_type": report_type,
                "url": absolute_url
            })

        else:
            print(f"Warning: Could not parse URL: {link}")

    return structured_data

def structured_data_download(structured_data, 
                             download_dir=DOWNLOAD_DIR, 
                             file_extension=".xlsx"
                            ):
    all_dataframes = defaultdict(list)
    for fiscal_year, year_data in structured_data.items():
        for date, date_data in year_data.items():
            for report_info in date_data["reports"]:
                report_type = report_info["report_type"]
                url = report_info["url"]

                # Construct a filename
                filename = f"{fiscal_year}_{date}_{report_type.replace(' ', '_')}{file_extension}"
                filepath = Path(download_dir) / filename

                # Download the file
                if utils.download_file(url, filepath):
                    try:
                        # Read the Excel file into a pandas DataFrame
                        df = pd.read_excel(filepath, header=1, skipfooter=1)
                        # print(filepath)
                        # break
                        # Add metadata columns
                        df["Fiscal Year"] = fiscal_year
                        df["Date"] = date
                        df['Datetime'] = pd.to_datetime(date, format='%B %Y')
                        # df["Country"] = df["Post"].map(mapping_post_country)
                        df["Report Type"] = report_type
                        df["Source URL"] = url

                        all_dataframes[report_type].append(df)
                    except Exception as e:
                        print(f"Error reading or processing {filepath}: {e}")
                else:
                    print(f"Failed to download {url}")

    print("concatenating")
    #Create the directory before attempting to write to it.
    output_directory = os.path.abspath("data/dataframe")
    os.makedirs(output_directory, exist_ok=True)

    for type, dfs_type in all_dataframes.items():
        dfs = pd.concat(dfs_type, ignore_index=True)
        filepath = Path(f"{output_directory}/all_data_{type}.csv")
        print(f"saving {len(dfs)} records, at:  {filepath}")
        dfs.to_csv(filepath) #correct path.
    return dfs

def main():
    # 1. Obter o HTML
    html_content = get_html_content(url=TARGET_URL)

    # 2. Analisar o HTML
    file_links = get_files_links(html_content, file_extension='.xlsx')

    # 3. Encontrar e Extrair Dados
    structured_data = structure_data(file_links, base_url="https://travel.state.gov/", url=TARGET_URL)

    # 4. Download, Estruturar e Imprimir/Salvar os Dados
    dfs = structured_data_download(structured_data, download_dir=DOWNLOAD_DIR, file_extension=".xlsx")


if __name__ == "__main__":
    main()  # Call the main() function from the main module