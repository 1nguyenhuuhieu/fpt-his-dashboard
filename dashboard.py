from flask import Flask
from flask import render_template
import pyodbc
from datetime import date, datetime, timedelta
from dateutil.relativedelta import *
from time import time

from flask import jsonify

import sql_query
import threading
import sqlite3



# Kết nối database sql server
def get_db():
    server = '192.168.123.254'
    database = 'eHospital_NgheAn'
    username = 'sa'
    password = 'toanthang'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server+';DATABASE='+database+';UID='+username+';PWD=' + password)
    return cnxn

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

    
# Tính trung bình số tiền trên mỗi xác nhận
def abs_confirmed(count, total):
    if count:
        avg = round(total/count)
    else:
        avg = 0

    return avg

# Convert to google chart data
def convert_to_chart(list):

    chart = dict(list)
    chart = [[k, int(v)] for k, v in chart.items()]

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

# SQL query -----------------------------------------

# SQL query số lượt xác nhận theo loại ngoại trú hoặc nội trú
def query_confirmed_day(day, loai, cursor):
    try:
        q = cursor.execute(
            """
            SELECT  
            COUNT(TiepNhan.TiepNhan_Id)
            FROM TiepNhan
            INNER JOIN XacNhanChiPhi
            ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            AND Loai=?

            """, day, loai
        ).fetchone()[0]
    except:
        q = 0

    return q


# SQL query số lượt xác nhận trong khoảng ngày
def query_all_confirmed_day(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT  
            COUNT(TiepNhan.TiepNhan_Id)
            FROM TiepNhan
            INNER JOIN XacNhanChiPhi
            ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
            WHERE XacNhanChiPhi.NgayXacNhan BETWEEN ? AND ?
            """, startday, endday
        ).fetchone()[0]
    except:
        q = 0

    return q

# SQL query thống kê tổng doanh thu theo nội trú, ngoại trú
def query_confirmed_money_day(day, loai, cursor):
    try:
        q = int(cursor.execute(
            """
            SELECT  
            SUM(TiepNhan.TongDoanhThu)
            FROM TiepNhan
            INNER JOIN XacNhanChiPhi
            ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            AND Loai=?

            """, day, loai
        ).fetchone()[0])
    except:
        q = 0

    return q


# SQL query thời gian update mới nhất doanh thu
def query_last_money_update(cursor):
    q = cursor.execute(
        """
        SELECT TOP 1 NgayTao
        FROM XacNhanChiPhi
        ORDER BY XacNhanChiPhi_Id DESC
        """
    ).fetchone()[0]

    return q

# Thống kê doanh thu từng khoa trong khoảng ngày
def query_between_day_money_department(startday, endday, cursor):
    q = cursor.execute(
        """
        SELECT TenPhongKham, COALESCE(SUM(TongDoanhThu),0) as 'total_money'
        FROM XacNhanChiPhi
        INNER JOIN TiepNhan
        ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
        WHERE XacNhanChiPhi.NgayXacNhan BETWEEN ? AND ?
        GROUP BY TenPhongKham
        ORDER BY total_money
        """, startday, endday
    ).fetchall()

    return q

# Xác nhận chi phí cuối cùng
def query_last_confirmed(cursor):
    q = cursor.execute(
        """
        SELECT TOP 1
        SoTiepNhan, XacNhanChiPhi.BenhNhan_Id, ThoiGianTiepNhan, XacNhanChiPhi.NgayTao, TongDoanhThu, Chandoan, Loai, TenPhongKham
        FROM TiepNhan
        INNER JOIN XacNhanChiPhi
        ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
        ORDER BY XacNhanChiPhi.XacNhanChiPhi_Id DESC
        """
    ).fetchone()

    return q


# -------------------------------------------------------------


app = Flask(__name__)

# register zip filter for pararell loop
app.jinja_env.filters['zip'] = zip

# Trang chủ
@app.route("/dashboard/<string:day_query>")
@app.route("/")
def home(day_query=None):


    # kết nối database sql server
    cnxn = get_db()
    cursor = cnxn.cursor()

    # lấy ngày xem dashboard
    day_dict = get_day(day_query)
    today = day_dict['today']
    yesterday = day_dict['yesterday']

    # Doanh thu trong 1 ngày
    today_money = sql_query.doanhthu_day(today, cursor)
    today_money_thanhtoan = sql_query.thanhtoan_day(today, cursor)
    yesterday_money = sql_query.doanhthu_day(yesterday, cursor)
    yesterday_money_thanhtoan = sql_query.thanhtoan_day(yesterday, cursor)
    percent_doanhthu = get_change(today_money, yesterday_money)
    percent_thanhtoan = get_change(today_money_thanhtoan, yesterday_money_thanhtoan)

    money_card = (
        ("Doanh thu", today_money, percent_doanhthu),
        ("Thanh toán", today_money_thanhtoan, percent_thanhtoan)
    )

    # Thống kê bệnh nhân
    patient_card = []

    today_in_hospital = sql_query.total_in_hospital_day(today, cursor)
    yesterday_in_hospital = sql_query.total_in_hospital_day(yesterday, cursor)

    percent_in_hospita = get_change(today_in_hospital, yesterday_in_hospital)
    patient_card.append(
        ("Bệnh nhân nội trú", 'fa-solid fa-hospital', today_in_hospital, percent_in_hospita))

    # Số lượt tiếp nhận
    today_visited = sql_query.visited_day(today, cursor)
    yesterday_visited = sql_query.visited_day(yesterday, cursor)
    percent_visited = get_change(today_visited, yesterday_visited)
    patient_card.append(
        ("Lượt tiếp nhận", 'fa-solid fa-hospital-user', today_visited, percent_visited))

    # Số bệnh nhân nhập viện
    today_hospitalize = sql_query.in_hospital_day(today, cursor)
    yesterday_hospitalize = sql_query.in_hospital_day(yesterday, cursor)
    percent_hospitalize = get_change(today_hospitalize, yesterday_hospitalize)
    patient_card.append(("Nhập viện nội trú", 'fa-solid fa-bed-pulse',
                        today_hospitalize, percent_hospitalize))

    # Lượt chuyển tuyến
    today_transfer = sql_query.transfer_day(today, cursor)
    yesterday_transfer = sql_query.transfer_day(yesterday, cursor)
    percent_transfer = get_change(today_transfer, yesterday_transfer)

    patient_card.append(
        ("Chuyển tuyến", 'fa-solid fa-truck-medical', today_transfer, percent_transfer))


    today_surgecies = sql_query.surgecies_day(today, cursor)
    yesterday_surgecies = sql_query.surgecies_day(yesterday, cursor)
    percent_surgecies = get_change(today_surgecies, yesterday_surgecies)
    patient_card.append(
        ("Phẫu thuật, thủ thuật", 'fa-solid fa-kit-medical', today_surgecies, percent_surgecies))


    today_born = sql_query.born_day(today, cursor)
    yesterday_born = sql_query.born_day(yesterday, cursor)
    percent_born = get_change(today_born, yesterday_born)
    patient_card.append(
        ("Số trẻ sinh", 'fa-solid fa-baby', today_born, percent_born))

    # Thống kê số lượt khám theo từng phòng khám
    visited_in_department = sql_query.visited_department_day(today, cursor)

    # Dữ liệu cho lượt khám bệnh chart
    visited_in_department = convert_to_chart(visited_in_department)
    visited_in_department_chart = visited_in_department.copy()
    visited_in_department_chart.insert(0, ["Phòng", 'Lượt khám'])
    
    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = sql_query.in_hostpital_department(today, cursor)

    patient_in_department = convert_to_chart(patient_in_department)
    patient_in_department_chart = patient_in_department.copy()
    patient_in_department_chart.insert(0, ["Khoa", 'Bệnh nhân'])

    # Chart 30 day số lượt khám
    last30days = today - timedelta(days=50)
    last30days_visited = sql_query.visited_betweenday(last30days, today, cursor)
    last30days_visited = [[day.strftime(
        "%A %d-%m-%Y"), int(visited)] for day, visited in last30days_visited]

    last30days_visited.reverse()

    # convert để hiện thị ở top filter
    today = today.strftime("%Y-%m-%d")

    context = {
        'money_card': money_card,
        'patient_card': patient_card,
        'today': today,
        'soluotkham30ngay': last30days_visited,
        'patient_in_department': patient_in_department,
        'patient_in_department_chart': patient_in_department_chart,
        'visited_in_department': visited_in_department,
        'visited_in_department_chart': visited_in_department_chart,
    }

    cnxn.close()
    return render_template('home.html', value=context, title="Dashboard")


# Trang doanh thu
@app.route('/revenue/<string:day_query>')
@app.route('/revenue')
def revenue(day_query=None):

    tic = time()

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
    today_money = sql_query.doanhthu_day(today, cursor)


    yesterday_money = sql_query.doanhthu_day(yesterday, cursor)
    percent_doanhthu = get_change(today_money, yesterday_money)
    money_card_top = ("Trong ngày này", today_money, percent_doanhthu)

    # Doanh thu 30 ngày gần nhất
    last30day = today - timedelta(days=50)
    last_30days_money = sql_query.doanhthu_betweenday(last30day, today, cursor)
    last_30days_money = [[ngayxacnhan.strftime(
        "%A %d-%m-%Y"), int(tongdoanhthu)] for ngayxacnhan, tongdoanhthu in last_30days_money]
    last_30days_money.reverse()

    # Doanh thu 30 ngày gần nhất theo từng khoa phòng
    last_30days_department_money = sql_query.money_department_betweenday(
        last30day, today, cursor)

    # Tạo dữ liệu cho chart
    last_30days_department_money_chart = convert_to_chart(last_30days_department_money)
    
    last_30days_department_money_chart.insert(0, ['Khoa', 'Số tiền'])

    confirmed_visited = query_confirmed_day(today, 'NgoaiTru', cursor)
    confirmed_hospital = query_confirmed_day(today, 'NoiTru', cursor)
    confirmed_total = confirmed_visited + confirmed_hospital

    money_visited = sql_query.doanhthu_loai_day(today, 'NgoaiTru', cursor)
    money_hospital = sql_query.doanhthu_loai_day(today, 'NoiTru', cursor)

    money_card_body = sql_query.doanhthu_dichvu_duoc_day(today, cursor)
    money_card_body = convert_to_chart(money_card_body)
    money_card_body_chart = money_card_body.copy()
    money_card_body_chart.insert(0, ['Mục', 'Số tiền'])
 
    visited_card_body = [
        ['Tổng số', confirmed_total],
        ['Ngoại trú', money_visited],
        ['Nội trú', money_hospital],
    ]

    # Thống kê trong tuần
    week_money = sql_query.total_money_between(mon_day, today, cursor)
    week_avg_confirmed = sql_query.avg_doanhthu_confirmed(mon_day, today, cursor)
    week_avg_money = sql_query.avg_doanhthu_between(startday=mon_day, endday=today, cursor=cursor)
    visited_money_week = sql_query.doanhthu_loai_between(
        mon_day, today, 'NgoaiTru', cursor)
    hospital_money_week = sql_query.doanhthu_loai_between(
        mon_day, today, 'NoiTru', cursor)



    # Thống kê trong tuần trước
    last_week_money = sql_query.total_money_between(
        last_week_monday, last_week_sun_day, cursor)
    last_week_avg_money = sql_query.avg_doanhthu_between(last_week_monday,last_week_sun_day, cursor)
    last_week_avg_confirmed = sql_query.avg_doanhthu_confirmed(last_week_monday,last_week_sun_day, cursor)
    visited_money_last_week = sql_query.doanhthu_loai_between(
        last_week_monday, last_week_sun_day, 'NgoaiTru', cursor)
    hospital_money_last_week = sql_query.doanhthu_loai_between(
        last_week_monday, last_week_sun_day, 'NoiTru', cursor)

        
    week_progress_bar_title = 'So với tuần trước'
    week_progress_bar_value = get_percent(week_money, last_week_money)


    twolast_week_money = sql_query.total_money_between(
        twolast_week_monday, twolast_week_sun_day, cursor)
    last_week_progress_bar_title = 'So với tuần trước'
    last_week_progress_bar_value = get_percent(last_week_money, twolast_week_money)




    # Thống kê trong tháng
    month_money = sql_query.total_money_between(first_month_day, today, cursor)

    month_avg_money = sql_query.avg_doanhthu_between(first_month_day, today, cursor)

    month_avg_confirmed = sql_query.avg_doanhthu_confirmed(first_month_day, today, cursor)

    visited_money_month = sql_query.doanhthu_loai_between(
        first_month_day, today, 'NgoaiTru', cursor)
    hospital_money_month = sql_query.doanhthu_loai_between(
        first_month_day, today, 'NoiTru', cursor)

    last_month_money =  sql_query.total_money_between(
        last_first_month_day, last_end_month_day, cursor)


    month_progress_bar_title = 'So với tháng trước'
    month_progress_bar_value = get_percent(month_money, last_month_money)

   
    # Thống kê trong năm
    year_money = sql_query.total_money_between(first_year_day, today, cursor)

    year_avg_money = sql_query.avg_doanhthu_between(first_year_day, today, cursor)

    year_avg_confirmed = sql_query.avg_doanhthu_confirmed(first_year_day, today, cursor)

    visited_money_year = sql_query.doanhthu_loai_between(
        first_year_day, today, 'NgoaiTru', cursor)
    hospital_money_year = sql_query.doanhthu_loai_between(
        first_year_day, today, 'NoiTru', cursor)

    
    last_year_money = sql_query.total_money_between(
        last_first_year_day, end_last_year_day, cursor)
    year_progress_bar_title = 'So với năm trước'
    year_progress_bar_value = get_percent(year_money, last_year_money)

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

        [
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
            
         ],
        [
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
    ]

    bellow_card_money_title = ['Tổng', 'Ngoại trú', 'Nội trú', 'Trung bình ngày', 'Trung bình mỗi xác nhận' ]

    confirmed_chart = [
        ['Loại', 'Doanh thu'],
        ['Ngoại trú', money_visited],
        ['Nội trú', money_hospital],
    ]

    # Doanh thu theo từng phòng khám, từng khoa
    money_department = sql_query.money_department_day(today, cursor)
    money_department = convert_to_chart(money_department)
    money_department_chart = money_department.copy()

    last_update_time = query_last_money_update(cursor)
    last_update_time = last_update_time.strftime("%H:%M:%S  %d-%m-%Y")

    last_confirmed = query_last_confirmed(cursor)

    recent_confirmed_in_day = sql_query.recent_confirmed_review(today, cursor)

    recent_confirmed_in_day = ([soxacnhan, thoigian.strftime("%H:%M:%S"), int(doanhthu), int(thanhtoan), nhanvien] for soxacnhan, thoigian, doanhthu, thanhtoan, nhanvien in recent_confirmed_in_day)

    top10_doanhthu = sql_query.top10_doanhthu(today, cursor)
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

    toc = time()
    print(toc-tic)

    return render_template('revenue.html', value=context, title="Doanh thu")

# Xác nhận chi tiết
@app.route('/confirmed')
@app.route('/confirmed/<string:day_query>')
def confirmed(day_query=None):
    cnxn = get_db()
    cursor = cnxn.cursor()

    today = get_day_query(day_query)

    all_confirmed = sql_query.all_confirmed(today, cursor)
    all_confirmed = ([thoigian.strftime("%H:%M:%S %d-%m-%Y"),soxacnhan,benhnhan_id,  int(doanhthu), int(thanhtoan), phongkham,nhanvien] for thoigian,soxacnhan, benhnhan_id, doanhthu, thanhtoan,phongkham, nhanvien in all_confirmed)

    today = today.strftime("%Y-%m-%d")


    context = {
        'all_confirmed': all_confirmed,
        'today': today
    }

    cnxn.close()
    

    return render_template('confirmed.html', value=context, title="Xác nhận")

@app.route('/confirmed/detail/<string:SoXacNhan_Id>')
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

    today_in_hospital = sql_query.total_in_hospital_day(today, cursor)
    recent_today_in_hospital = sql_query.in_hospital_day(today, cursor)
    yesterday_in_hostpital = sql_query.total_in_hospital_day(yesterday, cursor)
    out_hospital_day = sql_query.total_out_hospital_day(today, cursor)
    percent_change = get_change(today_in_hospital,yesterday_in_hostpital)
    percent = get_percent(today_in_hospital,yesterday_in_hostpital)

    card_top.append(["Nội trú hôm nay", today_in_hospital, percent_change, percent, yesterday_in_hostpital])

    card_top_body = []
    card_top_body.append(['Nhập mới', recent_today_in_hospital])
    card_top_body.append(['Ra viện', out_hospital_day])

    # Thống kê Số bệnh nhân nội trú từng khoa
    patient_in_department = sql_query.in_hostpital_department(today, cursor)

    patient_in_department = convert_to_chart(patient_in_department)
    patient_in_department_chart = patient_in_department.copy()
    patient_in_department_chart.insert(0, ["Khoa", 'Bệnh nhân'])

    # chart số bệnh nhân nội trú 30 ngày gần nhất
    last_30_day_chart = []
    for day in range(30):
        day_q = today - timedelta(days=day)
        count_patient = sql_query.total_in_hospital_day(day_q, cursor)
        
        last_30_day_chart.append([day_q.strftime("%A %d-%m-%Y"),count_patient])
    
    last_30_day_chart.reverse()

    # Bệnh nhân vừa nhập viện
    recent_hospitalized_in_day = sql_query.recent_confirmed_review(today, cursor)



    a = {
        'et': 'asdads'
    }

    print(a['et'])
    
    today = today.strftime("%Y-%m-%d")
    context = {
        'today': today,
        'card_top': card_top,
        'card_top_body': card_top_body,
        'patient_in_department': patient_in_department,
        'patient_in_department_chart': patient_in_department_chart,
        'last_30_day_chart': last_30_day_chart,
        'recent_hospitalized_in_day': recent_hospitalized_in_day
    }

    cnxn.close()
    return render_template('hospitalized.html', value=context, title="Nội trú")
