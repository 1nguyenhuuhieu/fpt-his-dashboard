# Chi tiết xác nhận theo tiếp nhận id
def detail(tiepnhan_id, cursor):
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

# SQL query số lượt xác nhận theo loại ngoại trú hoặc nội trú
def visited_hospitalized_day(day, loai, cursor):
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
        print("Lỗi query confirmed.visited_hospitalized_day")
        return None
    

     
# SQL số lượt xác nhận trong ngày
def list(day, cursor):
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
        print("Lỗi query confirmed.list")
        return None

