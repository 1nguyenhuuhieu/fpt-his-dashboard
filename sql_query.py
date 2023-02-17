from datetime import timedelta
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


# SQL query tổng tiền trong khoảng ngày trước ngày 17/2, dựa trên bảng nhh_revenue_day
def total_money_between_fast(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT COALESCE(SUM(tongdoanhthu),0)
            FROM nhh_revenue_day
            WHERE NgayXacNhan BETWEEN ? AND ?
            """, startday, endday
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query total_money_between")
        return None


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


# SQL query tổng tiền trong ngày fast từ bảng nhh_revenue
def total_money_between_fast(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            COALESCE(SUM(tongdoanhthu), 0) as 'tongdoanhthu'
            FROM nhh_revenue
            WHERE NgayXacNhan BETWEEN ? AND ?
            """, startday, endday
        ).fetchone()[0]

        return int(q)

    except:
        print("Lỗi query total_money_between_fast")
        return None

# SQL query thống kê số lượt nhập viện nội trú theo ngày
def total_in_hospital_between(startday, endday, cursor):
    query = """
            SELECT
            COALESCE(COUNT(BenhAn_Id), 0)
            FROM BenhAn
            WHERE NgayVaoKhoa BETWEEN ? AND ?
            """

    try:
        q = cursor.execute(query, startday, endday).fetchone()[0]
        return q
    except:
        print("Lỗi query total_in_hospital_between")
        return None
       