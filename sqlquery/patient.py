# Thông tin chi tiết của bệnh nhân
def detail(mayte, cursor):
    query = """
    SELECT  TenBenhNhan, NgaySinh,GioiTinh,  DiaChi, SoDienThoai, BenhNhan_Id, MaYTe, NgayTao,NgayCapNhat
    FROM [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    WHERE [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].MaYTe=?
    """
    try:
        q = cursor.execute(query, mayte).fetchone()
        return q
    except:
        print("Lỗi khi query patient.detail")
        return None
    

# Danh sách toàn bộ bệnh nhân có hoạt động gần nhất
def patients(cursor):
    query = """
        SELECT TOP 2000
        XacNhanChiPhi.NgayXacNhan, MaYTe, TenBenhNhan,NgaySinh, SoDienThoai, DiaChi
        FROM [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        INNER JOIN [eHospital_NgheAn].[dbo].[XacNhanChiPhi]
        ON XacNhanChiPhi.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        ORDER BY XacNhanChiPhi.NgayXacNhan DESC
        """
    try:
        q = cursor.execute(query).fetchall()

        return q
    except:
        print("Lỗi query hospitalized.patients")
        return None

# Lịchh sử tiếp nhận của bệnh nhân
def visited_history(mayte, cursor):
    query = """
       SELECT TenPhongBan,ChanDoanKhoaKham,  TenNhanVien,ThoiGianKham, Dictionary_Name, KhamBenh_Id, KhamBenh.TiepNhan_Id as tiepnhan_id
        FROM KhamBenh
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON KhamBenh.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien
        ON KhamBenh.BacSiKham_Id = [eHospital_NgheAn_Dictionary].[dbo].NhanVien.NhanVien_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan
        ON KhamBenh.PhongBan_Id = [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan.PhongBan_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary]
        ON KhamBenh.HuongGiaiQuyet_Id = [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Id
        WHERE [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].MaYTe = ?
        ORDER BY KhamBenh.KhamBenh_Id DESC

        """
    try:
        q = cursor.execute(query, mayte).fetchall()
        return q
    except:
        print("Lỗi khi query patient.visited_history")
        return None
    
# Lịchh sử nhập viện của bệnh nhân
def hospitalized_history(mayte, cursor):
    query = """
        SELECT TenPhongBan, ChanDoanVaoKhoa, TenNhanVien, ThoiGianVaoVien,ThoiGianRaVien,
        [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Name as ravien, SoBenhAn, ChanDoanRaVien, t2.Dictionary_Name as ketqua,BenhAn_Id
        FROM BenhAn
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien
        ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].NhanVien.NhanVien_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan
        ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan.PhongBan_Id
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary]
        ON BenhAn.LyDoXuatVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Id
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as t2
        ON BenhAn.KetQuaDieuTri_Id = t2.Dictionary_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        WHERE [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].MaYTe= ?
        ORDER BY BenhAn.BenhAn_Id DESC
        """
    try:
        q = cursor.execute(query, mayte).fetchall()
        return q
    except:
        print("Lỗi khi query patient.hospitalized_history")
        return None
    
# Tổng doanh thu của bệnh nhân
def doanhthu(mayte, cursor):
    query = """
    SELECT COALESCE(SUM(SoLuong * DonGiaDoanhThu),0) as 'doanhthu'
    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON XacNhanChiPhi.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
    WHERE [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].MaYTe=?
    """
    try:
        q = cursor.execute(query, mayte).fetchone()[0]
        return int(q)
    except:
        print("Lỗi khi query patient.doanhthu")
        return 0
        
    
# Tổng thanhtoán của bệnh nhân
def thanhtoan(mayte, cursor):
    query = """
    SELECT COALESCE(SUM(SoLuong * DonGiaThanhToan),0) as 'thanhtoan'
    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON XacNhanChiPhi.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
    WHERE [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].MaYTe=?
    """
    try:
        q = cursor.execute(query, mayte).fetchone()[0]
        return int(q)
    except:
        print("Lỗi khi query patient.thanhtoan")
        return 0
        
    
# Đơn thuốc theo khám bệnh id
def donthuoc(khambenh_id, cursor):
    query = """
        SELECT  Dictionary_Name, TenDuocDayDu,ToaThuoc.SoLuong
        FROM ToaThuoc
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_Duoc]
        ON ToaThuoc.Duoc_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_Duoc].Duoc_Id
        INNER JOIN KhamBenh
        ON ToaThuoc.KhamBenh_Id = KhamBenh.KhamBenh_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary]
        ON ToaThuoc.DuongDung_Id = [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Id

        WHERE ToaThuoc.KhamBenh_Id = ?
    """
    try:
        q = cursor.execute(query, khambenh_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.donthuoc")
        return 0
        

# Chỉ định CLS
def cls_yeucau(tiepnhan_id, cursor):
    query = """
     SELECT CLSYeuCau_Id, NoiDungChiTiet
    FROM CLSYeuCau
    WHERE TiepNhan_Id = ?
    """
    try:
        q = cursor.execute(query, tiepnhan_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.cls_yeucau")
        return 0
        
# kết quả CLS
def cls_ketqua(cls_id, cursor):
    query = """
    SELECT
    MoTa_Text,
    KetLuan,
    TenNhanVien,
    VungKhaoSat
    FROM [eHospital_NgheAn].[dbo].[CLSKetQua]
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nv
    ON BacSiKetLuan_Id = nv.NhanVien_Id
    WHERE CLSYeuCau_Id=? AND MoTa_Text IS NOT NULL

    """
    try:
        q = cursor.execute(query, cls_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.cls_ketqua")
        return None
        

# khám bệnh nội trú
def khambenh_noitru(benhan_id, cursor):
    query = """
    SELECT noitru.KhamBenh_Id, ThoiGianKham, TenNhanVien, DinhBenh, DienBien
    FROM [eHospital_NgheAn].[dbo].[NoiTru_KhamBenh] as noitru
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien as nhanvien
    ON noitru.BasSiKham_id= nhanvien.NhanVien_Id
    where benhan_id=?
    """
    try:
        q = cursor.execute(query, benhan_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.khambenh_noitru")
        return None
    
# khám bệnh nội trú dược
def khambenh_noitru_toathuoc(khambenh_id, cursor):
    query = """
    SELECT  Tenhang, SoLuong
    FROM [eHospital_NgheAn].[dbo].[NoiTru_ToaThuoc] as toathuoc
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_Duoc]
    ON toathuoc.Duoc_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_Duoc].Duoc_Id
    WHERE KhamBenh_Id = ?
    """
    try:
        q = cursor.execute(query, khambenh_id).fetchall()
        for row in q:
            row.SoLuong = int(row.SoLuong)
        return q
    except:
        print("Lỗi khi query patient.khambenh_noitru_toathuoc")
        return None
    
# cls nội trú
def cls_noitru(benhan_id, cursor):
    query = """
    select NoiDungChiTiet, MoTa_Text, KetLuan, TenNhanVien, ThoiGianThucHien
    from CLSYeuCau 
    INNER join CLSKetQua
    on CLSYeuCau.CLSYeuCau_Id = CLSKetQua.CLSYeuCau_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien as nhanvien
    ON CLSKetQua.BacSiKetLuan_Id= nhanvien.NhanVien_Id
    where BenhAn_Id=? AND MoTa_Text IS NOT NULL
    """
    try:
        q = cursor.execute(query, benhan_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.cls_noitru")
        return None
    
# cls nội trú
def xetnghiem_id(benhan_id, cursor):
    query = """
    select  CLSYeuCau.CLSYeuCau_Id as id
    from CLSYeuCau 
    INNER join CLSKetQua
    on CLSYeuCau.CLSYeuCau_Id = CLSKetQua.CLSYeuCau_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien as nhanvien
    ON CLSKetQua.BacSiKetLuan_Id= nhanvien.NhanVien_Id
    where BenhAn_Id=? AND MoTa_Text IS NULL
    """
    try:
        q = cursor.execute(query, benhan_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.xetnghiem")
        return None
    
# cls nội trú
def ketqua_xetnghiem(clsyeucau_id, cursor):
    query = """
    SELECT xetnghiem.ResultDateTime, NoiDungChiTiet, ServiceName, xetnghiem_ketqua.Unit, xetnghiem_ketqua.Value,
    xetnghiem_ketqua.Value2, xetnghiem_ketqua.MinLimited, xetnghiem_ketqua.MaxLimited
    FROM [eHospital_NgheAn].[dbo].[CLSYeuCau] as yeucau
    INNER JOIN [eLab_NgheAn].[dbo].[LabResult] as xetnghiem
    ON yeucau.CLSYeuCau_Id = xetnghiem.RequestID
    INNER JOIN [eLab_NgheAn].[dbo].[LabResultDetail] as xetnghiem_ketqua
    ON xetnghiem.ResultID = xetnghiem_ketqua.ResultID
    INNER JOIN [eLab_NgheAn].[dbo].[DIC_Service] as service_dict
    on service_dict.ServiceID = xetnghiem_ketqua.ServiceID
    where CLSYeuCau_Id = ? AND Value IS NOT NULL
    """
    try:
        q = cursor.execute(query, clsyeucau_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.ketqua_xetnghiem")
        return None
    