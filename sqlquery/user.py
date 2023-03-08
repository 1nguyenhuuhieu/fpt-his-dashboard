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
        print("Lỗi sql login user")
        return None
    
def new_post(time_created,title,body,username, plain_text,cursor):
    sql = """
    INSERT INTO post(time_created,title,body,username,plain_text)
              VALUES(?,?,?,?,?)
    """

    try:
        q = cursor.execute(sql, (time_created,title,body,username,plain_text))
        return True
    except:
        print("Lỗi sql new post")
        return False
    
def delete_post(post_id, cursor):
    sql = """
    DELETE FROM post WHERE post_id=?
    """
    try:
        q = cursor.execute(sql, (post_id))
        return True
    except:
        print("Lỗi sql delete_post")
        return False
    
def posts(cursor):
    sql = """
    SELECT *
    FROM post
    ORDER BY post_id DESC
    """

    try:
        q = cursor.execute(sql).fetchall()
        return q
    except:
        print("Lỗi sql posts")
        return None
    
def post(post_id, cursor):
    sql = """
    SELECT *
    FROM post
    WHERE post_id = ?
    """
    try:
        q = cursor.execute(sql, (post_id,)).fetchone()
        return q
    except:
        print("Lỗi sql post")
        return None  
