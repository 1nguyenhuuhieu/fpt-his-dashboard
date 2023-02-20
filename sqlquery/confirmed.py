# Chi tiết xác nhận theo tiếp nhận id
def detail(tiepnhan_id, cursor):
    print(tiepnhan_id)
    try:
        query = """
        SELECT
        SoTiepNhan, ThoiGianTiepNhan, MaYTe, TenBenhNhan
        FROM TiepNhan
        INNER JOIN [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan]
        ON TiepNhan.BenhNhan_Id = [eHospital_NgheAn_Dictionary].[dbo].[DM_BenhNhan].BenhNhan_Id
        WHERE TiepNhan.TiepNhan_Id = ?
        """

        q = cursor.execute(query, tiepnhan_id).fetchone()

        return q
    except:
        print("Lỗi query confirmed_detail")
        return None       

# SQL query số lượt xác nhận theo loại ngoại trú hoặc nội trú
def visited_hospitalized_day(day, loai, cursor):
    try:
        q = cursor.execute(
            """
            SELECT  
            COALESCE(COUNT(TiepNhan.TiepNhan_Id),0)
            FROM TiepNhan
            INNER JOIN XacNhanChiPhi
            ON TiepNhan.TiepNhan_Id = XacNhanChiPhi.TiepNhan_Id
            WHERE XacNhanChiPhi.NgayXacNhan = ?
            AND Loai=?
            """, day, loai
        ).fetchone()[0]

        return q
    except:
        print("Lỗi query confirmed.visited_hospitalized_day")
        return None
    