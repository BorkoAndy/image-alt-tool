import os
try:
    path = r"d:\__WEB__\googledescriptiveai\image-alt-tool\api\analyze.py"
    if os.path.exists(path):
        os.remove(path)
        print(f"Successfully deleted {path}")
    else:
        print(f"File not found: {path}")
except Exception as e:
    print(f"Error: {e}")
