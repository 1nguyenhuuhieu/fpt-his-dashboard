import datetime
from slugify import slugify
def info(sobenhan, cursor):
    sql = """
    SELECT BenhAn_Id, SoBenhAn,SoLuuTru, TenBenhNhan, benhnhan.NgaySinh, benhnhan.DiaChi,
    benhnhan.MaYTe, benhnhan.SoDienThoai, TenNhanVien, TenPhongBan, ThoiGianVaoKhoa, ThoiGianRaVien, SoNgayDieuTri,
    trangthairavien.Dictionary_Name as trangthai, ChanDoanVaoKhoa, ChanDoanRaVien, ketquaravien.Dictionary_Name as ketqua, MaGiuong, SUM(SoLuong* DonGiaDoanhThu) as doanhthu,
    YEAR(benhnhan.NgaySinh) as tuoi,
    TienSuBenh,benhnhan.GioiTinh as gioitinhbenhnhan
    FROM BenhAn
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
    ON BenhAn.BenhNhan_Id = benhnhan.BenhNhan_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
    ON BenhAn.BacSiDieuTri_Id = nhanvien.NhanVien_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_PhongBan] as khoa
    ON BenhAn.KhoaVao_Id = khoa.PhongBan_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as trangthairavien
    ON BenhAn.LyDoXuatVien_Id = trangthairavien.Dictionary_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as ketquaravien
    ON BenhAn.KetQuaDieuTri_Id = ketquaravien.Dictionary_Id
    LEFT JOIN XacNhanChiPhiChiTiet
    ON BenhAn.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id

    WHERE SoBenhAn = ?

    GROUP BY BenhAn_Id, SoBenhAn,SoLuuTru, TenBenhNhan, benhnhan.NgaySinh, benhnhan.DiaChi,benhnhan.SoDienThoai,
    benhnhan.MaYTe, TenNhanVien, TenPhongBan, ThoiGianVaoKhoa, ThoiGianRaVien, SoNgayDieuTri,
    trangthairavien.Dictionary_Name, ChanDoanVaoKhoa, ChanDoanRaVien, ketquaravien.Dictionary_Name, MaGiuong,
    TienSuBenh,benhnhan.GioiTinh
    """
    try:
        row = cursor.execute(sql, sobenhan).fetchone()

        if row.ThoiGianVaoKhoa: row.ThoiGianVaoKhoa = row.ThoiGianVaoKhoa.strftime("%H:%M %d/%m/%Y")
        if row.tuoi: row.tuoi = datetime.date.today().year - row.tuoi 
        if row.NgaySinh:  row.NgaySinh = row.NgaySinh.strftime("%d/%m/%Y")
        if row.ThoiGianRaVien: row.ThoiGianRaVien = row.ThoiGianRaVien.strftime("%H:%M %d/%m/%Y")
        if row.SoNgayDieuTri: row.SoNgayDieuTri = int(row.SoNgayDieuTri)
        if row.doanhthu: row.doanhthu = f'{round(int(row.doanhthu)/1000)*1000:,}' 
  
        return row
    except:
        print("Lỗi query medical_record.info")
        return None

def examinition(khambenh_id, cursor):
    sql = """
        SELECT KhamBenh_Id, ThoiGianKham, DinhBenh, DienBien, TenNhanVien
        FROM NoiTru_KhamBenh
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
        ON NoiTru_KhamBenh.BasSiKham_Id = nhanvien.NhanVien_Id
        WHERE KhamBenh_Id = ?
    """
    try:
        row = cursor.execute(sql, khambenh_id).fetchone()
        if row.ThoiGianKham: row.ThoiGianKham = row.ThoiGianKham.strftime("%H:%M %d/%m/%Y")
        return row
    except:
        print("Lỗi query medical_record.examinition")
        return None
    
def examinitions_id(benhan_id, cursor):
    sql = """SELECT KhamBenh_Id
            FROM NoiTru_KhamBenh
            WHERE BenhAn_Id = ?
            ORDER BY ThoiGianKham
            """
    try:
        row = cursor.execute(sql, benhan_id).fetchall()
        return row
    except:
        print("Lỗi query medical_record.examinitions_id")
        return None
    
def medicines(khambenh_id, cursor):
    sql = """SELECT SoLuong,SoLuongTrenLan, SoLanTrenNgay, SoLuong_BuoiSang,SoLuong_BuoiTrua,SoLuong_BuoiChieu,SoLuong_BuoiToi,SoNgay, DonViTinh, TenDuocDayDu, Dictionary_Name as duongdung
            FROM NoiTru_ToaThuoc
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_Duoc] as duoc
            ON NoiTru_ToaThuoc.Duoc_Id = duoc.Duoc_Id
            INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as dict
            ON duoc.DuongDung_Id = dict.Dictionary_Id
            WHERE KhamBenh_Id = ?
            """
    try:
        rows = cursor.execute(sql, khambenh_id).fetchall()
        for row in rows:
            row.SoLuong = int(row.SoLuong) 
            row.SoLuongTrenLan = int(row.SoLuongTrenLan) 
            if row.SoLuong_BuoiSang: row.SoLuong_BuoiSang = int(row.SoLuong_BuoiSang)
            if row.SoLuong_BuoiTrua: row.SoLuong_BuoiTrua = int(row.SoLuong_BuoiTrua) 
            if row.SoLuong_BuoiChieu: row.SoLuong_BuoiChieu = int(row.SoLuong_BuoiChieu) 
            if row.SoLuong_BuoiToi: row.SoLuong_BuoiToi = int(row.SoLuong_BuoiToi) 
        return rows
    except:
        print("Lỗi query medical_record.medicines")
        return None
    
def medical_images(benhan_id, cursor):
    sql = """SELECT ThoiGianThucHien, TenNhanVien as bacsiketluan, NoiDungChiTiet, MoTa_Text, KetLuan
        FROM CLSYeuCau
        INNER JOIN CLSKetQua as ketqua
        ON CLSYeuCau.CLSYeuCau_Id = ketqua.CLSYeuCau_Id
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
        ON ketqua.BacSiKetLuan_Id = nhanvien.NhanVien_Id
        WHERE BenhAn_Id = ?
        ORDER BY ThoiGianThucHien"""
    try:
        rows = cursor.execute(sql, benhan_id).fetchall()
        for row in rows:
            if row.ThoiGianThucHien: row.ThoiGianThucHien = row.ThoiGianThucHien.strftime("%H:%M %d/%m/%Y")
        return rows
    except:
        print("Lỗi query medical_record.medical_images")
        return None
    

# cls nội trú
def lab(clsyeucau_id, cursor):
    query = """
    SELECT ServiceName, xetnghiem_ketqua.Unit, xetnghiem_ketqua.Value,
    xetnghiem_ketqua.Value2, xetnghiem_ketqua.MinLimited, xetnghiem_ketqua.MaxLimited,
    TenNhanVien as bacsi,
	'text-dark' as color
    FROM [eHospital_NgheAn].[dbo].[CLSYeuCau] as yeucau
    INNER JOIN [eLab_NgheAn].[dbo].[LabResult] as xetnghiem
    ON yeucau.CLSYeuCau_Id = xetnghiem.RequestID
    INNER JOIN [eLab_NgheAn].[dbo].[LabResultDetail] as xetnghiem_ketqua
    ON xetnghiem.ResultID = xetnghiem_ketqua.ResultID
    INNER JOIN [eLab_NgheAn].[dbo].[DIC_Service] as service_dict
    on service_dict.ServiceID = xetnghiem_ketqua.ServiceID
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
    ON yeucau.BacSiChiDinh_Id = nhanvien.NhanVien_Id
    where CLSYeuCau_Id = ? AND Value IS NOT NULL
    """
    try:
        q = cursor.execute(query, clsyeucau_id).fetchall()
        for row in q:
            try:
                row.Value = float(row.Value)
                row.MinLimited = float(row.MinLimited)
                if row.Value < row.MinLimited:
                    row.color = 'text-danger'
                else:
                    row.color = 'text-success'
                try:
                    row.MaxLimited = float(row.MaxLimited)
                    if row.Value > row.MaxLimited:
                        row.color = 'text-danger'
                except:
                    pass
            except:
                pass



            if row.Value == 'Negative':
                row.color = 'text-success'
        

            

        return q
    except:
        print("Lỗi khi query patient.lab")
        return None
    
def medical_requests(benhan_id, cursor):
    query = """
    SELECT NoiDungChiTiet, COUNT(NoiDungChiTiet) as count, 'name' as id
    FROM CLSYeuCau
    WHERE BenhAn_Id = ? 
    GROUP BY NoiDungChiTiet
    ORDER BY NoiDungChiTiet
    """
    try:
        q = cursor.execute(query, benhan_id).fetchall()
        for row in q:
            row.id = row.NoiDungChiTiet
        return q
    except:
        print("Lỗi khi query patient.medical_requests")
        return None  
       
def medical_requests_id(benhan_id, cursor):
    query = """
        SELECT CLSYeuCau_Id, ThoiGianYeuCau, NoiDungChiTiet, TenNhanVien as bacsi
        FROM CLSYeuCau
        LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
        ON CLSYeuCau.BacSiChiDinh_Id = nhanvien.NhanVien_Id
        WHERE BenhAn_Id = ?
    """
    try:
        q = cursor.execute(query, benhan_id).fetchall()
        for row in q:
            if row.ThoiGianYeuCau: row.ThoiGianYeuCau = row.ThoiGianYeuCau.strftime("%H:%M %d/%m/%Y")
        return q
    except:
        print("Lỗi khi query patient.medical_requests")
        return None  
       
def surgery_ekip(BenhAnPhauThuat_Id, cursor):
    query = """
    SELECT TenNhanVien as ten,
    dict.Dictionary_Name as vaitro
    FROM [eHospital_NgheAn].[dbo].[BenhAnPhauThuat_EKip] as ekip
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[NhanVien] as nhanvien
    ON ekip.NhanVien_Id = nhanvien.NhanVien_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as dict
    ON ekip.VaiTro_Id = dict.Dictionary_Id
    WHERE BenhAnPhauThuat_Id = ?
    ORDER BY vaitro
    """
    try:
        q = cursor.execute(query, BenhAnPhauThuat_Id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.surgery_ekip")
        return None  
       
def surgeries(BenhAn_Id, cursor):
    query = """
    SELECT BenhAnPhauThuat_Id, ThoiGianBatDau, ThoiGianKetThuc, ICD_TruocPhauThuat_MoTa, ICD_SauPhauThuat_MoTa,
    dict_ppvc.Dictionary_Name as phuongphapvocam, dict_taibien.Dictionary_Name as taibien,
    CanThiepPhauThuat
    FROM BenhAnPhauThuat
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_LoaiPhauThuat] as loaiphauthuat
    ON BenhAnPhauThuat.LoaiPhauThuat = loaiphauthuat.LoaiPhauThuat
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as dict_ppvc
    ON BenhAnPhauThuat.PhuongPhapVoCam_Id = dict_ppvc.Dictionary_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[Lst_Dictionary] as dict_taibien
    ON BenhAnPhauThuat.TaiBien_Id = dict_taibien.Dictionary_Id
    WHERE BenhAn_Id = ?

    """
    try:
        q = cursor.execute(query, BenhAn_Id).fetchall()
        return q
    except:
        print("Lỗi khi query patient.surgery")
        return None     