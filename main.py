import pyodbc 
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = '192.168.123.254' 
database = 'eHospital_NgheAn' 
username = 'sa' 
password = 'toanthang' 
# ENCRYPT defaults to yes starting in ODBC Driver 18. It's good to always specify ENCRYPT=yes on the client side to avoid MITM attacks.
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
cursor.execute("""SELECT TOP 10 * 
FROM dbo.TiepNhan
ORDER BY TiepNhan_Id DESC;
""") 
row = cursor.fetchone() 

for col in row:
    print(col)

