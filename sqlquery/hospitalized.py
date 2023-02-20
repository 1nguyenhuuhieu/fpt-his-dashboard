# Số lượng nhập viện trong khoảng ngày
def in_hospital_betweenday(startday, endday, cursor):
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
        print("Lỗi query in_hospital_betweenday")
        return None
