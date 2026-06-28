import subprocess
import os

process = subprocess.Popen(['tesseract'], text=True)

for subdir, dirs, files in os.walk("./"):
    print(subdir)
    print(dirs)
    print(files)