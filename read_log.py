import sys

try:
    with open('sim_result.txt', 'r', encoding='utf-16') as f:
        print(f.read())
except Exception as e:
    print("UTF-16 failed, trying latin-1")
    try:
        with open('sim_result.txt', 'r', encoding='latin-1') as f:
            print(f.read())
    except Exception as e2:
        print(f"Read failed: {e2}")
