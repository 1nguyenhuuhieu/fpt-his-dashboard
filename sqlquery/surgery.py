# Số ca phẫu thuật trong ngày
def total(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAnPhauThuat_Id),0)
        FROM dbo.BenhAnPhauThuat
        WHERE ThoiGianKetThuc BETWEEN ? AND ?
        """,start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query surgery.total")
        return None

# danh sách chi tiết ca phẫu thuật
def list(start, end, cursor):
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
            WHERE BenhAnPhauThuat.ThoiGianKetThuc BETWEEN ? AND ?
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
            WHERE BenhAnPhauThuat.ThoiGianKetThuc BETWEEN ? AND ?
            GROUP BY BenhAnPhauThuat.ThoiGianKetThuc, CanThiepPhauThuat, TenPhongBan, TenLoaiPhauThuat, MaYTe, TenBenhNhan
            """
    try:
        q = cursor.execute(query, start, end, start, end).fetchall()
        for row in q:
            row.time = row.time.strftime("%Y-%m-%d %H:%M")
        return q
    except:
        print("Lỗi query surgery.list")
        return None
