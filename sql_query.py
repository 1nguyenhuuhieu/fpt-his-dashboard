from datetime import timedelta, datetime
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

    
 

