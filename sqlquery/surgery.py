# Số ca phẫu thuật trong ngày
def total_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAnPhauThuat_Id),0)
        FROM dbo.BenhAnPhauThuat
        WHERE NgayThucHien=?
        """,day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query surgery.total_day")
        return None

# danh sách chi tiết ca phẫu thuật
def list(day, cursor):
    query = """
            SELECT BenhAnPhauThuat.ThoiGianKetThuc as time,MaYTe,TenBenhNhan,CanThiepPhauThuat, TenLoaiPhauThuat, TenPhongBan
            FROM BenhAnPhauThuat
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAnPhauThuat.PhongBanThucHien_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_LoaiPhauThuat]
            ON BenhAnPhauThuat.LoaiPhauThuat = [eHospital_NgheAn_Dictionary].[dbo].[DM_LoaiPhauThuat].LoaiPhauThuat
            INNER JOIN BenhAn
            ON BenhAnPhauThuat.BenhAn_Id = BenhAn.BenhAn_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            WHERE BenhAnPhauThuat.NgayThucHien = ?
            GROUP BY BenhAnPhauThuat.ThoiGianKetThuc, CanThiepPhauThuat, TenPhongBan, TenLoaiPhauThuat, MaYTe, TenBenhNhan

            UNION

            SELECT BenhAnPhauThuat.ThoiGianKetThuc as time,MaYTe,TenBenhNhan,CanThiepPhauThuat, TenLoaiPhauThuat, TenPhongBan
            FROM BenhAnPhauThuat
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON BenhAnPhauThuat.PhongBanThucHien_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_LoaiPhauThuat]
            ON BenhAnPhauThuat.LoaiPhauThuat = [eHospital_NgheAn_Dictionary].[dbo].[DM_LoaiPhauThuat].LoaiPhauThuat
            INNER JOIN TiepNhan
            ON BenhAnPhauThuat.TiepNhan_Id = TiepNhan.TiepNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON TiepNhan.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            WHERE BenhAnPhauThuat.NgayThucHien = ?
            GROUP BY BenhAnPhauThuat.ThoiGianKetThuc, CanThiepPhauThuat, TenPhongBan, TenLoaiPhauThuat, MaYTe, TenBenhNhan
            """
    try:
        q = cursor.execute(query, day, day).fetchall()
        for row in q:
            row.time = row.time.strftime("%Y-%m-%d %H:%M")
        return q
    except:
        print("Lỗi query surgery.list")
        return None
