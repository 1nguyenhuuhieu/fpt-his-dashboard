# Kiểm tra thông tin đăng nhập
def login_user(user, pwd, cursor):
    query = """
    SELECT *
    FROM user
    WHERE user_name = ? AND password = ?
    """
    try:
        q = cursor.execute(query, (user, pwd)).fetchone()
        return q
    except:
        return None