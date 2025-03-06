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

def GetSRH(filename, date_str):
    base_url = 'https://ftp.rao.istp.ac.ru/SRH/corrPlot/'

    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code != 200:
            logging.error(f"Failed to access {base_url}, status code: {response.status_code}")
            return
    except requests.RequestException as e:
        logging.error(f"Error accessing {base_url}: {e}")
        return

    file_url = f'{base_url}/{date_str[0:4]}/{date_str[4:6]}/{filename}'
    if not os.path.exists('data'):
        os.makedirs('data')
    if os.path.isfile(f'data/{filename}'):
        os.unlink(f'data/{filename}')
    if not download_file(file_url, f'data/{filename}'):
        logging.error(f"Failed to download {filename} from {file_url}")

    logging.info("Download process completed")