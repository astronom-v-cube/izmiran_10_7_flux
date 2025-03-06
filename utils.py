import matplotlib.pyplot as plt

SMALL_SIZE = 10
MEDIUM_SIZE = 16
BIGGER_SIZE = 18

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def format_seconds(x, pos):
    hours = int(x // 3600)
    minutes = int((x % 3600) // 60)
    seconds = int(x % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def replace_zero_average(array_time, array_data):
    for i in range(2, len(array_time) - 1):
        if array_time[i] == 0 or array_time[i] < array_time[i-1]:
            average_time = (array_time[i - 1] + array_time[i + 1]) / 2.0
            array_time[i] = average_time
            for z in range(3):
                average_data = (array_data[z][i - 1] + array_data[z][i + 1]) / 2.0
                array_data[z][i] = average_data

def clear_time_line(array_time):
    for i in range(0, len(array_time) - 1):
        if array_time[i] < array_time[i-1]:
            array_time[i] = None
    return array_time