from db import *
import time
import pyodbc

server = '192.168.123.254'
database = 'eHospital_NgheAn'
username = 'dashboard'
password = 'ttytanhson@2023'
cnxn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}', server='localhost', database='eHospital_NgheAn',
                                trusted_connection='yes')
# cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER=' +
#                     server+';DATABASE='+database+';UID='+username+';PWD=' + password)
cursor = cnxn.cursor()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def test():
    query = """
    SELECT SUM(t2.SoLuong * t2.DonGiaDoanhThu)
    FROM
    (SELECT XacNhanChiPhi_Id FROM XacNhanChiPhi WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN '2022-01-01' AND '2023-01-01') as t1
    INNER JOIN XacNhanChiPhiChiTiet as t2
    ON t1.XacNhanChiPhi_Id = t2.XacNhanChiPhi_Id
    """
    try:
        q = cursor.execute(query).fetchall()
        return q
    except:
        print("Lỗi query phannhom_money")
        return 0    
def test2():
    query = """
    SELECT SUM(SoLuong * DonGiaDoanhThu)
    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN '2022-01-01' AND '2023-01-01'
    """
    try:
        q = cursor.execute(query).fetchall()
        return q
    except:
        print("Lỗi query phannhom_money")
        return 0    

total = 0
min = -100000
max = 100000
for i in range(10):
    start_time = time.time()
    t = test()
    q_time = time.time() - start_time
    if min < q_time:
        min = q_time
    if max > q_time:
        max = q_time

    total += q_time

print(f'{bcolors.OKGREEN}min q time: {max}; {bcolors.FAIL}max q time {min}; {bcolors.OKBLUE}average time: {total/10}')

total = 0
min = -100000
max = 100000
for i in range(10):
    start_time = time.time()
    t = test2()
    q_time = time.time() - start_time
    if min < q_time:
        min = q_time
    if max > q_time:
        max = q_time

    total += q_time

print(f'{bcolors.OKGREEN}min q time: {max}; {bcolors.FAIL}max q time {min}; {bcolors.OKBLUE}average time: {total/10}')
