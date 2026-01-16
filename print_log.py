try:
    with open('sim_result.txt', 'r', encoding='utf-16') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[-30:]):
            print(f"LINE {i}: {line.strip()}")
except Exception as e:
    print(f"Error reading with utf-16: {e}")
    with open('sim_result.txt', 'r', encoding='latin-1') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[-30:]):
            print(f"LINE {i}: {line.strip()}")
