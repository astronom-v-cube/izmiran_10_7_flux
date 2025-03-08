from config import days_count
from utils import make_flux_for_hours
import logging
from tqdm import tqdm

logging.basicConfig(filename = 'SRH_10_7_data.log',  filemode='a', level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', encoding = "UTF-8")
logging.info('Start working...')

def get_data():

    datas = []

    for day in tqdm(range(1, days_count+1)):
        data = make_flux_for_hours(day)
        datas.append(data)

    print(datas)
    return(datas)

if __name__ == "__main__":

    get_data()