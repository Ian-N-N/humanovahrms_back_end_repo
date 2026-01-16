import sqlite3

conn = sqlite3.connect('instance/hrms.db')
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(employees);")
cols = [col[1] for col in cursor.fetchall()]

if 'employee_number' not in cols:
    print("Adding employee_number column...")
    cursor.execute("ALTER TABLE employees ADD COLUMN employee_number VARCHAR(20);")
    conn.commit()
    print("Column added successfully!")
    
    # Generate employee numbers for existing employees
    cursor.execute("""
        SELECT e.id, d.name 
        FROM employees e 
        LEFT JOIN departments d ON e.department_id = d.id
    """)
    rows = cursor.fetchall()
    
    for emp_id, dept_name in rows:
        prefix = "GEN"
        if dept_name:
            name = dept_name.strip().upper()
            if len(name) <= 3:
                prefix = name
            else:
                consonants = ''.join([c for c in name if c not in 'AEIOU '])
                if len(consonants) >= 3:
                    prefix = consonants[:3]
                else:
                    prefix = name[:3]
        
        emp_number = f"{prefix}-{str(emp_id).zfill(3)}"
        cursor.execute("UPDATE employees SET employee_number = ? WHERE id = ?", (emp_number, emp_id))
        print(f"  Updated employee {emp_id} -> {emp_number}")
    
    conn.commit()
    print("All existing employees updated with employee numbers!")
else:
    print("employee_number column already exists")

conn.close()
