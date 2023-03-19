from datetime import timedelta

# Số lượng nhập viện trong khoảng thời gian
def new_in(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM BenhAn
        WHERE ThoiGianVaoVien BETWEEN ? AND ?
        """, start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query hospitalized.in_day")
        return None

# Số lượng nhập viện trong khoảng thời gian group by ngay
def new_in_between(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        NgayVaoVien,
        COALESCE(COUNT(BenhAn_Id),0)
        FROM BenhAn
        WHERE ThoiGianVaoVien BETWEEN ? AND ?
        GROUP BY NgayVaoVien
        """, start, end
        ).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.new_in_between")
        return None


# AVG Số lượng nhập viện trong khoảng thời gian
def avg_betweentime(start, end, cursor):
    query = """
    SELECT AVG(asset_count)
    FROM
    (SELECT COUNT(BenhAn_Id) as asset_count
    FROM BenhAn
    WHERE ThoiGianVaoVien BETWEEN ? AND ?
    GROUP BY NgayVaoVien) as inner_query
    """
    try:
        q = cursor.execute(query, start, end).fetchone()[0]
        return q
    except:
        print("Lỗi query hospitalized.in_betweentime")
        return None
    
# MAX Số lượng nhập viện trong khoảng thời gian
def max_betweentime(start, end, cursor):
    query = """
    SELECT MAX(asset_count)
    FROM
    (SELECT COUNT(BenhAn_Id) as asset_count
    FROM BenhAn
    WHERE ThoiGianVaoVien BETWEEN ? AND ?
    GROUP BY NgayVaoVien) as inner_query
    """
    try:
        q = cursor.execute(query, start, end).fetchone()[0]
        return q
    except:
        print("Lỗi query hospitalized.max_betweentime")
        return None
    
# MIN Số lượng nhập viện trong khoảng thời gian
def min_betweentime(start, end, cursor):
    query = """
    SELECT MIN(asset_count)
    FROM
    (SELECT COUNT(BenhAn_Id) as asset_count
    FROM BenhAn
    WHERE ThoiGianVaoVien BETWEEN ? AND ?
    GROUP BY NgayVaoVien) as inner_query
    """
    try:
        q = cursor.execute(query, start, end).fetchone()[0]
        return q
    except:
        print("Lỗi query hospitalized.min_betweentime")
        return None

# Số lượng bệnh nhân đang nội trú trong ngày
def total(day, cursor):
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
        print("Lỗi query hospitalized.total")
        return None

# Số lượng bệnh nhân nội trú từng khoa
def total_department(day, cursor):
    tomorrow = day + timedelta(days=1)

    try:
        q = cursor.execute(
        """
        SELECT
        TenPhongBan,
        COALESCE(COUNT(BenhAn_Id),0) as 'total'
        FROM dbo.BenhAn
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
        ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        GROUP BY TenPhongBan
        ORDER BY TenPhongBan

        """, day, tomorrow
        ).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.total_department")
        return None
    
# Số lượng bệnh nhân nội trú từng khoa sort by total
def total_department_sort_total(day, cursor):
    tomorrow = day + timedelta(days=1)

    try:
        q = cursor.execute(
        """
        SELECT
        TenPhongBan,
        COALESCE(COUNT(BenhAn_Id),0) as 'total'
        FROM dbo.BenhAn
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
        ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        GROUP BY TenPhongBan
        ORDER BY total DESC

        """, day, tomorrow
        ).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.total_department_sort_total")
        return None
# Số lượng bệnh nhân nội trú tại khoa
def bed_department(day,department_id, cursor):
    tomorrow = day + timedelta(days=1)

    try:
        q = cursor.execute(
        """
        SELECT COALESCE(COUNT(BenhAn.BenhAn_Id),0) AS 'count'
        FROM nhh_department
        INNER JOIN BenhAn
        ON BenhAn.KhoaVao_Id = nhh_department.PhongBan_Id
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        AND BenhAn.KhoaVao_Id = ?
        """, day, tomorrow, department_id
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query hospitalized.bed_department")
        return None
    

# Số lượng bệnh nhân nội trú từng khoa
def total_department_id(day, cursor):
    tomorrow = day + timedelta(days=1)

    try:
        q = cursor.execute(
        """
        SELECT TenPhongBan, COALESCE(COUNT(BenhAn.BenhAn_Id),0) AS 'count', BenhAn.KhoaVao_Id
        FROM nhh_department
        INNER JOIN BenhAn
        ON BenhAn.KhoaVao_Id = nhh_department.PhongBan_Id
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        GROUP BY TenPhongBan,BenhAn.KhoaVao_Id
        ORDER BY count DESC
        """, day, tomorrow
        ).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.total_department")
        return None


# Bệnh nhân đang nội trú ra viện trong ngày
def old_out(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM dbo.BenhAn
        WHERE ThoiGianRaVien BETWEEN ? AND ?
        """,start, end
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query hospitalized.old_out")
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
    
# SQL query thống kê số lượt nhập viện nội trú trong khoảng ngày group by department
def total_in_department(start, end, cursor):
    query = """
            SELECT
            TenPhongBan as name,
            COALESCE(COUNT(BenhAn_Id),0) as total
            FROM dbo.BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            WHERE ThoiGianVaoVien BETWEEN ? AND ?
            GROUP BY TenPhongBan
            ORDER BY total DESC
            """
    try:
        q = cursor.execute(query, start, end).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.total_in_department")
        return None
    

# Chi tiết bệnh nhân nhập viện nội trú trong ngày
# used for: new_patients
def new_list(start, end, cursor):
    query = """
            SELECT
            ThoiGianVaoKhoa,MaYTe, SoBenhAn, TenBenhNhan,ChanDoanVaoKhoa, TenPhongBan, TenNhanVien
            FROM BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            ON BenhAn.NguoiLap_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
            WHERE ThoiGianVaoVien BETWEEN ? AND ?
            GROUP BY ThoiGianVaoKhoa, SoBenhAn, MaYTe,ChanDoanVaoKhoa, TenPhongBan, TenNhanVien, TenBenhNhan

            """
    try:
        q = cursor.execute(query, start, end).fetchall()
        for row in q:
            row.ThoiGianVaoKhoa = row.ThoiGianVaoKhoa.strftime("%Y/%m/%d %H:%M")

        return q
    except:
        print("Lỗi query hospitalized.new_list")
        return None
    

# Chi tiết bệnh nhân ra viênj nội trú trong ngày
def out_list(start, end, cursor):
    query = """
            SELECT
            ThoiGianRaVien,MaYTe, SoBenhAn,  ChanDoanRaVien, Dictionary_Name ,TenNhanVien,TenPhongBan
            FROM BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary]
            ON LyDoXuatVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Id
            WHERE ThoiGianRaVien BETWEEN ? AND ?
            GROUP BY ThoiGianRaVien, SoBenhAn, MaYTe,ChanDoanRaVien, TenPhongBan, TenNhanVien, Dictionary_Name
            """
    try:
        q = cursor.execute(query, start, end).fetchall()

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


def patients(day,cursor):
    tomorrow = day + timedelta(days=1)
    query = """
        SELECT
        ThoiGianVaoKhoa,MaYTe, SoBenhAn, TenBenhNhan,ChanDoanRaVien, TenNhanVien, TenPhongBan
        FROM BenhAn
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
        ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
        ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
        WHERE (NgayRaVien IS NULL
                OR NgayRaVien > ?)
                AND NgayVaoVien < ?
        GROUP BY ThoiGianVaoKhoa, SoBenhAn, MaYTe,ChanDoanRaVien, TenPhongBan, TenNhanVien,TenBenhNhan

        """
    try:
        q = cursor.execute(query, day, tomorrow).fetchall()
        for row in q:
            row.ThoiGianVaoKhoa = row.ThoiGianVaoKhoa.strftime("%Y-%m-%d %H:%M")

        return q
    except:
        print("Lỗi query hospitalized.patients")
        return None


# 5 lượt nhập viện điều trị gần nhất trong ngày
def last5(day, cursor):
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
        print("Lỗi query last5")
        return None
    
# Danh sách bệnh nhân nội trú theo khoa
def list_department(day, department_id, cursor):
    tomorrow = day + timedelta(days=1)
    query = """
        SELECT ThoiGianVaoVien, MaYTe, TenBenhNhan, ChanDoanVaoKhoa,TenNhanVien
        FROM BenhAn
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
        ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
        WHERE (BenhAn.NgayRaVien IS NULL OR BenhAn.NgayRaVien > ?)
                AND BenhAn.NgayVaoVien < ?
        
        AND BenhAn.KhoaVao_Id = ?
        GROUP BY ThoiGianVaoVien, MaYTe, TenBenhNhan, ChanDoanVaoKhoa,TenNhanVien
        """
    try:
        q = cursor.execute(query, day,tomorrow, department_id).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.list_department")
        return None
    
# Danh sách bệnh nhân nội trú theo khoa
def patiens_department(day, department_name, cursor):
    tomorrow = day + timedelta(days=1)
    query = """
        SELECT ThoiGianVaoVien, MaYTe, TenBenhNhan,MaGiuong, ChanDoanVaoKhoa,TenNhanVien
        FROM BenhAn
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
        ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan] as dm_phongban
        ON BenhAn.KhoaVao_Id = dm_phongban.PhongBan_Id
        WHERE (BenhAn.NgayRaVien IS NULL OR BenhAn.NgayRaVien > ?)
                AND BenhAn.NgayVaoVien < ?
                
        AND dm_phongban.TenPhongBan= ?
        GROUP BY ThoiGianVaoVien, MaYTe, TenBenhNhan, ChanDoanVaoKhoa,TenNhanVien, MaGiuong
        """
    try:
        q = cursor.execute(query, day,tomorrow, department_name).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.patiens_department")
        return None
    
# Danh sách bệnh nhân nội trú nhập mới theo khoa
def patiens_department_new(day, department_name, cursor):
    query = """
        SELECT ThoiGianVaoVien, MaYTe, TenBenhNhan, ChanDoanVaoKhoa,TenNhanVien
        FROM BenhAn
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
        ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan] as dm_phongban
        ON BenhAn.KhoaVao_Id = dm_phongban.PhongBan_Id
        WHERE (BenhAn.NgayVaoVien = ?)
                
        AND dm_phongban.TenPhongBan= ?
        GROUP BY ThoiGianVaoVien, MaYTe, TenBenhNhan, ChanDoanVaoKhoa,TenNhanVien
        """
    try:
        q = cursor.execute(query, day, department_name).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.patiens_department")
        return None
    
# danh sách bệnh án
def medical_record_notin(department_id,archived_list,cursor):
    if len(archived_list) > 1:
        archived = tuple(archived_list)
        sql = f"""SELECT NgayRaVien, benhnhan.MaYTe,SoBenhAn, SoLuuTru, benhnhan.TenBenhNhan
        FROM BenhAn
        INNER JOIN  [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
        ON BenhAn.BenhNhan_Id = benhnhan.BenhNhan_Id
        WHERE BenhAn.KhoaVao_Id = ? AND ThoiGianVaoKhoa > '2023-01-01'
        AND ThoiGianRaVien IS NOT NULL
        AND SoLuuTru NOT IN{archived}"""
        try:
            q = cursor.execute(sql,department_id).fetchall()
            return q
        except:
            print("Lỗi query hospitalized.medical_record_notin")
            return None
    else:
        archived = archived_list[0]
        sql = f"""SELECT NgayRaVien, benhnhan.MaYTe,SoBenhAn, SoLuuTru, benhnhan.TenBenhNhan
        FROM BenhAn
        INNER JOIN  [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
        ON BenhAn.BenhNhan_Id = benhnhan.BenhNhan_Id
        WHERE BenhAn.KhoaVao_Id = ? AND ThoiGianVaoKhoa > '2023-01-01'
        AND ThoiGianRaVien IS NOT NULL
        AND SoLuuTru <> '{archived}'"""
        try:
            q = cursor.execute(sql,department_id).fetchall()
            return q
        except:
            print("Lỗi query hospitalized.medical_record_notin")
            return None
        
# danh sách bệnh án
def medical_record(department_id,cursor):
   
    sql = f"""SELECT NgayRaVien, benhnhan.MaYTe,SoBenhAn, SoLuuTru, benhnhan.TenBenhNhan
    FROM BenhAn
    INNER JOIN  [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
    ON BenhAn.BenhNhan_Id = benhnhan.BenhNhan_Id
    WHERE BenhAn.KhoaVao_Id = ? AND ThoiGianVaoKhoa > '2023-01-01'
    AND ThoiGianRaVien IS NOT NULL
    """
    try:
        q = cursor.execute(sql,department_id).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.medical_record")
        return None
    
# danh sách bệnh án với số lưu trữ đã nạp ở phòng kế hoạch
def medical_record_archived(department_id, cursor):
    sql = """
    SELECT soluutru
    FROM archived
    WHERE department_id = ?
    """
    try:
        q = cursor.execute(sql,(department_id,)).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.medical_record_archived")
        return None
        