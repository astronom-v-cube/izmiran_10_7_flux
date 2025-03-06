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

def clear_from_minus_flux(array_time:list, array_data:list, limit:int = 15):
    """
    Функция чистки значений данных + соответствующих значений времени от значений с потоком меньше нуля, или другой заданной величины (чистим от выбросов вниз)
    """
    mask = array_data >= limit
    array_time = array_time[mask]
    array_data = array_data[mask]
    return array_time, array_data

def clear_flux_with_std(array_time: list, array_data: list, coef: int = 0.75):
    """
    Выкидываем артефакты, которые дают отклонение в данных более std*coef. И вспышки туда же. (чистим от выбросов вверх)
    """
    times = list(array_time)
    datas = list(array_data)

    std = np.std(datas)
    mean = np.mean(datas)

    filtered_times = []
    filtered_datas = []

    for index in range(len(datas)):
        if datas[index] <= mean + coef * std:
            filtered_times.append(times[index])
            filtered_datas.append(datas[index])

    return np.array(filtered_times), np.array(filtered_datas)

def make_flux_for_hours(timedelta):
    """
    Получить значения потока на день, который отстоял на timedelta от сегодняшнего
    """

    day = (datetime.date.today() - datetime.timedelta(days=timedelta))
    day_str = str.replace(str(day), '-', '')
    logging.info(f'Date for analise: {day}')
    file = f'srh_0306_cp_{day_str}.fits'

    if download_fits:
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
        os.unlink(file)

    if replace_zero:
        time_line, flux = replace_zero_average(time_line, flux)

    if clear_from_minus:
        time_line, flux = clear_from_minus_flux(time_line, flux)

    if clear_with_std:
        time_line, flux = clear_flux_with_std(time_line, flux, 0.75)

    hourly_data = {}
    hourly_time = {}

    for hour in range(0, 12):
        temp_day_and_time = datetime.datetime.combine(day, datetime.time(hour=hour))
        start_time = hour * 3600
        end_time = (hour + 1) * 3600
        mask = (time_line >= start_time) & (time_line < end_time)
        if len(time_line[mask]) > 512:
            hourly_data[temp_day_and_time] = np.mean(flux[mask])
            hourly_time[temp_day_and_time] = np.mean(time_line[mask])
        else:
            hourly_data[temp_day_and_time] = np.nan
            hourly_time[temp_day_and_time] = np.nan

    if graphs:

        fig, ax = plt.subplots()
        for key, value in hourly_data.items():
            plt.scatter(hourly_time[key], value, s=70, c='b')
        # ax.scatter(np.mean(time), canada_data_3, s = 70, c='k', marker='X')
        plt.plot(time_line, flux)
        plt.ylabel('s.f.u.')
        plt.xlabel('UT')
        ax.xaxis.set_major_formatter(FuncFormatter(format_seconds))
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return hourly_time, hourly_data