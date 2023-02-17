import pyodbc
import sqlite3 

con = sqlite3.connect("dashboard.db")
cur = con.cursor()

#get data from sqlserver
server = '192.168.123.254' 
database = 'eHospital_NgheAn_Dictionary' 
username = 'sa' 
password = 'toanthang' 

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

cursor.execute("""SELECT
NhanVien_ID, TenNhanVien, NgaySinh, PhongBan_Id
FROM dbo.NhanVien
"""
) 

row = cursor.fetchall() 


for i in row:

    cur.execute("""
    INSERT INTO doctor VALUES (?,?,0,?,?,0)
    """,
    (i[0], i[3], i[1], i[2])
    )
    
con.commit()
con.close()
cnxn.close()