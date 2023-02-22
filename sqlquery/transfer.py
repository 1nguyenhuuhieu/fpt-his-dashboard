# Số lượng chuyển viện trong ngày
def total_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(ChuyenVien_Id),0)
        FROM dbo.ChuyenVien
        WHERE NgayChuyen=?
        """,day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.total_day")
        return None

# Số lượng chuyển viện từ các khoa nội trú
def total_department_day(day, cursor):
    query = """
    SELECT COALESCE(COUNT(BenhAn.BenhAn_Id), 0) as total
    FROM BenhAn
    WHERE LyDoXuatVien_Id = 546 AND NgayRaVien = ?
    """
    try:
        q = cursor.execute(query, day).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.total_department_day")
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
