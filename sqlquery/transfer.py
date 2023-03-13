# Số lượng chuyển viện trong ngày
def total(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(ChuyenVien_Id),0)
        FROM dbo.ChuyenVien
        WHERE NgayTao BETWEEN ? AND ?
        """,start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.total_day")
        return None

# Số lượng chuyển viện từ các khoa nội trú
def total_department(start, end, cursor):
    query = """
    SELECT COALESCE(COUNT(BenhAn.BenhAn_Id), 0) as total
    FROM BenhAn
    WHERE LyDoXuatVien_Id = 546 AND ThoiGianRaVien BETWEEN ? AND ?
    """
    try:
        q = cursor.execute(query, start, end).fetchone()[0]
        return q
    except:
        print("Lỗi query transfer.total_department")
        return None   
    

# Số lượng chuyển viện trong khoảng time
def total_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(ChuyenVien_Id),0)
        FROM dbo.ChuyenVien
        WHERE NgayTao BETWEEN ? AND ?
        """,start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.total_betweentime")
        return None
    
# AVG chuyển viện trong khoảng time
def avg_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""
        SELECT AVG(asset_count)
        FROM
        (SELECT
        COALESCE(COUNT(ChuyenVien_Id),0) as asset_count
        FROM dbo.ChuyenVien
        WHERE NgayTao BETWEEN ? AND ?
        GROUP BY NgayChuyen) as inner_query
        """,start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.avg_betweentime")
        return None
    
# max_betweentime chuyển viện trong khoảng time
def max_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""
        SELECT MAX(asset_count)
        FROM
        (SELECT
        COALESCE(COUNT(ChuyenVien_Id),0) as asset_count
        FROM dbo.ChuyenVien
        WHERE NgayTao BETWEEN ? AND ?
        GROUP BY NgayChuyen) as inner_query
        """,start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.max_betweentime")
        return None
    
# min_betweentime chuyển viện trong khoảng time
def min_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""
        SELECT MIN(asset_count)
        FROM
        (SELECT
        COALESCE(COUNT(ChuyenVien_Id),0) as asset_count
        FROM dbo.ChuyenVien
        WHERE NgayTao BETWEEN ? AND ?
        GROUP BY NgayChuyen) as inner_query
        """,start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.min_betweentime")
        return None

    

# Số lượng chuyển viện từ các khoa nội trú trong khoảng time
def total_department_betweentime(start, end, cursor):
    query = """
    SELECT COALESCE(COUNT(BenhAn.BenhAn_Id), 0) as total
    FROM BenhAn
    WHERE LyDoXuatVien_Id = 546 AND ThoiGianRaVien BETWEEN ? AND ?
    """
    try:
        q = cursor.execute(query, start,end).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.total_department_day")
        return None 
          
# avg chuyển viện từ các khoa nội trú trong khoảng time
def avg_department_betweentime(start, end, cursor):
    query = """
    SELECT AVG(asset_count)
    FROM
    (SELECT
    COALESCE(COUNT(ChuyenVien_Id),0) as asset_count
    FROM BenhAn
    WHERE  LyDoXuatVien_Id = 546 AND ThoiGianRaVien BETWEEN ? AND ?
    GROUP BY NgayRaVien) as inner_query
    """
    try:
        q = cursor.execute(query, start,end).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.avg_department_betweentime")
        return None       

# max chuyển viện từ các khoa nội trú trong khoảng time
def max_department_betweentime(start, end, cursor):
    query = """
    SELECT MAX(asset_count)
    FROM
    (SELECT
    COALESCE(COUNT(ChuyenVien_Id),0) as asset_count
    FROM BenhAn
    WHERE  LyDoXuatVien_Id = 546 AND ThoiGianRaVien BETWEEN ? AND ?
    GROUP BY NgayRaVien) as inner_query
    """
    try:
        q = cursor.execute(query, start,end).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.max_department_betweentime")
        return None 
          
# min chuyển viện từ các khoa nội trú trong khoảng time
def min_department_betweentime(start, end, cursor):
    query = """
    SELECT MIN(asset_count)
    FROM
    (SELECT
    COALESCE(COUNT(ChuyenVien_Id),0) as asset_count
    FROM BenhAn
    WHERE  LyDoXuatVien_Id = 546 AND ThoiGianRaVien BETWEEN ? AND ?
    GROUP BY NgayRaVien) as inner_query
    """
    try:
        q = cursor.execute(query, start,end).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.min_department_betweentime")
        return None       



# Danh sách bệnh nhân chuyển viện
def transfer(day, cursor):
    query = """
            SELECT
            ThoiGianRaVien, MaYTe,TenBenhNhan, ChanDoanRaVien,TenNhanVien, TenPhongBan
            FROM BenhAn
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary]
            ON LyDoXuatVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Id
            WHERE NgayRaVien = ? AND Dictionary_Name = N'Chuyển viện'
            GROUP BY ThoiGianRaVien,  MaYTe,ChanDoanRaVien, TenPhongBan, ChanDoanVaoKhoa, TenNhanVien, TenBenhNhan

            UNION

            SELECT ChuyenVien.NgayTao, MaYTe, TenBenhNhan, ChanDoan, TenNhanVien, HuongDieuTri
            FROM ChuyenVien
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON ChuyenVien.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            ON ChuyenVien.BacSiYeuCau_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
            WHERE NgayChuyen = ?
            GROUP BY ChuyenVien.NgayTao, MaYTe, TenBenhNhan, ChanDoan, TenNhanVien, HuongDieuTri

            """
    try:
        q = cursor.execute(query, day, day).fetchall()
        return q
    except:
        print("Lỗi query transfer.transfer")
        return None
