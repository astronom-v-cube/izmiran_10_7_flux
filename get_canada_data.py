from mysql.connector import connect, Error
from datetime import datetime, timedelta

def GetCANADA(startd, endd):
    try:
        with connect(
            host="crsb.izmiran.ru",
            user="users",
            password="users!!",
            database = "solar"
        ) as connection:
            # print(connection)
            #select_movies_query = "SELECT dt FROM rt_izmiran LIMIT 5"
            select_movies_query = """SELECT * FROM radio_f107 WHERE dt BETWEEN '%s' AND '%s'""" % (startd, endd)
            with connection.cursor() as cursor:
                cursor.execute(select_movies_query)
                radio_data = cursor.fetchall()

    except Error as e:
        print(e)

    return radio_data

# sdt_g = datetime(2025, 3, 1, 0, 0, 0) #9.2.2024
# edt_g = datetime(2025, 3, 5, 0, 0, 0) #18.2.2024

# DATA_F107 = GetCANADA(sdt_g, edt_g)
# print(DATA_F107)


