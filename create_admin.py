import pymysql
from werkzeug.security import generate_password_hash

# 1. Connection setup
try:
    db = pymysql.connect(
        host="192.168.1.4", 
        user="root", 
        password="aslamkj123", 
        database="attendance_db"
    )
    cur = db.cursor()

    username = "admin"
    password = "123" 
    hashed_pw = generate_password_hash(password)

    # 2. This query FORCES the password to update even if the user exists
    sql = """
    INSERT INTO users (username, password_hash) 
    VALUES (%s, %s) 
    ON DUPLICATE KEY UPDATE password_hash = %s
    """
    
    cur.execute(sql, (username, hashed_pw, hashed_pw))
    db.commit()
    
    print(f"--- SUCCESS ---")
    print(f"User '{username}' password has been FORCED to '{password}'")
    print(f"New Hash stored: {hashed_pw[:20]}...")

except Exception as e:
    print(f"ERROR: {e}")

finally:
    if 'db' in locals():
        db.close()