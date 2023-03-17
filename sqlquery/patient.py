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
        SELECT TOP 1000
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
        SELECT TenPhongBan, ChanDoanVaoKhoa, TenNhanVien, ThoiGianVaoVien,ThoiGianRaVien, Dictionary_Name
        FROM BenhAn
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].NhanVien
        ON BenhAn.BacSiDieuTri_Id = [eHospital_NgheAn_Dictionary].[dbo].NhanVien.NhanVien_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan
        ON BenhAn.KhoaVao_Id = [eHospital_NgheAn_Dictionary].[dbo].DM_PhongBan.PhongBan_Id
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary]
        ON BenhAn.LyDoXuatVien_Id = [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary].Dictionary_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON BenhAn.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        WHERE [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].MaYTe=?
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
    KetLuan
    FROM [eHospital_NgheAn].[dbo].[CLSKetQua]
    WHERE CLSYeuCau_Id=? AND MoTa_Text IS NOT NULL
    """
    try:
        q = cursor.execute(query, cls_id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.cls_ketqua")
        return None
        