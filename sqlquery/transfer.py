# Số lượng chuyển viện trong ngày
def total_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(ChuyenVien_Id),0)
        FROM dbo.ChuyenVien
        WHERE NgayChuyen=?
        """,day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query transfer.total_day")
        return None
