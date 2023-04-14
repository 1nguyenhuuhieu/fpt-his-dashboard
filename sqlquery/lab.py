def lab_result(start, end, cursor):
    query1 = """
    SELECT SoPhieuYeuCau, dm_benhnhan.MaYTe,
    dm_benhnhan.TenBenhNhan, 
    ThoiGianYeuCau,
    resultdetail.BarCodeID,
    dm_dichvu.TenDichVu as tendichvu, resultdetail.ResultDateTime as thoigianketqua,
    labresult.ResultID
    FROM
    CLSYeuCau
    INNER JOIN [eLab_NgheAn].[dbo].[LabResult] as labresult
    ON CLSYeuCau.CLSYeuCau_Id = labresult.RequestID
    INNER JOIN eLab_NgheAn.dbo.LabResultDetail as resultdetail
    ON labresult.ResultID = resultdetail.ResultID
    INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_DichVu as dm_dichvu
    ON resultdetail.ServiceID = dm_dichvu.DichVu_Id
    INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_BenhNhan as dm_benhnhan
    ON CLSYeuCau.BenhNhan_Id = dm_benhnhan.BenhNhan_Id
    WHERE CLSYeuCau.ThoiGianYeuCau BETWEEN ?  AND ?
    ORDER BY ThoiGianYeuCau DESC

    """
    query = """
    SELECT SoPhieuYeuCau, dm_benhnhan.MaYTe,
    dm_benhnhan.TenBenhNhan, 
    ThoiGianYeuCau,
    resultdetail.BarCodeID,
    NoiDungChiTiet as tendichvu, labresult.ResultDateTime as thoigianketqua,
    labresult.ResultID
    FROM
    CLSYeuCau
    INNER JOIN [eLab_NgheAn].[dbo].[LabResult] as labresult
    ON CLSYeuCau.CLSYeuCau_Id = labresult.RequestID
    INNER JOIN eHospital_NgheAn_Dictionary.dbo.DM_BenhNhan as dm_benhnhan
    ON CLSYeuCau.BenhNhan_Id = dm_benhnhan.BenhNhan_Id
    WHERE CLSYeuCau.ThoiGianYeuCau BETWEEN ?  AND ?
    ORDER BY ThoiGianYeuCau DESC

    """
    try:
        q = cursor.execute(query1, start, end).fetchall()
        for row in q:
            row.ThoiGianYeuCau = row.ThoiGianYeuCau.strftime("%Y-%m-%d %H:%M")
        return q
    except:
        print("Lỗi khi query lab.lab_result")
        return None  
       