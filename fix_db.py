import sqlite3
import os

# Path to the database
db_path = os.path.join('instance', 'hrms.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Attempting to add 'hours_worked' column to 'attendance' table...")
    cursor.execute("ALTER TABLE attendance ADD COLUMN hours_worked FLOAT DEFAULT 0.0")
    conn.commit()
    print("✅ Successfully added 'hours_worked' column.")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("ℹ️ Column 'hours_worked' already exists.")
    else:
        print(f"❌ Error: {e}")
finally:
    conn.close()
