from datetime import timedelta, datetime

# Số lượng nhập viện trong ngày
def in_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM BenhAn
        WHERE NgayVaoVien=?
        """, day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query hospitalized.in_day")
        return None

# Số lượng nhập viện trong khoảng ngày
def in_betweenday(startday, endday, cursor):
    query = """
    SELECT
    NgayVaoVien, COALESCE(COUNT(BenhAn_Id),0)
    FROM BenhAn
    WHERE NgayVaoVien BETWEEN ? AND ?
    GROUP BY NgayVaoVien 
    """
    try:
        q = cursor.execute(query, startday, endday).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.in_betweenday")
        return None

# Số lượng bệnh nhân đang nội trú trong ngày
def total_day(day, cursor):
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
        print("Lỗi query hospitalized.total_day")
        return None

# Số lượng bệnh nhân nội trú từng khoa
def total_department(day, cursor):
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
        print("Lỗi query hospitalized.total_department")
        return None

# Bệnh nhân đang nội trú ra viện trong ngày
def out_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM dbo.BenhAn
        WHERE NgayRaVien = ?
        """,day
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query hospitalized.out_day")
        return None

# Thống kê số lượng bệnh nhân nhập viện nội trú từng khoa trong ngày
def in_department_day(day, cursor):
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
        print("Lỗi query hospitalized.in_department_day")
        return None


# SQL query thống kê số lượt nhập viện nội trú trong khoảng ngày
def total_in_between(startday, endday, cursor):
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
    


# Chi tiết bệnh nhân nhập viện nội trú trong ngày
def new_list(day, cursor):
    query = """
            SELECT
            ThoiGianVaoKhoa, SoBenhAn, MaYTe,ChanDoanVaoKhoa, TenPhongBan, TenNhanVien
            FROM BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            ON BenhAn.NguoiLap_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
            WHERE NgayVaoVien = ?
            GROUP BY ThoiGianVaoKhoa, SoBenhAn, MaYTe,ChanDoanVaoKhoa, TenPhongBan, TenNhanVien

            UNION

            SELECT
            ThoiGianVaoKhoa, SoBenhAn, MaYTe,ChanDoanVaoKhoa, TenPhongBan, TenBenhNhan
            FROM BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            WHERE NgayVaoVien = ? AND NguoiLap_Id IS NULL
            GROUP BY ThoiGianVaoKhoa, SoBenhAn, MaYTe,ChanDoanVaoKhoa, TenPhongBan, TenBenhNhan

            """
    try:
        q = cursor.execute(query, day, day).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.new_list")
        return None
    

# Chi tiết bệnh nhân ra viênj nội trú trong ngày
def out_list(day, cursor):
    query = """
            SELECT
            ThoiGianRaVien, SoBenhAn, MaYTe,ChanDoanVaoKhoa, ChanDoanRaVien, Dictionary_Name ,TenPhongBan
            FROM BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            ON BenhAn.NguoiLap_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary]
            ON LyDoXuatVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Id
            WHERE NgayRaVien = ?
            GROUP BY ThoiGianRaVien, SoBenhAn, MaYTe,ChanDoanRaVien, TenPhongBan, ChanDoanVaoKhoa, Dictionary_Name
            """
    try:
        q = cursor.execute(query, day).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.out_list")
        return None


# Bệnh nhân đang nội trú ra viện trong ngày theo khoa
def out_department_day(day, cursor):
    query = """
            SELECT
            TenPhongBan,
            COALESCE(COUNT(BenhAn_Id),0) as total
            FROM dbo.BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaRa_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            WHERE NgayRaVien = ?
            GROUP BY TenPhongBan
            ORDER BY total DESC
            """
    try:
        q = cursor.execute(query, day).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.out_department_day")
        return None
