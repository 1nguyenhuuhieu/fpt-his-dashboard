# Số lượt tiếp nhận trong ngày
def total_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(KhamBenh_Id),0)
        FROM dbo.KhamBenh
        WHERE NgayKham=?;
        """,day
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query visited.total_day")
        return None
    
# Số lượt khám bệnh trong khoảng thời gian
def total_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(KhamBenh_Id),0)
        FROM dbo.KhamBenh
        WHERE ThoiGianKham BETWEEN ? AND ?;
        """,start, end
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query visited.total_day")
        return None
    
# Số lượt khám bệnh trung bình trong khoảng thời gian
def avg_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""
        SELECT AVG(asset_count)
        FROM
	(SELECT
	COALESCE(COUNT(KhamBenh_Id),0) AS asset_count
	FROM dbo.KhamBenh
	WHERE ThoiGianKham BETWEEN ? AND ?
	GROUP BY NgayKham) as inner_query

        """,start, end
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query visited.avg_betweentime")
        return None
    
# Số lượt khám bệnh nhiều nhất trong khoảng thời gian
def max_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""
        SELECT MAX(asset_count)
        FROM
	(SELECT
	COALESCE(COUNT(KhamBenh_Id),0) AS asset_count
	FROM dbo.KhamBenh
	WHERE ThoiGianKham BETWEEN ? AND ?
	GROUP BY NgayKham) as inner_query

        """,start, end
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query visited.max_betweentime")
        return None

    
# Số lượt khám bệnh nhiều nhất trong khoảng thời gian
def min_betweentime(start, end, cursor):
    try:
        q = cursor.execute("""
        SELECT MIN(asset_count)
        FROM
	(SELECT
	COALESCE(COUNT(KhamBenh_Id),0) AS asset_count
	FROM dbo.KhamBenh
	WHERE ThoiGianKham BETWEEN ? AND ?
	GROUP BY NgayKham) as inner_query

        """,start, end
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query visited.avg_betweentime")
        return None


# Số lượt khám mỗi ngày từ ngày start tới ngày end lấy 30 ngày
def day_betweenday(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT TOP 30 NgayKham,
            COUNT(KhamBenh_Id)
            FROM KhamBenh
            WHERE NgayKham BETWEEN ? AND ?
            GROUP BY NgayKham
            ORDER BY NgayKham DESC
            """, startday, endday
        ).fetchall()

        return q
    except:
        print("Lỗi query visited.perday_betweenday")
        return None
# Số lượt khám mỗi ngày từ ngày start tới ngày end lấy 30 ngày
def total_betweenday(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT COUNT(KhamBenh_Id)
            FROM KhamBenh
            WHERE NgayKham BETWEEN ? AND ?
            """, startday, endday
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query visited.total_betweenday")
        return None

# Số lượt khám bệnh theo từng khoa phòng trong ngày
def department_day(day, cursor):
    try:
        q = cursor.execute(
            """
            SELECT
            (CASE
                WHEN TenPhongBan IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongBan IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongBan
            END),
            COALESCE(COUNT(KhamBenh.KhamBenh_Id),0) AS 'TongLuotKham'
            FROM KhamBenh INNER JOIN nhh_department
            ON KhamBenh.PhongBan_Id=nhh_department.PhongBan_Id
            WHERE NgayKham=?
            GROUP BY 
            (CASE
                WHEN TenPhongBan IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongBan IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongBan END)
            ORDER BY TongLuotKham DESC
            """, day
        ).fetchall()

        return q
    except:
        print("Lỗi query visited.department_day")
        return None

# Danh sách khám bệnh trong ngày
def patients(day, cursor):
    query = """
    SELECT
    ThoiGianKham, MaYTe, TenBenhNhan, KhamBenh.TiepNhan_Id ,ChanDoanKhoaKham,TenNhanVien, TenPhongBan
    FROM KhamBenh
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
    ON KhamBenh.PhongBan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien
    ON KhamBenh.BacSiKham_Id = [eHospital_NgheAn_Dictionary].[dbo].NhanVien.NhanVien_Id
    WHERE NgayKham = ?
    GROUP BY ThoiGianKham, MaYTe, TenBenhNhan, TenNhanVien, ChanDoanKhoaKham, TenPhongBan, KhamBenh.TiepNhan_Id
    """
    try:
        q = cursor.execute(query, day).fetchall()
        for row in q:
            row.ThoiGianKham = row.ThoiGianKham.strftime("%Y-%m-%d %H:%M ")
        return q
    except:
        print("Lỗi query visited.patients")
        return None

# 5 lượt khám bệnh gần nhất trong ngày
def last5(day, cursor):
    query = """
            SELECT TOP 5
            ThoiGianKham,TenBenhNhan,TenPhongBan
            FROM KhamBenh
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON KhamBenh.PhongBan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            WHERE NgayKham = ?
            ORDER BY KhamBenh_ID DESC
            """
    try:
        q = cursor.execute(query, day).fetchall()

        return q
    
    except:
        print("Lỗi query visited.last5")
        return None
    
# lượt khám theo khoa phòng và department_id
def department_id_day(day, cursor):
    query = """
            SELECT
            (CASE
            WHEN TenPhongBan IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
            WHEN TenPhongBan IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
            ELSE TenPhongBan
            END),
            COALESCE(COUNT(KhamBenh.KhamBenh_Id),0) AS 'TongLuotKham',
            (CASE
            WHEN KhamBenh.PhongBan_Id IN(2309,2310) THEN 23092310
            WHEN KhamBenh.PhongBan_Id IN(1244,2304) THEN 12442304
            ELSE KhamBenh.PhongBan_Id
            END)
            FROM KhamBenh INNER JOIN nhh_department
            ON KhamBenh.PhongBan_Id=nhh_department.PhongBan_Id
            WHERE NgayKham= ?
            GROUP BY 
            (CASE
            WHEN TenPhongBan IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
            WHEN TenPhongBan IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
            ELSE TenPhongBan END),
            (CASE
            WHEN KhamBenh.PhongBan_Id IN(2309,2310) THEN 23092310
            WHEN KhamBenh.PhongBan_Id IN(1244,2304) THEN 12442304
            ELSE KhamBenh.PhongBan_Id
            END)
            ORDER BY TongLuotKham DESC
            """

    try:
        q = cursor.execute(query, day).fetchall()
        return q
    except:
        print("Lỗi query visited.department_id_day")
        return None      

# danh sách khám bệnh theo khoa phognf
def list_department(day,department_id, cursor):
    query = """
    SELECT ThoiGianKham, MaYTe, TenBenhNhan, ChanDoanKhoaKham,TenNhanVien
    FROM KhamBenh
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
    ON KhamBenh.BacSiKham_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id

    WHERE KhamBenh.NgayKham = ? AND KhamBenh.PhongBan_Id = ?

    GROUP BY ThoiGianKham, MaYTe, TenBenhNhan, ChanDoanKhoaKham,TenNhanVien
    """
    try:
        q = cursor.execute(query, day, department_id).fetchall()
        return q
    except:
        print("Lỗi query visited.list_department")
        return None 

# tên phòng ban theo ID
def name_department(department_id, cursor):
    query = """
    SELECT TenPhongBan
    FROM [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan
    WHERE [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan.PhongBan_Id = ?
    """
    try:
        q = cursor.execute(query, department_id).fetchone()[0]
        return q
    except:
        print("Lỗi query visited.name_department")
        return None 
    


# lượt khám theo khoa phòng và department_id
def department_id_between(startday,enday, d_id,cursor):
    if d_id == 23092310:
        query = """
                SELECT
                NgayKham,
                COALESCE(COUNT(KhamBenh.KhamBenh_Id),0) AS 'TongLuotKham'
                FROM KhamBenh INNER JOIN nhh_department
                ON KhamBenh.PhongBan_Id=nhh_department.PhongBan_Id
                WHERE (NgayKham BETWEEN ? AND ?) AND (KhamBenh.PhongBan_Id = 2309 OR KhamBenh.PhongBan_Id = 2310)
                GROUP BY 
                NgayKham
                ORDER BY NgayKham

                """
        try:
            q = cursor.execute(query, startday,enday).fetchall()
            for row in q:
                row.NgayKham = row.NgayKham.strftime('%A %Y-%m-%d')
            return q
        except:
            print("Lỗi query visited.department_id_between")
            return None

    elif d_id == 12442304:
        query = """
                SELECT
                NgayKham,
                COALESCE(COUNT(KhamBenh.KhamBenh_Id),0) AS 'TongLuotKham'
                FROM KhamBenh INNER JOIN nhh_department
                ON KhamBenh.PhongBan_Id=nhh_department.PhongBan_Id
                WHERE (NgayKham BETWEEN ? AND ?) AND (KhamBenh.PhongBan_Id = 1244 OR KhamBenh.PhongBan_Id = 2304)
                GROUP BY 
                NgayKham
                ORDER BY NgayKham

                """
        try:
            q = cursor.execute(query, startday,enday).fetchall()
            for row in q:
                row.NgayKham = row.NgayKham.strftime('%A %Y-%m-%d')
            return q
        except:
            print("Lỗi query visited.department_id_between")
            return None

    else:
        query = """
                SELECT
                NgayKham,
                COALESCE(COUNT(KhamBenh.KhamBenh_Id),0) AS 'TongLuotKham'
                FROM KhamBenh INNER JOIN nhh_department
                ON KhamBenh.PhongBan_Id=nhh_department.PhongBan_Id
                WHERE (NgayKham BETWEEN ? AND ?) AND KhamBenh.PhongBan_Id = ?
                GROUP BY 
                NgayKham
                ORDER BY NgayKham
                """
        try:
            q = cursor.execute(query, startday,enday,d_id ).fetchall()
            for row in q:
                row.NgayKham = row.NgayKham.strftime('%A %Y-%m-%d')
            return q
        except:
            print("Lỗi query visited.department_id_between")
            return None      
