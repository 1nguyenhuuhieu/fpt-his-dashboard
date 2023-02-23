# Số trẻ sinh trong ngày
def total_day(day, cursor):
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
        AND NgayThucHien = ?
        """, day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query born.total_day")
        return None


def list(day, cursor):
    query = """
    SELECT ThoiGianKetThuc,SoBenhAn, TenBenhNhan, ICD_SauPhauThuat_MoTa
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
    GROUP BY ThoiGianKetThuc,SoBenhAn, TenBenhNhan, ICD_SauPhauThuat_MoTa
    """
    try:
        q = cursor.execute(query, day).fetchall()
        return q

    except:
        print("Lỗi query born.list")
        return None      