from db import *
from models import *
from datetime import date
# Convert to google chart data
def convert_to_chart(list):
    chart = dict(list)
    chart = [[k, v] for k, v in chart.items()]

    return chart

# Convert to google chart data with first param = date
def convert_to_chart_date(list):
    chart = dict(list)
    chart = [[k.strftime("%A %Y-%m-%d"), v] for k, v in chart.items()]

    return chart

# Lấy danh sách khoa
def get_department_id_list(department_id):
    if department_id == 23092310:
        return [2309, 2310]
    elif department_id == (12442304):
        return [1244, 2304]
    else:
        return [department_id]

def diff_days(start, end):

    try:
        start_day = start.date()
        end_day = end.date()

    except:
        start_day = start
        end_day = end
    diff = (end_day - start_day).days

    return diff