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
SELECT xetnghiem.ResultDateTime, NoiDungChiTiet, ServiceName,
    xetnghiem_ketqua.Unit, xetnghiem_ketqua.Value,
    xetnghiem_ketqua.Value2, xetnghiem_ketqua.MinLimited, xetnghiem_ketqua.MaxLimited
    FROM [eHospital_NgheAn].[dbo].[CLSYeuCau] as yeucau
    INNER JOIN [eLab_NgheAn].[dbo].[LabResult] as xetnghiem
    ON yeucau.CLSYeuCau_Id = xetnghiem.RequestID
    INNER JOIN [eLab_NgheAn].[dbo].[LabResultDetail] as xetnghiem_ketqua
    ON xetnghiem.ResultID = xetnghiem_ketqua.ResultID
    INNER JOIN [eLab_NgheAn].[dbo].[DIC_Service] as service_dict
    on service_dict.ServiceID = xetnghiem_ketqua.ServiceID
    where CLSYeuCau_Id = 271482 AND AssayCode IS NOT NULL
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
