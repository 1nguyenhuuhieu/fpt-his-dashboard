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
def phannhom_money():
    query = """
    SELECT 
    SUM(SoLuong*DonGiaDoanhThu) AS 'TongDoanhThu', XacNhanChiPhiChiTiet.Loai_IDRef
    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id

    WHERE ThoiGianXacNhan BETWEEN '2022-01-01' AND '2023-01-01'
    GROUP BY XacNhanChiPhiChiTiet.Loai_IDRef
    """
    try:
        q = cursor.execute(query).fetchall()
        return q
    except:
        print("Lỗi query phannhom_money")
        return 0    

total = 0
for i in range(10):
    start_time = time.time()

    t = phannhom_money()
    total += time.time() - start_time
    print("--- %s seconds ---" % (total))
