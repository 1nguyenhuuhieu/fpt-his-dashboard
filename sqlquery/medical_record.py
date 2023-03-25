import datetime
def info(sobenhan, cursor):
    sql = """
    SELECT BenhAn_Id, SoBenhAn,SoLuuTru, TenBenhNhan, benhnhan.NgaySinh, benhnhan.DiaChi,
    benhnhan.MaYTe, benhnhan.SoDienThoai, TenNhanVien, TenPhongBan, ThoiGianVaoKhoa, ThoiGianRaVien, SoNgayDieuTri,
    trangthairavien.Dictionary_Name as trangthai, ChanDoanVaoKhoa, ChanDoanRaVien, ketquaravien.Dictionary_Name as ketqua, MaGiuong, SUM(SoLuong* DonGiaDoanhThu) as doanhthu,
    YEAR(benhnhan.NgaySinh) as tuoi
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
    trangthairavien.Dictionary_Name, ChanDoanVaoKhoa, ChanDoanRaVien, ketquaravien.Dictionary_Name, MaGiuong
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
    