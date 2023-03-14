from flask import Flask, redirect, url_for, flash
from flask import render_template

from datetime import date, datetime, timedelta
from dateutil.relativedelta import *
from time import time

from flask import jsonify
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

from db import *
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

from flask import session
from flask import request
import sqlite3


from slugify import slugify

from models import *
from myfunc import *

total_bed = {
    'TTYT Anh Sơn': (200, 72, 272),
    'Khoa Ngoại tổng hợp': (44, 8, 52),
    'Khoa Nội tổng hơp': (37, 15, 52),
    'Khoa Hồi sức cấp cứu': (44, 10, 54),
    'Khoa Phụ Sản': (30, 11, 41),
    'Liên chuyên khoa TMH-RHM-Mắt': (17, 8, 25),
    'Khoa Y học cổ truyền': (28, 20, 48)
}

# -------------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'edcac19b15911795fe4a7ece9e27613a8565d1f549cb7535f04c035bffc91315'

Breadcrumbs(app=app)

# register zip filter for pararell loop
app.jinja_env.filters['zip'] = zip

print('test')
# Trang chủ
@app.route("/dashboard/<string:day_query>", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
@register_breadcrumb(app, '.', 'Trang chủ')
def home(day_query=None):
    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()
    
    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get =  request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query,time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)


    # Tổng Doanh thu
    current = query_revenue.total_money_betweentime(start, end, cursor)
    previous = query_revenue.total_money_betweentime(previous_start, previous_end, cursor)
    money_card = MoneyCard(current, previous)

    # Service card
    all_service_card = []
    # Tổng Doanh thu dược
    current = query_revenue.service_money(start, end, 'DU', cursor)
    card = ServiceCard('Dược',current, money_card.current, 'fa-solid fa-pills', 'medicine')
    all_service_card.append(card)

    # Tổng Doanh thu dịch vụ
    current = query_revenue.service_money(start, end, 'DV', cursor)
    card = ServiceCard('Dịch vụ',current, money_card.current, 'fa-solid fa-stethoscope', 'service')
    all_service_card.append(card)

    # Thống kê bệnh nhân
    patient_card = []


    # Số bệnh nhân nội trú
    current = 0
    previous = 0
    for i in range(diff):
        day = start + timedelta(days=i)
        previous_day = previous_start + timedelta(days=i)
        if day <= datetime.now():
            current += query_hospitalized.total(day, cursor)
        if previous_day <= datetime.now():
            previous += query_hospitalized.total(previous_day, cursor)

    card = PatientHomeCard('fa-solid fa-hospital', 'Lượt nội trú', current,previous, 'hospitalized')
    patient_card.append(card)   

    # Số lượt khám bệnh
    current = query_visited.total(start, end, cursor)
    previous = query_visited.total(previous_start, previous_end,cursor)
    card = PatientHomeCard('fa-solid fa-hospital-user', 'Lượt khám bệnh', current,previous, 'visited'  )
    patient_card.append(card)

    # Số bệnh nhân nhập viện
    current = query_hospitalized.new_in(start, end, cursor)
    previous = query_hospitalized.new_in(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-bed-pulse', 'Bệnh nhân nội trú mới', current,previous, 'new_patients')
    patient_card.append(card)

    # Lượt chuyển tuyến
    current = query_transfer.total(start, end, cursor) + query_transfer.total_department(start, end, cursor)
    previous = query_transfer.total(previous_start, previous_end,cursor) + query_transfer.total_department(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-truck-medical', 'Chuyển tuyến', current, previous,'transfer' )
    patient_card.append(card)

    # Số ca phẫu thuật thủ thuật
    current = query_surgery.total(start, end, cursor)
    previous = query_surgery.total(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-kit-medical', 'Phẫu thuật, thủ thuật', current, previous,'surgery_list' )
    patient_card.append(card)

    # Số ca đẻ
    current = query_born.total(start, end, cursor)
    previous = query_born.total(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-baby', 'Số trẻ sinh', current, previous,'born' )
    patient_card.append(card)

    # Số lượt khám theo từng phòng khám
    visited_in_department_id = query_visited.department_with_id(start,end, cursor)

    # Dữ liệu cho lượt khám bệnh chart
    visited_in_department = query_visited.department(start,end, cursor)
    visited_in_department_chart = convert_to_chart(visited_in_department)
    visited_in_department_chart.insert(0, ["Phòng", 'Lượt khám'])

    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = []
    patient_in_department_id = []
    for i in range(diff):
        day = start + timedelta(days=i)
        if day <= datetime.now():
            query = query_hospitalized.total_department(day, cursor)
            query_id = query_hospitalized.total_department_id(day, cursor)
            if not i:
                patient_in_department = query
                patient_in_department_id = query_id
            else:
                for index, row in enumerate(query):
                    patient_in_department[index][1] += row[1]
                    patient_in_department_id[index][1] += row[1]
    
    patient_in_department = convert_to_chart(patient_in_department)
    patient_in_department_chart = patient_in_department.copy()
    patient_in_department_chart.insert(0, ["Khoa", 'Bệnh nhân'])

    # Chart 30 day số lượt khám
    last30days = today - timedelta(days=50)
    last30days_visited = query_visited.day_betweenday(
        last30days, today, cursor)
    last30days_visited = [[day.strftime(
        "%A %d-%m-%Y"), int(visited)] for day, visited in last30days_visited]

    last30days_visited.reverse()


    # tin tức
    con_sqlite = get_db_dashboard()
    cursor_sqlite = con_sqlite.cursor()
    list_post = query_user.posts(cursor_sqlite)

    close_db()
    close_db_dashboard()

    # convert để hiện thị ở top filter
    today = today.strftime("%Y-%m-%d")

    context = {
        'start': start,
        'end': end,
        'diff': diff,
        'today': today,
        'soluotkham30ngay': last30days_visited,
        'patient_in_department': patient_in_department_id,
        'patient_in_department_chart': patient_in_department_chart,
        'visited_in_department': visited_in_department_id,
        'visited_in_department_chart': visited_in_department_chart,
        'posts': list_post,
        'money_card': money_card,
        'all_service_card': all_service_card,
        'patient_card': patient_card

    }

    return render_template('home/index.html', value=context,  active="home")


# Trang doanh thu
@app.route('/revenue/<string:day_query>')
@app.route('/revenue')
@register_breadcrumb(app, '..revenue', 'Doanh thu')
def revenue(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()
    
    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get =  request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query,time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    # Money card
    current = query_revenue.total_money_betweentime(start, end, cursor)
    previous = query_revenue.total_money_betweentime(previous_start, previous_end, cursor)
    extra_info = query_revenue.tenphanhom_service_format(start, end, cursor)
    money_card = MoneyRevenueCard('fa-solid fa-money-bill', 'Tổng doanh thu', current, previous, extra_info)
    
    # chart cho money card
    tmp = query_revenue.tenphanhom_service(start, end, cursor)
    money_card_chart = convert_to_chart(tmp)
    money_card_chart = money_card_chart.copy()
    money_card_chart.insert(0, ['Mục', 'Số tiền'])
    
    # Confirm card
    confirmed_visited = query_confirmed.visited_loai(
        start, end, 'NgoaiTru', cursor)
    confirmed_hospital = query_confirmed.visited_loai(
        start, end, 'NoiTru', cursor)
    money_visited = query_revenue.total_loai(
        start, end, 'NgoaiTru', cursor)
    money_hospital = query_revenue.total_loai(
        start, end, 'NoiTru', cursor)
    
    bhtt = query_revenue.bhtt(start, end, cursor)
    bntt = query_revenue.bntt(start, end, cursor)    

    confirm_card = ConfirmRevenueCard('fa-solid fa-clipboard-check', 'Hoàn tất thanh toán',confirmed_visited, confirmed_hospital,money_visited, money_hospital, bhtt, bntt)
    confirm_card_chart = [
        ['Loại', 'Doanh thu'],
        ['Ngoại trú', money_visited ],
        ['Nội trú', money_hospital]]
    
    confirm_card_extra = [
        ['Bảo hiểm thanh toán', confirm_card.bhyt_money_format()],
        ['Bệnh nhân thanh toán', confirm_card.bntt_money_format()],
    ]
    # Doanh thu 30 ngày gần nhất
    last30day = today - timedelta(days=50)
    last_30days_money = query_revenue.day_betweenday(last30day, today, cursor)
    last_30days_money = [[ngayxacnhan.strftime(
        "%A %d-%m-%Y"), int(tongdoanhthu)] for ngayxacnhan, tongdoanhthu in last_30days_money]
    last_30days_money.reverse()


    bellow_card = []
    # Thống kê trong kì này và kì trước
    is_first_loop = True
    for s,e in zip([start,previous_start], [end, previous_end]):
        current = query_revenue.total_money_betweentime(s, e, cursor)
        money_visited = query_revenue.total_loai(
            start, end, 'NgoaiTru', cursor)
        avg_confirmed = query_revenue.avg_confirmed(s, e, cursor)
        avg_money = query_revenue.avg_between(s, e, cursor)
        money_visited = query_revenue.total_loai(
            s, e, 'NgoaiTru', cursor)
        money_hospital = query_revenue.total_loai(
            s, e, 'NoiTru', cursor)
        
        if is_first_loop:
            icon = "fa-solid fa-calendar-day"
            title = 'Kì này'
            is_first_loop = False
        else:
            icon = 'fa-solid fa-backward-step'
            title = 'Kì trước'

        card = BellowRevenueCard(icon, title, current, money_card.previous,money_visited, avg_money, avg_confirmed, s, e)

        bellow_card.append(card)

    # 5 lượt xác nhận thanh toán gần nhất
    recent_confirmed = query_confirmed.last(today, cursor)



    # Doanh thu theo từng phòng khám, từng khoa
    departments = query_revenue.departments(start, end, cursor)
    departments_chart = query_revenue.departments_chart(start, end, cursor)
    departments_chart = convert_to_chart(departments_chart)
    departments_chart.insert(0, ['Khoa', 'Doanh thu'])

    top10_doanhthu = query_revenue.top_service(today, cursor)
    top10_doanhthu_table = ([noidung, tenphongkham, count, int(
        tongdoanhthu)] for noidung, tenphongkham, count, tongdoanhthu in top10_doanhthu)
    
    if diff > 30:
        total_chart = query_revenue.total_chart(start, end, cursor)
    else:
        last_30_days = today + timedelta(days=-30)
        total_chart = query_revenue.total_chart(last_30_days, today, cursor)

    total_chart = convert_to_chart(total_chart)
   
    today = today.strftime("%Y-%m-%d")
    context = {
        
        'last_30days_money': last_30days_money,
        'departments_chart': departments_chart,
        'top10_doanhthu_table': top10_doanhthu_table,

        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'money_card': money_card,
        'money_card_chart': money_card_chart,
        'confirm_card': confirm_card,
        'confirm_card_extra': confirm_card_extra,
        'confirm_card_chart': confirm_card_chart,
        'bellow_card': bellow_card,

        'departments': departments,
        'recent_confirmed': recent_confirmed,
        'total_chart': total_chart


    }
    close_db()

    return render_template('revenue/index.html', value=context, active="revenue")

# Danh sách xác nhận thanh toán
@app.route('/revenue/confirmed')
@app.route('/revenue/confirmed/<string:day_query>')
@register_breadcrumb(app, '..revenue.confirmed', 'Danh sách')
def confirmed(day_query=None):
    
    cnxn = get_db()
    cursor = cnxn.cursor()
    
    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get =  request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query,time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end
    diff = diff_days(start, end)

    all_confirmed = query_confirmed.list(start, end, cursor)

    table_column_title = ['Thời gian', 'Mã y tế', 'Số xác nhận',
                          'Loại', 'Doanh thu', 'Thanh toán', 'Nhân viên']

    staff_money = query_confirmed.staff_money(start, end, cursor)
    staff_money = list([staff, f'{int(money1):,}', f'{int(money2):,}']
                       for money1, money2, staff in staff_money)

    staff_confirmed = query_confirmed.staff_confirmed(start, end, cursor)
    staff_confirmed_chart = list([i, j] for i, j in staff_confirmed)
    staff_confirmed_chart.insert(0, ['Tên nhân viên', 'Số lượt xác nhận'])

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'list': all_confirmed,
        'table_column_title': table_column_title,
        'staff_money': staff_money,
        'staff_confirmed_chart': staff_confirmed_chart
    }

    close_db()

    return render_template('revenue/confirmed_list.html', value=context, active='revenue')


# Trang bệnh nhân nội trú
@app.route('/hospitalized/<string:day_query>')
@app.route('/hospitalized')
@register_breadcrumb(app, '.hospitalized', 'Nội trú')
def hospitalized(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()
    
    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get =  request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query,time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start

    diff = diff_days(start, end)
    # Số bệnh nhân nội trú
    current = 0
    previous = 0
    for i in range(diff):
        day = start + timedelta(days=i)
        previous_day = previous_start + timedelta(days=i)
        if day <= datetime.now():
            current += query_hospitalized.total(day, cursor)
        if previous_day <= datetime.now():
            previous += query_hospitalized.total(previous_day, cursor)

    new_in = query_hospitalized.new_in(start, end, cursor)
    old_out = query_hospitalized.old_out(start, end, cursor)
    card_top = TopHospitalCard('fa-solid fa-hospital', 'Lượt nội trú', current, previous, new_in, old_out)

    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = query_hospitalized.total_department(today, cursor)
    patient_in_department_id = query_hospitalized.total_department_id(
        today, cursor)

    patient_in_department = convert_to_chart(patient_in_department)
    patient_in_department_chart = patient_in_department.copy()
    patient_in_department_chart.insert(0, ["Khoa", 'Bệnh nhân'])

    # Thống kê Số bệnh nhân nội trú nhập mới từng khoa
    patient_in_department_today = query_hospitalized.in_department_day(
        today, cursor)

    # chart số bệnh nhân nội trú 30 ngày gần nhất
    last_30_day_chart = []
    for day in range(30):
        day_q = today - timedelta(days=day)
        count_patient = query_hospitalized.total(day_q, cursor)

        last_30_day_chart.append(
            [day_q.strftime("%A %d-%m-%Y"), count_patient])

    last_30_day_chart.reverse()

    # Bệnh nhân vừa nhập viện
    recent_hospitalized_in_day = sql_query.recent_confirmed_review(
        today, cursor)
    last_patients = query_hospitalized.last5(today, cursor)
    last_patients = ([time_in_department.strftime("%H:%M %d/%m/%Y"), patient_name, department]
                     for time_in_department, patient_name, department in last_patients)

    bellow_card = []

    current = query_hospitalized.new_in(day_class.monday(), day_class.sunday(), cursor)
    previous = query_hospitalized.new_in(day_class.lastweek_monday(), day_class.monday(), cursor)
    card = BellowHospitalCard(current, previous, 'Tuần này', 'Tuần trước')
    bellow_card.append(card)

    current = query_hospitalized.new_in(day_class.first_day_month(), day_class.end_day_month(), cursor)
    previous = query_hospitalized.new_in(day_class.first_day_2month(), day_class.first_day_month(), cursor)
    card = BellowHospitalCard(current, previous, 'Tháng này', 'Tháng trước')
    bellow_card.append(card)

    current = query_hospitalized.new_in(day_class.first_day_year(), day_class.end_day_year(), cursor)
    previous = query_hospitalized.new_in(day_class.first_day_2year(), day_class.first_day_year(), cursor)
    card = BellowHospitalCard(current, previous, 'Năm này', 'Năm trước')
    bellow_card.append(card)

    # Tính công suất giường bệnh
    r=     ['TTYT Anh Sơn', 0,272]
    percent_bed = [
        ['Khoa Hồi sức cấp cứu',0, 0,54],
        ['Khoa Ngoại tổng hợp', 0,0,52],
        ['Khoa Nội tổng hơp', 0,0,52],
        ['Khoa Phụ Sản', 0,0,41],
        ['Khoa Y học cổ truyền', 0,0,48],
        ['Liên chuyên khoa TMH-RHM-Mắt',0, 0,25]
    ]
    for i in range(diff):
        day = start + timedelta(days=i)
        if day <= datetime.now():
            total = query_hospitalized.total(day, cursor)
            departments = query_hospitalized.total_department(day, cursor)
            for index, department in enumerate(departments):
                percent_bed[index][1] += department[1]
                percent_bed[index][2] += percent_bed[index][3]
    percent_bed_table = []
    for department in percent_bed:
        bed = Bed(department[0], department[1], department[2])
        percent_bed_table.append(bed)


    
    chart_30_days = []

    # chart công suất toàn viện 30 ngày
    for n in range(31):
        day = today - timedelta(n)
        today_real_bed = query_hospitalized.total(day, cursor)
        total_percent = get_percent(
            today_real_bed, total_bed['TTYT Anh Sơn'][2])
        percent = total_percent[1]
        if percent > 95:
            color = 'red'
        elif percent > 70:
            color = 'green'
        elif percent > 60:
            color = 'orange'
        else:
            color = 'gray'
        chart_30_days.append([day.strftime("%d/%m/%Y"), percent, color])
    chart_30_days.reverse()
    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'patient_in_department': patient_in_department_id,
        'patient_in_department_today': patient_in_department_today,
        'patient_in_department_chart': patient_in_department_chart,
        'last_30_day_chart': last_30_day_chart,
        'recent_hospitalized_in_day': recent_hospitalized_in_day,
        'last_patients': last_patients,
        'chart_30_days': chart_30_days,
        'percent_bed_table': percent_bed_table

    }

    close_db()
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

    table_column_title = ['Thời gian', 'Mã y tế', 'Số bệnh án',
                          'Tên bệnh nhân', 'Chẩn đoán', 'Khoa', 'Nhân viên']

    list_patients = query_hospitalized.new_list(today, cursor)
    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2, e3, e7, e4, e5, e6]
                         for e1, e2, e3, e7, e4, e5, e6 in list_patients)

    patients_department_chart = query_hospitalized.in_department_day(
        today, cursor)
    patients_department_chart = list([i, j]
                                     for i, j in patients_department_chart)

    patients_department_chart.insert(0, ['Khoa', 'Số bệnh nhân nhập mới'])
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

    table_column_title = ['Thời gian', 'Mã y tế',  'Số bệnh án',
                          'Chẩn đoán ra viện', 'Lí do', 'Bác sĩ', 'Khoa']

    list_patients = query_hospitalized.out_list(today, cursor)

    chart = query_hospitalized.out_department_day(today, cursor)
    chart = list([i, j] for i, j in chart)

    chart.insert(0, ['Khoa', 'Số bệnh nhân ra viện'])
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

    table_column_title = ['Thời gian', 'Mã y tế', 'Tên bệnh nhân',
                          'Chẩn đoán ra viện', 'Bác sĩ', 'Khoa phòng']

    list_patients = query_transfer.transfer(today, cursor)

    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2, e3, e7, e4, e5]
                         for e1, e2, e3, e7, e4, e5 in list_patients)

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

    table_column_title = ['Thời gian vào khoa', 'Mã y tế',  'Số bệnh án',
                          'Tên bệnh nhân', 'Chẩn đoán trong khoa', 'Bác sĩ', 'Khoa']

    list_patients = query_hospitalized.patients(today, cursor)

    chart = query_hospitalized.total_department(today, cursor)
    chart = list([i, j] for i, j in chart)

    chart.insert(0, ['Khoa', 'Số bệnh nhân'])
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
    percent_change = get_change(total, yesterday_visited)
    percent = get_percent(total, yesterday_visited)

    card_top.append(["Số lượt khám bệnh", total,
                    percent_change, percent, yesterday_visited])

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

        last_30_day_chart.append(
            [day_q.strftime("%A %d-%m-%Y"), count_patient])

    last_30_day_chart.reverse()

    # Bệnh nhân vừa nhập viện
    recent_hospitalized_in_day = sql_query.recent_confirmed_review(
        today, cursor)
    last_patients = query_visited.last5(today, cursor)
    last_patients = ([time_in_department.strftime("%H:%M %d/%m/%Y"), patient_name, department]
                     for time_in_department, patient_name, department in last_patients)

    card_bellow = []
    this_week = query_visited.total_betweenday(mon_day, today, cursor)
    this_month = query_visited.total_betweenday(first_month_day, today, cursor)
    this_year = query_visited.total_betweenday(first_year_day, today, cursor)

    last_week = query_visited.total_betweenday(
        last_week_monday, last_week_sun_day, cursor)
    last_month = query_visited.total_betweenday(
        last_first_month_day, last_end_month_day, cursor)
    last_year = query_visited.total_betweenday(
        last_first_year_day, end_last_year_day, cursor)

    week_percent = get_percent(this_week, last_week)
    month_percent = get_percent(this_month, last_month)
    year_percent = get_percent(this_year, last_year)

    card_bellow.append(
        ['Tuần này', this_week, 'Tuần trước', last_week, week_percent])
    card_bellow.append(
        ['Tháng này', this_month, 'Tháng trước', last_month, month_percent])
    card_bellow.append(
        ['Năm này', this_year, 'Năm trước', last_year, year_percent])

    # Chart 30 day số lượt khám
    last30days = today - timedelta(days=50)
    last30days_visited = query_visited.day_betweenday(
        last30days, today, cursor)
    last30days_visited = [[day.strftime(
        "%A %d-%m-%Y"), int(visited)] for day, visited in last30days_visited]

    last30days_visited.reverse()

    # tổng số lượt khám 30 ngày gần nhất theo từng khoa phòng
    last30days_visited_department = query_visited.department_week(last30days,today, cursor)
    last30days_visited_department = convert_to_chart(last30days_visited_department)
    last30days_visited_department.insert(0, ["Phòng khám", 'Bệnh nhân'])

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'card_top': card_top,
        'card_bellow': card_bellow,
        'card_top_body': card_top_body,
        'patient_in_department': patient_in_department,
        'visited_in_department_today': visited_in_department_today,
        'patient_in_department_chart': last30days_visited_department,
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

    table_column_title = ['Thời gian khám', 'Mã y tế', 'Tên bệnh nhân',
                          'Số tiếp nhận', 'Chẩn đoán trong khoa', 'Giải quyết','Bác sĩ', 'Khoa']

    list_patients = query_visited.patients(today, cursor)

    chart = query_visited.department_day(today, cursor)
    chart = list([i, j] for i, j in chart)

    chart.insert(0, ['Khoa', 'Số bệnh nhân'])
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

    table_column_title = ['Thời gian khám', 'Mã y tế',
                          'Tên bệnh nhân', 'Chẩn đoán trong khoa', 'Bác sĩ', 'Khoa']

    list_patients = query_visited.patients(today, cursor)
    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2, e3, e4, e5, e6]
                         for e1, e2, e3, e4, e5, e6 in list_patients)

    chart = query_visited.department_day(today, cursor)
    chart = list([i, j] for i, j in chart)

    chart.insert(0, ['Khoa', 'Số bệnh nhân'])
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

    table_column_title = ['Thời gian kết thúc', 'Mã y tế',
                          'Tên bệnh nhân', 'Can thiệp', 'Loại', 'Nơi thực hiện']

    list_patients = query_surgery.list(today, cursor)
    chart = query_visited.department_day(today, cursor)
    chart = list([i, j] for i, j in chart)

    chart.insert(0, ['Khoa', 'Số bệnh nhân'])
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

    table_column_title = ['Thời gian kết thúc', 'Mã Y tế',
                          'Tên bệnh nhân', 'Can thiệp phẫu thuật', 'Mô tả sau phẫu thuật']

    if day_query == 'thisyear':
        list_patients = query_born.list_between(first_year_day, today, cursor)
    else:
        list_patients = query_born.list(today, cursor)

    chart = query_visited.department_day(today, cursor)
    chart = list([i, j] for i, j in chart)

    chart.insert(0, ['Khoa', 'Số bệnh nhân'])
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

    table_column_title = ['Nội dung', 'Tên',
                          'Khoa/Phòng', 'Số lượt', 'Tổng doanh thu']

    list_patients = query_revenue.services(today, cursor)
    list_patients = list(
        [e1, e2, e3, e4, f'{ int(e5):,}'] for e1, e2, e3, e4, e5 in list_patients)

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

    table_column_title = ['Nội dung', 'Tên',
                          'Khoa/Phòng', 'Số lượt', 'Tổng doanh thu']

    list_patients = query_revenue.services_type(today, 'DU', cursor)
    list_patients = list(
        [e1, e2, e3, e4, f'{ int(e5):,}'] for e1, e2, e3, e4, e5 in list_patients)

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

    table_column_title = ['Nội dung', 'Tên',
                          'Khoa/Phòng', 'Số lượt', 'Tổng doanh thu']

    list_patients = query_revenue.services_type(today, 'DV', cursor)
    list_patients = list(
        [e1, e2, e3, e4, f'{ int(e5):,}'] for e1, e2, e3, e4, e5 in list_patients)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
    }
    cnxn.close()
    return render_template('revenue/service.html', value=context, active='revenue', order_column=4)


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

    table_column_title = ['Thời gian', 'Mã Y tế',
                          'Tên bệnh nhân', 'Chẩn đoán', 'Giải quyết','Bác sĩ']

    list_patients = []

    for d_id in department_id_list:
        list_patients.extend(
            query_visited.list_department(today, d_id, cursor))

    department_name = ''
    for d_id in department_id_list:
        department_name += (query_visited.name_department(d_id,
                            cursor)) + ' - '
    startday = today + timedelta(days=-30)
    visited_department_chart = query_visited.department_id_between(
        startday, today, department_id, cursor)
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

    table_column_title = ['Thời gian', 'Mã Y tế',
                          'Tên bệnh nhân', 'Chẩn đoán', 'Bác sĩ']

    list_patients = query_hospitalized.list_department(
        today, department_id, cursor)

    list_patients = list([e1.strftime("%H:%M %d-%m-%Y"), e2, e3, e4, e5]
                         for e1, e2, e3, e4, e5 in list_patients)
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
    cnxn = get_db()
    cursor = cnxn.cursor()

    day_dict = get_day(day_query)
    today = day_dict['today']

    chart_30_days = []
    # chart công suất toàn viện 30 ngày
    for n in range(31):
        day = today - timedelta(n)
        today_real_bed = query_hospitalized.total_day(day, cursor)
        total_percent = get_percent(
            today_real_bed, total_bed['TTYT Anh Sơn'][2])
        percent = total_percent[1]
        if percent > 95:
            color = 'red'
        elif percent > 70:
            color = 'green'
        elif percent > 60:
            color = 'orange'
        else:
            color = 'gray'
        chart_30_days.append([day.strftime("%d/%m/%Y"), percent, color])
    chart_30_days.reverse()
    if request.method == 'POST':
        bed_list_betweenday = []
        start_day = request.form['start_date']
        start_day = datetime.strptime(start_day, '%Y-%m-%d')
        end_day = request.form['end_date']
        end_day = datetime.strptime(end_day, '%Y-%m-%d')
        count_day = int((end_day - start_day).days) + 1
        for n in range(count_day):
            today = start_day + timedelta(n)
            bed_list = bed_caculator(today, cursor)
            bed_list_betweenday.append(bed_list)

        today_real_bed = sum(i[0][1] for i in bed_list_betweenday)
        total_percent = get_percent(
            today_real_bed, total_bed['TTYT Anh Sơn'][2] * count_day)
        ttyt = ('TTYT Anh Sơn', today_real_bed,
                total_bed['TTYT Anh Sơn'][2] * count_day, total_percent)

        # công suất khoa ngoại
        ngoai_real_bed = sum(i[1][1] for i in bed_list_betweenday)
        ngoai_percent = get_percent(
            ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2] * count_day)
        ngoai = ('Khoa Ngoại tổng hợp', ngoai_real_bed,
                 total_bed['Khoa Ngoại tổng hợp'][2] * count_day, ngoai_percent)

        # công suất khoa nội
        noi_real_bed = sum(i[2][1] for i in bed_list_betweenday)
        noi_percent = get_percent(
            noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2] * count_day)
        noi = ('Khoa Nội-Truyền nghiễm', noi_real_bed,
               total_bed['Khoa Nội-Truyền nghiễm'][2] * count_day, noi_percent)

        # công suất khoa hscc
        hscc_real_bed = sum(i[3][1] for i in bed_list_betweenday)
        hscc_percent = get_percent(
            hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2] * count_day)
        hscc = ('Khoa HSCC-Nhi', hscc_real_bed,
                total_bed['Khoa HSCC-Nhi'][2] * count_day, hscc_percent)

        # công suất khoa sản
        san_real_bed = sum(i[4][1] for i in bed_list_betweenday)
        san_percent = get_percent(
            san_real_bed, total_bed['Khoa Phụ Sản'][2] * count_day)
        san = ('Khoa Phụ Sản', san_real_bed,
               total_bed['Khoa Phụ Sản'][2] * count_day, san_percent)

        # công suất khoa Liên chuyên khoa TMH-RHM-Mắt
        lck_real_bed = sum(i[5][1] for i in bed_list_betweenday)
        lck_percent = get_percent(
            lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2] * count_day)
        lck = ('Liên chuyên khoa TMH-RHM-Mắt', lck_real_bed,
               total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2] * count_day, lck_percent)

        # công suất khoa yhct
        yhct_real_bed = sum(i[6][1] for i in bed_list_betweenday)
        yhct_percent = get_percent(
            yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2] * count_day)
        yhct = ('Khoa Đông Y&PHCN', yhct_real_bed,
                total_bed['Khoa Đông Y&PHCN'][2] * count_day, yhct_percent)

        bed_list = [ttyt, ngoai, noi, hscc, san, lck,  yhct]
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
    table_column_title = ['Ngày tạo', 'Mã Y tế',
                          'Tên bệnh nhân', 'Ngày sinh', 'Số điện thoại', 'Địa chỉ']
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
    card1 = ['Doanh thu theo từng mục', 'Mẫu báo cáo 79 của BHYT',
             'Chi tiết doanh thu từng mục: Tiền CĐHA, Tiền Xét nghiệm, Tiền Thuốc, Tiền Phẫu thuật, Tiền Khám, Tiền Giường', 'report_79']

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
        start_day = datetime.strptime(start_day, '%Y-%m-%d')
        end_day = request.form['end_date']
        end_day = datetime.strptime(end_day, '%Y-%m-%d')
        for n in range(int((end_day - start_day).days)):
            day = start_day + timedelta(n)
            list_id.extend(query_report.list_tiepnhan_id(day, cursor))

    else:
        list_id = query_report.list_tiepnhan_id(today, cursor)

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

    total_service = query_report.total_service_money(
        first_year_day, today, cursor)
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


# Báo cáo tổng hợp
@app.route('/report/general/<string:day_query>', methods=['GET', 'POST'])
@app.route('/report/general', methods=['GET', 'POST'])
@register_breadcrumb(app, '..report.general', 'Tổng hợp')
def report_general(day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()
    day_class = DayQuery(day_query)

    if request.method == 'POST' and 'filter_btn' in request.form:
        list_id = []
        start_day = request.form['start_date']
        start = datetime.strptime(start_day, '%Y-%m-%dT%H:%M')
        end_day = request.form['end_date']
        end = datetime.strptime(end_day, '%Y-%m-%dT%H:%M')
        count_day = int((end - start).days) + 1
    else:
        start = day_class.today
        end = start + timedelta(days=1)
        count_day = 1

    money = query_revenue.total_money_betweentime(start, end, cursor)
    revenue_table_data = ['Doanh thu', money]

    money_bhtt = query_revenue.bhtt_betweentime(start, end, cursor)
    revenue_bhtt_table_data = ['Bảo hiểm thanh toán', money_bhtt]

    money_bntt = query_revenue.bntt_betweentime(start, end, cursor)
    revenue_bntt_table_data = ['Bệnh nhân thanh toán', money_bntt]

    total_visited = query_visited.total_betweentime(start, end, cursor)
    visited_table_data = ['Lượt khám bệnh', total_visited]

    total_hospitalized = query_hospitalized.in_betweentime(start, end, cursor)
    hospital_table_data = ['Lượt nhập viện', total_hospitalized]

    total_transfer = query_transfer.total_betweentime(
        start, end, cursor) + query_transfer.total_department_betweentime(start, end, cursor)
    transfer_table_data1 = ['Lượt chuyển tuyến', total_transfer]
    transfer_table_data2 = ['Lượt chuyển tuyến ngoại trú',
                            query_transfer.total_betweentime(start, end, cursor)]
    transfer_table_data3 = ['Lượt chuyển tuyến nội trú',
                            query_transfer.total_department_betweentime(start, end, cursor)]

    table_data = [revenue_table_data, revenue_bhtt_table_data, revenue_bntt_table_data, visited_table_data,
                  hospital_table_data, transfer_table_data1, transfer_table_data2, transfer_table_data3]
    today = day_class.today.strftime("%Y-%m-%d")
    cnxn.close()
    context = {
        'today': today,
        'table_data': table_data,
        'start': start,
        'end': end,
        'count_day': count_day


    }

    return render_template('report/general.html', value=context, active='report')


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

            is_posted = query_user.new_post(
                time_created, title, body, username, plain_text, cursor)
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


# Trang tin tức
@app.route('/news')
@register_breadcrumb(app, '..news', 'Thông tin công việc')
def news():
    con = sqlite3.connect("dashboard.db")
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    list_post = query_user.posts(cursor)
    day_class = DayQuery(None)
    today = day_class.today.strftime("%Y-%m-%d")
    context = {
        'posts': list_post,
        'today': today
    }
    con.close()
    return render_template('news/index.html', value=context, active='news', order_column=4)


# chi tiết bài viết
@app.route('/news/post/<int:post_id>')
@register_breadcrumb(app, '..news.post', 'Bài viết')
def detail_post(post_id):
    con = sqlite3.connect("dashboard.db")
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    post = query_user.post(post_id, cursor)

    day_class = DayQuery(None)
    today = day_class.today.strftime("%Y-%m-%d")

    context = {
        'post': post,
        'today': today
    }
    con.close()

    return render_template('news/post.html', value=context, active='news', hidden_top_filter=True)

# trang báo cáo thu tiền dịch vụ
@app.route('/admin/money', methods=['GET', 'POST'])
@register_breadcrumb(app, '..admin.money', 'Tiền dịch vụ')
def admin_money():
    day_dict = get_day(None)
    today = day_dict['today']


    if session.get('username'):
        con = sqlite3.connect("dashboard.db")
        con.row_factory = sqlite3.Row
        cursor = con.cursor()

        sql_list_report = """
        SELECT *
        FROM report_money
        ORDER BY id DESC
        """
        list_reports = cursor.execute(sql_list_report).fetchall()
        titles = cursor.execute(sql_list_report).description
            
        list_form_title_money = [["Tiền khám bệnh"],["Viện phí"],["Xét nghiệm"],["Điện tim"],["Test covid 19"],["Lưu huyết não"],["Siêu âm"],["XQ"],["Nội soi dạ dày, thực quản"],["Nội soi TMH"],["Nội soi CTC"],["Khám sức khỏe"],["Bó bột gây mê"],["Chụp CT"],["Tiêm SAT"],["Tiêm phòng dại"],["Tiêm VGB 1ml"],["Tiêm VGB 0.5ml"],["Vắc xin Rotamin"],["Vắc xin Sởi - Quai bị - Rubella"],["Vắc xin Cúm"],["Vắc xin Quimihib"],["Thuốc"]]
        for i in list_form_title_money:
            i.append(slugify(i[0]).replace('-','_'))

        if request.method == 'POST' and 'new_report' in request.form:
           
            values = []
     
            for i in (request.form):
            
                values.append(request.form[i])
            
            values.pop(-1)

            sql = """
            INSERT INTO report_money(ngay,tien_kham_benh,vien_phi,xet_nghiem,dien_tim,test_covid_19,luu_huyet_nao,sieu_am,xq,noi_soi_da_day_thuc_quan,noi_soi_tmh,noi_soi_ctc,kham_suc_khoe,bo_bot_gay_me,chup_ct,tiem_sat,tiem_phong_dai,tiem_vgb_1ml,tiem_vgb_0_5ml,vac_xin_rotamin,vac_xin_soi_quai_bi_rubella,vac_xin_cum,vac_xin_quimihib,thuoc)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """
            cursor.execute(sql, values)
            con.commit()
            return redirect(url_for('admin_money'))

        
        if request.method == 'POST' and 'delete_report' in request.form:
            sql = """
            DELETE FROM report_money WHERE id = ?
            """
            id = request.form['report_id']
            print(id)
            cursor.execute(sql, (request.form['report_id']))
            con.commit()
            return redirect(url_for('admin_money'))
        


        today = today.strftime("%Y-%m-%d")
        context = {
            'today': today,
            'list_form_title_money': list_form_title_money,
            'list_reports': list_reports,
            'titles': titles
        }
        con.close()

        return render_template('admin/report-money.html', value=context)
    else:
        return redirect(url_for('user_login'))

# Trang danh bạ
@app.route('/addressbook')
@register_breadcrumb(app, '..addressbook', 'Danh bạ nhân viên')
def addressbook():

    con = sqlite3.connect("dashboard.db")
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    address_book = query_user.users(cursor)
    day_class = DayQuery(None)
    today = day_class.today.strftime("%Y-%m-%d")
    context = {
        'address_book': address_book,
        'today': today
    }
    con.close()
    return render_template('user/addressbook.html', value=context, active='addressbook', hidden_top_filter=True)


# API Thông tin của bệnh nhân
@app.route('/patient-api/<string:mayte>')
def patient_api_detail(mayte):
    cnxn = get_db()
    cursor = cnxn.cursor()

    info = query_patient.detail(mayte, cursor)
    info_json = jsonify(
        name=info[0],
        born_date=info[1],
        sex=info[2],
        address=info[3],
        phone=info[4],
        patient_id=info[5],
        mayte=info[6],
        created_date=info[7],
        update_date=info[8]
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
