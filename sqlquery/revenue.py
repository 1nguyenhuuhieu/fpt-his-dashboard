import time
# SQL query tổng doanh thu trong khoảng thời gian
def total_money_betweentime(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            SUM(SoLuong*DonGiaDoanhThu)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            """, start, end
        ).fetchone()[0]
        return int(q)
    except:
        print("Lỗi query revenue.total_money_betweentime")
        return 0


# SQL query tổng doanh thu trong khoảng thời gian group by ngày
def total_chart(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhi.NgayXacNhan,
            SUM(SoLuong*DonGiaDoanhThu) as 'total'
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY XacNhanChiPhi.NgayXacNhan
            """, start, end
        ).fetchall()
        for row in q:
            row.total = int(row.total)
        return q
    except:
        print("Lỗi query revenue.total_chart")
        return 0



# SQL query tổng doanh thu trong khoảng ngày
def bhtt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            SUM(SoLuong*DonGiaHoTroChiTra)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.bhtt_betweentime")
        return 0
    
# SQL query tổng doanh thu trong khoảng thời gian
def bntt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            SUM(SoLuong*DonGiaThanhToan)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.bntt_betweentime")
        return 0

# SQL query tổng doanh thu trong khoảng ngày
def avg_money_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT AVG(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaDoanhThu) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.avg_money_betweentime")
        return 0
    
# SQL query tổng doanh thu trong khoảng ngày
def avg_bhtt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT AVG(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaHoTroChiTra) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.avg_bhtt_betweentime")
        return 0
    
# SQL query tổng doanh thu trong khoảng ngày
def avg_bntt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT AVG(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaThanhToan) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.avg_bntt_betweentime")
        return 0
    

# SQL query  doanh thu Lớn nhất trong khoảng ngày
def max_money_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT MAX(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaDoanhThu) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.max_money_betweentime")
        return 0

# SQL query  doanh thu Lớn nhất trong khoảng ngày
def max_bhtt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT MAX(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaHoTroChiTra) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.max_bhtt_betweentime")
        return 0
    
# SQL query  doanh thu Lớn nhất trong khoảng ngày
def max_bntt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT MAX(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaThanhToan) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]

        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.max_bntt_betweentime")
        return 0

# SQL query  doanh thu bé nhất trong khoảng ngày
def min_money_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT MIN(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaDoanhThu) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]
        print(q)
        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.min_money_betweentime")
        return 0
    
# SQL query  doanh thu bé nhất trong khoảng ngày
def min_bhtt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT MIN(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaHoTroChiTra) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]
        print(q)
        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.min_bhtt_betweentime")
        return 0
    
# SQL query  doanh thu bé nhất trong khoảng ngày
def min_bntt_betweentime(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
        SELECT MIN(asset_sums)
        FROM
            (SELECT
            SUM(SoLuong*DonGiaThanhToan) AS asset_sums, NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as inner_query
            """, startday, endday
        ).fetchone()[0]
        print(q)
        return f'{int(q):,}'
    except:
        print("Lỗi query revenue.min_bntt_betweentime")
        return 0
    



# Thống kê tiền BHYTtrong 1 ngày
def bhtt(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(SoLuong*DonGiaHoTroChiTra),0)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            """, start, end
        ).fetchone()[0]
        return int(q)
    except:
        print('Lỗi query bhtt')
        return 0

# Thống kê tiền BNTT trong 1 ngày
def bntt(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(SoLuong*DonGiaThanhToan),0)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            """, start, end
        ).fetchone()[0]
        return int(q)
    except:
        print('Lỗi query total_bhtt_day')
        return 0


# Tổng doanh thu dược trong ngày theo phân nhóm: (DV= Dịch vụ, DU = DƯợc)
def service_money(start,end, phannhom ,cursor):
    query = """
    SELECT 
    COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'TongDoanhThu'
    FROM XacNhanChiPhi
    INNER JOIN (XacNhanChiPhiChiTiet LEFT JOIN VienPhiNoiTru_Loai_IDRef ON XacNhanChiPhiChiTiet.Loai_IDRef=VienPhiNoiTru_Loai_IDRef.Loai_IDRef)
    ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    WHERE ThoiGianXacNhan BETWEEN ? AND ? AND PhanNhom=?
    GROUP BY PhanNhom
    """
    try:
        q = cursor.execute(query, start, end, phannhom).fetchone()[0]
        return int(q)
    except:
        print("Lỗi query service_medicine_day")
        return 0    
    
def phannhom_money(start,end ,cursor):
    query = """
    SELECT 
    SUM(SoLuong*DonGiaDoanhThu) AS 'TongDoanhThu', PhanNhom
    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
	LEFT JOIN VienPhiNoiTru_Loai_IDRef ON XacNhanChiPhiChiTiet.Loai_IDRef=VienPhiNoiTru_Loai_IDRef.Loai_IDRef
    WHERE ThoiGianXacNhan BETWEEN ? AND ?
    GROUP BY PhanNhom
    """
    try:
        q = cursor.execute(query, start, end).fetchall()
        return q
    except:
        print("Lỗi query phannhom_money")
        return 0    


# SQL query tổng doanh thu trong khoảng ngày
def day_betweenday(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT TOP 30
            NgayXacNhan,
            SUM(SoLuong*DonGiaDoanhThu)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE NgayXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan
            ORDER BY NgayXacNhan DESC
            """, startday, endday
        ).fetchall()

        return q
    except:
        print("Lỗi query revenue.perday_betweenday")
        return 0


# SQl query thống kê doanh thu theo từng khoa phòng trong khoảng ngày
def departments(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            (CASE
                WHEN TenPhongKham IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongKham IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongKham END),
            
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'TongDoanhThu'

            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id

            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY 
            (CASE
                WHEN TenPhongKham IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongKham IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongKham END)
            ORDER BY TongDoanhThu DESC
            """, start, end
        ).fetchall()

        for row in q:
            row.TongDoanhThu = f'{round(int(row.TongDoanhThu)*0.001)*1000:,} đ'

        return q
    except:
        print("Lỗi query revenue.departments")
        return 0

# SQl query thống kê doanh thu theo từng khoa phòng trong khoảng ngày
def departments_chart(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            (CASE
                WHEN TenPhongKham IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongKham IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongKham END),
            
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'TongDoanhThu'

            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id

            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY 
            (CASE
                WHEN TenPhongKham IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongKham IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongKham END)
            ORDER BY TongDoanhThu DESC
            """, start, end
        ).fetchall()

        for row in q:
            row.TongDoanhThu = int(row.TongDoanhThu)

        return q
    except:
        print("Lỗi query revenue.departments")
        return 0
    
# SQL query tổng doanh thu ngoại trú, nội trú trong ngày
def total_loai(start, end,loai,cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0)
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ? AND XacNhanChiPhiChiTiet.Loai=?
            """, start,end, loai
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.total_loai")
        return 0


# SQL Query thống kê doanh thu trong ngày dựa theo từng ten phan nhom
def tenphanhom_service(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT 
                (CASE
                WHEN TenPhanNhom IS NULL THEN N'Dược Ngoại Trú'
                WHEN TenPhanNhom=N'Dược' THEN N'Dược Nội Trú'
                ELSE TenPhanNhom
                END
            ),
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'TongDoanhThu'
            FROM XacNhanChiPhi
            INNER JOIN (XacNhanChiPhiChiTiet INNER JOIN VienPhiNoiTru_Loai_IDRef ON XacNhanChiPhiChiTiet.Loai_IDRef=VienPhiNoiTru_Loai_IDRef.Loai_IDRef)
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY TenPhanNhom
            ORDER BY TongDoanhThu   
            """, start, end
        ).fetchall()
        for row in q:
            row.TongDoanhThu = int(row.TongDoanhThu)
        return q
    except:
        print("Lỗi query tenphanhom_service")
        return 0

# SQL Query thống kê doanh thu trong ngày dựa theo từng ten phan nhom
def tenphanhom_service_format(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT 
                (CASE
                WHEN TenPhanNhom IS NULL THEN N'Dược Ngoại Trú'
                WHEN TenPhanNhom=N'Dược' THEN N'Dược Nội Trú'
                ELSE TenPhanNhom
                END
            ),
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'TongDoanhThu'
            FROM XacNhanChiPhi
            INNER JOIN (XacNhanChiPhiChiTiet INNER JOIN VienPhiNoiTru_Loai_IDRef ON XacNhanChiPhiChiTiet.Loai_IDRef=VienPhiNoiTru_Loai_IDRef.Loai_IDRef)
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY TenPhanNhom
            ORDER BY TongDoanhThu   
            """, start, end
        ).fetchall()
        for row in q:
            row.TongDoanhThu = f'{round(int(row.TongDoanhThu)*0.001)*1000:,} đ'
        return q
    except:
        print("Lỗi query tenphanhom_service_format")
        return 0


# SQL query tổng tiền trong khoảng ngày
def total_between(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT SUM(SoLuong*DonGiaDoanhThu)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE NgayXacNhan BETWEEN ? AND ?
            """, startday, endday
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.total_between")
        return 0

# SQL query trung bình doanh thu mỗi ngày trong khoảng ngày
def avg_between(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT AVG(total_money)
            FROM
            (SELECT COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'total_money', NgayXacNhan
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY NgayXacNhan) as avg_total_money
            """, startday, endday
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.avg_between")
        return 0
    
# SQL query trung bình doanh thu mỗi xác nhận
def avg_confirmed(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT AVG(total_money)
            FROM
            (SELECT COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'total_money', XacNhanChiPhi.XacNhanChiPhi_Id
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY XacNhanChiPhi.XacNhanChiPhi_Id) as avg_total_confirmed
            """, startday, endday
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.avg_confirmed")
        return 0

# SQL query tổng doanh thu ngoại trú, nội trú trong khoảng ngày
def visited_hospitalized_between(startday, endday , loai, cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0)
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            WHERE NgayXacNhan BETWEEN ? AND ? AND XacNhanChiPhiChiTiet.Loai=?
            """, startday, endday, loai
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.visited_hospitalized_between")
        return 0
# SQl query thống kê doanh thu theo từng khoa phòng
def department_day(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            (CASE
                WHEN TenPhongKham IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongKham IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongKham END),
            
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'TongDoanhThu'

            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id

            WHERE NgayXacNhan=?
            GROUP BY 
            (CASE
                WHEN TenPhongKham IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongKham IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongKham END)
            ORDER BY TongDoanhThu DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query revenue.department_day")
        return 0


# SQL top 10 khoa phòng nhiều doanh thu nhất trong ngày
def top_service(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT TOP 10
            XacNhanChiPhiChiTiet.NoiDung,
            XacNhanChiPhi.TenPhongKham,
            COALESCE(COUNT(XacNhanChiPhiChiTiet.NoiDung),0) as 'count',
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi 
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            GROUP BY
            XacNhanChiPhiChiTiet.NoiDung,
            XacNhanChiPhi.TenPhongKham
            ORDER BY tongdoanhthu DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query revenue.top_service")
        return 0




# SQL query tổng tiền trong khoảng ngày fast dựa trên bảng nhh_revennue từ ngày 2023-02-01 trở về trước 
def total_between_union(startday, endday, cursor):
    query = """
            SELECT SUM(tongdoanhthu) FROM(
            SELECT
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) as 'tongdoanhthu', NgayXacNhan
            FROM
            (XacNhanChiPhi INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            AND NgayXacNhan > '2023-01-31')
            GROUP BY NgayXacNhan
            UNION
            (SELECT tongdoanhthu, NgayXacNhan
            FROM nhh_revenue)
            ) AS T
            WHERE NgayXacNhan BETWEEN ? AND ?
            """
    try:
        q = cursor.execute(query, startday, endday).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.total_between_union")
        return 0


# SQL query tổng doanh thu ngoại trú trong khoảng ngày union với bảng nhh_revennue_visited từ ngày 2023/02/01 trở về trước
def visited_between_union(startday, endday, cursor):
    query = """
            SELECT SUM(tongdoanhthu) FROM(
            SELECT
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) as 'tongdoanhthu', NgayXacNhan
            FROM
            (XacNhanChiPhi INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            AND NgayXacNhan > '2023-01-31' AND XacNhanChiPhi.Loai = 'NgoaiTru')
            GROUP BY NgayXacNhan
            UNION
            (SELECT tongdoanhthu, NgayXacNhan
            FROM nhh_revenue_visited)
            ) AS T
            WHERE NgayXacNhan BETWEEN ? AND ?
            """
    try:
        q = cursor.execute(query, startday, endday).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.visited_between_union")
        return 0


# SQL query tổng doanh thu nội trú trong khoảng ngày union với bảng nhh_revennue_visited từ ngày 2023/02/01 trở về trước
def hospitalized_between_union(startday, endday, cursor):
    query = """
            SELECT SUM(tongdoanhthu) FROM(
            SELECT
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) as 'tongdoanhthu', NgayXacNhan
            FROM
            (XacNhanChiPhi INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            AND NgayXacNhan > '2023-01-31' AND XacNhanChiPhi.Loai = 'NoiTru')
            GROUP BY NgayXacNhan
            UNION
            (SELECT tongdoanhthu, NgayXacNhan
            FROM nhh_revenue_hospitalized)
            ) AS T
            WHERE NgayXacNhan BETWEEN ? AND ?
            """
    try:
        q = cursor.execute(query, startday, endday).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.hospitalized_between_union")
        return 0


# SQL query trung bình doanh thu mỗi ngày trong khoảng ngày UNION với bảng nhh_revenue
def avg_between_union(startday, endday, cursor):
    query = """
            SELECT AVG(tongdoanhthu) FROM(
            SELECT
            COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) as 'tongdoanhthu', NgayXacNhan
            FROM
            (XacNhanChiPhi INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            AND NgayXacNhan > '2023-01-31')
            GROUP BY NgayXacNhan
            UNION
            (SELECT tongdoanhthu, NgayXacNhan
            FROM nhh_revenue)
            ) AS T
            WHERE NgayXacNhan BETWEEN ? AND ?
            """
    try:
        q = cursor.execute(query, startday, endday).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.avg_between_union")
        return 0



# SQL query trung bình doanh thu mỗi xác nhận trong khoảng ngày UNION với bảng nhh_revenue_confirmed từ ngày 2023-02-01 trở về trước
def avg_confirmed_union(startday, endday, cursor):
    query = """
    SELECT AVG(tongdoanhthu) FROM(
    SELECT
    COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) as 'tongdoanhthu', XacNhanChiPhi.XacNhanChiPhi_Id, XacNhanChiPhi.NgayXacNhan
    FROM
    (XacNhanChiPhi INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    AND NgayXacNhan > '2023-01-31')
    GROUP BY XacNhanChiPhi.XacNhanChiPhi_Id, XacNhanChiPhi.NgayXacNhan
    UNION
    (SELECT tongdoanhthu, XacNhanChiPhi_Id, NgayXacNhan
    FROM nhh_revenue_confirmed)
    ) AS T
    WHERE NgayXacNhan BETWEEN ? AND ?
    """
    try:
        q = cursor.execute(query, startday, endday).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.avg_confirmed_union")
        return 0


# SQL danh sách doanh thu trong khoảng ngày
def services(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhiChiTiet.NoiDung,
            Loai_IDRef_Name,
            XacNhanChiPhi.TenPhongKham,
            XacNhanChiPhiChiTiet.DonGiaDoanhThu,
            COALESCE(COUNT(XacNhanChiPhiChiTiet_Id),0) as 'count',
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi 
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            INNER JOIN VienPhiNoiTru_Loai_IDRef
            ON XacNhanChiPhiChiTiet.Loai_IDRef = VienPhiNoiTru_Loai_IDRef.Loai_IDRef
            WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN ? AND ?
            GROUP BY
            XacNhanChiPhiChiTiet.NoiDung,
            XacNhanChiPhiChiTiet.DonGiaDoanhThu,
            Loai_IDRef_Name,
            XacNhanChiPhi.TenPhongKham

            ORDER BY tongdoanhthu DESC
            """, start, end
        ).fetchall()
        for row in q:
            row.tongdoanhthu = f'{int(row.tongdoanhthu):,}'
        return q
    except:
        print("Lỗi query revenue.services")
        return None


def list_medicine(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhiChiTiet.NoiDung,
            XacNhanChiPhi.TenPhongKham,
            XacNhanChiPhiChiTiet.DonGiaDoanhThu as dongia,
            COALESCE(COUNT(XacNhanChiPhiChiTiet_Id),0) as 'count',
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi 
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            INNER JOIN VienPhiNoiTru_Loai_IDRef
            ON XacNhanChiPhiChiTiet.Loai_IDRef = VienPhiNoiTru_Loai_IDRef.Loai_IDRef
            WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN ? AND ? AND PhanNhom = 'DU'
            GROUP BY
            XacNhanChiPhiChiTiet.NoiDung,
            XacNhanChiPhi.TenPhongKham,
            XacNhanChiPhiChiTiet.DonGiaDoanhThu

            ORDER BY tongdoanhthu DESC
            """, start, end
        ).fetchall()

        for row in q:
            row.tongdoanhthu = f'{int(row.tongdoanhthu):,}'
            row.dongia = f'{int(row.dongia):,}'

        return q
    except:
        print("Lỗi query revenue.list_medicine")
        return 0



def list_service(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhiChiTiet.NoiDung,
            XacNhanChiPhi.TenPhongKham,
            XacNhanChiPhiChiTiet.DonGiaDoanhThu as dongia,
            COALESCE(COUNT(XacNhanChiPhiChiTiet_Id),0) as 'count',
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi 
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            INNER JOIN VienPhiNoiTru_Loai_IDRef
            ON XacNhanChiPhiChiTiet.Loai_IDRef = VienPhiNoiTru_Loai_IDRef.Loai_IDRef
            WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN ? AND ? AND PhanNhom = 'DV'
            GROUP BY
            XacNhanChiPhiChiTiet.NoiDung,
            XacNhanChiPhi.TenPhongKham,
            XacNhanChiPhiChiTiet.DonGiaDoanhThu

            ORDER BY tongdoanhthu DESC
            """, start, end
        ).fetchall()

        for row in q:
            row.tongdoanhthu = f'{int(row.tongdoanhthu):,}'
            row.dongia = f'{int(row.dongia):,}'

        return q
    except:
        print("Lỗi query revenue.list_service")
        return None

# danh sách chi phí theo tên khoa/phòng
def list_department(start, end,name, cursor):
    query = """
        SELECT
        XacNhanChiPhiChiTiet.NoiDung,
        XacNhanChiPhiChiTiet.DonGiaDoanhThu as dongia,
        COALESCE(COUNT(XacNhanChiPhiChiTiet_Id),0) as 'count',
        COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
        FROM XacNhanChiPhiChiTiet
        INNER JOIN XacNhanChiPhi 
        ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
        WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN ? AND ? AND XacNhanChiPhi.TenPhongKham = ?
        GROUP BY
        XacNhanChiPhiChiTiet.NoiDung,
        XacNhanChiPhiChiTiet.DonGiaDoanhThu
        ORDER BY tongdoanhthu DESC    
        """
    try:
        rows = cursor.execute(query, start, end, name).fetchall()
        for row in rows:
            row.tongdoanhthu = f'{int(row.tongdoanhthu):,}'
            row.dongia = f'{int(row.dongia):,}'
        return rows
    except:
        print("Lỗi query revenue.list_department")
        return None

# Tổng chi phí theo tên khoa phòng
def total_department(start, end,name, cursor):
    query = """
        SELECT
        COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
        FROM XacNhanChiPhiChiTiet
        INNER JOIN XacNhanChiPhi 
        ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
        WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN ? AND ? AND XacNhanChiPhi.TenPhongKham = ?
        """
    try:
        row = cursor.execute(query, start, end, name).fetchone()[0]
        return int(row)
    except:
        print("Lỗi query revenue.total_department")
        return None
    

def revenue_department(start, end,name, cursor):
    query = """
        SELECT
        COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
        FROM XacNhanChiPhiChiTiet
        INNER JOIN XacNhanChiPhi 
        ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
        INNER JOIN VienPhiNoiTru_Loai_IDRef
        ON XacNhanChiPhiChiTiet.Loai_IDRef = VienPhiNoiTru_Loai_IDRef.Loai_IDRef
        WHERE XacNhanChiPhi.ThoiGianXacNhan BETWEEN ? AND ? AND XacNhanChiPhi.TenPhongKham = ?
        GROUP BY
        ORDER BY tongdoanhthu DESC    
        """
    try:
        rows = cursor.execute(query, start, end, name).fetchall()
        return rows
    except:
        print("Lỗi query revenue.list_department")
        return None

def doctor_department(start, end, cursor):
    sql = """
        SELECT dm_noiyeucau.TenPhongBan as noiyeucau, dm_bacsichidinh.TenNhanVien as bacsichidinh,
        dm_noithuchien.TenPhongBan as noithuchien, dm_nhomdichvu.TenNhomDichVu, NoiDungChiTiet,
        yeucauchitiet.DonGiaDoanhThu as dongia,
        count(NoiDungChiTiet) as soluot, count(NoiDungChiTiet)*yeucauchitiet.DonGiaDoanhThu as tongdoanhthu
        FROM CLSYeuCau as yeucau
        INNER JOIN CLSYeuCauChiTiet as yeucauchitiet
        ON yeucau.CLSYeuCau_Id = yeucauchitiet.CLSYeuCau_Id
        INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_PhongBan as dm_noiyeucau
        ON yeucau.NoiYeuCau_Id = dm_noiyeucau.PhongBan_Id
        INNER JOIN eHospital_NgheAn_Dictionary.dbo.NhanVien as dm_bacsichidinh
        ON yeucau.BacSiChiDinh_Id = dm_bacsichidinh.NhanVien_Id
        INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_PhongBan as dm_noithuchien
        ON yeucau.NoiThucHien_Id = dm_noithuchien.PhongBan_Id
        INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_NhomDichVu as dm_nhomdichvu
        ON yeucau.NhomDichVu_Id = dm_nhomdichvu.NhomDichVu_Id
        WHERE yeucau.ThoiGianYeuCau BETWEEN ? AND ?

        GROUP BY dm_noiyeucau.TenPhongBan, dm_bacsichidinh.TenNhanVien,
        dm_noithuchien.TenPhongBan, dm_nhomdichvu.TenNhomDichVu, NoiDungChiTiet,
        yeucauchitiet.DonGiaDoanhThu

        """
    try:
        rows = cursor.execute(sql, start, end).fetchall()
        for row in rows:
            row.dongia = f'{int(row.dongia):,}'
            row.tongdoanhthu = f'{int(row.tongdoanhthu):,}'
        return rows
    except:
        print("Lỗi query revenue.doctor_department")
        return None
 