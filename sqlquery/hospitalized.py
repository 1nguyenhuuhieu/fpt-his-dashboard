from datetime import timedelta, datetime

# Số lượng nhập viện trong ngày
def in_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM BenhAn
        WHERE NgayVaoVien=?
        """, day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query hospitalized.in_day")
        return None

# Số lượng nhập viện trong khoảng ngày
def in_betweenday(startday, endday, cursor):
    query = """
    SELECT
    NgayVaoVien, COALESCE(COUNT(BenhAn_Id),0)
    FROM BenhAn
    WHERE NgayVaoVien BETWEEN ? AND ?
    GROUP BY NgayVaoVien 
    """
    try:
        q = cursor.execute(query, startday, endday).fetchall()
        return q
    except:
        print("Lỗi query hospitalized.in_betweenday")
        return None

# Số lượng bệnh nhân đang nội trú trong ngày
def total_day(day, cursor):
    tomorrow = day + timedelta(days=1)
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(BenhAn_Id),0)
        FROM dbo.BenhAn
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        """,day, tomorrow
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query hospitalized.total_day")
        return None

# Số lượng bệnh nhân nội trú từng khoa
def total_department(day, cursor):
    tomorrow = day + timedelta(days=1)

    try:
        q = cursor.execute(
        """
        SELECT TenPhongBan, COALESCE(COUNT(BenhAn.BenhAn_Id),0) AS 'count'
        FROM nhh_department
        INNER JOIN BenhAn
        ON BenhAn.KhoaVao_Id = nhh_department.PhongBan_Id
        WHERE (NgayRaVien IS NULL
        OR NgayRaVien > ?)
        AND NgayVaoVien < ?
        GROUP BY TenPhongBan
        ORDER BY count DESC
        """, day, tomorrow
        ).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.total_department")
        return None
