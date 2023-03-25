import datetime
def info(sobenhan, cursor):
    sql = """
    SELECT BenhAn_Id, SoBenhAn,SoLuuTru, TenBenhNhan, benhnhan.NgaySinh, benhnhan.DiaChi,
    benhnhan.MaYTe, TenNhanVien, TenPhongBan, ThoiGianVaoKhoa, ThoiGianRaVien, SoNgayDieuTri,
    trangthairavien.Dictionary_Name as trangthai, ChanDoanVaoKhoa, ChanDoanRaVien, ketquaravien.Dictionary_Name as ketqua, MaGiuong, SUM(SoLuong* DonGiaDoanhThu) as doanhthu,
    YEAR(benhnhan.NgaySinh) as tuoi
    FROM BenhAn
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as benhnhan
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

    GROUP BY BenhAn_Id, SoBenhAn,SoLuuTru, TenBenhNhan, benhnhan.NgaySinh, benhnhan.DiaChi,
    benhnhan.MaYTe, TenNhanVien, TenPhongBan, ThoiGianVaoKhoa, ThoiGianRaVien, SoNgayDieuTri,
    trangthairavien.Dictionary_Name, ChanDoanVaoKhoa, ChanDoanRaVien, ketquaravien.Dictionary_Name, MaGiuong
    """
    try:
        row = cursor.execute(sql, sobenhan).fetchone()
        row.NgaySinh = row.NgaySinh.strftime("%d/%m/%Y")
        row.ThoiGianVaoKhoa = row.ThoiGianVaoKhoa.strftime("%H:%M %d/%m/%Y")
        row.ThoiGianRaVien = row.ThoiGianRaVien.strftime("%H:%M %d/%m/%Y")
        row.SoNgayDieuTri = int(row.SoNgayDieuTri)
        row.doanhthu = f'{round(int(row.doanhthu)/1000)*1000:,}' 
        row.tuoi = datetime.date.today().year - row.tuoi
        return row
    except:
        print("Lỗi query medical_record.info")
        return None
