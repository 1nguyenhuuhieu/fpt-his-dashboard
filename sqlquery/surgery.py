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