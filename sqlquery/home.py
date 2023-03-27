def money(start, end, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            SUM(SoLuong*DonGiaDoanhThu)
            FROM XacNhanChiPhi
            INNER JOIN XacNhanChiPhiChiTiet
            ON XacNhanChiPhi.XacNhanChiPhi_Id=XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
            WHERE ThoiGianXacNhan BETWEEN ? AND ?
            """, start, end
        ).fetchone()[0]
        return int(q)
    except:
        print("Lỗi query home.money")
        return 0
