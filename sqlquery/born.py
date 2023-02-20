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