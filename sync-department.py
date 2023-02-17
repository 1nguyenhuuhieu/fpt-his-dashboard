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
PhongBan_Id, TenPhongBan
FROM dbo.DM_PhongBan
"""
) 

row = cursor.fetchall() 


for i in row:

    cur.execute("""
    INSERT INTO department VALUES (?,?)
    """,
    (i[0], i[1])
    )
    
con.commit()
con.close()
cnxn.close()