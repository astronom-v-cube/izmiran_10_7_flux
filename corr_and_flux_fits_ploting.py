import os
import logging
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from matplotlib.ticker import FuncFormatter
from tqdm import tqdm
import datetime
import sys
from get_canada_data import GetCANADA
from get_srh_data import GetSRH
import numpy as np
from utils import *
np.set_printoptions(threshold=np.inf)

logging.basicConfig(filename = 'SRH_10_7_data.log',  filemode='w', level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', encoding = "UTF-8")

download_fits = False
delete_fits = False
replace_zero = True
clear_from_minus = True
clear_with_std = True
freq = 0

logging.info('Start working...')

day_3 = (datetime.date.today() - datetime.timedelta(days=1))
day_2 = (datetime.date.today() - datetime.timedelta(days=2))
day_1 = (datetime.date.today() - datetime.timedelta(days=3))

day_3_str = str.replace(str(day_3), '-', '')
day_2_str = str.replace(str(day_2), '-', '')
day_1_str = str.replace(str(day_1), '-', '')

logging.info(f'Dates for analise: {day_3}, {day_2}, {day_1}')

file_3 = f'srh_0306_cp_{day_3_str}.fits'
file_2 = f'srh_0306_cp_{day_2_str}.fits'
file_1 = f'srh_0306_cp_{day_1_str}.fits'

dates_str = [day_3_str, day_2_str, day_1_str]
filenames = [file_3, file_2, file_1]

canada_data_3 = GetCANADA(datetime.datetime.combine(day_3, datetime.time(0, 0, 0)), datetime.datetime.combine(day_3, datetime.time(12, 0, 0)))[0][1]
canada_data_2 = GetCANADA(datetime.datetime.combine(day_2, datetime.time(0, 0, 0)), datetime.datetime.combine(day_2, datetime.time(12, 0, 0, 0)))[0][1]
canada_data_1 = GetCANADA(datetime.datetime.combine(day_1, datetime.time(0, 0, 0)), datetime.datetime.combine(day_1, datetime.time(12, 0, 0, 0)))[0][1]

if download_fits:
    GetSRH(filenames, dates_str)

fig0306, ax = plt.subplots()

try:
    hdul0306_3 = fits.open(os.path.join('data', file_3))
    hdul0306_2 = fits.open(os.path.join('data', file_2))
    hdul0306_1 = fits.open(os.path.join('data', file_1))

    freqs_0306 = np.array(hdul0306_3[1].data.copy(), dtype='float') / 1e6

    data_0306_3 = hdul0306_3[2].data.copy()
    data_0306_2 = hdul0306_2[2].data.copy()
    data_0306_1 = hdul0306_1[2].data.copy()

    times = [data_0306_3[freq][0], data_0306_2[freq][0], data_0306_1[freq][0]]
    fluxs = [data_0306_3[freq][3], data_0306_2[freq][3], data_0306_1[freq][3]]

    hdul0306_3.close()
    hdul0306_2.close()
    hdul0306_1.close()

except Exception as er:
    logging.info(f'One of the files was not found, or some kind of error occurred: {er}')
    sys.exit()

if delete_fits:
    for file in tqdm(filenames, desc='Удаление файлов'):
        os.unlink(file)

hourly_data_1, hourly_data_2, hourly_data_3 = {}, {}, {}
hourly_time_1, hourly_time_2, hourly_time_3 = {}, {}, {}
hourly_datas = [hourly_data_3, hourly_data_2, hourly_data_1]
hourly_times = [hourly_time_3, hourly_time_2, hourly_time_1]

colors = plt.cm.jet(np.linspace(0, 1, 3))

if replace_zero:
    times[0], fluxs[0] = replace_zero_average(times[0], fluxs[0])
    times[1], fluxs[1] = replace_zero_average(times[1], fluxs[1])
    times[2], fluxs[2] = replace_zero_average(times[2], fluxs[2])

if clear_from_minus:
    times[0], fluxs[0] = clear_from_minus_flux(times[0], fluxs[0])
    times[1], fluxs[1] = clear_from_minus_flux(times[1], fluxs[1])
    times[2], fluxs[2] = clear_from_minus_flux(times[2], fluxs[2])

if clear_with_std:
    times[0], fluxs[0] = clear_flux_with_std(times[0], fluxs[0], 0.75)
    times[1], fluxs[1] = clear_flux_with_std(times[1], fluxs[1], 0.75)
    times[2], fluxs[2] = clear_flux_with_std(times[2], fluxs[2], 0.75)

for index, flux in enumerate(fluxs):
    for hour in range(0, 12):
        start_time = hour * 3600
        end_time = (hour + 1) * 3600
        mask = (times[index] >= start_time) & (times[index] < end_time)
        if len(times[index][mask]) > 512:
            hourly_datas[index][hour] = np.mean(fluxs[index][mask])
            hourly_times[index][hour] = np.mean(times[index][mask])
        else:
            hourly_datas[index][hour] = np.nan
            hourly_times[index][hour] = np.nan

for x in range(0, 12):
    ax.scatter(hourly_times[0][x], hourly_datas[0][x], s = 40, c='b')

for x in range(0, 12):
    ax.scatter(hourly_times[1][x], hourly_datas[1][x], s = 40, c='k')

ax.scatter(np.mean(times[1]), canada_data_3, s = 70, c='k', marker='X')

ax.plot(times[0], fluxs[0], label=f'{freqs_0306[freq]} GHz', color=colors[freq])
ax.plot(times[1], fluxs[1], label=f'{freqs_0306[freq]} GHz', color=colors[freq])
ax.plot(times[2], fluxs[2], label=f'{freqs_0306[freq]} GHz', color=colors[freq])
# ax.plot(data_0306[freq][0], data_0306[freq][4], color=colors[freq]) stocks V


# print(times[0])
# print(times[1])
# print(times[2])
# plt.scatter(range(len(times[1])), times[1], c = 'g')
# plt.scatter(range(len(times[2])), times[2], c = 'r')
# plt.scatter(range(len(times[0])), times[0], c = 'b')

ax.legend()
ax.set_ylabel('s.f.u.')
ax.xaxis.set_major_formatter(FuncFormatter(format_seconds))
ax.set_xlabel('UT')
ax.grid(True)
plt.tight_layout()
plt.show()