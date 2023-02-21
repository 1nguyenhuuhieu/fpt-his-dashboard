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
            MaYTe,
            XacNhanChiPhi.Loai,
            SUM(SoLuong*DonGiaDoanhThu) as 'doanhthu',
            SUM(SoLuong*DonGiaThanhToan) as 'thanhtoan',
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].TenNhanVien
            FROM
            (XacNhanChiPhi
            INNER JOIN
            XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id)

            INNER JOIN

            ([eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            INNER JOIN
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping]
            ON [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping].NhanVien_Id)

            ON XacNhanChiPhi.NguoiTao_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping].User_Id

            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id = XacNhanChiPhi.BenhNhan_Id

            WHERE XacNhanChiPhi.NgayXacNhan = ?

            GROUP BY
            XacNhanChiPhi.BenhNhan_Id,
            MaYTe,
            XacNhanChiPhi.NgayTao, XacNhanChiPhi.Loai,
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].TenNhanVien,
            XacNhanChiPhi.SoXacNhan
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query confirmed.list")
        return None

# SQL số lượt xác nhận trong ngày
def staff_money(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            SUM(SoLuong*DonGiaDoanhThu) as 'doanhthu',
            SUM(SoLuong*DonGiaThanhToan) as 'thanhtoan',
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].TenNhanVien
            FROM
            (XacNhanChiPhi
            INNER JOIN
            XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id)

            INNER JOIN

            ([eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            INNER JOIN
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping]
            ON [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping].NhanVien_Id)

            ON XacNhanChiPhi.NguoiTao_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping].User_Id

            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id = XacNhanChiPhi.BenhNhan_Id

            WHERE XacNhanChiPhi.NgayXacNhan = ?

            GROUP BY
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].TenNhanVien

            ORDER BY doanhthu DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query confirmed.staff_money")
        return None

# SQL số lượt xác nhận trong ngày
def staff_confirmed(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].TenNhanVien,
            COUNT(XacNhanChiPhi.XacNhanChiPhi_Id) as 'confirmed'
            FROM
            (XacNhanChiPhi
            INNER JOIN
            XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id)

            INNER JOIN

            ([eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
            INNER JOIN
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping]
            ON [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping].NhanVien_Id)

            ON XacNhanChiPhi.NguoiTao_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien_User_Mapping].User_Id

            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id = XacNhanChiPhi.BenhNhan_Id

            WHERE XacNhanChiPhi.NgayXacNhan = ?

            GROUP BY
            [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].TenNhanVien

            ORDER BY confirmed DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query confirmed.staff_confirmed")
        return None



