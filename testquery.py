from db import *
import time
import pyodbc

server = '192.168.123.254'
database = 'eHospital_NgheAn'
username = 'dashboard'
password = 'ttytanhson@2023'
cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER=' +
                    server+';DATABASE='+database+';UID='+username+';PWD=' + password)
cursor = cnxn.cursor()
def test():
    query = """
    SELECT
    SUM(SoLuong*DonGiaDoanhThu)
    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    WHERE ThoiGianXacNhan BETWEEN '2022-01-01' AND '2023-01-01'
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
    test()
    q_time = time.time() - start_time
    if min < q_time:
        min = q_time
    if max > q_time:
        max = q_time

    total += q_time

print(f'min q time: {max}; max q time {min}; average time: {total/10}')
