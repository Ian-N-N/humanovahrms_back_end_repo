import sqlite3

conn = sqlite3.connect('instance/hrms.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for t in tables:
    print(f"  - {t[0]}")

# Check if system_settings exists
if ('system_settings',) in tables:
    print("\nsystem_settings table EXISTS")
    cursor.execute("PRAGMA table_info(system_settings);")
    cols = cursor.fetchall()
    print("Columns:")
    for c in cols:
        print(f"  {c[1]} ({c[2]})")
else:
    print("\nsystem_settings table DOES NOT EXIST")

conn.close()
