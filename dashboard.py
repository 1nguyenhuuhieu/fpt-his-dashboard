from flask import Flask
from flask import render_template
import pyodbc
from datetime import date, datetime, timedelta
from dateutil.relativedelta import *
from time import time

from flask import jsonify

import sql_query

from sqlquery import hospitalized as query_hospitalized
from sqlquery import confirmed as query_confirmed
from sqlquery import revenue as query_revenue
from sqlquery import visited as query_visited
from sqlquery import transfer as query_transfer
from sqlquery import surgery as query_surgery
from sqlquery import born as query_born

import textwrap

from flask_breadcrumbs import Breadcrumbs, register_breadcrumb


# Kết nối database sql server
def get_db():
    server = '192.168.123.254'
    database = 'eHospital_NgheAn'
    username = 'sa'
    password = 'toanthang'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server+';DATABASE='+database+';UID='+username+';PWD=' + password)
    return cnxn

# def get_db():
#     cnxn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}', server='localhost', database='eHospital_NgheAn',               
#                trusted_connection='yes')
#     return cnxn

def get_change(current, previous):
    if not current:
        current = 0
    if not previous:
        previous = 0
    if current == previous:
        return 100
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
        return 100
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
    if day:
        today = datetime.strptime(day, '%Y-%m-%d')
    else:
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


huonggiaiquyet = {
    454: "Cấp toa cho về",
    455: "Điều trị ngoại trú",
    456: "Cấp toa & Hẹn tái khám",
    457: "Nhập viện",
    458: "Chuyển tuyến",
    460: "Cho thực hiện CLS...",
    1331: "Không toa",
    2981: "Hẹn lấy kết quả CLS",
    4011: "Cấp toa nghỉ ốm",
    4030: "Cấp toa chuyển tuyến dưới",
    8055: "Khám Sức Khỏe",
    8056: "Không Khám Bệnh",
    9165: "Khám Thêm Phòng"
}

# -------------------------------------------------------------
app = Flask(__name__)
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
    yesterday_money = query_revenue.total_day(yesterday, cursor)
    percent_doanhthu = get_change(today_money, yesterday_money)
    top_card = ('fa-solid fa-money-bill',"Tổng doanh thu", today_money, percent_doanhthu)


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
        ('hospitalized',"Bệnh nhân ngoại trú", 'fa-solid fa-hospital-user', today_visited, percent_visited))

    # Số bệnh nhân nhập viện
    today_hospitalize = query_hospitalized.in_day(today, cursor)
    yesterday_hospitalize = query_hospitalized.in_day(yesterday, cursor)
    percent_hospitalize = get_change(today_hospitalize, yesterday_hospitalize)
    patient_card.append(('hospitalized',"Bệnh nhân nội trú mới", 'fa-solid fa-bed-pulse',
                        today_hospitalize, percent_hospitalize))

    # Lượt chuyển tuyến
    today_transfer = query_transfer.total_day(today, cursor)
    yesterday_transfer = query_transfer.total_day(yesterday, cursor)
    percent_transfer = get_change(today_transfer, yesterday_transfer)

    patient_card.append(
        ('hospitalized',"Chuyển tuyến", 'fa-solid fa-truck-medical', today_transfer, percent_transfer))

    # Số ca phẫu thuật thủ thuật
    today_surgecies = query_surgery.total_day(today, cursor)
    yesterday_surgecies = query_surgery.total_day(yesterday, cursor)
    percent_surgecies = get_change(today_surgecies, yesterday_surgecies)
    patient_card.append(
        ('hospitalized',"Phẫu thuật, thủ thuật", 'fa-solid fa-kit-medical', today_surgecies, percent_surgecies))

    # Số ca đẻ
    today_born = query_born.total_day(today, cursor)
    yesterday_born = query_born.total_day(yesterday, cursor)
    percent_born = get_change(today_born, yesterday_born)
    patient_card.append(
        ('hospitalized',"Số trẻ sinh", 'fa-solid fa-baby', today_born, percent_born))

    # Thống kê số lượt khám theo từng phòng khám
    visited_in_department = query_visited.department_day(today, cursor)

    # Dữ liệu cho lượt khám bệnh chart
    visited_in_department = convert_to_chart(visited_in_department)
    visited_in_department_chart = visited_in_department.copy()
    visited_in_department_chart.insert(0, ["Phòng", 'Lượt khám'])
    
    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = query_hospitalized.total_department(today, cursor)

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


    # convert để hiện thị ở top filter
    today = today.strftime("%Y-%m-%d")

    context = {
        'top_card': top_card,
        'medicine_card': medicine_card,
        'service_card': service_card,
        'patient_card': patient_card,
        'today': today,
        'soluotkham30ngay': last30days_visited,
        'patient_in_department': patient_in_department,
        'patient_in_department_chart': patient_in_department_chart,
        'visited_in_department': visited_in_department,
        'visited_in_department_chart': visited_in_department_chart,
        'recent_action_time': recent_action_time,
        'recent_action_tiepnhan_id': recent_action_tiepnhan_id,
        'recent_detail': recent_detail
    }

    cnxn.close()
    return render_template('home/index.html', value=context, title="Dashboard")


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

    return render_template('revenue/index.html', value=context, title="Doanh thu")



# Trang doanh thu
@app.route('/revenue/detail/<string:day_query>')
@app.route('/revenue/detail')
@register_breadcrumb(app, '..revenue.detail', 'Thống kê doanh thu')
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
    return render_template('revenue/detail.html', value=context)

# Danh sách xác nhận thanh toán
@app.route('/revenue/confirmed')
@app.route('/revenue/confirmed/<string:day_query>')
@register_breadcrumb(app, '..revenue.confirmed', 'Danh sách xác nhận')
def confirmed(day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']

    all_confirmed = query_confirmed.list(today, cursor)
    all_confirmed = ([thoigian.strftime("%H:%M:%S %d-%m-%Y"),soxacnhan,benhnhan_id,  f'{int(doanhthu):,}', int(thanhtoan), phongkham,nhanvien] for thoigian,soxacnhan, benhnhan_id, doanhthu, thanhtoan,phongkham, nhanvien in all_confirmed)

    table_column_title = ['Thời gian', 'Số xác nhận', 'ID Bệnh nhân', 'Doanh thu', 'Thanh toán', 'Phòng khám', 'Nhân viên']

    today = today.strftime("%Y-%m-%d")


    context = {
        'today': today,
        'all_confirmed': all_confirmed,
        'table_column_title': table_column_title
    }

    cnxn.close()
    

    return render_template('revenue/confirmed_list.html', value=context, title="Xác nhận")

@app.route('/confirmed/detail/<string:SoXacNhan_Id>')
@register_breadcrumb(app, './revenue/detail', 'Chi tiết xác nhận')
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
    print(detail_json)
    cnxn.close()
    return detail_json

@app.route('/hospitalized/<string:day_query>')
@app.route('/hospitalized')
@register_breadcrumb(app, './hospitalized', 'Nội trú')
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

    card_top.append(["Nội trú hôm nay", today_in_hospital, percent_change, percent, yesterday_in_hostpital])

    card_top_body = []
    card_top_body.append(['Nhập mới', recent_today_in_hospital])
    card_top_body.append(['Ra viện', out_hospital_day])

    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = query_hospitalized.total_department(today, cursor)

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
    last_patients = sql_query.last_in_hospitalized(today, cursor)
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

    tic = time()
    last_50_day = today + timedelta(days=-50)
    last_30_day_in_hostpital_chart = query_hospitalized.in_betweenday(last_50_day, today, cursor)
    last_30_day_in_hostpital_chart = convert_to_chart_date(last_30_day_in_hostpital_chart)
    print(last_30_day_in_hostpital_chart)
    
    print(f'load time: {time()-tic}')

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'card_top': card_top,
        'card_bellow': card_bellow,
        'card_top_body': card_top_body,
        'patient_in_department': patient_in_department,
        'patient_in_department_today': patient_in_department_today,
        'patient_in_department_chart': patient_in_department_chart,
        'last_30_day_chart': last_30_day_chart,
        'last_30_day_in_hostpital_chart': last_30_day_in_hostpital_chart,
        'recent_hospitalized_in_day': recent_hospitalized_in_day,
        'last_patients': last_patients
    }

    cnxn.close()
    return render_template('hospitalized/index.html', value=context, title="Nội trú")
