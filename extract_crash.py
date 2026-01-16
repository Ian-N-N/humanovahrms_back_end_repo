import traceback

try:
    with open('sim_result.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    with open('sim_result.txt', 'r', encoding='latin-1') as f:
        content = f.read()

if "CRASH DETECTED" in content:
    idx = content.find("CRASH DETECTED")
    print(content[idx:idx+1000]) # Print 1000 chars after the crash marker
else:
    print("Crash marker not found. Full content tail:")
    print(content[-500:])
