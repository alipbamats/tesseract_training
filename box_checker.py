import re
import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser(
    description=""
)

# 2. Add arguments
# Required positional argument
parser.add_argument("--dir", type=str, help="")
args = parser.parse_args()
for root, dirs, files in os.walk(args.dir):
    for file in files:
        if not file.endswith(".box"):
            continue
        file_path=Path(root)/file
        print(file_path)
        with open(file_path,'rb') as file:
            box_text=file.read()
        with open(file_path,'wb') as out_file:
            for box_line in box_text.split(b'\r\n'):
                match=re.search(rb"(.*)\s(.*)\s(.*)\s(.*)\s(.*)\s(.*)",box_line)
                if match:
                    print(match.group(1).hex(),match.group(1).decode("utf-8"))
                    box_items = [match.group(i) for i in range(1,7)]
                    if box_items[0].hex() == "d380":
                        box_items[0]=b"\x49"
                    new_box_line=b" ".join(box_items)+b"\r\n"
                    out_file.write(new_box_line)
