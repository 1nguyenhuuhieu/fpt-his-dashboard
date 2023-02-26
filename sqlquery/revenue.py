# Thống kê tiền doanh thu trong 1 ngày
def total_day(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(SoLuong*DonGiaDoanhThu),0)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE NgayXacNhan=?
            """, day
        ).fetchone()[0]

        return int(q)
    except:
        print('Lỗi query total_day')
        return 0

# Tổng doanh thu dược trong ngày theo phân nhóm: (DV= Dịch vụ, DU = DƯợc)
def service_medicine_day(day, phannhom ,cursor):
    query = """
    SELECT 
    COALESCE(SUM(SoLuong*DonGiaDoanhThu),0) AS 'TongDoanhThu'
    FROM XacNhanChiPhi
    INNER JOIN (XacNhanChiPhiChiTiet INNER JOIN VienPhiNoiTru_Loai_IDRef ON XacNhanChiPhiChiTiet.Loai_IDRef=VienPhiNoiTru_Loai_IDRef.Loai_IDRef)
    ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    WHERE NgayXacNhan = ? AND PhanNhom=?
    GROUP BY PhanNhom
    """
    try:
        q = cursor.execute(query, day, phannhom).fetchone()[0]
        return int(q)
    except:
        print("Lỗi query service_medicine_day")
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
def day_department_betweenday(startday, endday, cursor):
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

            WHERE NgayXacNhan BETWEEN ? AND ?
            GROUP BY 
            (CASE
                WHEN TenPhongKham IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongKham IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongKham END)
            ORDER BY TongDoanhThu
            """, startday, endday
        ).fetchall()

        return q
    except:
        print("Lỗi query revenue.day_department_betweenday")
        return 0

# SQL query tổng doanh thu ngoại trú, nội trú trong ngày
def visited_hospitalized_day(day,loai,cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0)
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            WHERE NgayXacNhan=? AND XacNhanChiPhiChiTiet.Loai=?
            """, day, loai
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query revenue.visited_hospitalized_day")
        return 0


# SQL Query thống kê doanh thu trong ngày dựa theo từng ten phan nhom
def tenphanhom_service_medicine_day(day, cursor):
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
            WHERE NgayXacNhan = ?
            GROUP BY TenPhanNhom
            ORDER BY TongDoanhThu   
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query doanhthu_dichvu_duoc_day")
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
            WHERE NgayXacNhan BETWEEN ? AND ?
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
            WHERE NgayXacNhan BETWEEN ? AND ?
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


# SQL top 10 khoa phòng nhiều doanh thu nhất trong ngày
def services(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhiChiTiet.NoiDung,
            Loai_IDRef_Name,
            XacNhanChiPhi.TenPhongKham,
            COALESCE(COUNT(XacNhanChiPhiChiTiet_Id),0) as 'count',
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi 
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            INNER JOIN VienPhiNoiTru_Loai_IDRef
            ON XacNhanChiPhiChiTiet.Loai_IDRef = VienPhiNoiTru_Loai_IDRef.Loai_IDRef
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            GROUP BY
            XacNhanChiPhiChiTiet.NoiDung,
            Loai_IDRef_Name,
            XacNhanChiPhi.TenPhongKham

            ORDER BY tongdoanhthu DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query revenue.top_service")
        return 0


def services_type(day,type, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhiChiTiet.NoiDung,
            Loai_IDRef_Name,
            XacNhanChiPhi.TenPhongKham,
            COALESCE(COUNT(XacNhanChiPhiChiTiet_Id),0) as 'count',
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu'
            FROM XacNhanChiPhiChiTiet
            INNER JOIN XacNhanChiPhi 
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            INNER JOIN VienPhiNoiTru_Loai_IDRef
            ON XacNhanChiPhiChiTiet.Loai_IDRef = VienPhiNoiTru_Loai_IDRef.Loai_IDRef
            WHERE XacNhanChiPhi.NgayXacNhan = ? AND PhanNhom = ?
            GROUP BY
            XacNhanChiPhiChiTiet.NoiDung,
            Loai_IDRef_Name,
            XacNhanChiPhi.TenPhongKham

            ORDER BY tongdoanhthu DESC
            """, day, type
        ).fetchall()

        return q
    except:
        print("Lỗi query revenue.top_service")
        return 0
