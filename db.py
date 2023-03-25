from flask import g

import pyodbc
import sqlite3
# Kết nối database sql server
def get_db():
    server = '192.168.1.5'
    database = 'eHospital_NgheAn11'
    username = 'homereader'
    password = 'ttytanhson@123'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server+';DATABASE='+database+';UID='+username+';PWD=' + password)
    return cnxn

server_location = 'work'

# def get_db():
#     if server_location == 'home':
#         if 'db' not in g:
#             g.db = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}', server='localhost', database='eHospital_NgheAn',
#                                 trusted_connection='yes')
#             return g.db
#     else:
#         if 'db' not in g:
#             server = '192.168.123.254'
#             database = 'eHospital_NgheAn'
#             username = 'dashboard'
#             password = 'ttytanhson@2023'
#             g.db = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER=' +
#                                 server+';DATABASE='+database+';UID='+username+';PWD=' + password)
#             return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def get_db_dashboard():
    if 'db_dashboard' not in g:
        g.db = sqlite3.connect("dashboard.db")
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db_dashboard(e=None):
    db = g.pop('db_dashboard', None)

    if db is not None:
        db.close()