import os
import logging
import time
import requests

def download_file(url, filename, retries=10, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                logging.info(f"Successfully downloaded {filename}")
                return True

            else:
                logging.warning(f"Failed to download {filename}, status code: {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1}: Error downloading {filename}: {e}")
        time.sleep(2 ** attempt)
    return False

def GetSRH(filenames: list, dates_str: list):
    for index, date in enumerate(dates_str):
        base_url = f'https://ftp.rao.istp.ac.ru/SRH/corrPlot/'

        try:
            response = requests.get(base_url, timeout=10)
            if response.status_code != 200:
                logging.error(f"Failed to access {base_url}, status code: {response.status_code}")
                continue
        except requests.RequestException as e:
            logging.error(f"Error accessing {base_url}: {e}")
            continue

        file_url = f'{base_url}/{date[0:4]}/{date[4:6]}/{filenames[index]}'
        if os.path.isfile(f'data/{filenames[index]}'):
            os.unlink(f'data/{filenames[index]}')
        if not download_file(file_url, f'data/{filenames[index]}'):
            logging.error(f"Failed to download {filenames[index]} from {file_url}")

    logging.info("Download process completed")
