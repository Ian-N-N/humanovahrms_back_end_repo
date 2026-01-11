import sqlite3
import os

# Adjust path to where we think the DB is
db_path = os.path.join(os.getcwd(), 'instance', 'hrms.db')

print(f"Checking database at: {db_path}")

if not os.path.exists(db_path):
    print("Database file does not exist!")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables found:", tables)
        
        if ('users',) in tables:
            cursor.execute("PRAGMA table_info(users);")
            columns = cursor.fetchall()
            print("Columns in users table:", [col[1] for col in columns])
            
        conn.close()
    except Exception as e:
        print(f"Error inspecting DB: {e}")
