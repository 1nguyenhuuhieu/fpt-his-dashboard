# Lấy danh sách tiếp nhận ID đã xác nhận chi phí trong ngày
def list_tiepnhan_id(day, cursor):
    query = """
    SELECT TiepNhan_Id
    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    WHERE NgayXacNhan = '2023-03-01'
    """
    try:
        q = cursor.excute(query).fetchall()
        return q
    except:
        print('Lỗi query report.list_tiepnhan_id')
        return None

# Lấy thông tin bệnh nhân từ số tiếp nhận


def patient_info(tiepnhan_id, cursor):
    query = """
    SELECT MaYTe, TenBenhNhan, NgaySinh, GioiTinh, DiaChi, TiepNhan.SoBHYT, BHYTTuNgay, BHYTDenNgay, MaBenh, BenhKhac, XacNhanChiPhi.NgayVao, XacNhanChiPhi.NgayRa, TenPhongKham,
    SUM(XacNhanChiPhiChiTiet.SoLuong*XacNhanChiPhiChiTiet.DonGiaDoanhThu) as 'Tổng Doanh Thu',
    SUM(XacNhanChiPhiChiTiet.SoLuong*XacNhanChiPhiChiTiet.DonGiaHoTroChiTra) as 'Tổng Bảo Hiểm thanh toán',
    SUM(XacNhanChiPhiChiTiet.SoLuong*XacNhanChiPhiChiTiet.DonGiaThanhToan) as 'Tổng Bệnh nhân thanh toán'
    FROM TiepNhan
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan] as DM_BenhNhan
    ON DM_BenhNhan.BenhNhan_Id = TiepNhan.BenhNhan_Id
    INNER JOIN XacNhanChiPhi
    ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    WHERE TiepNhan.TiepNhan_Id = ?
    GROUP BY MaYTe, TenBenhNhan, NgaySinh, GioiTinh, DiaChi, TiepNhan.SoBHYT, BHYTTuNgay, BHYTDenNgay, MaBenh, BenhKhac, XacNhanChiPhi.NgayVao, XacNhanChiPhi.NgayRa, TenPhongKham
    """

    try:
        q = cursor.excute(query, tiepnhan_id).fetchone()
        return q
    except:
        print('Lỗi query report.patient_info')
        return None


# Lấy chi tiết chi phí xác nhận theo từng mục
def service_money(tiepnhan_id, cursor):
    query = """
    SELECT
    SUM(Soluong*DonGiaDoanhThu) as 'Doanh Thu',
        (CASE
        WHEN TenNhomDichVu IN(N'XN HÓA SINH',
        N'XN HÓA SINH NƯỚC TIỂU',
        N'XN HUYẾT HỌC',
        N'XN VI SINH, KÝ SINH TRÙNG') THEN N'Tiền xét nghiệm'
        WHEN TenNhomDichVu IN(N'CT-SCANNER',
        N'ĐIỆN NÃO ĐỒ, LƯU HUYẾT NÃO',
        N'NỘI SOI CHẨN ĐOÁN CAN THIỆP',
        N'NỘI SOI TAI-MŨI-HỌNG',
        N'SIÊU ÂM',
        N'SIÊU ÂM MÀU',
        N'THĂM DÒ CHỨC NĂNG',
        N'X-QUANG KTS') THEN N'Tiền CĐHA'
        WHEN TenNhomDichVu IN(
        N'I.HỒI SỨC CẤP CỨU VÀ CHỐNG ĐỘC',
        N'II. NỘI KHOA',
        N'III. NHI KHOA',
        N'IX. GÂY MÊ HỒI SỨC',
        N'V. DA LIỄU',
        N'VII. NỘI TIẾT',
        N'VIII. Y HỌC CỔ TRUYỀN',
        N'X. NGOẠI KHOA',
        N'XI. BỎNG',
        N'XII. UNG BƯỚU',
        N'XIII. PHỤ SẢN',
        N'XIV. MẮT',
        N'XV. TAI MŨI HỌNG',
        N'XVI. RĂNG HÀM MẶT',
        N'XVII. PHỤC HỒI CHỨC NĂNG',
        N'XXI. THĂM DÒ CHỨC NĂNG',
        N'XXVII. PHẪU THUẬT NỘI SOI',
        N'XXVIII. PHẪU THUẬT TẠO HÌNH THẨM MỸ',
        N'PHẪU THUẬT MẮT',
        N'PHẪU THUẬT RĂNG HÀM MẶT',
        N'PHẪU THUẬT TAI - MŨI - HỌNG') THEN N'Tiền Phẫu thuật, thủ thuật'
        WHEN TenNhomDichVu IN(N'Số ml máu truyền') THEN N'Tiền máu'
        WHEN TenNhomDichVu IN(N'Giường bệnh',
        N'NGÀY GIƯỜNG BAN NGÀY') THEN N'Tiền Giường'
        WHEN TenNhomDichVu IN(N'KHÁM BỆNH') THEN N'Tiền Khám'
        WHEN TenNhomDichVu IN(N'VẬN CHUYỂN') THEN N'Tiền vận chuyển'
        WHEN TenNhomDichVu IS NULL THEN N'Tiền thuốc'

        ELSE TenNhomDichVu
        END) AS  'group_name'

    FROM XacNhanChiPhi
    INNER JOIN XacNhanChiPhiChiTiet
    ON XacNhanChiPhi.XacNhanChiPhi_Id = XacNhanChiPhiChiTiet.XacNhanChiPhi_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_DichVu]
    ON XacNhanChiPhiChiTiet.NoiDung_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_DichVu].DichVu_Id
    LEFT JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_NhomDichVu]
    ON [eHospital_NgheAn_Dictionary].[dbo].[DM_DichVu].NhomDichVu_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_NhomDichVu].NhomDichVu_Id
    INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
    ON XacNhanChiPhi.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id

    WHERE XacNhanChiPhi.TiepNhan_Id = ?

    GROUP BY
        (CASE
        WHEN TenNhomDichVu IN(N'XN HÓA SINH',
        N'XN HÓA SINH NƯỚC TIỂU',
        N'XN HUYẾT HỌC',
        N'XN VI SINH, KÝ SINH TRÙNG') THEN N'Tiền xét nghiệm'
        WHEN TenNhomDichVu IN(N'CT-SCANNER',
        N'ĐIỆN NÃO ĐỒ, LƯU HUYẾT NÃO',
        N'NỘI SOI CHẨN ĐOÁN CAN THIỆP',
        N'NỘI SOI TAI-MŨI-HỌNG',
        N'SIÊU ÂM',
        N'SIÊU ÂM MÀU',
        N'THĂM DÒ CHỨC NĂNG',
        N'X-QUANG KTS') THEN N'Tiền CĐHA'
        WHEN TenNhomDichVu IN(
        N'I.HỒI SỨC CẤP CỨU VÀ CHỐNG ĐỘC',
        N'II. NỘI KHOA',
        N'III. NHI KHOA',
        N'IX. GÂY MÊ HỒI SỨC',
        N'V. DA LIỄU',
        N'VII. NỘI TIẾT',
        N'VIII. Y HỌC CỔ TRUYỀN',
        N'X. NGOẠI KHOA',
        N'XI. BỎNG',
        N'XII. UNG BƯỚU',
        N'XIII. PHỤ SẢN',
        N'XIV. MẮT',
        N'XV. TAI MŨI HỌNG',
        N'XVI. RĂNG HÀM MẶT',
        N'XVII. PHỤC HỒI CHỨC NĂNG',
        N'XXI. THĂM DÒ CHỨC NĂNG',
        N'XXVII. PHẪU THUẬT NỘI SOI',
        N'XXVIII. PHẪU THUẬT TẠO HÌNH THẨM MỸ',
        N'PHẪU THUẬT MẮT',
        N'PHẪU THUẬT RĂNG HÀM MẶT',
        N'PHẪU THUẬT TAI - MŨI - HỌNG') THEN N'Tiền Phẫu thuật, thủ thuật'
        WHEN TenNhomDichVu IN(N'Số ml máu truyền') THEN N'Tiền máu'
        WHEN TenNhomDichVu IN(N'Giường bệnh',
        N'NGÀY GIƯỜNG BAN NGÀY') THEN N'Tiền Giường'
        WHEN TenNhomDichVu IN(N'KHÁM BỆNH') THEN N'Tiền Khám'
        WHEN TenNhomDichVu IN(N'VẬN CHUYỂN') THEN N'Tiền vận chuyển'
        WHEN TenNhomDichVu IS NULL THEN N'Tiền thuốc'

        ELSE TenNhomDichVu
        END)
    """
    try:
        q = cursor.excute(query, tiepnhan_id).fetchall()
        return q
    except:
        print('Lỗi query report.service_money')
        return None
