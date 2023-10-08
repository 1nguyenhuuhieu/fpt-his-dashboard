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
from sqlquery import medical_record as query_medical_record
from sqlquery import home as query_home
from sqlquery import lab as query_lab

from db import *
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

from flask import session
from flask import request
import sqlite3


from slugify import slugify

from models import *
from myfunc import *

import time

from functools import wraps
from flask import g, request, redirect, url_for


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



# login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            flash('Đăng nhập để sử dụng')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

# manager decorator
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None or session['username'] != 'manager':
            flash('Đăng nhập tài khoản quản lý để sử dụng')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

# manager decorator
def lab_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None or session['username'] != 'lab':
            flash('Đăng nhập tài khoản xét nghiệm để sử dụng')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function


# Trang chủ
@app.route("/dashboard/<string:day_query>", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
@register_breadcrumb(app, '.', 'Trang chủ')
@login_required
def home(day_query=None):
    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    start_time = time.time()
    if session['username'] == 'manager':
        print('true')
        phannhom_money = query_revenue.phannhom_money(start, end, cursor)
        previous_phannhom_money = query_revenue.phannhom_money(previous_start, previous_end, cursor)
        # Tổng Doanh thu
        current = sum(int(row.TongDoanhThu) for row in phannhom_money)
        previous = sum(int(row.TongDoanhThu) for row in previous_phannhom_money)
        money_card = MoneyCard(current, previous)

        # Service card
        all_service_card = []
        # Tổng Doanh thu dược
        if phannhom_money:
            for row in phannhom_money:
                if row.PhanNhom == 'DU':
                    current1 = int(row.TongDoanhThu)
                elif  row.PhanNhom == 'DV' :
                    current2 = int(row.TongDoanhThu)
        else:
            current1 = 0
            current2 = 0

        card = ServiceCard('Dược', current1, money_card.current,
                        'fa-solid fa-pills', 'medicine')
        all_service_card.append(card)

        # Tổng Doanh thu dịch vụ
        card = ServiceCard('Dịch vụ', current2, money_card.current,
                        'fa-solid fa-stethoscope', 'service')
        all_service_card.append(card)
    else:
        all_service_card = None
        money_card = None


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

    card = PatientHomeCard('fa-solid fa-hospital',
                           'Lượt nội trú', current, previous, 'hospitalized')
    patient_card.append(card)

    # Số lượt khám bệnh
    current = query_visited.total(start, end, cursor)
    previous = query_visited.total(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-hospital-user',
                           'Lượt khám bệnh', current, previous, 'visited')
    patient_card.append(card)

    # Số bệnh nhân nhập viện
    current = query_hospitalized.new_in(start, end, cursor)
    previous = query_hospitalized.new_in(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-bed-pulse',
                           'Bệnh nhân nội trú mới', current, previous, 'new_patients')
    patient_card.append(card)

    # Lượt chuyển tuyến
    current = query_transfer.total(
        start, end, cursor) + query_transfer.total_department(start, end, cursor)
    previous = query_transfer.total(previous_start, previous_end, cursor) + \
        query_transfer.total_department(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-truck-medical',
                           'Chuyển tuyến', current, previous, 'transfer')
    patient_card.append(card)

    # Số ca phẫu thuật thủ thuật
    current = query_surgery.total(start, end, cursor)
    previous = query_surgery.total(previous_start, previous_end, cursor)
    card = PatientHomeCard('fa-solid fa-kit-medical',
                           'Phẫu thuật, thủ thuật', current, previous, 'surgery_list')
    patient_card.append(card)

    # Số ca đẻ
    current = query_born.total(start, end, cursor)
    previous = query_born.total(previous_start, previous_end, cursor)
    card = PatientHomeCard(
        'fa-solid fa-baby', 'Số trẻ sinh', current, previous, 'born')
    patient_card.append(card)

    # Số lượt khám theo từng phòng khám
    visited_in_department_id = query_visited.department_with_id(
        start, end, cursor)

    # Dữ liệu cho lượt khám bệnh chart
    visited_in_department = query_visited.departments(start, end, cursor)
    visited_in_department_chart = convert_to_chart(visited_in_department)
    visited_in_department_chart.insert(0, ["Phòng", 'Lượt khám'])

    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = []
    for i in range(diff):
        day = start + timedelta(days=i)
        if day <= datetime.now():
            query = query_hospitalized.total_department(day, cursor)
            if not i:
                patient_in_department = query
            else:
                for index, row in enumerate(query):
                    patient_in_department[index][1] += row[1]

    # Sắp xếp các khoa theo số lượng bệnh nhân nội trú
    department_patient_dict = {
        department[0]: department[1] for department in patient_in_department}
    department_patient_dict = dict(
        sorted(department_patient_dict.items(), key=lambda item: item[1], reverse=True))
    department_patient = convert_to_chart(department_patient_dict)
    patient_in_department_chart = department_patient.copy()
    patient_in_department_chart.insert(0, ["Khoa", 'Bệnh nhân'])

    # Chartsố lượt khám
    if diff < 30:
        start_day_chart = today - timedelta(days=30)
        end_day_chart = today
    else:
        start_day_chart = start
        end_day_chart = end
    
    last30days_visited = query_visited.day_betweenday(
        start_day_chart, end_day_chart, cursor)
    last30days_hospitalized = query_hospitalized.new_in_between(start_day_chart, end_day_chart, cursor)
    
    visited_hospitalized_chart = []
    for row in last30days_hospitalized:
        total_visited = query_visited.total_day(row[0], cursor)
        row_chart = [row[0].strftime("%d/%m/%Y"), total_visited, row[1]]
        visited_hospitalized_chart.append(row_chart)

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
        'visited_hospitalized_chart': visited_hospitalized_chart,
        'list_department': department_patient,
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
@manager_required
def revenue(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    phannhom_money = query_revenue.phannhom_money(start, end, cursor)
    previous_phannhom_money = query_revenue.phannhom_money(previous_start, previous_end, cursor)

    # Money card
    current = sum(int(row.TongDoanhThu) for row in phannhom_money)
    previous = sum(int(row.TongDoanhThu) for row in previous_phannhom_money)
    extra_info = query_revenue.tenphanhom_service_format(start, end, cursor)
    money_card = MoneyRevenueCard(
        'fa-solid fa-money-bill', 'Tổng doanh thu', current, previous, extra_info)

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

    confirm_card = ConfirmRevenueCard('fa-solid fa-clipboard-check', 'Hoàn tất thanh toán',
                                      confirmed_visited, confirmed_hospital, money_visited, money_hospital, bhtt, bntt)
    confirm_card_chart = [
        ['Loại', 'Doanh thu'],
        ['Ngoại trú', money_visited],
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
    for s, e in zip([start, previous_start], [end, previous_end]):
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

        card = BellowRevenueCard(
            icon, title, current, money_card.previous, money_visited, avg_money, avg_confirmed, s, e)

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
@login_required
def confirmed(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end
    diff = diff_days(start, end)

    all_confirmed = query_confirmed.list(start, end, cursor)

    table_column_title = ['Thời gian', 'Mã y tế', 'Số xác nhận',
                          'Loại', "Khoa/Phòng",'Doanh thu', 'Thanh toán', 'Nhân viên']

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
@login_required
def hospitalized(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
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
    card_top = TopHospitalCard(
        'fa-solid fa-hospital', 'Lượt nội trú', current, previous, new_in, old_out)

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
    for day in range(31):
        day_q = today - timedelta(days=day)
        count_patient = query_hospitalized.total(day_q, cursor)

        last_30_day_chart.append(
            [day_q.strftime("%A %d-%m-%Y"), count_patient])

    last_30_day_chart.reverse()

    # chart lượt nhập viện 30 ngày gần nhất
    last_30_days = today + timedelta(days=-30)
    new_in_chart = query_hospitalized.new_in_between(last_30_days, today, cursor)
    for row in new_in_chart:
        row.NgayVaoVien = row.NgayVaoVien.strftime("%A %d/%m/%Y")
    new_in_chart = convert_to_chart(new_in_chart)

    # Bệnh nhân vừa nhập viện
    recent_hospitalized_in_day = sql_query.recent_confirmed_review(
        today, cursor)
    last_patients = query_hospitalized.last5(today, cursor)
    last_patients = ([time_in_department.strftime("%H:%M %d/%m/%Y"), patient_name, department]
                     for time_in_department, patient_name, department in last_patients)

    bellow_card = []

    current = query_hospitalized.new_in(
        day_class.monday(), day_class.sunday(), cursor)
    previous = query_hospitalized.new_in(
        day_class.lastweek_monday(), day_class.monday(), cursor)
    card = BellowHospitalCard(current, previous, 'Tuần này', 'Tuần trước')
    bellow_card.append(card)

    current = query_hospitalized.new_in(
        day_class.first_day_month(), day_class.end_day_month(), cursor)
    previous = query_hospitalized.new_in(
        day_class.first_day_2month(), day_class.first_day_month(), cursor)
    card = BellowHospitalCard(current, previous, 'Tháng này', 'Tháng trước')
    bellow_card.append(card)

    current = query_hospitalized.new_in(
        day_class.first_day_year(), day_class.end_day_year(), cursor)
    previous = query_hospitalized.new_in(
        day_class.first_day_2year(), day_class.first_day_year(), cursor)
    card = BellowHospitalCard(current, previous, 'Năm này', 'Năm trước')
    bellow_card.append(card)

    # Tính công suất giường bệnh
    percent_bed = [
        ['Khoa Hồi sức cấp cứu', 0, 0, 54],
        ['Khoa Ngoại tổng hợp', 0, 0, 52],
        ['Khoa Nội tổng hơp', 0, 0, 52],
        ['Khoa Phụ Sản', 0, 0, 41],
        ['Khoa Y học cổ truyền', 0, 0, 48],
        ['Liên chuyên khoa TMH-RHM-Mắt', 0, 0, 25]
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

    current = sum(bed.current for bed in percent_bed_table)
    total = sum(bed.total for bed in percent_bed_table)
    bed = Bed('TTYT Anh Sơn', current, total)
    department_bed = percent_bed_table.copy()
    percent_bed_table.insert(0, bed)

    # PieChart số lượt nội trú mỗi khoa trong khoảng ngày
    department_patient_dict = {
        department.title: department.current for department in department_bed}
    department_patient_dict = dict(
        sorted(department_patient_dict.items(), key=lambda item: item[1], reverse=True))
    department_patient_chart = convert_to_chart(department_patient_dict)
    list_department = department_patient_chart.copy()
    department_patient_chart.insert(0, ['Khoa', 'Lượt nội trú'])

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
        'start': start,
        'end': end,
        'diff': diff,
        'patient_in_department': patient_in_department_id,
        'patient_in_department_today': patient_in_department_today,
        'patient_in_department_chart': patient_in_department_chart,
        'last_30_day_chart': last_30_day_chart,
        'recent_hospitalized_in_day': recent_hospitalized_in_day,
        'last_patients': last_patients,
        'chart_30_days': chart_30_days,


        'percent_bed_table': percent_bed_table,
        'card_top': card_top,
        'bellow_card': bellow_card,
        'department_patient_chart': department_patient_chart,
        'list_department': list_department,
        'new_in_chart': new_in_chart

    }

    close_db()
    return render_template('hospitalized/index.html', value=context, active="hospitalized")


# Danh sách bệnh nhân nội trú mới trong ngày
@app.route('/hospitalized/new-patients/<string:day_query>')
@app.route('/hospitalized/new-patients')
@register_breadcrumb(app, '..hospitalized.new-patients', 'Nhập viện mới')
@login_required
def new_patients(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start

    diff = diff_days(start, end)
    
    # card
    current = query_hospitalized.new_in(start, end, cursor )
    previous = query_hospitalized.new_in(previous_start, start, cursor )
    card = CardWithPercent('fa-solid fa-hospital', 'Lượt nhập viện', current, previous )

    # chart department
    department_chart = query_hospitalized.total_in_department(start, end, cursor)
    department_chart = convert_to_chart(department_chart)
    department_chart.insert(0, ['Khoa', 'Lượt nhập viện'])

    # chart lượt nhập viện 30 ngày gần nhất
    last_30_days = today + timedelta(days=-30)
    new_in_chart = query_hospitalized.new_in_between(last_30_days, today, cursor)
    for row in new_in_chart:
        row.NgayVaoVien = row.NgayVaoVien.strftime("%A %d/%m/%Y")
    new_in_chart = convert_to_chart(new_in_chart)

    table_column_title = ['Thời gian', 'Mã y tế', 'Số bệnh án',
                          'Tên bệnh nhân', 'Chẩn đoán', 'Khoa', 'Nhân viên']

    list_patients = query_hospitalized.new_list(start, end, cursor)

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'list': list_patients,
        'table_column_title': table_column_title,
        'card': card,
        'department_chart': department_chart,
        'new_in_chart': new_in_chart
      

    }
    close_db()
    return render_template('hospitalized/new-patients.html', value=context)

# Danh sách bệnh nhân nội trú ra viện trong ngày


@app.route('/hospitalized/out-patients/<string:day_query>')
@app.route('/hospitalized/out-patients')
@register_breadcrumb(app, '..hospitalized.out-patients', 'Ra viện')
@login_required
def out_patients(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)


    table_column_title = ['Thời gian', 'Mã y tế',  'Số bệnh án',
                          'Chẩn đoán ra viện', 'Lí do', 'Bác sĩ', 'Khoa']

    list_patients = query_hospitalized.out_list(start, end, cursor)


    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,


    }
    close_db()
    return render_template('hospitalized/out-patients.html', value=context)

# Danh sách bệnh nhân chuyển viện trong ngày


@app.route('/transfer/<string:day_query>')
@app.route('/transfer')
@register_breadcrumb(app, '..transfer', 'Chuyển viện')
@login_required
def transfer(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

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
    close_db()
    return render_template('hospitalized/transfer.html', value=context)


# Danh sách bệnh nhân nội trú
@app.route('/hospitalized/patients/<string:day_query>')
@app.route('/hospitalized/patients')
@register_breadcrumb(app, '..hospitalized.patients', 'Bệnh nhân')
@login_required
def patients(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start

    diff = diff_days(start, end)

    table_column_title = ['Thời gian vào khoa', 'Mã y tế',  'Số bệnh án',
                          'Tên bệnh nhân', 'Chẩn đoán trong khoa', 'Bác sĩ', 'Khoa']

    list_patients = query_hospitalized.patients(today, cursor)

    chart = query_hospitalized.total_department_sort_total(today, cursor)
    chart = list([i, j] for i, j in chart)

    chart.insert(0, ['Khoa', 'Số bệnh nhân'])

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'list': list_patients,
        'table_column_title': table_column_title,
        'chart': chart


    }
    close_db()
    return render_template('hospitalized/patients.html', value=context)


# Trang bệnh nhân ngoại trú
@app.route('/visited/<string:day_query>')
@app.route('/visited')
@register_breadcrumb(app, '.visited', 'Khám bệnh')
@login_required
def visited(day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start

    diff = diff_days(start, end)

    # card top
    current = query_visited.total(start, end, cursor)
    previous = query_visited.total(previous_start, start, cursor)
    new_hospital = query_visited.in_hospital(start, end, cursor)
    transfer_visited = query_visited.transfer(start, end, cursor)
    card_top = TopHospitalCard('fa-solid fa-hospital-user', 'Lượt khám bệnh', current, previous, new_hospital, transfer_visited)

    # card bellow
    bellow_card = []

    current = query_visited.total(
        day_class.monday(), day_class.sunday(), cursor)
    previous = query_visited.total(
        day_class.lastweek_monday(), day_class.monday(), cursor)
    card = BellowHospitalCard(current, previous, 'Tuần này', 'Tuần trước')
    bellow_card.append(card)

    current = query_visited.total(
        day_class.first_day_month(), day_class.end_day_month(), cursor)
    previous = query_visited.total(
        day_class.first_day_2month(), day_class.first_day_month(), cursor)
    card = BellowHospitalCard(current, previous, 'Tháng này', 'Tháng trước')
    bellow_card.append(card)

    current = query_visited.total(
        day_class.first_day_year(), day_class.end_day_year(), cursor)
    previous = query_visited.total(
        day_class.first_day_2year(), day_class.first_day_year(), cursor)
    card = BellowHospitalCard(current, previous, 'Năm này', 'Năm trước')
    bellow_card.append(card)

    # Thống kê Số bệnh nhân ngoại trú từng phòng
    list_count = query_visited.departments(start, end, cursor)
    list_count_chart = convert_to_chart(list_count)
    list_count_chart.insert(0, ["Phòng khám", 'Lượt khám'])

    # Số lượt khám theo tên bác sĩ
    doctors = query_visited.doctors(start, end, cursor)

    # Lượt khám theo phòng khám
    visited_in_department_id = query_visited.department_with_id(
        start, end, cursor)
    
    # 5 lượt khám bệnh gần nhất trong khoảng thời gian
    last_5 = query_visited.last5(start, end, cursor)

    # thống kê thời gian khám
    time_overview = query_visited.time_overview(start, end, cursor)
    # Chartsố lượt khám
    if diff < 30:
        start_day_chart = today - timedelta(days=30)
        end_day_chart = today
    else:
        start_day_chart = start
        end_day_chart = end
    
    last30days_visited = query_visited.day_betweenday(
        start_day_chart, end_day_chart, cursor)
    for row in last30days_visited:
        row.NgayKham = row.NgayKham.strftime('%d/%m/%Y')
    last30days_visited = convert_to_chart(last30days_visited)
    last30days_visited.reverse()
    

    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'card_top': card_top,
        'bellow_card': bellow_card,
        'pie_chart_1': list_count_chart,
        'doctors': doctors,
        'visited_in_department': visited_in_department_id,
        'last_5': last_5,
        'last30days_visited': last30days_visited,
        'time_overview': time_overview
    }

    close_db()
    return render_template('visited/index.html', value=context, active='visited')


# Danh sách bệnh nhân ngoại trú trong ngày
@app.route('/visited/patients/<string:day_query>')
@app.route('/visited/patients')
@register_breadcrumb(app, '..visited.patients', 'Bệnh nhân')
@login_required
def visited_patients(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)


    table_column_title = ['Thời gian khám', 'Mã y tế', 'Tên bệnh nhân',
                          'Số tiếp nhận', 'Chẩn đoán trong khoa', 'Giải quyết', 'Bác sĩ', 'Khoa']

    list_patients = query_visited.patients(start, end, cursor)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'list': list_patients,
        'table_column_title': table_column_title,
    }
    close_db()
    return render_template('visited/patients.html', value=context)




# Thời gian khám ngoại trú
@app.route('/visited/time-overview/<string:day_query>')
@app.route('/visited/time-overview')
@register_breadcrumb(app, '..visited.time_overview', 'Thời gian khám')
@login_required
def time_overview(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    time_overview = query_visited.time_overview(start, end, cursor)
    time_departments = query_visited.time_departments(start, end, cursor)
    time_service = query_visited.time_service(start, end, cursor)



    table_column_title = ['Bệnh nhân', 'Dịch vụ', 'Thời gian tiếp nhận',
                          'Thời gian yêu cầu', 'Thời gian thực hiện', 'Thời gian có kết quả', 'Thời gian hoàn tất khám bệnh', 'Thời gian xác nhận thanh toán', 'Thời gian chờ khám', 'Thời gian chờ thực hiện yêu cầu', 'Thời gian chờ có kết quả', 'Thời gian chờ hoàn tất khám bệnh', 'Thời gian chờ xác nhận thanh toán', 'Tổng thời gian']

    list_patients = query_visited.time_patients(start, end, cursor)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'list': list_patients,
        'table_column_title': table_column_title,
        'time_overview': time_overview,
        'time_departments': time_departments,
        'time_service': time_service
    }
    close_db()
    return render_template('visited/time-overview.html', value=context, not_patient_btn = True)


# Trang phẫu thuật thủ thuật
@app.route('/surgery/<string:day_query>')
@app.route('/surgery')
@register_breadcrumb(app, '..surgery', 'Phẫu thuật, thủ thuật')
@login_required
def surgery(day_query=None):
    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

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
    close_db()
    return render_template('surgery/index.html', value=context)


# Trang phẫu thuật thủ thuật
@app.route('/surgery/list/<string:day_query>')
@app.route('/surgery/list')
@register_breadcrumb(app, '..surgery.list', 'Danh sách')
@login_required
def surgery_list(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Thời gian kết thúc', 'Mã y tế',
                          'Tên bệnh nhân', 'Can thiệp', 'Loại', 'Nơi thực hiện']

    list_patients = query_surgery.list(start, end, cursor)


    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title
    }
    close_db()
    return render_template('surgery/list.html', value=context)


# Số trẻ sinh
@app.route('/born/<string:day_query>')
@app.route('/born')
@register_breadcrumb(app, '..surgery.born', 'Trẻ sinh')
@login_required
def born(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Thời gian kết thúc', 'Mã Y tế',
                          'Tên bệnh nhân', 'Can thiệp phẫu thuật', 'Mô tả sau phẫu thuật']

    list_patients = query_born.list_between(start, end, cursor)
   
    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title
    }
    close_db()
    return render_template('born/index.html', value=context)


# Doanh thu theo tên dịch vụ
@app.route('/revenue/list/<string:day_query>')
@app.route('/revenue/list')
@register_breadcrumb(app, '..revenue.list', 'Danh sách')
@login_required
def list_revenue(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Nội dung', 'Tên',
                          'Khoa/Phòng', 'Người chỉ định','Đơn giá', 'Số lượt', 'Tổng doanh thu']

    list_patients = query_revenue.services(start,end, cursor)

    

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'list': list_patients,
        'table_column_title': table_column_title,
    }
    close_db()
    return render_template('revenue/list.html', value=context, active='revenue', order_column=5, not_patient_btn = True)


# Doanh thu theo dược
@app.route('/revenue/medicine/<string:day_query>')
@app.route('/revenue/medicine/')
@register_breadcrumb(app, '..revenue.medicine', 'Dược')
@login_required
def medicine(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Nội dung',
                          'Khoa/Phòng', 'Đơn giá','Số lượt', 'Tổng doanh thu']

    list_medicine = query_revenue.list_medicine(start, end, cursor)

    departments_chart = query_revenue.departments_chart(start, end, cursor)
    departments_chart = convert_to_chart(departments_chart)
    departments_chart.insert(0, ['Khoa/Phòng', 'Doanh thu'])

    # medicine card
    current = query_revenue.service_money(start, end, 'DU', cursor)
    previous = query_revenue.service_money(previous_start, previous_end, 'DU', cursor)
    card = CardWithPercent('fa-solid fa-pills', 'Doanh thu dược', current, previous)


    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'card': card,
        'list': list_medicine,
        'table_column_title': table_column_title,
        'departments_chart': departments_chart
    }
    close_db()
    return render_template('revenue/medicine.html', value=context, active='revenue', order_column=3, not_patient_btn=True)


# Doanh thu theo dịch vụ
@app.route('/revenue/service/<string:day_query>')
@app.route('/revenue/service/')
@register_breadcrumb(app, '..revenue.service', 'Dịch vụ')
@login_required
def service(day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Nội dung',
                          'Khoa/Phòng', 'Đơn giá','Số lượt', 'Tổng doanh thu']

    list_medicine = query_revenue.list_service(start, end, cursor)

    departments_chart = query_revenue.departments_chart(start, end, cursor)
    departments_chart = convert_to_chart(departments_chart)
    departments_chart.insert(0, ['Khoa/Phòng', 'Doanh thu'])

    # medicine card
    current = query_revenue.service_money(start, end, 'DV', cursor)
    previous = query_revenue.service_money(previous_start, previous_end, 'DV', cursor)
    card = CardWithPercent('fa-solid fa-stethoscope', 'Doanh thu dịch vụ', current, previous)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'card': card,
        'list': list_medicine,
        'table_column_title': table_column_title,
        'departments_chart': departments_chart
    }
    close_db()
    return render_template('revenue/service.html', value=context, active='revenue', order_column=3, not_patient_btn=True)


# Doanh thu theo khoa phòng
@app.route('/revenue/department/<string:department_name>/<string:day_query>')
@app.route('/revenue/service/<string:department_name>')
@register_breadcrumb(app, '..revenue.department', 'Khoa/Phòng')
@login_required
def revenue_department(department_name,day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Nội dung', 'Đơn giá','Số lượt', 'Tổng doanh thu']

    list_medicine = query_revenue.list_department(start, end,department_name, cursor)


    # card
    current = query_revenue.total_department(start, end, department_name, cursor)
    previous = query_revenue.total_department(previous_start, previous_end, department_name, cursor)
    card = CardWithPercent('fa-solid fa-stethoscope', department_name, current, previous)


    total = query_revenue.total_money_betweentime(start, end, cursor)
    departments_chart = [['Khoa', 'Doanh thu'], [department_name,current], ['Các khoa còn lại', total-current]]

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'card': card,
        'list': list_medicine,
        'table_column_title': table_column_title,
        'departments_chart': departments_chart,
        'department_name': department_name
    }
    close_db()
    return render_template('revenue/department.html', value=context, active='revenue', order_column=3, not_patient_btn=True)



# Trang bệnh nhân khám bệnh theo từng khoa
@app.route('/visited/<int:department_id>/<string:day_query>')
@app.route('/visited/<int:department_id>')
@register_breadcrumb(app, '..visited.department', 'Danh sách')
@login_required
def visited_department(department_id, day_query=None):

    department_id_list = get_department_id_list(department_id)
    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Thời gian', 'Mã Y tế',
                          'Tên bệnh nhân', 'Chẩn đoán', 'Giải quyết', 'Bác sĩ']

    list_patients = []

    for d_id in department_id_list:
        list_patients.extend(
            query_visited.list_department(start, end, d_id, cursor))

    if department_id > 9999:
        doctors_count_khambenh = query_visited.doctors_department_merge(start, end, department_id, cursor)

    else:
        doctors_count_khambenh = query_visited.doctors_department(start, end, department_id, cursor)

    doctors_count_khambenh_chart = convert_to_chart(doctors_count_khambenh)
    doctors_count_khambenh_chart.insert(0, ['Bác sĩ', 'Lượt khám'])

    department_name = ''
    for d_id in department_id_list:
        department_name += (query_visited.name_department(d_id,
                            cursor)) + ' - '
    startday = today + timedelta(days=-30)
    visited_department_chart = query_visited.department_id_between(
        startday, today, department_id, cursor)
    visited_department_chart = convert_to_chart(visited_department_chart)
    total = len(list_patients)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'department_id': department_id,
        'department_name': department_name,
        'visited_department_chart': visited_department_chart,
        'doctors_count_khambenh_chart': doctors_count_khambenh_chart,
        'total': total
    }
    close_db()
    return render_template('visited/department.html', value=context, active='visited', order_column=0)


# Trang bệnh nhân nội trú theo từng khoa
@app.route('/hospitalized/department/<string:department_name>/<string:day_query>')
@app.route('/hospitalized/department/<string:department_name>')
@register_breadcrumb(app, '..hospitalized.department', 'Danh sách')
@login_required
def hospitalized_department(department_name, day_query=None):
 
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    table_column_title = ['Thời gian', 'Mã Y tế',
                          'Tên bệnh nhân','Mã giường', 'Chẩn đoán', 'Bác sĩ']

    list_patients = query_hospitalized.patiens_department(
        today, department_name, cursor)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'department_name': department_name,
    }
    cnxn.close()
    return render_template('hospitalized/department.html', value=context, active='hospitalized', order_column=0)


# Trang bệnh nhân nội trú nhập mới theo từng khoa
@app.route('/hospitalized/new/<string:department_name>/<string:day_query>')
@app.route('/hospitalized/new/<string:department_name>')
@register_breadcrumb(app, '..hospitalized.department_new', 'Nhập mới')
@login_required
def hospitalized_department_new(department_name, day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today

    table_column_title = ['Thời gian', 'Mã Y tế',
                          'Tên bệnh nhân', 'Chẩn đoán', 'Bác sĩ']

    list_patients = query_hospitalized.patiens_department_new(
        today, department_name, cursor)

    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'department_name': department_name,
    }
    cnxn.close()
    return render_template('hospitalized/department.html', value=context, active='hospitalized', order_column=0, title="Nhập mới")


# Trang danh sách bệnh nhân
@app.route('/patients/')
@register_breadcrumb(app, '..patients', 'Bệnh nhân')
@login_required
def all_patients():

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()
    
    con = sqlite3.connect("medical_record_pinned.db")
    cursor_sqlite = con.cursor()
    cursor_sqlite.row_factory = sqlite3.Row

    pinneds = cursor_sqlite.execute("""SELECT * FROM pinned""").fetchall()


    # lấy ngày xem dashboard

    search_input = request.args.get('search')
    rows = None
    if search_input:
        q = f"""
            SELECT TOP 1000
            benhnhan.NgayTao, MaYTe, TenBenhNhan,NgaySinh, SoDienThoai, DiaChi
            FROM [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
            WHERE MaYTe LIKE '%{search_input}%'
            OR TenBenhNhan LIKE N'%{search_input}%'

            ORDER BY benhnhan.NgayCapNhat DESC 
        """
        list_patients = cursor.execute(q).fetchall()
    else:

        list_patients = query_patient.patients(cursor)
    table_column_title = ['Ngày tạo', 'Mã Y tế',
                          'Tên bệnh nhân', 'Ngày sinh', 'Số điện thoại', 'Địa chỉ']
    
    today = datetime.today().strftime('%Y-%m-%d')


    context = {
        'today': today,
        'list': list_patients,
        'table_column_title': table_column_title,
        'search_input': search_input,
        'pinneds': pinneds
    }

    con.close()

    close_db()
    return render_template('patient/index.html', value=context, active='patient')


# Trang chi tiết bệnh nhân
@app.route('/patient/<string:mayte>')
@register_breadcrumb(app, '..patients.detail', 'Chi tiết')
@login_required
def patient_detail(mayte):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    detail = query_patient.detail(mayte, cursor)

    history_visited = query_patient.visited_history(mayte, cursor)
    history_hospital = query_patient.hospitalized_history(mayte, cursor)
    history_hospital_list = []

    for row in history_hospital:
        extrainfo_khambenh_list = []
        khambenhs = query_patient.khambenh_noitru(row.BenhAn_Id, cursor)
        cls = query_patient.cls_noitru(row.BenhAn_Id, cursor)
        xetnghiems = query_patient.xetnghiem_id(row.BenhAn_Id, cursor)
        for khambenh in khambenhs:
            khambenh_noitru_toathuoc = query_patient.khambenh_noitru_toathuoc(khambenh.KhamBenh_Id, cursor)
            extrainfo_khambenh = HospitalizedPatientKhamBenh(khambenh,khambenh_noitru_toathuoc)
            extrainfo_khambenh_list.append(extrainfo_khambenh)
        xn = []
        for xetnghiem in xetnghiems:
            ketqua_xetnghiem = query_patient.ketqua_xetnghiem(xetnghiem.id, cursor)
            xn.append(ketqua_xetnghiem)
        
        info = HospitalizedPatient(row,extrainfo_khambenh_list, cls, xn)
        history_hospital_list.append(info)

    doanhthu = query_patient.doanhthu(mayte, cursor)
    thanhtoan = query_patient.thanhtoan(mayte, cursor)

    today = datetime.today().strftime('%Y-%m-%d')

    context = {
        'today': today,
        'mayte': mayte,
        'detail': detail,
        'history_visited': history_visited,
        'doanhthu': doanhthu,
        'thanhtoan': thanhtoan,
        'history_hospital_list': history_hospital_list
    }
    close_db()
    return render_template('patient/detail.html', value=context, active='patient')


#Trang lịch sử nội trú điều trị
@app.route('/medical-record/<string:sobenhan>',methods=['GET', 'POST'])
@register_breadcrumb(app, '..medical_record', 'Chi tiết bệnh án')
@login_required
def patient_hospitalized(sobenhan):
    cnxn = get_db()
    cursor = cnxn.cursor()

    con = sqlite3.connect("medical_record_pinned.db")
    cursor_sqlite = con.cursor()
    cursor_sqlite.row_factory = sqlite3.Row
    medical_record = MedicalRecord(sobenhan, cursor)
    
    if request.method == "POST" and 'pinned' in request.form:
        benhan_id_input = request.form['benhan_id']
        tenbenhnhan = request.form['tenbenhnhan']
        is_pinned_form = request.form['pinned']
        if is_pinned_form == "False":
            time_created = datetime.now()
            sql = """
            INSERT INTO pinned(sobenhan, time_created, note)
            VALUES(?,?,?)
            """
            cursor_sqlite.execute(sql, (benhan_id_input, time_created, tenbenhnhan))
        else:
            sql = """
            DELETE FROM pinned
            WHERE sobenhan = ?
            """
            cursor_sqlite.execute(sql, (benhan_id_input,))
        con.commit()

    sql = """SELECT id FROM pinned WHERE sobenhan = ?"""
    q = cursor_sqlite.execute(sql, (medical_record.info.SoBenhAn,)).fetchone()
    
    if q:
        is_pinned = True
    else:
        is_pinned = False
    

    today = datetime.today().strftime('%Y-%m-%d')
    value = {
        'today': today,
        'medical_record': medical_record,
        'is_pinned': is_pinned
    }
    con.close()
    return render_template('patient/hospitalized.html', value=value)

# Trang danh sách báo cáo
@app.route('/report/<string:day_query>')
@app.route('/report')
@register_breadcrumb(app, '..report', 'Báo cáo')
@manager_required
def report(day_query=None):

    cnxn = get_db()
    cursor = cnxn.cursor()
    card = []
    card1 = ['Doanh thu theo từng mục', 'Mẫu báo cáo 79 của BHYT',
             'Chi tiết doanh thu từng mục: Tiền CĐHA, Tiền Xét nghiệm, Tiền Thuốc, Tiền Phẫu thuật, Tiền Khám, Tiền Giường', 'report_79']

    card.append(card1)

    today = datetime.today().strftime('%Y-%m-%d')

    context = {
        'today': today,
        'card': card

    }
    close_db()
    return render_template('report/index.html', value=context, active='report')

# Báo cáo 79


@app.route('/report/79/<string:day_query>', methods=['GET', 'POST'])
@app.route('/report/79', methods=['GET', 'POST'])
@register_breadcrumb(app, '..report.report-79', 'Chi tiết doanh thu xác nhận')
@manager_required
def report_79(day_query=None):
    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

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
        day_class.first_day_year(), today, cursor)
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
        user = request.form['username'].lower()
        pwd = request.form['password']

        login_user = query_user.login_user(user, pwd, cursor)
        if login_user:
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        else:
            flash('Đăng nhập thất bại')
    today = datetime.today().strftime('%Y-%m-%d')
    context = {
        'today': today
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
@login_required
def admin():
    
    con = get_db_dashboard()
    cursor = con.cursor()
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

        today = datetime.today().strftime('%Y-%m-%d')

        context = {
            'today': today,
            'list_post': list_post
        }
        close_db_dashboard()

        return render_template('admin/index.html', value=context)
    else:
        return redirect(url_for('user_login'))


# Trang tin tức
@app.route('/news')
@register_breadcrumb(app, '..news', 'Thông tin công việc')
def news():
    con = get_db_dashboard()
    cursor = con.cursor()
    list_post = query_user.posts(cursor)

    today = datetime.today().strftime('%Y-%m-%d')
    context = {
        'posts': list_post,
        'today': today
    }
    close_db_dashboard()
    return render_template('news/index.html', value=context, active='news', order_column=4)


# chi tiết bài viết
@app.route('/news/post/<int:post_id>')
@register_breadcrumb(app, '..news.post', 'Bài viết')
def detail_post(post_id):
    con = get_db_dashboard()
    cursor = con.cursor()

    today = datetime.today().strftime('%Y-%m-%d')


    post = query_user.post(post_id, cursor)

    context = {
        'post': post,
        'today': today
    }
    close_db_dashboard()

    return render_template('news/post.html', value=context, active='news', hidden_top_filter=True)

# trang thu tiền dịch vụ
@app.route('/admin/money', methods=['GET', 'POST'])
@register_breadcrumb(app, '..admin.money', 'Tiền dịch vụ')
@manager_required
def admin_money():

    if session.get('username'):
        con = sqlite3.connect("dashboard.db")
        cursor = con.cursor()
        cursor.row_factory = sqlite3.Row


        sql_list_report = """
        SELECT *
        FROM report_money
        ORDER BY id DESC
        """
        list_reports = cursor.execute(sql_list_report).fetchall()
        titles = cursor.execute(sql_list_report).description

        list_form_title_money = [["Tiền khám bệnh"],["Viện phí"],["Xét nghiệm"],["Điện tim"],["Test nhanh covid 19"],["Lưu huyết não"],["Siêu âm"],["XQ"],["Nội soi dạ dày, thực quản"],["Nội soi TMH"],["Nội soi CTC"],["Khám sức khỏe"],["Bó bột gây mê"],["Chụp CT"],["Tiêm SAT"],["Tiêm phòng dại"],["Tiêm VGB 1ml"],["Tiêm VGB 0.5ml"],["Vắc xin Rotamin"],["Xông hơi thuốc bắc"],["Vắc xin Cúm"],["Vắc xin Quimihib"],["Thuốc"],["HIV"],["HBsAg"],["Sao bệnh án"],["Test HP"]]
        j = []
        for i in list_form_title_money:
            i.append(slugify(i[0]).replace('-', '_'))
        
        place_holders = (len(list_form_title_money) + 3) * '?,'
        place_holders = place_holders + '?'
        if request.method == 'POST' and 'new_report' in request.form:

            values = []
            values.append(datetime.now())
            values.append(session['username'])

            for i in (request.form):
                values.append(request.form[i])

            values.pop(-1)

            total = 0
            for index, number in enumerate(values):
                if index >= 3:
                    total += int(number)
                

            values.append(total)

            sql = f"""
            INSERT INTO report_money(time_created,username,time_report,tien_kham_benh,vien_phi,xet_nghiem,dien_tim,test_nhanh_covid_19,luu_huyet_nao,sieu_am,xq,noi_soi_da_day_thuc_quan,noi_soi_tmh,noi_soi_ctc,kham_suc_khoe,bo_bot_gay_me,chup_ct,tiem_sat,tiem_phong_dai,tiem_vgb_1ml,tiem_vgb_0_5ml,vac_xin_rotamin,xong_hoi_thuoc_bac,vac_xin_cum,vac_xin_quimihib,thuoc,hiv,hbsag,sao_benh_an,test_hp, total)
            VALUES ({place_holders})
            """
            try:
                cursor.execute(sql, values)
                con.commit()
            except:
                con.close()
            return redirect(url_for('admin_money'))

        if request.method == 'POST' and 'delete_report' in request.form:
            sql = "DELETE FROM report_money WHERE id=?"
            report_id = int(request.form['report_id'])
  
            cursor.execute(sql, (report_id,))
            con.commit()

            return redirect(url_for('admin_money'))

        today = datetime.today().strftime('%Y-%m-%d')

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
    


# trang báo cáo thu tiền dịch vụ
@app.route('/report/service-money/<string:day_query>')
@register_breadcrumb(app, '..report.service_money', 'Tiền dịch vụ')
@manager_required
def report_service_money(day_query=None):
    con = get_db_dashboard()
    cursor = con.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    sql_list_report = """
    SELECT *
    FROM report_money
    ORDER BY id DESC
    """
    list_reports = cursor.execute(sql_list_report).fetchall()
    titles = cursor.execute(sql_list_report).description

    list_form_title_money = [["Tiền khám bệnh"],["Viện phí"],["Xét nghiệm"],["Điện tim"],["Test nhanh covid 19"],["Lưu huyết não"],["Siêu âm"],["XQ"],["Nội soi dạ dày, thực quản"],["Nội soi TMH"],["Nội soi CTC"],["Khám sức khỏe"],["Bó bột gây mê"],["Chụp CT"],["Tiêm SAT"],["Tiêm phòng dại"],["Tiêm VGB 1ml"],["Tiêm VGB 0.5ml"],["Vắc xin Rotamin"],["Xông hơi thuốc bắc"],["Vắc xin Cúm"],["Vắc xin Quimihib"],["Thuốc"],["HIV"],["HBsAg"],["Sao bệnh án"],["Test HP"]]
    for i in list_form_title_money:
        i.append(slugify(i[0]).replace('-', '_'))
    list_dict = dict(list_form_title_money)

    close_db_dashboard()
    today = datetime.today().strftime('%Y-%m-%d')
    context = {
        'list_reports': list_reports,
         'titles': titles,
         'list_dict': list_dict,
         'today': today

    }

    return render_template('report/report-service-money.html', value=context)

# chi tiết bài viết
@app.route('/admin/medical-record-tracking', methods=['GET', 'POST'])
@register_breadcrumb(app, '..admin.medical_record', 'Theo dõi bệnh án')
@login_required
def medical_record():
    if session.get('username'):
        # kết nối database sql server
        cnxn = get_db()
        cursor_sqlserver = cnxn.cursor()
    
        con = sqlite3.connect("medical_record.db")
        cursor = con.cursor()
        active_archived=1


        # Nạp bệnh án
        if request.method == 'POST' and 'insert' in request.form:
            if request.form['soluutru']:
                str_soluutru = request.form['soluutru']
                list_soluutru = str_soluutru.split(";")
                for soluutru in list_soluutru:
                    if soluutru:
                        patient_info = query_hospitalized.medical_record_info(soluutru,cursor_sqlserver)
                        time_created = datetime.now()
                        tenbenhnhan = patient_info.TenBenhNhan
                        department_name = patient_info.TenPhongBan
                        sobenhan = patient_info.SoBenhAn
                        ngayravien = patient_info.NgayRaVien
                        is_giveback= False
                        sql = """
                        INSERT INTO archived(time_created, soluutru, sobenhan,benhnhan,khoa,ngayravien,is_giveback)
                        VALUES(?,?,?,?,?,?,?)
                        """
                        cursor.execute(sql, (time_created, soluutru, sobenhan, tenbenhnhan,department_name,ngayravien,is_giveback ))
                        con.commit()
                flash('Nạp bệnh án thành công')
                active_archived = 1
                
        # Xóa bệnh án đã nạp
        if request.method == 'POST' and 'delete' in request.form:
            if request.form['soluutru_delete']:
                soluutru = request.form['soluutru_delete']
  
                sql = """
                DELETE FROM archived
                WHERE soluutru = ?
                """
                cursor.execute(sql, (soluutru,))
                con.commit()  
                active_archived=2
                flash('Thu hồi bệnh án đã nạp thành công')

        # trả bệnh án đã nạp
        if request.method == 'POST' and 'update' in request.form:
            if request.form['soluutru_update']:
                note = request.form['note']
                soluutru = request.form['soluutru_update']
  
                sql = """
                UPDATE archived
                SET is_giveback = True, note = ?
                WHERE soluutru = ?
                """
                cursor.execute(sql, (note, soluutru))
                con.commit() 
                active_archived=2
                flash('Trả bệnh án thành công')
        
        # nạp bệnh án đã trả
        if request.method == 'POST' and 'update_giveback' in request.form:
            if request.form['soluutru3']:
                str_soluutru = request.form['soluutru3']
                list_soluutru = str_soluutru.split(";")
                for soluutru in list_soluutru:
                    if soluutru:
                        print(soluutru)
                        sql = """
                        UPDATE archived
                        SET is_giveback = False
                        WHERE soluutru = ?
                        """
                        cursor.execute(sql, (soluutru,))
                        con.commit()
                active_archived=3
                flash('Nạp lại bệnh án thành công')


        today = datetime.today()
        first_month = today.replace(day=1)
        start_day = request.args.get('start_day')
        end_day = request.args.get('end_day')
        is_start_day = True
        
        if not start_day:
            is_start_day = False
            start_day = first_month.strftime('%Y-%m-%d')
            end_day = today.strftime('%Y-%m-%d')
        
        start_day_sqlite = datetime.strptime(start_day,'%Y-%m-%d')
        end_day_sqlite = datetime.strptime(end_day,'%Y-%m-%d')
        archived_list = query_hospitalized.medical_record_archived_all(start_day, end_day_sqlite,cursor)
        archived_list_nogiveback = query_hospitalized.medical_record_archived_no_giveback(start_day, end_day_sqlite,cursor)
        archived_list_giveback = query_hospitalized.medical_record_archived_giveback(start_day, end_day_sqlite,cursor)
        
        if archived_list:
            # Lấy danh sách số lưu trữ
            soluutru_archived_list = tuple(i[2] for i in archived_list )
            medical_records_not_archived = query_hospitalized.medical_records_not_archived(start_day, end_day,soluutru_archived_list, cursor_sqlserver)
            list_no_archived = medical_records_not_archived
        else:
            # Nếu archived table trống
            medical_records_not_archived = query_hospitalized.medical_records(start_day, end_day, cursor_sqlserver)
            list_no_archived = medical_records_not_archived

        table_column_title1 = ['Thời gian ra viện', 'Số bệnh an','Số lưu trữ','Tên bệnh nhân','Khoa']
        table_column_title2 = ['Ngày ra viện','Số bệnh án','Số lưu trữ','Tên bệnh nhân', 'Khoa', 'Thời gian nạp', 'Thao tác']
        table_column_title3 = ['Ngày ra viện','Số bệnh án','Số lưu trữ','Tên bệnh nhân', 'Khoa',  'Ghi chú']
        


        list_count_medical_record = query_hospitalized.medical_record_between(start_day, end_day, cursor_sqlserver)
        analytics = []
        for department in list_count_medical_record:
            khoa = department.TenPhongBan
            archived = query_hospitalized.archived_department(start_day_sqlite, end_day_sqlite, khoa, cursor)
            giveback = query_hospitalized.archived_department_giveback(start_day_sqlite, end_day_sqlite, khoa, cursor)
         
            d = DepartmentRecord(khoa, department.total, archived, giveback)
            analytics.append(d)
 
        today = today.strftime('%Y-%m-%d')
        context = {
            'today': today,
            'start_day': start_day,
            'end_day': end_day,
            'table_column_title1': table_column_title1,
            'table_column_title2': table_column_title2,
            'table_column_title3': table_column_title3,
            'list_no_archived': list_no_archived,
            'list_archived': archived_list,
            'list_archived_nogiveback' :archived_list_nogiveback,
            'is_start_day': is_start_day,
            'active_archived': active_archived,
            'archived_list_giveback': archived_list_giveback,
            'analytics': analytics
        }
        close_db()
        con.close()

        return render_template('admin/medical-report.html', value=context,  hidden_top_filter=True)
    
    else:
        return redirect(url_for('user_login'))
    
# Trang danh bạ
@app.route('/addressbook')
@register_breadcrumb(app, '..addressbook', 'Danh bạ nhân viên')
@login_required
def addressbook():

    con = get_db_dashboard()
    cursor = con.cursor()

    address_book = query_user.users(cursor)
    today = datetime.today().strftime('%Y-%m-%d')
    context = {
        'address_book': address_book,
        'today': today
    }
    close_db_dashboard()
    return render_template('user/addressbook.html', value=context, active='addressbook')

# Trang lịch trực
@app.route('/schedule')
@register_breadcrumb(app, '..schedule', 'Lịch trực')
def schedule():

    table_column_title = ['Lãnh đạo', 'Hội chẩn', 'Ngoại, Sản, 3CK', 'HSCC,Nội, YHCT', 'Khám bệnh', 'CLS', 'Dược', 'Hành chính', 'Thường trú', 'Hộ tống']

    context = {
        'table_column_title': table_column_title
    }
    return render_template('admin/schedule.html', value=context, active='schedule')

# Trang lịch trực
@app.route('/search')
@register_breadcrumb(app, '..patients.search', 'Tìm kiếm bệnh nhân')
def search():

    table_column_title = ['Lãnh đạo', 'Hội chẩn', 'Ngoại, Sản, 3CK', 'HSCC,Nội, YHCT', 'Khám bệnh', 'CLS', 'Dược', 'Hành chính', 'Thường trú', 'Hộ tống']

    context = {
        'table_column_title': table_column_title
    }
    return render_template('patient/search.html', value=context, active='schedule')

# Trang doanh thu theo chỉ định
@app.route('/revenue/medical-indication/<string:day_query>')
@app.route('/revenue/medical-indication')
@register_breadcrumb(app, '..revenue.medical-indication', 'Thống kê chỉ định')
@manager_required
def revenue_medical_indication(day_query=None):

    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)

    top_department = query_revenue.department_clsyeucau(start,end, cursor)
    top_doctor = query_revenue.doctor_clsyeucau(start,end, cursor)
    top_noithuchien = query_revenue.thuchien_clsyeucau(start,end, cursor)
    top_nhomdichvu = query_revenue.nhomdichvu_clsyeucau(start,end, cursor)
    top_department_nhomdichvu_clsyeucau = query_revenue.department_nhomdichvu_clsyeucau(start,end, cursor)
    nhomdichvu_clsyeucau = query_revenue.nhomdichvu_doanhthu(start,end, cursor)
    nhomdichvu_chart_column = convert_to_chart(nhomdichvu_clsyeucau)
    nhomdichvu_chart = convert_to_chart(nhomdichvu_clsyeucau)
    nhomdichvu_chart.insert(0, ['Nội dung', 'Doanh thu'])

    table_column_title = ['Người chỉ định', 'Tên nhóm DV', 'Số lượt', 'Doanh thu']
    list_data = query_revenue.doctor_department(start, end, cursor)
    today = today.strftime("%Y-%m-%d")

    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'table_column_title': table_column_title,
        'list': list_data,
        'top_department': top_department,
        'top_doctor': top_doctor,
        'top_noithuchien': top_noithuchien,
        'top_nhomdichvu': top_nhomdichvu,
        'top_department_nhomdichvu_clsyeucau': top_department_nhomdichvu_clsyeucau,
        'nhomdichvu_chart': nhomdichvu_chart,
        'nhomdichvu_chart_column': nhomdichvu_chart_column
    }
    close_db()

    return render_template('revenue/medical-indication.html', value=context, active='revenue', not_patient_btn=True,order_column=3)


# trang sửa thời gian kết quả xét nghiệm
@app.route('/admin/time-labresult',methods=['GET', 'POST'])
@app.route('/admin/time-labresult/<string:day_query>',methods=['GET', 'POST'])
@register_breadcrumb(app, '..admin.time_labresult', 'Kết quả xét nghiệm')
@lab_required
def time_labresult(day_query=None):
    con = get_db_edit()
    cursor = con.cursor()

    # ngày bắt đầu và kết thúc truy vấn dữ liệu
    time_filter = request.args.get('time')
    start_get = request.args.get('start')
    end_get = request.args.get('end')

    # lấy ngày xem dashboard
    day_class = DayQuery(day_query, time_filter, start_get, end_get)
    today = day_class.today
    start = day_class.start
    end = day_class.end

    previous_start = day_class.previous_start
    previous_end = day_class.previous_end

    diff = diff_days(start, end)
    table_column_title = ['Số phiếu yêu cầu', 'Mã y tế','Tên bệnh nhân', 'Thời gian yêu cầu','BarcodeID',  'Nội dung', 'ResultDatetime','Action']


    if request.method == 'POST':
        time_edit = request.form['time_edit']
        result_id = request.form['result_change_id']
        new_time = datetime.strptime(time_edit, '%Y-%m-%dT%H:%M')
        q = """update  eLab_NgheAn..LabResultDetail set ResultDateTime=?  where ResultDetailID = ?"""
        cursor.execute(q, new_time, result_id)
        con.commit()
        flash('Sửa thời gian thành công')



    lab_list = query_lab.lab_result(start, end, cursor)


    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'start': start,
        'end': end,
        'diff': diff,
        'list': lab_list,
        'table_column_title': table_column_title
    }
    close_db()

    return render_template('admin/time-labresult.html', value=context)




# ----------------------------------------------------------------------------------------
# API Thông tin của bệnh nhân
@app.route('/patient-api/<string:mayte>')
@login_required
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

    close_db()

    return info_json

# API đơn thuốc của bệnh nhân
@app.route('/prescription-api/<int:khambenh_id>')
@login_required
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
    close_db()

    return j

# API chỉ định của bệnh nhân
@app.route('/cls-api/<int:tiepnhan_id>')
@login_required
def cls_api(tiepnhan_id):
    cnxn = get_db()
    cursor = cnxn.cursor()

    info = query_patient.cls_yeucau(tiepnhan_id, cursor)
    info_list = []
    for i in info:
        d = collections.OrderedDict()
        d['cls_yeucau_id'] = i[0]
        d['chidinh'] = i[1]

        info_list.append(d)

    j = jsonify(info_list)
    close_db()

    return j

# API kết quả của bệnh nhân
@app.route('/ketqua-api/<int:cls_id>')
@login_required
def ketqua_api(cls_id):
    cnxn = get_db()
    cursor = cnxn.cursor()

    info = query_patient.cls_ketqua(cls_id, cursor)
    info_list = []
    for i in info:
        d = collections.OrderedDict()
        d['mota'] = i[0]
        d['ketluan'] = i[1]
        d['bacsi'] = i[2]
        d['chidinh'] = i[3]

        info_list.append(d)

    j = jsonify(info_list)
    close_db()

    return j

# API nhân viên trong khoa
@app.route('/staff-department-api/<int:department_id>')
@login_required
def staff_department_api(department_id):
    cnxn = get_db()
    cursor = cnxn.cursor()

    info = query_user.staff_department(department_id, cursor)
    info_list = []
    for i in info:
        d = collections.OrderedDict()
        d['name'] = i[0]
        d['id'] = i[1]
        d['bod'] = i[2]

        info_list.append(d)

    j = jsonify(info_list)
    close_db()

    return j

# chi tiết bài viết
@app.route('/mlWteF6XdB')
def mlWteF6XdB():

    return render_template('include/mlWteF6XdB.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
