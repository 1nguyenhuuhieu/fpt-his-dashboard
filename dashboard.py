from flask import Flask,redirect, url_for, flash
from flask import render_template
import pyodbc
from datetime import date, datetime, timedelta
from dateutil.relativedelta import *
from time import time

from flask import jsonify
import json
import collections

import sql_query

from sqlquery import hospitalized as query_hospitalized
from sqlquery import confirmed as query_confirmed
from sqlquery import revenue as query_revenue
from sqlquery import visited as query_visited
from sqlquery import transfer as query_transfer
from sqlquery import surgery as query_surgery
from sqlquery import born as query_born
from sqlquery import patient as query_patient
from sqlquery import report as query_report
from sqlquery import user as query_user

from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

from flask import session
from flask import request
import sqlite3

import pandas as pd


# Kết nối database sql server
# def get_db():
#     server = '192.168.123.254'
#     database = 'eHospital_NgheAn'
#     username = 'sa'
#     password = 'toanthang'
#     cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
#                           server+';DATABASE='+database+';UID='+username+';PWD=' + password)
#     return cnxn
# def get_db():
#     server = '192.168.123.254'
#     database = 'eHospital_NgheAn'
#     username = 'sa'
#     password = 'toanthang'
#     cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER=' +
#                           server+';DATABASE='+database+';UID='+username+';PWD=' + password)
#     return cnxn

def get_db():
    cnxn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}', server='localhost', database='eHospital_NgheAn',               
               trusted_connection='yes')
    return cnxn

def get_change(current, previous):
    if not current:
        current = 0
    if not previous:
        previous = 0
    if current == previous:
        return (current == previous, 0)
    try:
        return (current > previous, round((abs(current - previous) / previous) * 100, 1))
    except ZeroDivisionError:
        return (current > previous, 0)
    
def get_percent(current, previous):
    if not current:
        current = 0
    if not previous:
        previous = 0
    if current == previous:
        return (True, 100)
    try:
        return (current > previous, round((current/ previous) * 100, 1))
    except ZeroDivisionError:
        return (current > previous, 0)

# Convert to google chart data
def convert_to_chart(list):
    chart = dict(list)
    chart = [[k, int(v)] for k, v in chart.items()]

    return chart

# Convert to google chart data with first param = date
def convert_to_chart_date(list):

    chart = dict(list)
    chart = [[k.strftime("%A %Y-%m-%d"), int(v)] for k, v in chart.items()]

    return chart

# get day of week, month, year
def get_day(day):
    day_dict = {}
    try:
        today = datetime.strptime(day, '%Y-%m-%d')
    except:
        today = date.today()

    yesterday = today - timedelta(days=1)
    mon_day = today - timedelta(days=today.weekday())
    last_week_monday = mon_day - timedelta(days=7)
    last_week_sun_day = last_week_monday + timedelta(days=6)
    twolast_week_monday = last_week_monday - timedelta(days=7)
    twolast_week_sun_day = last_week_sun_day - timedelta(days=7)
    first_month_day = today.replace(day=1)
    last_first_month_day = first_month_day + relativedelta(months=-1)
    last_end_month_day = first_month_day + timedelta(days=-1)
    first_year_day = today.replace(day=1, month=1)
    last_first_year_day = first_year_day + relativedelta(years=-1)
    end_last_year_day = first_year_day + timedelta(days=-1)

    day_dict['today'] = today
    day_dict['yesterday'] = yesterday
    day_dict['mon_day'] = mon_day
    day_dict['last_week_monday'] = last_week_monday
    day_dict['last_week_sun_day'] = last_week_sun_day
    day_dict['twolast_week_monday'] = twolast_week_monday
    day_dict['twolast_week_sun_day'] = twolast_week_sun_day
    day_dict['first_month_day'] = first_month_day
    day_dict['last_first_month_day'] = last_first_month_day
    day_dict['last_end_month_day'] = last_end_month_day
    day_dict['first_year_day'] = first_year_day
    day_dict['last_first_year_day'] = last_first_year_day
    day_dict['end_last_year_day'] = end_last_year_day
    
    return day_dict

# Lấy danh sách khoa
def get_department_id_list(department_id):
    if department_id == 23092310:
        return [2309,2310]
    elif department_id == (12442304):
        return [1244,2304]
    else:
        return [department_id]
    

# -------------------------------------------------------------
app = Flask(__name__)

app.secret_key = 'edcac19b15911795fe4a7ece9e27613a8565d1f549cb7535f04c035bffc91315'

Breadcrumbs(app=app)


# register zip filter for pararell loop
app.jinja_env.filters['zip'] = zip

# Trang chủ
@app.route("/dashboard/<string:day_query>")
@app.route("/")
@register_breadcrumb(app, '.', 'Trang chủ')
def home(day_query=None):
    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()
    # lấy ngày xem dashboard
    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']

    # Tổng Doanh thu trong 1 ngày
    today_money = query_revenue.total_day(today, cursor)
    today_money_format = f'{today_money:,}'
    yesterday_money = query_revenue.total_day(yesterday, cursor)
    percent_doanhthu = get_change(today_money, yesterday_money)
    top_card = ('fa-solid fa-money-bill',"Tổng doanh thu", today_money_format, percent_doanhthu)


    # Tổng Doanh thu dược
    today_money_medicine = query_revenue.service_medicine_day(today, 'DU', cursor)
    percent_duoc = get_percent(today_money_medicine, today_money )

    medicine_card = (today_money_medicine, percent_duoc[1] )
    
    # Tổng Doanh thu dịch vụ
    today_money_service = query_revenue.service_medicine_day(today, 'DV', cursor)
    percent_service = get_percent(today_money_service, today_money )

    service_card = (today_money_service, percent_service[1] )


    # Thống kê bệnh nhân
    patient_card = []
    today_in_hospital = query_hospitalized.total_day(today, cursor)
    yesterday_in_hospital = query_hospitalized.total_day(yesterday, cursor)

    percent_in_hospita = get_change(today_in_hospital, yesterday_in_hospital)
    patient_card.append(
        ('hospitalized',"Tổng bệnh nhân nội trú", 'fa-solid fa-hospital', today_in_hospital, percent_in_hospita))

    # Số lượt tiếp nhận
    today_visited = query_visited.total_day(today, cursor)
    yesterday_visited = query_visited.total_day(yesterday, cursor)
    percent_visited = get_change(today_visited, yesterday_visited)
    patient_card.append(
        ('visited',"Số lượt khám bệnh", 'fa-solid fa-hospital-user', today_visited, percent_visited))

    # Số bệnh nhân nhập viện
    today_hospitalize = query_hospitalized.in_day(today, cursor)
    yesterday_hospitalize = query_hospitalized.in_day(yesterday, cursor)
    percent_hospitalize = get_change(today_hospitalize, yesterday_hospitalize)
    patient_card.append(('new_patients',"Bệnh nhân nội trú mới", 'fa-solid fa-bed-pulse',
                        today_hospitalize, percent_hospitalize))

    # Lượt chuyển tuyến
    today_transfer = query_transfer.total_day(today, cursor) + query_transfer.total_department_day(today, cursor)
    yesterday_transfer = query_transfer.total_day(yesterday, cursor) + query_transfer.total_department_day(yesterday, cursor)
    percent_transfer = get_change(today_transfer, yesterday_transfer)

    patient_card.append(
        ('transfer',"Chuyển tuyến", 'fa-solid fa-truck-medical', today_transfer, percent_transfer))

    # Số ca phẫu thuật thủ thuật
    today_surgecies = query_surgery.total_day(today, cursor)
    yesterday_surgecies = query_surgery.total_day(yesterday, cursor)
    percent_surgecies = get_change(today_surgecies, yesterday_surgecies)
    patient_card.append(
        ('surgery_list',"Phẫu thuật, thủ thuật", 'fa-solid fa-kit-medical', today_surgecies, percent_surgecies))

    # Số ca đẻ
    today_born = query_born.total_day(today, cursor)
    yesterday_born = query_born.total_day(yesterday, cursor)
    percent_born = get_change(today_born, yesterday_born)
    patient_card.append(
        ('born',"Số trẻ sinh", 'fa-solid fa-baby', today_born, percent_born))

    # Thống kê số lượt khám theo từng phòng khám
    visited_in_department = query_visited.department_day(today, cursor)
    visited_in_department_id = query_visited.department_id_day(today, cursor)

    # Dữ liệu cho lượt khám bệnh chart
    visited_in_department = convert_to_chart(visited_in_department)
    visited_in_department_chart = visited_in_department.copy()
    visited_in_department_chart.insert(0, ["Phòng", 'Lượt khám'])
    
    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = query_hospitalized.total_department(today, cursor)
    patient_in_department_id = query_hospitalized.total_department_id(today, cursor)

    patient_in_department = convert_to_chart(patient_in_department)
    patient_in_department_chart = patient_in_department.copy()
    patient_in_department_chart.insert(0, ["Khoa", 'Bệnh nhân'])

    # Chart 30 day số lượt khám
    last30days = today - timedelta(days=50)
    last30days_visited = query_visited.day_betweenday(last30days, today, cursor)
    last30days_visited = [[day.strftime(
        "%A %d-%m-%Y"), int(visited)] for day, visited in last30days_visited]

    last30days_visited.reverse()

    # Cập nhập mới nhất, so sánh giữa thời gian tiếp nhận và thời gian xác nhận
    if sql_query.last_receiver(cursor)[0] > sql_query.last_confirmer(cursor)[0]:
        recent_action = sql_query.last_receiver(cursor)
    else:
        recent_action = sql_query.last_confirmer(cursor)

    recent_action_time = recent_action[0].strftime("%H:%M %d-%m-%Y")
    recent_action_tiepnhan_id = recent_action[1]

    recent_detail = query_confirmed.detail(recent_action_tiepnhan_id, cursor)

    # tin tức
    con_sqlite = sqlite3.connect("dashboard.db")
    con_sqlite.row_factory = sqlite3.Row
    cursor_sqlite = con_sqlite.cursor()

    list_post = query_user.posts(cursor_sqlite)
    # convert để hiện thị ở top filter
    today = today.strftime("%Y-%m-%d")

    context = {
        'top_card': top_card,
        'medicine_card': medicine_card,
        'service_card': service_card,
        'patient_card': patient_card,
        'today': today,
        'soluotkham30ngay': last30days_visited,
        'patient_in_department': patient_in_department_id,
        'patient_in_department_chart': patient_in_department_chart,
        'visited_in_department': visited_in_department_id,
        'visited_in_department_chart': visited_in_department_chart,
        'recent_action_time': recent_action_time,
        'recent_action_tiepnhan_id': recent_action_tiepnhan_id,
        'recent_detail': recent_detail,
        'posts': list_post
    }

    cnxn.close()
    return render_template('home/index.html', value=context,  active="home")


# Trang doanh thu
@app.route('/revenue/<string:day_query>')
@app.route('/revenue')
@register_breadcrumb(app, '..revenue', 'Doanh thu')
def revenue(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()
    
    # lấy ngày xem dashboard
    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


   
    # Doanh thu trong ngày
    today_money = query_revenue.total_day(today, cursor)
    yesterday_money = query_revenue.total_day(yesterday, cursor)
    percent_doanhthu = get_change(today_money, yesterday_money)
    money_card_top = ("Trong ngày này", today_money, percent_doanhthu)
    
   
    # Doanh thu 30 ngày gần nhất
    last30day = today - timedelta(days=50)
    last_30days_money = query_revenue.day_betweenday(last30day, today, cursor)
    last_30days_money = [[ngayxacnhan.strftime(
        "%A %d-%m-%Y"), int(tongdoanhthu)] for ngayxacnhan, tongdoanhthu in last_30days_money]
    last_30days_money.reverse()
    

    # Doanh thu 30 ngày gần nhất theo từng khoa phòng
    last_30days_department_money = query_revenue.day_department_betweenday(
        last30day, today, cursor)
    # Tạo dữ liệu cho chart
    last_30days_department_money_chart = convert_to_chart(last_30days_department_money)
    
    last_30days_department_money_chart.insert(0, ['Khoa', 'Số tiền'])

    confirmed_visited = query_confirmed.visited_hospitalized_day(today, 'NgoaiTru', cursor)
    confirmed_hospital = query_confirmed.visited_hospitalized_day(today, 'NoiTru', cursor)
    confirmed_total = confirmed_visited + confirmed_hospital

    money_visited = query_revenue.visited_hospitalized_day(today, 'NgoaiTru', cursor)
    money_hospital = query_revenue.visited_hospitalized_day(today, 'NoiTru', cursor)

    money_card_body = query_revenue.tenphanhom_service_medicine_day(today, cursor)
    money_card_body = convert_to_chart(money_card_body)
    money_card_body_chart = money_card_body.copy()
    money_card_body_chart.insert(0, ['Mục', 'Số tiền'])
 
    visited_card_body = [
        ['Tổng số', confirmed_total],
        ['Ngoại trú', money_visited],
        ['Nội trú', money_hospital],
    ]

    c_time = time()
    # Thống kê trong tuần
    week_money = query_revenue.total_between(mon_day, today, cursor)
    week_avg_confirmed = query_revenue.avg_confirmed(mon_day, today, cursor)
    week_avg_money = query_revenue.avg_between(startday=mon_day, endday=today, cursor=cursor)
    visited_money_week = query_revenue.visited_hospitalized_between(
        mon_day, today,'NgoaiTru', cursor)
    hospital_money_week = query_revenue.visited_hospitalized_between(
        mon_day, today,'NoiTru', cursor)

    # Thống kê trong tuần trước
    last_week_money = query_revenue.total_between(
        last_week_monday, last_week_sun_day, cursor)
    last_week_avg_money = query_revenue.avg_between(last_week_monday,last_week_sun_day, cursor)
    last_week_avg_confirmed = query_revenue.avg_confirmed(last_week_monday,last_week_sun_day, cursor)
    visited_money_last_week = query_revenue.visited_hospitalized_between(
        last_week_monday, last_week_sun_day,'NgoaiTru', cursor)
    hospital_money_last_week = query_revenue.visited_hospitalized_between(
        last_week_monday, last_week_sun_day,'NoiTru', cursor)

    week_progress_bar_title = 'So với tuần trước'
    week_progress_bar_value = get_percent(week_money, last_week_money)


    twolast_week_money = query_revenue.total_between(
        twolast_week_monday, twolast_week_sun_day, cursor)
    last_week_progress_bar_title = 'So với tuần trước'
    last_week_progress_bar_value = get_percent(last_week_money, twolast_week_money)
    bellow_card = [
        [
            'fa-solid fa-calendar-week',
            'Trong tuần này',
            f'ngày {mon_day.strftime("%d-%m-%Y")} đến {today.strftime("%d-%m-%Y")}',
            [week_money,
             visited_money_week,
             hospital_money_week,
             week_avg_money,
             week_avg_confirmed],
             week_progress_bar_title,
             week_progress_bar_value,
             last_week_money
         ],
        [
            'fa-solid fa-calendar-week',
            'Trong tuần trước',
            f'ngày {last_week_monday.strftime("%d-%m-%Y")} đến {last_week_sun_day.strftime("%d-%m-%Y")}',
         [last_week_money,
          visited_money_last_week,
          hospital_money_last_week,
          last_week_avg_money,
          last_week_avg_confirmed],
            last_week_progress_bar_title,
            last_week_progress_bar_value,
            twolast_week_money
         ],

    ]

    bellow_card_money_title = ['Tổng', 'Ngoại trú', 'Nội trú', 'Trung bình ngày', 'Trung bình mỗi xác nhận' ]

    confirmed_chart = [
        ['Loại', 'Doanh thu'],
        ['Ngoại trú', money_visited],
        ['Nội trú', money_hospital],
    ]

    # Doanh thu theo từng phòng khám, từng khoa
    money_department = query_revenue.department_day(today, cursor)
    money_department = convert_to_chart(money_department)
    last_update_time = sql_query.last_money_update(cursor)
    last_update_time = last_update_time.strftime("%H:%M:%S  %d-%m-%Y")

    last_confirmed = sql_query.last_confirmer(cursor)

    recent_confirmed_in_day = sql_query.recent_confirmed_review(today, cursor)

    recent_confirmed_in_day = ([soxacnhan, thoigian.strftime("%H:%M:%S"), int(doanhthu), int(thanhtoan), nhanvien] for soxacnhan, thoigian, doanhthu, thanhtoan, nhanvien in recent_confirmed_in_day)

    top10_doanhthu = query_revenue.top_service(today, cursor)
    top10_doanhthu_table = ([noidung, tenphongkham, count, int(tongdoanhthu)] for noidung, tenphongkham, count, tongdoanhthu in top10_doanhthu)


    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'money_card_top': money_card_top,
        'money_card_body': money_card_body,
        'money_card_body_chart': money_card_body_chart,
        'confirmed_visited': confirmed_visited,
        'confirmed_hospital': confirmed_hospital,
        'last_30days_money': last_30days_money,
        'last_30days_department_money_chart': last_30days_department_money_chart,
        'confirmed_total': confirmed_total,
        'visited_card_body': visited_card_body,
        'confirmed_chart': confirmed_chart,
        'bellow_card': bellow_card,
        'bellow_card_money_title': bellow_card_money_title,
        'money_department': money_department,
        'last_update_time': last_update_time,
        'last_confirmed': last_confirmed,
        'recent_confirmed_in_day': recent_confirmed_in_day,
        'top10_doanhthu_table': top10_doanhthu_table

    }
    cnxn.close()

    return render_template('revenue/index.html', value=context, active="revenue")



# Trang doanh thu
@app.route('/revenue/detail/<string:day_query>')
@app.route('/revenue/detail')
@register_breadcrumb(app, '..revenue.detail', 'Thống kê')
def revenue_detail(day_query=None):
    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()
    
    # lấy ngày xem dashboard
    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']

    # Thống kê trong tuần
    week_money = query_revenue.total_between(mon_day, today, cursor)
    week_avg_confirmed =  query_revenue.avg_confirmed(mon_day, today, cursor)
    week_avg_money = query_revenue.avg_between(startday=mon_day, endday=today, cursor=cursor)
    visited_money_week = query_revenue.visited_hospitalized_between(
        mon_day, today,'NgoaiTru', cursor)
    hospital_money_week = query_revenue.visited_hospitalized_between(
        mon_day, today,'NoiTru', cursor)

    # Thống kê trong tuần trước
    last_week_money = query_revenue.total_between(
        last_week_monday, last_week_sun_day, cursor)
    last_week_avg_money = query_revenue.avg_between(last_week_monday,last_week_sun_day, cursor)
    last_week_avg_confirmed =  query_revenue.avg_confirmed(last_week_monday,last_week_sun_day, cursor)
    visited_money_last_week = query_revenue.visited_hospitalized_between(
        last_week_monday, last_week_sun_day,'NgoaiTru', cursor)
    hospital_money_last_week = query_revenue.visited_hospitalized_between(
        last_week_monday, last_week_sun_day,'NoiTru', cursor)

    week_progress_bar_title = 'So với tuần trước'
    week_progress_bar_value = get_percent(week_money, last_week_money)


    twolast_week_money = query_revenue.total_between(
        twolast_week_monday, twolast_week_sun_day, cursor)
    last_week_progress_bar_title = 'So với tuần trước'
    last_week_progress_bar_value = get_percent(last_week_money, twolast_week_money)
        
    
    # Thống kê trong tháng
    month_money = query_revenue.total_between_union(first_month_day, today, cursor)
    month_avg_money = query_revenue.avg_between_union(first_month_day, today, cursor)

    month_avg_confirmed =  query_revenue.avg_confirmed_union(first_month_day, today, cursor)

    visited_money_month = query_revenue.visited_between_union(
        first_month_day, today, cursor)
    hospital_money_month = query_revenue.hospitalized_between_union(
        first_month_day, today, cursor)
    

    last_month_money =  query_revenue.total_between(
        last_first_month_day, last_end_month_day, cursor)


    month_progress_bar_title = 'So với tháng trước'
    month_progress_bar_value = get_percent(month_money, last_month_money)

    month_card_list =  [
            'fa-solid fa-calendar-days',
            'Trong tháng này',
            f'ngày {first_month_day.strftime("%d-%m-%Y")} đến {today.strftime("%d-%m-%Y")}',
         [month_money,
         visited_money_month,
          hospital_money_month,
          month_avg_money,
          month_avg_confirmed],
            month_progress_bar_title,
            month_progress_bar_value,
            last_month_money,
            
         ]
 
    # Thống kê trong năm
 
    year_money = query_revenue.total_between_union(first_year_day, today, cursor)
   
    year_avg_money = query_revenue.avg_between_union(first_year_day, today, cursor)
    year_avg_confirmed =  query_revenue.avg_confirmed_union(first_year_day, today, cursor)

    visited_money_year = query_revenue.visited_between_union(
        first_year_day, today, cursor)
    hospital_money_year = query_revenue.hospitalized_between_union(
        first_year_day, today, cursor)
 
    last_year_money = query_revenue.total_between_union(
        last_first_year_day, end_last_year_day, cursor)
    
    
    year_progress_bar_title = 'So với năm trước'
    year_progress_bar_value = get_percent(year_money, last_year_money)

    year_card_list =  [
            'fa-regular fa-calendar',
            'Trong năm này',
            f'ngày {first_year_day.strftime("%d-%m-%Y")} đến {today.strftime("%d-%m-%Y")}',
         [
            year_money,
            visited_money_year,
            hospital_money_year,
            year_avg_money,
            year_avg_confirmed],
            year_progress_bar_title,
            year_progress_bar_value,
            last_year_money
         ]
    
    bellow_card = [
        [
            'fa-solid fa-calendar-week',
            'Trong tuần này',
            f'ngày {mon_day.strftime("%d-%m-%Y")} đến {today.strftime("%d-%m-%Y")}',
            [week_money,
             visited_money_week,
             hospital_money_week,
             week_avg_money,
             week_avg_confirmed],
             week_progress_bar_title,
             week_progress_bar_value,
             last_week_money
         ],
        [
            'fa-solid fa-calendar-week',
            'Trong tuần trước',
            f'ngày {last_week_monday.strftime("%d-%m-%Y")} đến {last_week_sun_day.strftime("%d-%m-%Y")}',
         [last_week_money,
          visited_money_last_week,
          hospital_money_last_week,
          last_week_avg_money,
          last_week_avg_confirmed],
            last_week_progress_bar_title,
            last_week_progress_bar_value,
            twolast_week_money
         ],
         month_card_list,
         year_card_list

    ]
    bellow_card_money_title = ['Tổng', 'Ngoại trú', 'Nội trú', 'Trung bình ngày', 'Trung bình mỗi xác nhận' ]

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'bellow_card': bellow_card,
        'bellow_card_money_title': bellow_card_money_title

    }
    cnxn.close()
    return render_template('revenue/detail.html', value=context,active='revenue')

# Danh sách xác nhận thanh toán
@app.route('/revenue/confirmed')
@app.route('/revenue/confirmed/<string:day_query>')
@register_breadcrumb(app, '..revenue.confirmed', 'Danh sách')
def confirmed(day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']

    all_confirmed = query_confirmed.list(today, cursor)
    all_confirmed = ([thoigian.strftime("%H:%M:%S %d-%m-%Y"),soxacnhan,benhnhan_id, loai ,f'{int(doanhthu):,}', f'{int(thanhtoan):,}', nhanvien] for thoigian,soxacnhan, benhnhan_id,loai, doanhthu, thanhtoan, nhanvien in all_confirmed)

    table_column_title = ['Thời gian','Mã y tế', 'Số xác nhận',  'Loại', 'Doanh thu', 'Thanh toán', 'Nhân viên']

    staff_money = query_confirmed.staff_money(today, cursor)
    staff_money = list([staff, f'{int(money1):,}',f'{int(money2):,}'] for money1, money2, staff in staff_money)

    staff_confirmed = query_confirmed.staff_confirmed(today, cursor)
    staff_confirmed_chart = list([i,j] for i,j in staff_confirmed)
    staff_confirmed_chart.insert(0,['Tên nhân viên', 'Số lượt xác nhận'])

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': all_confirmed,
        'table_column_title': table_column_title,
        'staff_money': staff_money,
        'staff_confirmed_chart': staff_confirmed_chart
    }

    cnxn.close()
    

    return render_template('revenue/confirmed_list.html', value=context,active='revenue')

@app.route('/confirmed/detail/<string:SoXacNhan_Id>')
@register_breadcrumb(app, './revenue/detail', 'Chi tiết')
def confirmed_detail(SoXacNhan_Id):
    cnxn = get_db()
    cursor = cnxn.cursor()
    detail = sql_query.confirmed_detail(SoXacNhan_Id, cursor)
    detail_json = jsonify(
        Ngaytao = detail[0].strftime("%Y-%m-%d"),
        SoXacNhan = detail[1],
        BenhNhan_Id = detail[2],
        TongDoanhThu = int(detail[3]),
        TongThanhToan = int(detail[4]),
        TenPhongKham = detail[5],
        TenNhanVien = detail[6]
    )
    cnxn.close()
    return detail_json

# Trang bệnh nhân nội trú
@app.route('/hospitalized/<string:day_query>')
@app.route('/hospitalized')
@register_breadcrumb(app, '.hospitalized', 'Nội trú')
def hospitalized(day_query=None):

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']

    cnxn = get_db()
    cursor = cnxn.cursor()

    card_top = []

    today_in_hospital = query_hospitalized.total_day(today, cursor)
    recent_today_in_hospital = query_hospitalized.in_day(today, cursor)
    yesterday_in_hostpital = query_hospitalized.total_day(yesterday, cursor)
    out_hospital_day = query_hospitalized.out_day(today, cursor)
    percent_change = get_change(today_in_hospital,yesterday_in_hostpital)
    percent = get_percent(today_in_hospital,yesterday_in_hostpital)

    card_top.append(["Bệnh nhân nội trú", today_in_hospital, percent_change, percent, yesterday_in_hostpital])

    transfer_day = query_transfer.total_day(today, cursor)

    card_top_body = []
    card_top_body.append(['Nhập mới', recent_today_in_hospital])
    card_top_body.append(['Ra viện', out_hospital_day])

    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = query_hospitalized.total_department(today, cursor)
    patient_in_department_id = query_hospitalized.total_department_id(today, cursor)

    patient_in_department = convert_to_chart(patient_in_department)
    patient_in_department_chart = patient_in_department.copy()
    patient_in_department_chart.insert(0, ["Khoa", 'Bệnh nhân'])
    
    # Thống kê Số bệnh nhân nội trú nhập mới từng khoa
    patient_in_department_today = query_hospitalized.in_department_day(today, cursor)

    # chart số bệnh nhân nội trú 30 ngày gần nhất
    last_30_day_chart = []
    for day in range(30):
        day_q = today - timedelta(days=day)
        count_patient = query_hospitalized.total_day(day_q, cursor)
        
        last_30_day_chart.append([day_q.strftime("%A %d-%m-%Y"),count_patient])
    
    last_30_day_chart.reverse()

    # Bệnh nhân vừa nhập viện
    recent_hospitalized_in_day = sql_query.recent_confirmed_review(today, cursor)
    last_patients = query_hospitalized.last5(today, cursor)
    last_patients = ([time_in_department.strftime("%H:%M %d/%m/%Y"), patient_name, department] for time_in_department, patient_name, department in last_patients)

    card_bellow = []
    this_week = query_hospitalized.total_in_between(mon_day, today, cursor)
    this_month = query_hospitalized.total_in_between(first_month_day, today, cursor)
    this_year = query_hospitalized.total_in_between(first_year_day, today, cursor)

    last_week = query_hospitalized.total_in_between(last_week_monday, last_week_sun_day, cursor)
    last_month = query_hospitalized.total_in_between(last_first_month_day, last_end_month_day, cursor)
    last_year = query_hospitalized.total_in_between(last_first_year_day, end_last_year_day, cursor)

    week_percent = get_percent(this_week, last_week)
    month_percent = get_percent(this_month, last_month)
    year_percent = get_percent(this_year, last_year)

    card_bellow.append(['Tuần này', this_week, 'Tuần trước', last_week, week_percent])
    card_bellow.append(['Tháng này', this_month, 'Tháng trước', last_month, month_percent])
    card_bellow.append(['Năm này', this_year, 'Năm trước', last_year, year_percent])

    last_50_day = today + timedelta(days=-50)
    last_30_day_in_hostpital_chart = query_hospitalized.in_betweenday(last_50_day, today, cursor)
    last_30_day_in_hostpital_chart = convert_to_chart_date(last_30_day_in_hostpital_chart)


    total_bed = {
        'TTYT Anh Sơn': (200,72,272),
        'Khoa Ngoại tổng hợp': (44,8,52),
        'Khoa Nội-Truyền nghiễm': (37,15,52),
        'Khoa HSCC-Nhi': (44,10,54),
        'Khoa Phụ Sản': (30,11,48),
        'Liên chuyên khoa TMH-RHM-Mắt': (17,8,25),
        'Khoa Đông Y&PHCN': (28,20,48)
    }
    # Tính công suất toàn viện trong ngày
    today_real_bed = query_hospitalized.total_day(today, cursor)
    total_percent = get_percent(today_real_bed, total_bed['TTYT Anh Sơn'][2])
    ttyt = ('TTYT Anh Sơn', today_real_bed, total_bed['TTYT Anh Sơn'][2], total_percent )


    # công suất khoa hscc
    hscc_real_bed = query_hospitalized.bed_department(today,1228,cursor)
    hscc_percent = get_percent(hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2])
    hscc = ('Khoa HSCC-Nhi', hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2], hscc_percent )
    
    # công suất khoa ngoại
    ngoai_real_bed = query_hospitalized.bed_department(today,1219,cursor)
    ngoai_percent = get_percent(ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2])
    ngoai = ('Khoa Ngoại tổng hợp', ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2], ngoai_percent )
    
    # công suất khoa nội
    noi_real_bed = query_hospitalized.bed_department(today,1215,cursor)
    noi_percent = get_percent(noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2])
    noi = ('Khoa Nội-Truyền nghiễm', noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2], noi_percent )
    
    # công suất khoa yhct
    yhct_real_bed = query_hospitalized.bed_department(today,1227,cursor)
    yhct_percent = get_percent(yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2])
    yhct = ('Khoa Đông Y&PHCN', yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2], yhct_percent )
    
    # công suất khoa sản
    san_real_bed = query_hospitalized.bed_department(today,1218,cursor)
    san_percent = get_percent(san_real_bed, total_bed['Khoa Phụ Sản'][2])
    san = ('Khoa Phụ Sản', san_real_bed, total_bed['Khoa Phụ Sản'][2], san_percent )

    # công suất khoa Liên chuyên khoa TMH-RHM-Mắt
    lck_real_bed = query_hospitalized.bed_department(today,2385,cursor)
    lck_percent = get_percent(lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2])
    lck = ('Liên chuyên khoa TMH-RHM-Mắt', lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2], lck_percent )



    bed_list = [ttyt,ngoai,noi, hscc, san, lck,  yhct]

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'card_top': card_top,
        'card_bellow': card_bellow,
        'card_top_body': card_top_body,
        'patient_in_department': patient_in_department_id,
        'patient_in_department_today': patient_in_department_today,
        'patient_in_department_chart': patient_in_department_chart,
        'last_30_day_chart': last_30_day_chart,
        'last_30_day_in_hostpital_chart': last_30_day_in_hostpital_chart,
        'recent_hospitalized_in_day': recent_hospitalized_in_day,
        'last_patients': last_patients,
        'bed_list': bed_list
    }

    cnxn.close()
    return render_template('hospitalized/index.html', value=context, active="hospitalized")


# Danh sách bệnh nhân nội trú mới trong ngày
@app.route('/hospitalized/new-patients/<string:day_query>')
@app.route('/hospitalized/new-patients')
@register_breadcrumb(app, '..hospitalized.new-patients', 'Nhập viện mới')
def new_patients(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Thời gian','Mã y tế', 'Số bệnh án',  'Tên bệnh nhân','Chẩn đoán', 'Khoa', 'Nhân viên']

    list_patients = query_hospitalized.new_list(today, cursor)
    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2,e3,e7,e4,e5,e6] for e1,e2,e3,e7,e4,e5,e6 in list_patients)

    patients_department_chart = query_hospitalized.in_department_day(today, cursor)
    patients_department_chart = list([i,j] for i,j in patients_department_chart)

    patients_department_chart.insert(0,['Khoa', 'Số bệnh nhân nhập mới'])
    total = query_hospitalized.in_day(today, cursor)

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': patients_department_chart,
        'total': total


    }
    cnxn.close()
    return render_template('hospitalized/new-patients.html', value=context)

# Danh sách bệnh nhân nội trú ra viện trong ngày
@app.route('/hospitalized/out-patients/<string:day_query>')
@app.route('/hospitalized/out-patients')
@register_breadcrumb(app, '..hospitalized.out-patients', 'Ra viện')
def out_patients(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Thời gian','Mã y tế',  'Số bệnh án', 'Chẩn đoán ra viện', 'Lí do','Bác sĩ', 'Khoa']

    list_patients = query_hospitalized.out_list(today, cursor)

    chart = query_hospitalized.out_department_day(today, cursor)
    chart = list([i,j] for i,j in chart)

    chart.insert(0,['Khoa', 'Số bệnh nhân ra viện'])
    total = query_hospitalized.out_day(today, cursor)


    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': chart,
        'total': total


    }
    cnxn.close()
    return render_template('hospitalized/out-patients.html', value=context)

# Danh sách bệnh nhân chuyển viện trong ngày
@app.route('/transfer/<string:day_query>')
@app.route('/transfer')
@register_breadcrumb(app, '..transfer', 'Chuyển viện')
def transfer(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Thời gian', 'Mã y tế', 'Tên bệnh nhân','Chẩn đoán ra viện','Bác sĩ' ,'Khoa phòng']

    list_patients = query_transfer.transfer(today, cursor)

    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2,e3,e7,e4,e5] for e1,e2,e3,e7,e4,e5 in list_patients)


    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title
    }
    cnxn.close()
    return render_template('hospitalized/transfer.html', value=context)


# Danh sách bệnh nhân nội trú
@app.route('/hospitalized/patients/<string:day_query>')
@app.route('/hospitalized/patients')
@register_breadcrumb(app, '..hospitalized.patients', 'Bệnh nhân')
def patients(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']


    table_column_title = ['Thời gian vào khoa','Mã y tế',  'Số bệnh án', 'Tên bệnh nhân', 'Chẩn đoán trong khoa','Bác sĩ', 'Khoa']

    list_patients = query_hospitalized.patients(today, cursor)

    chart = query_hospitalized.total_department(today, cursor)
    chart = list([i,j] for i,j in chart)

    chart.insert(0,['Khoa', 'Số bệnh nhân'])
    total = query_hospitalized.total_day(today, cursor)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': chart,
        'total': total


    }
    cnxn.close()
    return render_template('hospitalized/patients.html', value=context)


# Trang bệnh nhân ngoại trú
@app.route('/visited/<string:day_query>')
@app.route('/visited')
@register_breadcrumb(app, '.visited', 'Khám bệnh')
def visited(day_query=None):
    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']

    cnxn = get_db()
    cursor = cnxn.cursor()

    card_top = []

    # Bệnh nhân ngoại trú trong ngày
    total = query_visited.total_day(today, cursor)
    recent_today_in_hospital = query_visited.total_day(today, cursor)
    yesterday_visited = query_visited.total_day(yesterday, cursor)
    out_hospital_day = query_hospitalized.out_day(today, cursor)
    percent_change = get_change(total,yesterday_visited)
    percent = get_percent(total,yesterday_visited)

    card_top.append(["Số lượt khám bệnh", total, percent_change, percent, yesterday_visited])

    card_top_body = []
    card_top_body.append(['Nhập mới', recent_today_in_hospital])
    card_top_body.append(['Ra viện', out_hospital_day])

    # Thống kê Số bệnh nhân ngoại trú từng phòng
    patient_in_department = query_visited.department_day(today, cursor)

    patient_in_department = convert_to_chart(patient_in_department)
    patient_in_department_chart = patient_in_department.copy()
    patient_in_department_chart.insert(0, ["Phòng khám", 'Bệnh nhân'])

    visited_in_department = query_visited.department_id_day(today, cursor)
    
    # Thống kê Số bệnh nhân nội trú nhập mới từng khoa
    visited_in_department_today = query_visited.department_day(today, cursor)
   

    # chart số bệnh nhân nội trú 30 ngày gần nhất
    last_30_day_chart = []
    for day in range(30):
        day_q = today - timedelta(days=day)
        count_patient = query_hospitalized.total_day(day_q, cursor)
        
        last_30_day_chart.append([day_q.strftime("%A %d-%m-%Y"),count_patient])
    
    last_30_day_chart.reverse()

    # Bệnh nhân vừa nhập viện
    recent_hospitalized_in_day = sql_query.recent_confirmed_review(today, cursor)
    last_patients = query_visited.last5(today, cursor)
    last_patients = ([time_in_department.strftime("%H:%M %d/%m/%Y"), patient_name, department] for time_in_department, patient_name, department in last_patients)

    card_bellow = []
    this_week = query_visited.total_betweenday(mon_day, today, cursor)
    this_month = query_visited.total_betweenday(first_month_day, today, cursor)
    this_year = query_visited.total_betweenday(first_year_day, today, cursor)

    last_week = query_visited.total_betweenday(last_week_monday, last_week_sun_day, cursor)
    last_month = query_visited.total_betweenday(last_first_month_day, last_end_month_day, cursor)
    last_year = query_visited.total_betweenday(last_first_year_day, end_last_year_day, cursor)

    week_percent = get_percent(this_week, last_week)
    month_percent = get_percent(this_month, last_month)
    year_percent = get_percent(this_year, last_year)

    card_bellow.append(['Tuần này', this_week, 'Tuần trước', last_week, week_percent])
    card_bellow.append(['Tháng này', this_month, 'Tháng trước', last_month, month_percent])
    card_bellow.append(['Năm này', this_year, 'Năm trước', last_year, year_percent])


    
    # Chart 30 day số lượt khám
    last30days = today - timedelta(days=50)
    last30days_visited = query_visited.day_betweenday(last30days, today, cursor)
    last30days_visited = [[day.strftime(
        "%A %d-%m-%Y"), int(visited)] for day, visited in last30days_visited]

    last30days_visited.reverse()


    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'card_top': card_top,
        'card_bellow': card_bellow,
        'card_top_body': card_top_body,
        'patient_in_department': patient_in_department,
        'visited_in_department_today': visited_in_department_today,
        'patient_in_department_chart': patient_in_department_chart,
        'last_30_day_chart': last30days_visited,
        'recent_hospitalized_in_day': recent_hospitalized_in_day,
        'last_patients': last_patients,
        'visited_in_department': visited_in_department
    }

    cnxn.close()
    return render_template('visited/index.html', value=context, active='visited')


# Danh sách bệnh nhân ngoại trú trong ngày
@app.route('/visited/patients/<string:day_query>')
@app.route('/visited/patients')
@register_breadcrumb(app, '..visited.patients', 'Bệnh nhân')
def visited_patients(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Thời gian khám', 'Mã y tế', 'Tên bệnh nhân', 'Số tiếp nhận','Chẩn đoán trong khoa','Bác sĩ', 'Khoa']

    list_patients = query_visited.patients(today, cursor)

    chart = query_visited.department_day(today, cursor)
    chart = list([i,j] for i,j in chart)

    chart.insert(0,['Khoa', 'Số bệnh nhân'])
    total = query_visited.total_day(today, cursor)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': chart,
        'total': total


    }
    cnxn.close()
    return render_template('visited/patients.html', value=context)



# Trang phẫu thuật thủ thuật
@app.route('/surgery/<string:day_query>')
@app.route('/surgery')
@register_breadcrumb(app, '..surgery', 'Phẫu thuật, thủ thuật')
def surgery(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Thời gian khám', 'Mã y tế', 'Tên bệnh nhân', 'Chẩn đoán trong khoa','Bác sĩ', 'Khoa']

    list_patients = query_visited.patients(today, cursor)
    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2,e3,e4,e5,e6] for e1,e2,e3,e4,e5,e6 in list_patients)

    chart = query_visited.department_day(today, cursor)
    chart = list([i,j] for i,j in chart)

    chart.insert(0,['Khoa', 'Số bệnh nhân'])
    total = query_visited.total_day(today, cursor)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': chart,
        'total': total


    }
    cnxn.close()
    return render_template('surgery/index.html', value=context)


# Trang phẫu thuật thủ thuật
@app.route('/surgery/list/<string:day_query>')
@app.route('/surgery/list')
@register_breadcrumb(app, '..surgery.list', 'Danh sách')
def surgery_list(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']

    table_column_title = ['Thời gian kết thúc', 'Mã y tế', 'Tên bệnh nhân', 'Can thiệp','Loại', 'Nơi thực hiện']

    list_patients = query_surgery.list(today, cursor)
    chart = query_visited.department_day(today, cursor)
    chart = list([i,j] for i,j in chart)

    chart.insert(0,['Khoa', 'Số bệnh nhân'])
    total = query_visited.total_day(today, cursor)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': chart,
        'total': total
    }
    cnxn.close()
    return render_template('surgery/list.html', value=context)



# Số trẻ sinh
@app.route('/born/<string:day_query>')
@app.route('/born')
@register_breadcrumb(app, '..surgery.born', 'Trẻ sinh')
def born(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Thời gian kết thúc', 'Mã Y tế', 'Tên bệnh nhân', 'Can thiệp phẫu thuật','Mô tả sau phẫu thuật']

    if day_query == 'thisyear':
        list_patients = query_born.list_between(first_year_day, today, cursor)
    else:
        list_patients = query_born.list(today, cursor)

    chart = query_visited.department_day(today, cursor)
    chart = list([i,j] for i,j in chart)

    chart.insert(0,['Khoa', 'Số bệnh nhân'])
    total = query_visited.total_day(today, cursor)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': chart,
        'total': total
    }
    cnxn.close()
    return render_template('born/index.html', value=context)


# Doanh thu theo tên dịch vụ
@app.route('/revenue/list/<string:day_query>')
@app.route('/revenue/list')
@register_breadcrumb(app, '..revenue.list', 'Danh sách')
def list_revenue(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Nội dung', 'Tên', 'Khoa/Phòng', 'Số lượt', 'Tổng doanh thu']

    list_patients = query_revenue.services(today, cursor)
    list_patients = list([e1,e2,e3,e4,f'{ int(e5):,}'] for e1,e2,e3,e4,e5 in list_patients)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
    }
    cnxn.close()
    return render_template('revenue/list.html', value=context, active='revenue', order_column=4)


# Doanh thu theo dược
@app.route('/revenue/medicine/<string:day_query>')
@app.route('/revenue/medicine/')
@register_breadcrumb(app, '..revenue.medicine', 'Dược')
def medicine(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Nội dung', 'Tên', 'Khoa/Phòng', 'Số lượt', 'Tổng doanh thu']

    list_patients = query_revenue.services_type(today,'DU', cursor)
    list_patients = list([e1,e2,e3,e4,f'{ int(e5):,}'] for e1,e2,e3,e4,e5 in list_patients)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
    }
    cnxn.close()
    return render_template('revenue/medicine.html', value=context, active='revenue', order_column=4)


# Doanh thu theo dịch vụ
@app.route('/revenue/service/<string:day_query>')
@app.route('/revenue/service/')
@register_breadcrumb(app, '..revenue.service', 'Dịch vụ')
def service(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']


    table_column_title = ['Nội dung', 'Tên', 'Khoa/Phòng', 'Số lượt', 'Tổng doanh thu']

    list_patients = query_revenue.services_type(today,'DV', cursor)
    list_patients = list([e1,e2,e3,e4,f'{ int(e5):,}'] for e1,e2,e3,e4,e5 in list_patients)

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
    }
    cnxn.close()
    return render_template('revenue/service.html', value=context, active='revenue', order_column=4)

# Trang tin tức
@app.route('/news')
@register_breadcrumb(app, '..news', 'Thông tin công việc')
def news():
    con = sqlite3.connect("dashboard.db")
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    list_post = query_user.posts(cursor)
    context = {
        'posts': list_post
    }
    con.close()
    return render_template('news/index.html', value=context, active='news', order_column=4)

# Trang bệnh nhân khám bệnh theo từng khoa
@app.route('/visited/<int:department_id>/<string:day_query>')
@app.route('/visited/<int:department_id>')
@register_breadcrumb(app, '..visited.department', 'Danh sách')
def visited_department(department_id, day_query=None):

    department_id_list = get_department_id_list(department_id)
    cnxn = get_db()
    cursor = cnxn.cursor()
    day_dict = get_day(day_query)
    today = day_dict['today']

    table_column_title = ['Thời gian', 'Mã Y tế', 'Tên bệnh nhân', 'Chẩn đoán', 'Bác sĩ']

    list_patients = []

    for d_id in department_id_list:
        list_patients.extend(query_visited.list_department(today,d_id, cursor))

    
    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2,e3,e4,e5] for e1,e2,e3,e4,e5 in list_patients )
    department_name = ''
    for d_id in department_id_list:
        department_name += (query_visited.name_department(d_id, cursor)) + ' - '
    startday = today + timedelta(days=-30)
    visited_department_chart = query_visited.department_id_between(startday, today, department_id, cursor)
    visited_department_chart = convert_to_chart(visited_department_chart)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'department_id': department_id,
        'department_name': department_name,
        'visited_department_chart': visited_department_chart
    }
    cnxn.close()
    return render_template('visited/department.html', value=context, active='visited', order_column=0)


# Trang bệnh nhân nội trú theo từng khoa
@app.route('/hospitalized/<int:department_id>/<string:day_query>')
@app.route('/hospitalized/<int:department_id>')
@register_breadcrumb(app, '..hospitalized.department', 'Danh sách')
def hospitalized_department(department_id, day_query=None):

    department_id_list = get_department_id_list(department_id)
    cnxn = get_db()
    cursor = cnxn.cursor()
    day_dict = get_day(day_query)
    today = day_dict['today']

    table_column_title = ['Thời gian', 'Mã Y tế', 'Tên bệnh nhân', 'Chẩn đoán', 'Bác sĩ']

    list_patients = query_hospitalized.list_department(today,department_id, cursor)

    
    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2,e3,e4,e5] for e1,e2,e3,e4,e5 in list_patients )
    department_name = query_visited.name_department(department_id, cursor)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'department_id': department_id,
        'department_name': department_name,
    }
    cnxn.close()
    return render_template('hospitalized/department.html', value=context, active='hospitalized', order_column=0)

# Trang công suất giường bệnh
@app.route('/hospitalized/bed/<string:day_query>', methods=['GET', 'POST'])
@app.route('/hospitalized/bed', methods=['GET', 'POST'])
@register_breadcrumb(app, '..hospitalized.bed', 'Công suất giường bệnh')
def hospitalized_bed(day_query=None):

    def bed_caculator(today, cursor):
        # Tính công suất toàn viện trong ngày
        today_real_bed = query_hospitalized.total_day(today, cursor)
        total_percent = get_percent(today_real_bed, total_bed['TTYT Anh Sơn'][2])
        ttyt = ('TTYT Anh Sơn', today_real_bed, total_bed['TTYT Anh Sơn'][2], total_percent )


        # công suất khoa hscc
        hscc_real_bed = query_hospitalized.bed_department(today,1228,cursor)
        hscc_percent = get_percent(hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2])
        hscc = ('Khoa HSCC-Nhi', hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2], hscc_percent )
        
        # công suất khoa ngoại
        ngoai_real_bed = query_hospitalized.bed_department(today,1219,cursor)
        ngoai_percent = get_percent(ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2])
        ngoai = ('Khoa Ngoại tổng hợp', ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2], ngoai_percent )
        
        # công suất khoa nội
        noi_real_bed = query_hospitalized.bed_department(today,1215,cursor)
        noi_percent = get_percent(noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2])
        noi = ('Khoa Nội-Truyền nghiễm', noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2], noi_percent )
        
        # công suất khoa yhct
        yhct_real_bed = query_hospitalized.bed_department(today,1227,cursor)
        yhct_percent = get_percent(yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2])
        yhct = ('Khoa Đông Y&PHCN', yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2], yhct_percent )
        
        # công suất khoa sản
        san_real_bed = query_hospitalized.bed_department(today,1218,cursor)
        san_percent = get_percent(san_real_bed, total_bed['Khoa Phụ Sản'][2])
        san = ('Khoa Phụ Sản', san_real_bed, total_bed['Khoa Phụ Sản'][2], san_percent )

        # công suất khoa Liên chuyên khoa TMH-RHM-Mắt
        lck_real_bed = query_hospitalized.bed_department(today,2385,cursor)
        lck_percent = get_percent(lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2])
        lck = ('Liên chuyên khoa TMH-RHM-Mắt', lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2], lck_percent )

        return [ttyt,ngoai,noi, hscc, san, lck,  yhct]
    
    
    cnxn = get_db()
    cursor = cnxn.cursor()
    total_bed = {
        'TTYT Anh Sơn': (200,72,272),
        'Khoa Ngoại tổng hợp': (44,8,52),
        'Khoa Nội-Truyền nghiễm': (37,15,52),
        'Khoa HSCC-Nhi': (44,10,54),
        'Khoa Phụ Sản': (30,11,48),
        'Liên chuyên khoa TMH-RHM-Mắt': (17,8,25),
        'Khoa Đông Y&PHCN': (28,20,48)
    }
    day_dict = get_day(day_query)
    today = day_dict['today']

    chart_30_days = []
    # chart công suất toàn viện 30 ngày
    for n in range(31):
        day = today + timedelta(n)
        today_real_bed = query_hospitalized.total_day(day, cursor)
        total_percent = get_percent(today_real_bed, total_bed['TTYT Anh Sơn'][2])
        percent = total_percent[1]
        if percent > 95:
            color = 'red'
        elif percent > 70:
            color = 'green'
        elif percent > 60:
            color = 'orange'
        else:
            color = 'gray'
        chart_30_days.append([day.strftime("%d/%m/%Y"),percent,color])  
 
    if request.method == 'POST':
        bed_list_betweenday = []
        start_day = request.form['start_date']
        start_day = datetime.strptime(start_day,'%Y-%m-%d')
        end_day = request.form['end_date']
        end_day = datetime.strptime(end_day,'%Y-%m-%d')
        count_day = int((end_day - start_day).days) + 1
        for n in range(count_day):
            today = start_day + timedelta(n)
            bed_list = bed_caculator(today, cursor)
            bed_list_betweenday.append(bed_list)
        

        today_real_bed = sum(i[0][1] for i in bed_list_betweenday )
        total_percent = get_percent(today_real_bed, total_bed['TTYT Anh Sơn'][2] * count_day )
        ttyt = ('TTYT Anh Sơn', today_real_bed, total_bed['TTYT Anh Sơn'][2] * count_day, total_percent )

        # công suất khoa ngoại
        ngoai_real_bed = sum(i[1][1] for i in bed_list_betweenday )
        ngoai_percent = get_percent(ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2]* count_day)
        ngoai = ('Khoa Ngoại tổng hợp', ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2]* count_day, ngoai_percent )
        
        # công suất khoa nội
        noi_real_bed = sum(i[2][1] for i in bed_list_betweenday )
        noi_percent = get_percent(noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2]* count_day)
        noi = ('Khoa Nội-Truyền nghiễm', noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2]* count_day, noi_percent )
        
        # công suất khoa hscc
        hscc_real_bed = sum(i[3][1] for i in bed_list_betweenday )
        hscc_percent = get_percent(hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2]* count_day)
        hscc = ('Khoa HSCC-Nhi', hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2]* count_day, hscc_percent )

        # công suất khoa sản
        san_real_bed = sum(i[4][1] for i in bed_list_betweenday )
        san_percent = get_percent(san_real_bed, total_bed['Khoa Phụ Sản'][2]* count_day)
        san = ('Khoa Phụ Sản', san_real_bed, total_bed['Khoa Phụ Sản'][2]* count_day, san_percent )

        # công suất khoa Liên chuyên khoa TMH-RHM-Mắt
        lck_real_bed = sum(i[5][1] for i in bed_list_betweenday )
        lck_percent = get_percent(lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2]* count_day)
        lck = ('Liên chuyên khoa TMH-RHM-Mắt', lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2]* count_day, lck_percent )

        # công suất khoa yhct
        yhct_real_bed = sum(i[6][1] for i in bed_list_betweenday )
        yhct_percent = get_percent(yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2]* count_day)
        yhct = ('Khoa Đông Y&PHCN', yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2]* count_day, yhct_percent )

        bed_list = [ttyt,ngoai,noi, hscc, san, lck,  yhct]
        filter_date = [start_day, end_day, count_day]
    else:          
        bed_list = bed_caculator(today, cursor)
        filter_date = None
    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'bed_list': bed_list,
        'chart_30_days': chart_30_days,
        'filter_date': filter_date
    }
    cnxn.close()
    return render_template('hospitalized/bed.html', value=context, active='hospitalized')


# Trang danh sách bệnh nhân
@app.route('/patients/')
@register_breadcrumb(app, '..patients', 'Bệnh nhân')
def all_patients():

    cnxn = get_db()
    cursor = cnxn.cursor()
    day_dict = get_day(None)
    today = day_dict['today']
    
    list_patients = query_patient.patients(cursor)
    table_column_title = ['Ngày tạo', 'Mã Y tế', 'Tên bệnh nhân', 'Ngày sinh', 'Số điện thoại', 'Địa chỉ']
    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title
    }
    cnxn.close()
    return render_template('patient/index.html', value=context, active='patient')



# Trang chi tiết bệnh nhân
@app.route('/patient/<string:mayte>')
@register_breadcrumb(app, '..patients.detail', 'Chi tiết')
def patient_detail(mayte):

    cnxn = get_db()
    cursor = cnxn.cursor()
    day_dict = get_day(None)
    today = day_dict['today']

    detail = query_patient.detail(mayte, cursor)

    history_visited = query_patient.visited_history(mayte, cursor)
    history_hospital = query_patient.hospitalized_history(mayte, cursor)
    doanhthu = query_patient.doanhthu(mayte, cursor)
    thanhtoan = query_patient.thanhtoan(mayte, cursor)
    

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'mayte': mayte,
        'detail': detail,
        'history_visited': history_visited,
        'history_hospital': history_hospital,
        'doanhthu': doanhthu,
        'thanhtoan': thanhtoan
    }
    cnxn.close()
    return render_template('patient/detail.html', value=context, active='patient')


# Trang danh sách báo cáo
@app.route('/report/<string:day_query>')
@app.route('/report')
@register_breadcrumb(app, '..report', 'Báo cáo')
def report(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()
    day_dict = get_day(day_query)
    today = day_dict['today']
    card = []
    card1 = ['Doanh thu theo từng mục', 'Mẫu báo cáo 79 của BHYT', 'Chi tiết doanh thu từng mục: Tiền CĐHA, Tiền Xét nghiệm, Tiền Thuốc, Tiền Phẫu thuật, Tiền Khám, Tiền Giường', 'report_79']

    card.append(card1)

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'card': card

    }
    cnxn.close()
    return render_template('report/index.html', value=context, active='report')

# Báo cáo 79 
@app.route('/report/79/<string:day_query>', methods=['GET', 'POST'])
@app.route('/report/79', methods=['GET', 'POST'])
@register_breadcrumb(app, '..report.report-79', 'Chi tiết doanh thu xác nhận')
def report_79(day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()
    day_dict = get_day(day_query)
    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']
    mon_day = day_dict['mon_day']
    last_week_monday = day_dict['last_week_monday']
    last_week_sun_day = day_dict['last_week_sun_day']
    twolast_week_monday = day_dict['twolast_week_monday']
    twolast_week_sun_day = day_dict['twolast_week_sun_day']
    first_month_day = day_dict['first_month_day']
    last_first_month_day = day_dict['last_first_month_day']
    last_end_month_day = day_dict['last_end_month_day']
    first_year_day = day_dict['first_year_day']
    last_first_year_day = day_dict['last_first_year_day']
    end_last_year_day = day_dict['end_last_year_day']

    if request.method == 'POST':
        list_id = []
        start_day = request.form['start_date']
        start_day = datetime.strptime(start_day,'%Y-%m-%d')
        end_day = request.form['end_date']
        end_day = datetime.strptime(end_day,'%Y-%m-%d')
        for n in range(int((end_day - start_day).days)):
            day = start_day + timedelta(n)
            list_id.extend(query_report.list_tiepnhan_id(day,cursor))

    else:
        list_id = query_report.list_tiepnhan_id(today,cursor)

    list_data = []

    for id in list_id:
        t = list(query_report.patient_info(id, cursor))

        
        s = list(query_report.service_money(id, cursor))
        s = dict(s)

        if not 'Tiền xét nghiệm' in s:
            s['Tiền xét nghiệm'] = 0
        if not 'Tiền CĐHA' in s:
            s['Tiền CĐHA'] = 0
        if not 'Tiền Phẫu thuật, thủ thuật' in s:
            s['Tiền Phẫu thuật, thủ thuật'] = 0
        if not 'Tiền Giường' in s:
            s['Tiền Giường'] = 0
        if not 'Tiền Khám' in s:
            s['Tiền Khám'] = 0
        if not 'Tiền vận chuyển, Oxy, Máu' in s:
            s['Tiền vận chuyển, Oxy, Máu'] = 0
        if not 'Tiền thuốc' in s:
            s['Tiền thuốc'] = 0

        for i in sorted(s.keys()):

            t.append(s[i])

        list_data.append(t)
    
    table_column_title = ['Thời gian', 'Mã y tế', 'Mã thẻ BHYT', 'Tổng doanh thu', 'BHYT trả', 'BN trả',
                            'Tiền CĐHA',
                            'Tiền Giường',
                            'Tiền Khám',
                            'Tiền Phẫu thuật, thủ thuật',
                            'Tiền thuốc',
                            'Tiền vận chuyển, Oxy, Máu',
                            'Tiền xét nghiệm']
                                
    total_service = query_report.total_service_money(first_year_day, today, cursor)
    total_service = convert_to_chart(total_service)
    total_service_chart = total_service.copy()
    total_service.insert(0, ['Mục', 'Doanh thu'])

    today = today.strftime("%Y-%m-%d")
    cnxn.close()
    context = {
        'today': today,
        'list': list_data,
        'table_column_title': table_column_title,
        'total_service': total_service,
        'total_service_chart': total_service_chart

    }

    return render_template('report/79.html', value=context, active='report')

# USER
# trang đăng nhập
@app.route('/admin/login', methods=['GET', 'POST'])
def user_login():
    con = sqlite3.connect("dashboard.db")
    cursor = con.cursor()

    if request.method == "POST":
        user = request.form['username']
        pwd = request.form['password']

        login_user = query_user.login_user(user, pwd, cursor)
        if login_user:
            session['username'] = request.form['username']
            return redirect(url_for('admin'))
        else:
            flash('Đăng nhập thất bại')
    context = {

    }

    con.close()
    return render_template('admin/login.html', value=context)


# url đăng xuất
@app.route('/admin/logout')
def user_logout():
    session.clear()
    return redirect(url_for('home'))


# trang quản trị
@app.route('/admin', methods=['GET', 'POST'])
@register_breadcrumb(app, '..admin', 'Quản trị')
def admin():
    day_dict = get_day(None)
    today = day_dict['today']

    if session.get('username'):
        con = sqlite3.connect("dashboard.db")
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        list_post = query_user.posts(cursor)

        if request.method == 'POST' and 'new_post' in request.form:
            time_created = datetime.now().strftime('%H:%M %d/%m/%Y')
            title = request.form['titlePost']
            body = request.form['bodyPost']
            username = session['username']
            plain_text = request.form['plain_text_input']

            is_posted = query_user.new_post(time_created,title,body,username, plain_text,cursor)
            if is_posted:
                con.commit()
                return redirect(url_for('admin'))
            
        if request.method == 'POST' and 'delete_post' in request.form:
            post_id = request.form['post_id']
            is_deleted = query_user.delete_post(post_id, cursor)
            if is_deleted:
                con.commit()
                return redirect(url_for('admin'))
            
        today = today.strftime("%Y-%m-%d")
        context = {
            'today': today,
            'list_post': list_post
        }
        con.close()

        return render_template('admin/index.html', value=context)
    else:
        return redirect(url_for('user_login'))


# bài viết mới
@app.route('/admin/new-post', methods=['GET', 'POST'])
@register_breadcrumb(app, '..admin.new_post', 'Bài viết mới')
def new_post():
    con = sqlite3.connect("dashboard.db")
    cursor = con.cursor()


    context = {


    }
    con.close()

    return render_template('admin/new-post.html', value=context)



# Trang danh bạ
@app.route('/addressbook')
@register_breadcrumb(app, '..addressbook', 'Danh bạ nhân viên')
def addressbook():

    cnxn = get_db()
    cursor = cnxn.cursor()
    day_dict = get_day(None)
    today = day_dict['today']
    address_book = pd.read_excel('static/document/addressbook.xlsx')
    address_book = address_book.values.tolist()
    
    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'address_book': address_book
    }
    cnxn.close()
    return render_template('user/addressbook.html', value=context, active='addressbook')


# API Thông tin của bệnh nhân
@app.route('/patient-api/<string:mayte>')
def patient_api_detail(mayte):
    cnxn = get_db()
    cursor = cnxn.cursor()

    info = query_patient.detail(mayte, cursor)
    info_json = jsonify(
        name = info[0],
        born_date = info[1],
        sex = info[2],
        address = info[3],
        phone = info[4],
        patient_id = info[5],
        mayte = info[6],
        created_date = info[7],
        update_date = info[8]
    )


    cnxn.close()

    return info_json

# API đơn thuốc của bệnh nhân 
@app.route('/prescription-api/<int:khambenh_id>')
def prescription_api(khambenh_id):
    cnxn = get_db()
    cursor = cnxn.cursor()

    info = query_patient.donthuoc(khambenh_id, cursor)
    info_list = []
    for i in info:
        d = collections.OrderedDict()
        d['duongdung'] = i[0]
        d['thuoc'] = i[1]
        d['soluong'] = int(i[2])
        
        info_list.append(d)
    
    j = jsonify(info_list)
    cnxn.close()

    return j

