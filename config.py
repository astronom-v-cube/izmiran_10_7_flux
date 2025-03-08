import matplotlib.pyplot as plt

# Скачивать файлы или брать загруженные из папки data. False удобно задавать для отладки кода, чтобы не ждать скачивания каждый раз
download_fits = True

# Удалять ли файлы после загрузки и чтения
delete_fits = False

# Заменить битые (нулевые) моменты времени на среднее между соседними
replace_zero = True

# Убрать поток меньше и больше заданной величины
clear_from_nonrealistic = True
under_limit = 62
uppeer_limit = 1000

# Очищать ли выбросы от артефактов с помощью стандартного отклонения, каким методом
clear_with_std = True
clear_std_method = 'dmitry' # 'dmitry' or 'sofia'

# Рисовать ли график для каждого дня
graphs = True

# Частота с которой работаем
freq = 0    # 0 - 2.8 GHz, 1 - 3.0 GHz, 2 - 3.2 GHz, ...

# Коэффициент, на который умножаем std, все что выше\ниже отрезаем
std_coef = 1.2

# Сколько дней назад берем для анализа
days_count = 10

####################################
SMALL_SIZE = 12
MEDIUM_SIZE = 16
BIGGER_SIZE = 18

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize