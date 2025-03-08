import os
import logging
import time
import requests
from config import delete_fits

def download_file(url, filename, retries=10, timeout=45):
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

def GetSRH(filename, date_str, max_retries_connect=5):

    base_url = 'https://ftp.rao.istp.ac.ru/SRH/corrPlot/'

    for attempt in range(max_retries_connect):

        try:
            response = requests.get(base_url, timeout=10)
            if response.status_code != 200:
                logging.error(f"Failed to access {base_url}, status code: {response.status_code}")

            else:
                logging.info(f"Status code: {response.status_code}")
                return

        except requests.RequestException as e:
            logging.error(f"Error accessing {base_url}: {e}")
            if attempt < max_retries_connect - 1:
                time.sleep(2)
            else:
                logging.error(f"All {max_retries_connect} attempts check status code failed")

    file_url = f'{base_url}/{date_str[0:4]}/{date_str[4:6]}/{filename}'
    if not os.path.exists('data'):
        os.makedirs('data')
    if os.path.isfile(f'data/{filename}') and delete_fits:
        os.unlink(f'data/{filename}')
    if not download_file(file_url, f'data/{filename}'):
        logging.error(f"Failed to download {filename} from {file_url}")

    logging.info("Download process completed")