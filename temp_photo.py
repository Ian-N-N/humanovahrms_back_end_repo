with open('.env', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if 'CLOUDINARY' in line:
            print(f"[{line.strip()}]")
