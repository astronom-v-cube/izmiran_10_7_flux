import matplotlib.pyplot as plt
import numpy as np
from config import *
import os
import logging
from astropy.io import fits
from matplotlib.ticker import FuncFormatter
import datetime
import sys
from get_srh_data import GetSRH

def format_seconds(x, pos):
    """
    Это для нормальной оси Х при построении графика (если построения включены)
    """
    hours = int(x // 3600)
    minutes = int((x % 3600) // 60)
    seconds = int(x % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def smooth(flux_I, delta:int, iter:int):
    flux = np.array(flux_I)
    for i in range(iter): ##### ERROR
        for i in range(len(flux_I)):
            flux[i] = np.mean(flux[:delta])
        for i in range(delta, len(flux)-delta-1):
            flux[i] = np.mean(flux[i-delta:i+delta])
        for i in range[: (len(flux) - delta)]:
            flux[i] = np.mean(flux[:delta])
    return flux

def truncate_forest(time, flux, minutes):
    return  time[:-15*60], flux[:-minutes*60]

def truncate_std(flux_I, k):
    flux = np.array(flux_I)
    sigm = (np.mean((flux - np.mean(flux))**2))**(1/2)
    E_math = np.mean(flux)
    for i in range(len(flux)):
        if (flux[i] >= E_math + sigm*k) or (flux[i] <= E_math - sigm):
                flux[i]= E_math
    print('sigm, E_math =   ', sigm, E_math)
    return flux, sigm, E_math

def replace_zero_average(array_time, array_data):
    """
    Заменяем нулевые значения и значения, которые меньше предыдущего в массиве времени на средние значения соседних элементов
    """
    for i in range(2, len(array_time) - 1):
        if array_time[i] == 0 or array_time[i] < array_time[i-1]:
            average_time = (array_time[i - 1] + array_time[i + 1]) / 2.0
            array_time[i] = average_time
            for z in range(3):
                average_data = (array_data[z][i - 1] + array_data[z][i + 1]) / 2.0
                array_data[z][i] = average_data
    return array_time, array_data

def clear_from_nonrealistic_flux(array_time:list, array_data:list, under_limit:int = under_limit, uppeer_limit:int = uppeer_limit):
    """
    Функция чистки значений данных + соответствующих значений времени от значений с потоком меньше минимально возможной величины в минимуме солнечной активности
    """
    mask = (array_data >= under_limit) & (array_data <= uppeer_limit)
    array_time = array_time[mask]
    array_data = array_data[mask]
    return array_time, array_data

def clear_flux_with_std(array_time: list, array_data: list, coef: int = 1):
    """
    Выкидываем артефакты, которые дают отклонение в данных более std*coef. И вспышки туда же
    """
    times = list(array_time)
    datas = list(array_data)

    std = np.std(datas)
    mean = np.mean(datas)

    filtered_times = []
    filtered_datas = []

    for index in range(len(datas)):
        if (datas[index] <= mean + coef * std) and (datas[index] >= mean - coef * std):
            filtered_times.append(times[index])
            filtered_datas.append(datas[index])

    return np.array(filtered_times), np.array(filtered_datas), mean, std

def clear_daily_flux(time, flux, coef=1):

    #head, time, flux_I, flux_V, freq = get_flux_data(datapath,filename, 2)
    flux_s1 = smooth(flux, 3, 10)
    flux_t1, sigm, E_math = truncate_std(flux_s1, coef)
    #flux_t2, sigm, E_math = truncate_std(flux_t1, coef)
    #flux_s2 = smooth(flux_t2, 20, 5)
    #flux_t3, sigm, E_math = truncate_std(flux_s2, coef)

    return time, flux_t1, sigm, E_math

def make_flux_for_hours(timedelta):
    """
    Получить значения потока на день, который отстоял на timedelta от сегодняшнего
    """

    day = (datetime.date.today() - datetime.timedelta(days=timedelta))
    day_str = str.replace(str(day), '-', '')
    logging.info(f'Date for analise: {day}')
    file = f'srh_0306_cp_{day_str}.fits'

    if download_fits:
        if not delete_fits:
            if not os.path.exists(f'data/{file}'):
                GetSRH(file, day_str)
        else:
            GetSRH(file, day_str)

    try:
        hdul = fits.open(os.path.join('data', file))
        data = hdul[2].data.copy()
        hdul.close()

        time_line = data[freq][0]
        flux = data[freq][3]

    except Exception as er:
        logging.info(f'One of the files was not found, or some kind of error occurred: {er}')
        sys.exit()

    if delete_fits:
        os.unlink(f'data/{file}')

    if replace_zero:
        time_line, flux = replace_zero_average(time_line, flux)

    if clear_from_nonrealistic:
        time_line, flux = clear_from_nonrealistic_flux(time_line, flux)

    if clear_with_std:
        if clear_std_method == 'dmitry':
            time_line, flux, mean, std = clear_flux_with_std(time_line, flux, std_coef)
        elif clear_std_method == 'sofia':
            time_line, flux, mean, std = clear_daily_flux(time_line, flux, 1)

    hourly_data = {}
    hourly_time = {}

    for hour in range(0, 12):
        temp_day_and_time = datetime.datetime.combine(day, datetime.time(hour=hour))
        start_time = hour * 3600 + 1800
        end_time = (hour + 1) * 3600 + 1800
        mask = (time_line >= start_time) & (time_line < end_time)
        if len(time_line[mask]) > 512:
            hourly_data[temp_day_and_time] = np.mean(flux[mask])
            hourly_time[temp_day_and_time] = np.mean(time_line[mask])
        else:
            hourly_data[temp_day_and_time] = np.nan
            hourly_time[temp_day_and_time] = np.nan

    if graphs:
        if not os.path.exists('img'):
            os.makedirs('img')

        fig, ax = plt.subplots(figsize=(9, 6))
        for key, value in hourly_data.items():
            plt.scatter(hourly_time[key], value, s=70, c='orange', zorder = 4)
        # ax.scatter(np.mean(time), canada_data_3, s = 70, c='k', marker='X')
        plt.plot(time_line, flux, zorder=3)
        plt.ylabel('s.f.u.')
        plt.xlabel('UT')
        ax.xaxis.set_major_formatter(FuncFormatter(format_seconds))
        plt.grid(True)
        # plt.ylim(min(flux)-5, max(flux)+5)
        plt.axhline(mean, c='k', linestyle='--', label='mean')
        plt.axhline(mean+std*std_coef, c='r', linestyle=':', label=r'mean $\pm$ std*coef')
        plt.axhline(mean-std*std_coef, c='r', linestyle=':')
        ax.set_xticks([i * 3600 for i in range(0, 12)])
        ax.set_xticklabels([f"{i:02}:00" for i in range(12)])
        ax.axvline(x=4*3600, color='g', linestyle='--', linewidth=2, label='midday', zorder=2)
        plt.legend(framealpha = 1)
        plt.tight_layout()
        plt.savefig(f'img/{file[:-5]}.png', dpi=300)

    return hourly_data