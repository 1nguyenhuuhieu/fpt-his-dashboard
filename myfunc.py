
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


# Tính công suất giường bệnh = số giường đang dùng/số giường thực kê
def bed_caculator(today, cursor):
    # Tính công suất toàn viện trong ngày
    today_real_bed = query_hospitalized.total_day(today, cursor)
    total_percent = get_percent(today_real_bed, total_bed['TTYT Anh Sơn'][2])
    ttyt = ('TTYT Anh Sơn', today_real_bed,
            total_bed['TTYT Anh Sơn'][2], total_percent)

    # công suất khoa hscc
    hscc_real_bed = query_hospitalized.bed_department(today, 1228, cursor)
    hscc_percent = get_percent(hscc_real_bed, total_bed['Khoa HSCC-Nhi'][2])
    hscc = ('Khoa HSCC-Nhi', hscc_real_bed,
            total_bed['Khoa HSCC-Nhi'][2], hscc_percent)

    # công suất khoa ngoại
    ngoai_real_bed = query_hospitalized.bed_department(today, 1219, cursor)
    ngoai_percent = get_percent(
        ngoai_real_bed, total_bed['Khoa Ngoại tổng hợp'][2])
    ngoai = ('Khoa Ngoại tổng hợp', ngoai_real_bed,
             total_bed['Khoa Ngoại tổng hợp'][2], ngoai_percent)

    # công suất khoa nội
    noi_real_bed = query_hospitalized.bed_department(today, 1215, cursor)
    noi_percent = get_percent(
        noi_real_bed, total_bed['Khoa Nội-Truyền nghiễm'][2])
    noi = ('Khoa Nội-Truyền nghiễm', noi_real_bed,
           total_bed['Khoa Nội-Truyền nghiễm'][2], noi_percent)

    # công suất khoa yhct
    yhct_real_bed = query_hospitalized.bed_department(today, 1227, cursor)
    yhct_percent = get_percent(yhct_real_bed, total_bed['Khoa Đông Y&PHCN'][2])
    yhct = ('Khoa Đông Y&PHCN', yhct_real_bed,
            total_bed['Khoa Đông Y&PHCN'][2], yhct_percent)

    # công suất khoa sản
    san_real_bed = query_hospitalized.bed_department(today, 1218, cursor)
    san_percent = get_percent(san_real_bed, total_bed['Khoa Phụ Sản'][2])
    san = ('Khoa Phụ Sản', san_real_bed,
           total_bed['Khoa Phụ Sản'][2], san_percent)

    # công suất khoa Liên chuyên khoa TMH-RHM-Mắt
    lck_real_bed = query_hospitalized.bed_department(today, 2385, cursor)
    lck_percent = get_percent(
        lck_real_bed, total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2])
    lck = ('Liên chuyên khoa TMH-RHM-Mắt', lck_real_bed,
           total_bed['Liên chuyên khoa TMH-RHM-Mắt'][2], lck_percent)

    return [ttyt, ngoai, noi, hscc, san, lck,  yhct]
