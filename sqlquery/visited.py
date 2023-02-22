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
    ThoiGianKham, MaYTe, TenBenhNhan,  ChanDoanKhoaKham,TenNhanVien, TenPhongBan
    FROM KhamBenh
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
    ON KhamBenh.PhongBan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien
    ON KhamBenh.BacSiKham_Id = [eHospital_NgheAn_Dictionary].[dbo].NhanVien.NhanVien_Id
    WHERE NgayKham = ?
    GROUP BY ThoiGianKham, MaYTe, TenBenhNhan, TenNhanVien, ChanDoanKhoaKham, TenPhongBan
    """
    try:
        q = cursor.execute(query, day).fetchall()
        return q
    except:
        print("Lỗi query visited.patients")
        return None
