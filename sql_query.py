from datetime import timedelta, datetime
# Thống kê tiền doanh thu trong 1 ngày



def doanhthu_day(day, cursor):
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
        print('Lỗi query doanhthu_day')
        return None


# Thống kê tiền thanh toán trong 1 ngày
def thanhtoan_day(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(SoLuong*DonGiaThanhToan),0)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE NgayXacNhan=?
            """, day
        ).fetchone()[0]

        return int(q)
    except:
        print('Lỗi query thanhtoan_day')
        return None


# Bệnh nhân đang nội trú trong ngày
def total_in_hospital_day(day, cursor):
    tomorrow = day + timedelta(days=1)
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM dbo.BenhAn
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        """,day, tomorrow
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query total_in_hospital_day")
        return None

# Bệnh nhân đang nội trú ra viện trong ngày
def total_out_hospital_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM dbo.BenhAn
        WHERE NgayRaVien = ?
        """,day
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query total_in_hospital_day")
        return None


# Số lượt tiếp nhận trong ngày
def visited_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(KhamBenh_Id),0)
        FROM dbo.KhamBenh
        WHERE NgayKham=?;
        """,day
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query visited_day")
        return None

# Số lượng nhập viện trong ngày
def in_hospital_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM dbo.BenhAn
        WHERE NgayVaoVien=? 
        """,day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query in_hospital_day")
        return None

# Số lượng chuyển viện trong ngày
def transfer_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(ChuyenVien_Id),0)
        FROM dbo.ChuyenVien
        WHERE NgayChuyen=?
        """,day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer_day")
        return None

# Số ca phẫu thuật trong ngày
def surgecies_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAnPhauThuat_Id),0)
        FROM dbo.BenhAnPhauThuat
        WHERE NgayThucHien=?
        """,day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query surgecies_day")
        return None

# Số trẻ sinh trong ngày
def born_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COUNT(BenhAnPhauThuat_Id)
        FROM dbo.BenhAnPhauThuat
        WHERE CanThiepPhauThuat IN
        (N'Đỡ đẻ thường ngôi chỏm;',
        N'Phẫu thuật lấy thai lần đầu;',
        N'Phẫu thuật lấy thai lần hai trở lên;',
        N'Đỡ đẻ từ sinh đôi trở lên;',
        N'Đỡ đẻ ngôi ngược (*);',
        N'Đỡ đẻ thường ngôi chỏm',
        N'Đỡ đẻ thường ngôi chỏm; bóc rau'
        )
        AND NgayThucHien = ?
        """, day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query born_day")
        return None

# Số lượt khám bệnh theo từng khoa phòng trong ngày
def visited_department_day(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            (CASE
                WHEN TenPhongBan IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongBan IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongBan
            END),
            COALESCE(COUNT(KhamBenh.KhamBenh_Id),0) AS 'TongLuotKham'
            FROM KhamBenh INNER JOIN nhh_department
            ON KhamBenh.PhongBan_Id=nhh_department.PhongBan_Id
            WHERE NgayKham=?
            GROUP BY 
            (CASE
                WHEN TenPhongBan IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongBan IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongBan END)
            ORDER BY TongLuotKham DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query visited_department")
        return None


# Thống kê số lượng bệnh nhân nội trú từng khoa
def in_hostpital_department(day, cursor):
    tomorrow = day + timedelta(days=1)

    try:
        q = cursor.execute(
        """
        SELECT TenPhongBan, COALESCE(COUNT(BenhAn.BenhAn_Id),0) AS 'count'
        FROM nhh_department
        INNER JOIN BenhAn
        ON BenhAn.KhoaVao_Id = nhh_department.PhongBan_Id
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        GROUP BY TenPhongBan
        ORDER BY count DESC
        """, day, tomorrow
        ).fetchall()

        return q
    except:
        print("Lỗi query in_hostpital_department")
        return None

# Thống kê số lượng bệnh nhân nhập viện nội trú từng khoa trong ngày
def in_hostpital_department_in_day(day, cursor):
    try:
        q = cursor.execute(
        """
        SELECT TenPhongBan, COALESCE(COUNT(BenhAn.BenhAn_Id),0) AS 'count'
        FROM [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
        INNER JOIN BenhAn
        ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
        WHERE NgayVaoVien = ?
        GROUP BY TenPhongBan
        ORDER BY count DESC
        """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query in_hostpital_department_in_day")
        return None


# SQL query thống kê số lượt khám từ ngày start tới ngày end
def visited_betweenday(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT TOP 30 NgayKham,
            COUNT(KhamBenh_Id)
            FROM KhamBenh
            WHERE NgayKham BETWEEN ? AND ?
            GROUP BY NgayKham
            ORDER BY NgayKham DESC
            """, startday, endday
        ).fetchall()

        return q
    except:
        print("Lỗi query visited_betweenday")
        return None


# SQL query tổng doanh thu trong khoảng ngày
def doanhthu_betweenday(startday, endday, cursor):
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
        print("Lỗi query doanhthu_betweenday")
        return None

# SQL query tổng doanh thu ngoại trú, nội trú trong ngày
def doanhthu_loai_day(day,loai,cursor):
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
        print("Lỗi query doanhthu_visited_day")
        return None

# SQL Query thống kê doanh thu trong ngày dựa theo từng loại
def doanhthu_dichvu_duoc_day(day, cursor):
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
        return None


# SQL query tổng tiền trong khoảng ngày
def total_money_between(startday, endday, cursor):
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
        print("Lỗi query total_money_between")
        return None
    

# SQL query tổng tiền trong khoảng ngày fast dựa trên bảng nhh_revennue từ ngày 2023-02-01 trở về trước 
def total_money_between_union(startday, endday, cursor):
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
        print("Lỗi query total_money_between")
        return None
    
# Tổng doanh thu trong khoảng ngày + với giá trị tính trước
def total_money_between_year(startday, endday, cursor):
    total_money_after = int(383950334280.523000)
    break_day = '2023-02-01'
    break_day = datetime.strptime(break_day, '%Y-%m-%d')


# SQL query tổng doanh thu ngoại trú, nội trú trong khoảng ngày
def doanhthu_loai_between(startday, endday , loai, cursor):
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
        print("Lỗi query doanhthu_visited_day")
        return None

# SQL query tổng doanh thu ngoại trú trong khoảng ngày union với bảng nhh_revennue_visited từ ngày 2023/02/01 trở về trước
def doanhthu_visited_between_union(startday, endday, cursor):
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
        print("Lỗi query doanhthu_visited_between")
        return None


# SQL query tổng doanh thu nội trú trong khoảng ngày union với bảng nhh_revennue_visited từ ngày 2023/02/01 trở về trước
def doanhthu_hospitalized_between_union(startday, endday, cursor):
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
        print("Lỗi query doanhthu_hospitalized_between")
        return None

# SQL query trung bình doanh thu mỗi ngày trong khoảng ngày
def avg_doanhthu_between(startday, endday, cursor):
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
        print("Lỗi query avg_doanhthu_between")
        return None
    
# SQL query trung bình doanh thu mỗi ngày trong khoảng ngày UNION với bảng nhh_revenue
def avg_doanhthu_between_union(startday, endday, cursor):
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
        print("Lỗi query avg_doanhthu_between")
        return None

# SQL query trung bình doanh thu mỗi xác nhận
def avg_doanhthu_confirmed(startday, endday, cursor):
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
        print("Lỗi query avg_doanhthu_confirmed")
        return None

# SQL query trung bình doanh thu mỗi xác nhận trong khoảng ngày UNION với bảng nhh_revenue_confirmed từ ngày 2023-02-01 trở về trước
def avg_doanhthu_confirmed_union(startday, endday, cursor):
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
        print("Lỗi query avg_doanhthu_confirmed")
        return None


# SQl query thống kê doanh thu theo từng khoa phòng
def money_department_day(day, cursor):
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
        print("Lỗi query money_department_day")
        return None
     
# SQl query thống kê doanh thu theo từng khoa phòng trong khoảng ngày
def money_department_betweenday(startday, endday, cursor):
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
        print("Lỗi query money_department_day")
        return None
     
# SQL 5 số lượt xác nhận trong ngày
def recent_confirmed_review(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT TOP 5
            XacNhanChiPhi.SoXacNhan,
            XacNhanChiPhi.NgayTao,
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu',
            COALESCE(SUM(SoLuong*DonGiaThanhToan), 0) as 'tongthanhtoan',
            nhh_staff.TenNhanVien
            FROM XacNhanChiPhiChiTiet
            INNER JOIN
            (XacNhanChiPhi INNER JOIN nhh_staff
            ON XacNhanChiPhi.NguoiTao_Id=nhh_staff.User_Id)
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            GROUP BY
            XacNhanChiPhiChiTiet.XacNhanChiPhi_Id,
            XacNhanChiPhi.NgayTao,
            XacNhanChiPhi.NguoiTao_Id,
            nhh_staff.TenNhanVien,
            XacNhanChiPhi.SoXacNhan
            ORDER BY XacNhanChiPhi.NgayTao DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query confirmed_detail")
        return None

     
# SQL số lượt xác nhận trong ngày
def all_confirmed(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhi.NgayTao,
            XacNhanChiPhi.SoXacNhan,

            BenhNhan_Id,
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu',
            COALESCE(SUM(SoLuong*DonGiaThanhToan), 0) as 'tongthanhtoan',
            XacNhanChiPhi.TenPhongKham,
            nhh_staff.TenNhanVien

            FROM XacNhanChiPhiChiTiet
            INNER JOIN
            (XacNhanChiPhi INNER JOIN nhh_staff
            ON XacNhanChiPhi.NguoiTao_Id=nhh_staff.User_Id)
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            GROUP BY
            XacNhanChiPhiChiTiet.XacNhanChiPhi_Id,
            XacNhanChiPhi.NgayTao,
            XacNhanChiPhi.TenPhongKham,
            XacNhanChiPhi.NguoiTao_Id,
            BenhNhan_Id,
            nhh_staff.TenNhanVien,
            XacNhanChiPhi.SoXacNhan
            ORDER BY XacNhanChiPhi.SoXacNhan DESC

            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query all_confirmed")
        return None


     
# SQL chi tiết xác nhận
def confirmed_detail(soxacnhan_id, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            XacNhanChiPhi.NgayTao,
            XacNhanChiPhi.SoXacNhan,

            BenhNhan_Id,
            COALESCE(SUM(SoLuong*DonGiaDoanhThu), 0) as 'tongdoanhthu',
            COALESCE(SUM(SoLuong*DonGiaThanhToan), 0) as 'tongthanhtoan',
            XacNhanChiPhi.TenPhongKham,
            nhh_staff.TenNhanVien

            FROM XacNhanChiPhiChiTiet
            INNER JOIN
            (XacNhanChiPhi INNER JOIN nhh_staff
            ON XacNhanChiPhi.NguoiTao_Id=nhh_staff.User_Id)
            ON XacNhanChiPhiChiTiet.XacNhanChiPhi_Id=XacNhanChiPhi.XacNhanChiPhi_Id
            WHERE XacNhanChiPhi.SoXacNhan= ?
            GROUP BY
            XacNhanChiPhiChiTiet.XacNhanChiPhi_Id,
            XacNhanChiPhi.NgayTao,
            XacNhanChiPhi.TenPhongKham,
            XacNhanChiPhi.NguoiTao_Id,
            BenhNhan_Id,
            nhh_staff.TenNhanVien,
            XacNhanChiPhi.SoXacNhan

            """, soxacnhan_id
        ).fetchone()

        return q
    except:
        print("Lỗi query confirmed_detail")
        return None

# SQL top 20 hạng mục nhiều doanh thu nhất trong ngày
def top10_doanhthu(day, cursor):
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
        print("Lỗi query top10_doanhthu")
        return None

# SQL query thống kê số lượt nhập viện nội trú trong khoảng ngày
def total_in_hospital_between(startday, endday, cursor):
    query = """
            SELECT
            COALESCE(COUNT(BenhAn_Id), 0)
            FROM BenhAn
            WHERE NgayVaoVien BETWEEN ? AND ?
            """
    try:
        q = cursor.execute(query, startday, endday).fetchone()[0]
        return q
    except:
        print("Lỗi query total_in_hospital_between")
        return None

# SQL query số lượt xác nhận theo loại ngoại trú hoặc nội trú
def confirmed_loai_day(day, loai, cursor):
    try:
        q = cursor.execute(
            """
            SELECT  
            COALESCE(COUNT(TiepNhan.TiepNhan_Id),0)
            FROM TiepNhan
            INNER JOIN XacNhanChiPhi
            ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            AND Loai=?
            """, day, loai
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query confirmed_loai_day")
        return None
    

# SQL query thời gian update mới nhất doanh thu
def last_money_update(cursor):
    q = cursor.execute(
        """
        SELECT TOP 1 NgayTao
        FROM XacNhanChiPhi
        ORDER BY XacNhanChiPhi_Id DESC
        """
    ).fetchone()[0]

    return q

# Thời gian Tiếp nhận mới nhất
def last_receiver(cursor):
    query = """
    SELECT TOP 1 ThoiGianTiepNhan, TiepNhan_Id
    FROM TiepNhan
    ORDER BY TiepNhan_Id DESC
    """
    try:
        q = cursor.execute(query).fetchone()
        return q
    except:
        print("Lỗi query get_last_receiver")
        return None


# Thời gian Xác nhận chi phí mới nhất
def last_confirmer(cursor):
    try:
        query = """
        SELECT TOP 1 ThoiGianXacNhan, TiepNhan_Id
        FROM XacNhanChiPhi
        ORDER BY XacNhanChiPhi_Id DESC
        """
        q = cursor.execute(query).fetchone()
        
        return q
    except:
        print("Lỗi query last_confirmer")
        return None
  

# Chi tiết xác nhận theo tiếp nhận id
def confirmed_detail(tiepnhan_id, cursor):
    print(tiepnhan_id)
    try:
        query = """
        SELECT
        SoTiepNhan, ThoiGianTiepNhan, MaYTe, TenBenhNhan
        FROM TiepNhan
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON TiepNhan.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        WHERE TiepNhan.TiepNhan_Id = ?
        """

        q = cursor.execute(query, tiepnhan_id).fetchone()

        return q
    except:
        print("Lỗi query confirmed_detail")
        return None       
    
# Tổng doanh thu dược trong ngày theo phân nhóm: (DV= Dịch vụ, DU = DƯợc)
def money_phannhom(day, phannhom ,cursor):
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
        print("Lỗi query money_phannhom")
        return 1      

# 5 lượt nhập viện điều trị gần nhất trong ngày
def last_in_hospitalized(day, cursor):
    query = """
            SELECT TOP 5
            ThoiGianVaoKhoa,TenBenhNhan,TenPhongBan
            FROM BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAN.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            WHERE NgayVaoVien = ?
            ORDER BY BenhAn_Id DESC
            """
    try:
        q = cursor.execute(query, day).fetchall()

        return q
    
    except:
        print("Lỗi query last_in_hospitalized")
        return None