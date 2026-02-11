import pymysql
from werkzeug.security import generate_password_hash

db = pymysql.connect(host="192.168.1.4", user="root", password="aslamkj123", database="attendance_db")
cursor = db.cursor()

# Clear and Reset
cursor.execute("DELETE FROM users")
password_to_hash = "123"
hashed_password = generate_password_hash(password_to_hash)

cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", ("admin", hashed_password))
db.commit()
db.close()
print("Done! Login with username 'admin' and password '123'")