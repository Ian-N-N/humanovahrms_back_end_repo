import os

log_path = 'error.log'
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        lines = f.readlines()
        print("LAST_LOG_LINES:")
        for line in lines[-50:]:
            print(line.strip())
else:
    print("Log file not found.")
