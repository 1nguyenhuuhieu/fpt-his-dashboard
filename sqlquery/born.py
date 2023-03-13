# Số trẻ sinh trong ngày
def total(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COUNT(BenhAnPhauThuat_Id)
        FROM dbo.BenhAnPhauThuat
        WHERE CanThiepPhauThuat IN
        (N'Đỡ đẻ thường ngôi chỏm;',
        N'Phẫu thuật lấy thai lần đầu;',
        N'Phẫu thuật lấy thai lần hai trở lên;',
        N'Đỡ đẻ từ sinh đôi trở lên;',
        N'Đỡ đẻ ngôi ngược (*);',
        N'Đỡ đẻ thường ngôi chỏm',
        N'Đỡ đẻ thường ngôi chỏm; bóc rau'
        )
        AND ThoiGianKetThuc BETWEEN ? AND ?
        """, start, end
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query born.total")
        return None


def list(day, cursor):
    query = """
    SELECT ThoiGianKetThuc,MaYTe, TenBenhNhan,CanThiepPhauThuat, ICD_SauPhauThuat_MoTa
    FROM dbo.BenhAnPhauThuat
    INNER JOIN BenhAn
    ON BenhAnPhauThuat.BenhAn_Id = BenhAn.BenhAn_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
    ON BenhAn.BenhNhan_Id = benhnhan.BenhNhan_Id
    WHERE CanThiepPhauThuat IN
    (N'Đỡ đẻ thường ngôi chỏm;',
    N'Phẫu thuật lấy thai lần đầu;',
    N'Phẫu thuật lấy thai lần hai trở lên;',
    N'Đỡ đẻ từ sinh đôi trở lên;',
    N'Đỡ đẻ ngôi ngược (*);',
    N'Đỡ đẻ thường ngôi chỏm',
    N'Đỡ đẻ thường ngôi chỏm; bóc rau'
    )
    AND NgayThucHien = ?
    GROUP BY ThoiGianKetThuc,MaYTe, TenBenhNhan, CanThiepPhauThuat,ICD_SauPhauThuat_MoTa
    """
    try:
        q = cursor.execute(query, day).fetchall()
        for row in q:
            row.ThoiGianKetThuc = row.ThoiGianKetThuc.strftime('%Y/%m/%d %H:%M')
        return q

    except:
        print("Lỗi query born.list")
        return None      
    
def list_between(startday,endday, cursor):
    query = """
    SELECT ThoiGianKetThuc,MaYTe, TenBenhNhan,CanThiepPhauThuat, ICD_SauPhauThuat_MoTa
    FROM dbo.BenhAnPhauThuat
    INNER JOIN BenhAn
    ON BenhAnPhauThuat.BenhAn_Id = BenhAn.BenhAn_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
    ON BenhAn.BenhNhan_Id = benhnhan.BenhNhan_Id
    WHERE CanThiepPhauThuat IN
    (N'Đỡ đẻ thường ngôi chỏm;',
    N'Phẫu thuật lấy thai lần đầu;',
    N'Phẫu thuật lấy thai lần hai trở lên;',
    N'Đỡ đẻ từ sinh đôi trở lên;',
    N'Đỡ đẻ ngôi ngược (*);',
    N'Đỡ đẻ thường ngôi chỏm',
    N'Đỡ đẻ thường ngôi chỏm; bóc rau'
    )
    AND NgayThucHien BETWEEN ? AND ?
    GROUP BY ThoiGianKetThuc,MaYTe, TenBenhNhan, CanThiepPhauThuat,ICD_SauPhauThuat_MoTa
    """
    try:
        q = cursor.execute(query, startday, endday).fetchall()
        for row in q:
            row.ThoiGianKetThuc = row.ThoiGianKetThuc.strftime('%Y/%m/%d %H:%M')
        return q

    except:
        print("Lỗi query born.list")
        return None      