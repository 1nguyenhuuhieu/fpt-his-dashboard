from datetime import date, datetime, timedelta

# Số lượt khám bệnh trong khoảng ngày
def total(start, end, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(KhamBenh_Id),0)
        FROM dbo.KhamBenh
        WHERE ThoiGianKham BETWEEN ? AND ?;
        """,start, end
        ).fetchone()[0]

        return int(q)
    except:
        print("Lỗi query visited.total")
        return None


# Số lượt nhập viện khi khám bệnh
# Used for: visited
def in_hospital(start, end, cursor):
    query = """
        SELECT
        COALESCE(COUNT(KhamBenh_Id),0)
        FROM dbo.KhamBenh
        WHERE ThoiGianKham BETWEEN ? AND ? AND HuongGiaiQuyet_Id=457;
        """
    try:
        rows = cursor.execute(query,start, end).fetchone()[0]
        return rows
    except:
        print("Lỗi query visited.in_hospital")
        return None

# Số lượt chuyển viện viện khi khám bệnh
# Used for: visited    
def transfer(start, end, cursor):
    query = """
        SELECT
        COALESCE(COUNT(KhamBenh_Id),0)
        FROM dbo.KhamBenh
        WHERE ThoiGianKham BETWEEN ? AND ? AND HuongGiaiQuyet_Id=458;
        """
    try:
        rows = cursor.execute(query,start, end).fetchone()[0]
        return rows
    except:
        print("Lỗi query visited.transfer")
        return None

# Số lượt khám bệnh trong  ngày
def total_day(day, cursor):
    try:
        q = cursor.execute("""SELECT
        COALESCE(COUNT(KhamBenh_Id),0)
        FROM dbo.KhamBenh
        WHERE NgayKham = ?;
        """,day
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query visited.total_day")
        return 0
    
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


# Số lượt khám mỗi ngày từ ngày start tới ngày end
# used for: home
def day_betweenday(startday, endday, cursor):
    try:
        q = cursor.execute(
            """
            SELECT NgayKham,
            COALESCE(COUNT(KhamBenh_Id),0)
            FROM KhamBenh
            WHERE NgayKham BETWEEN ? AND ?
            GROUP BY NgayKham
            ORDER BY NgayKham DESC
            """, startday, endday
        ).fetchall()


        return q
    except:
        print("Lỗi query visited.day_betweenday")
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
    
# Số lượt khám bệnh theo từng khoa phòng trong khoảng ngày
def departments(start,end, cursor):

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
            FROM KhamBenh
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan] as dm_phongban
            ON KhamBenh.PhongBan_Id=dm_phongban.PhongBan_Id
            WHERE ThoiGianKham BETWEEN ? AND ?
            GROUP BY 
            (CASE
                WHEN TenPhongBan IN(N'Phòng Khám Cao Huyết áp (10)', N'Phòng Khám Cao Huyết áp (10)_A' ) THEN N'Phòng Khám Cao Huyết áp (10)'
                WHEN TenPhongBan IN(N'Phòng Khám Tiểu Đường (08)', N'Phòng Khám Tiểu Đường (08)_A') THEN N'Phòng Khám Tiểu Đường (08)'
                ELSE TenPhongBan END)
            ORDER BY TongLuotKham DESC
            """, start, end
        ).fetchall()

        return q
    except:
        print("Lỗi query visited.department_week")
        return None

# Danh sách khám bệnh trong ngày
def patients(start, end, cursor):
    query = """
    SELECT
    ThoiGianKham, MaYTe, TenBenhNhan, KhamBenh.TiepNhan_Id ,ChanDoanKhoaKham,Dictionary_Name,TenNhanVien, TenPhongBan
    FROM KhamBenh
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
    ON KhamBenh.PhongBan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien
    ON KhamBenh.BacSiKham_Id = [eHospital_NgheAn_Dictionary].[dbo].NhanVien.NhanVien_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as dict
    ON KhamBenh.HuongGiaiQuyet_Id = dict.Dictionary_Id
    WHERE ThoiGianKham BETWEEN ? AND ?
    GROUP BY ThoiGianKham, MaYTe, TenBenhNhan, TenNhanVien, ChanDoanKhoaKham, TenPhongBan, KhamBenh.TiepNhan_Id,Dictionary_Name
    """
    try:
        q = cursor.execute(query, start, end).fetchall()
        for row in q:
            row.ThoiGianKham = row.ThoiGianKham.strftime("%Y-%m-%d %H:%M ")
        return q
    except:
        print("Lỗi query visited.patients")
        return None

# 5 lượt khám bệnh gần nhất trong ngày
def last5(start, end, cursor):
    query = """
            SELECT TOP 5
            ThoiGianKham,TenBenhNhan,TenPhongBan
            FROM KhamBenh
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
            ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan]
            ON KhamBenh.PhongBan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan].PhongBan_Id
            WHERE ThoiGianKham BETWEEN ? AND ?
            ORDER BY KhamBenh_ID DESC
            """
    try:
        q = cursor.execute(query, start, end).fetchall()
        for row in q:
            row.ThoiGianKham = row.ThoiGianKham.strftime('%H:%M %d/%m/%Y')

        return q
    
    except:
        print("Lỗi query visited.last5")
        return None
    
# lượt khám theo khoa phòng và department_id
def department_with_id(start, end, cursor):
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
            WHERE ThoiGianKham BETWEEN ? AND ?
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
        q = cursor.execute(query, start, end).fetchall()
        return q
    except:
        print("Lỗi query visited.department_id_day")
        return None      

# danh sách khám bệnh theo khoa phognf
def list_department(start, end,department_id, cursor):
    query = """
    SELECT ThoiGianKham, MaYTe, TenBenhNhan, ChanDoanKhoaKham,Dictionary_Name,TenNhanVien
    FROM KhamBenh
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien]
    ON KhamBenh.BacSiKham_Id = [eHospital_NgheAn_Dictionary].[dbo].[NhanVien].NhanVien_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as dict
    ON KhamBenh.HuongGiaiQuyet_Id = dict.Dictionary_Id
    WHERE KhamBenh.ThoiGianKham BETWEEN ? AND ? AND KhamBenh.PhongBan_Id = ?

    GROUP BY ThoiGianKham, MaYTe, TenBenhNhan, ChanDoanKhoaKham,TenNhanVien,Dictionary_Name
    """
    try:
        q = cursor.execute(query, start, end, department_id).fetchall()
        for row in q:
            row.ThoiGianKham = row.ThoiGianKham.strftime("%Y-%m-%d %H:%M")
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

# Số lượt khám theo bác sĩ
def doctors(start, end, cursor):
    query = """
            SELECT
            TenNhanVien as name,
            COALESCE(COUNT(KhamBenh_Id), 0) as total
            FROM KhamBenh
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
            ON KhamBenh.BacSiKham_Id = nhanvien.NhanVien_Id
            WHERE ThoiGianKham BETWEEN ? AND ?
            GROUP BY TenNhanVien
            ORDER BY total DESC
    """
    try:
        q = cursor.execute(query, start, end).fetchall()
        return q
    except:
        print("Lỗi query visited.doctors")
        return None 
    
# Số lượt khám theo bác sĩ
def doctors_department(start, end, d_id,cursor):
    query = """
            SELECT
            TenNhanVien as name,
            COALESCE(COUNT(KhamBenh_Id), 0) as total
            FROM KhamBenh
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
            ON KhamBenh.BacSiKham_Id = nhanvien.NhanVien_Id
            WHERE ThoiGianKham BETWEEN ? AND ?
            AND KhamBenh.PhongBan_id = ?
            GROUP BY TenNhanVien
            ORDER BY total DESC
    """
    try:
        q = cursor.execute(query, start, end, d_id).fetchall()
        return q
    except:
        print("Lỗi query visited.doctors_department")
        return None 
    
# Số lượt khám theo bác sĩ 2 phòng gộp 1
def doctors_department_merge(start, end, d_id,cursor):
    d_id = str(d_id)
    d_id_1 = d_id[:4]
    d_id_2 = d_id[4:]


    query = """
            SELECT
            TenNhanVien as name,
            COALESCE(COUNT(KhamBenh_Id), 0) as total
            FROM KhamBenh
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
            ON KhamBenh.BacSiKham_Id = nhanvien.NhanVien_Id
            WHERE ThoiGianKham BETWEEN ? AND ?
            AND (KhamBenh.PhongBan_id = ? OR KhamBenh.PhongBan_id = ?)
            GROUP BY TenNhanVien
            ORDER BY total DESC
            """
    try:
        q = cursor.execute(query, start, end, d_id_1, d_id_2).fetchall()
        return q
    except:
        print("Lỗi query visited.doctors_department_merge")
        return None 

    
# Thời gian khám
def time_overview(start, end,cursor):
    query = """
        SELECT COUNT(TiepNhan.TiepNhan_Id) as count,
        AVG(DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan,XacNhanChiPhi.ThoiGianXacNhan)) as avg_time,
        AVG(DATEDIFF(minute,KhamBenh.NgayCapNhat ,XacNhanChiPhi.ThoiGianXacNhan)) as avg_time_thanhtoan,
        MAX(DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan,XacNhanChiPhi.ThoiGianXacNhan)) as max_time,
        MIN(DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan,XacNhanChiPhi.ThoiGianXacNhan)) as min_time
        FROM TiepNhan
        INNER JOIN XacNhanChiPhi
        ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id AND TiepNhan.NgayTiepNhan = XacNhanChiPhi.NgayXacNhan
        INNER JOIN KhamBenh
        ON TiepNhan.TiepNhan_Id = KhamBenh.TiepNhan_Id
        AND KhamBenh.NgayCapNhat IS NOT NULL
        WHERE TiepNhan.ThoiGianTiepNhan BETWEEN ? AND ?
        """
    try:
        q = cursor.execute(query, start, end).fetchone()
        return q
    except:
        print("Lỗi query visited.time_overview")
        return None 

# danh sách id tiếp nhận khám bệnh và thanh toán trong ngày
def tiepnhan_id_inday(start, end, cursor):
    query = """
        SELECT TiepNhan.TiepNhan_Id,TiepNhan.ThoiGianTiepNhan, XacNhanChiPhi.ThoiGianXacNhan as thoigianxacnhan,
        DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan,thoigianxacnhan) as totaltime
        FROM TiepNhan
        INNER JOIN XacNhanChiPhi
        ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id AND TiepNhan.NgayTiepNhan = XacNhanChiPhi.NgayXacNhan
        WHERE TiepNhan.ThoiGianTiepNhan BETWEEN ? AND ?
        order by totaltime desc
        """
    try:
        q = cursor.execute(query, start, end).fetchall()
        return q
    except:
        print("Lỗi query visited.tiepnhan_id_inday")
        return None 
    
# danh sách bệnh nhân tiếp nhận khám bệnh và thanh toán trong ngày
def time_patients(start, end, cursor):
    query = """
    SELECT  dm_benhnhan.TenBenhNhan,
    dm_dichvu.TenNhomDichVu,
    TiepNhan.ThoiGianTiepNhan,
    CLSYeuCau.ThoiGianYeuCau as thoigianyeucau,
    CLSKetQua.ThoiGianThucHien as thoigianthuchien,
    CLSKetQua.NgayTao as thoigiancoketqua,
    KhamBenh.NgayCapNhat as thoigian_hoantatkhambenh,
    XacNhanChiPhi.ThoiGianXacNhan,
    DATEDIFF(minute, TiepNhan.ThoiGianTiepNhan, CLSYeuCau.ThoiGianYeuCau) as thoigiancho_bacsikham,
    DATEDIFF(minute, CLSYeuCau.ThoiGianYeuCau, CLSKetQua.ThoiGianThucHien) as thoigiancho_cls,
    DATEDIFF(minute, CLSKetQua.ThoiGianThucHien, CLSKetQua.NgayTao) as thoigian_cho_ketqua_cls,
    DATEDIFF(minute, CLSKetQua.NgayTao, KhamBenh.NgayCapNhat) as thoigian_cho_hoantatkhambenh,
    DATEDIFF(minute, CLSKetQua.NgayTao, XacNhanChiPhi.NgayTao) as thoigian_cho_thanhtoan,
    DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan, XacNhanChiPhi.NgayTao) as tongthoigian
    FROM CLSYeuCau
    INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_NhomDichVu as dm_dichvu
    ON CLSYeuCau.NhomDichVu_Id = dm_dichvu.NhomDichVu_Id
    LEFT JOIN CLSKetQua
    ON CLSYeuCau.CLSYeuCau_Id = CLSKetQua.CLSYeuCau_Id
    INNER JOIN XacNhanChiPhi
    ON CLSYeuCau.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
    INNER JOIN TiepNhan
    ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
    INNER JOIN KhamBenh
    ON TiepNhan.TiepNhan_Id = KhamBenh.TiepNhan_Id
    INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_BenhNhan as dm_benhnhan
    ON TiepNhan.BenhNhan_Id = dm_benhnhan.BenhNhan_Id
    WHERE TiepNhan.ThoiGianTiepNhan BETWEEN ? AND ?
    AND TiepNhan.NgayTiepNhan = XacNhanChiPhi.NgayXacNhan
    AND KhamBenh.NgayCapNhat IS NOT NULL

    ORDER BY TiepNhan.TiepNhan_Id


        """
    try:
        q = cursor.execute(query, start, end).fetchall()
        for row in q:
            for i in (2,3,4,5,6,7):
                if row[i]: row[i] = row[i].strftime("%H:%M")
        return q
    except:
        print("Lỗi query visited.time_patients")
        return None 
    
# thời gian khám từng khoa phòng
def time_departments(start, end, cursor):
    query = """
        SELECT 
        TenPhongBan,
        COUNT(TenPhongBan) as soluot,
        AVG(DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan,KhamBenh.ThoiGianKham)) as avg_thoigiankham,
        MAX(DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan,KhamBenh.ThoiGianKham)) as max_thoigiankham,
        MIN(DATEDIFF(minute,TiepNhan.ThoiGianTiepNhan,KhamBenh.ThoiGianKham)) as min_thoigiankham
        FROM CLSYeuCau
        INNER JOIN TiepNhan
        ON CLSYeuCau.TiepNhan_Id = TiepNhan.TiepNhan_Id
        INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_PhongBan as dm_phongban
        ON CLSYeuCau.NoiThucHien_Id = dm_phongban.PhongBan_Id
        INNER JOIN KhamBenh
        ON TiepNhan.TiepNhan_Id = KhamBenh.TiepNhan_Id
        WHERE TiepNhan.ThoiGianTiepNhan BETWEEN ? AND ?
        AND CLSYeuCau.NhomDichVu_Id = 27
        GROUP BY TenPhongBan
        ORDER BY soluot DESC
        """
    try:
        q = cursor.execute(query, start, end).fetchall()
        return q
    except:
        print("Lỗi query visited.time_departments")
        return None 
    
# thời gian khám từng dịch vụ
def time_service(start, end, cursor):
    query = """
SELECT  
dm_dichvu.TenNhomDichVu,
COUNT(dm_dichvu.TenNhomDichVu) as soluot,
AVG(DATEDIFF(minute, CLSYeuCau.ThoiGianYeuCau, CLSKetQua.ThoiGianThucHien)) as avg_thoigiancho_cls
FROM CLSYeuCau
INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_NhomDichVu as dm_dichvu
ON CLSYeuCau.NhomDichVu_Id = dm_dichvu.NhomDichVu_Id
LEFT JOIN CLSKetQua
ON CLSYeuCau.CLSYeuCau_Id = CLSKetQua.CLSYeuCau_Id
INNER JOIN XacNhanChiPhi
ON CLSYeuCau.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
INNER JOIN TiepNhan
ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
INNER JOIN KhamBenh
ON TiepNhan.TiepNhan_Id = KhamBenh.TiepNhan_Id
WHERE TiepNhan.ThoiGianTiepNhan BETWEEN ? AND ?
AND TiepNhan.NgayTiepNhan = XacNhanChiPhi.NgayXacNhan
AND KhamBenh.NgayCapNhat IS NOT NULL
AND CLSKetQua.ThoiGianThucHien IS NOT NULL

GROUP BY dm_dichvu.TenNhomDichVu
ORDER BY soluot DESC
        """
    try:
        q = cursor.execute(query, start, end).fetchall()
        return q
    except:
        print("Lỗi query visited.time_service")
        return None 
