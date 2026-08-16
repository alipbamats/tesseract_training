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
parser.add_argument("--verbose","-v", action='store_true', help="Verbose")
args = parser.parse_args()
for root, dirs, files in os.walk(args.dir):
    for file in files:
        if not file.endswith(".box"):
            continue
        file_path=Path(root)/file
        print("File:",file_path)
        with open(file_path,'rb') as file:
            box_text=file.read()
        with open(file_path,'wb') as out_file:
            box_text=box_text.replace(b'\r',b'')
            for box_line in box_text.split(b'\n'):
                match=re.search(rb"(.*)\s(.*)\s(.*)\s(.*)\s(.*)\s(.*)",box_line)
                if match:
                    box_items = [match.group(i) for i in range(1,7)]
                    if box_items[0].hex() =="49":
                        box_items[0]=b"\xd3\x80" #декодируется в кириллическую букву Ӏ (палочка, U+04C0 CYRILLIC LETTER PALOCHKA).
                        if args.verbose:
                            print("-->", "sym: \"{}\", code: \"{}\", ##EDIT".format(match.group(1).decode("utf-8"), match.group(1).hex()))
                        else:
                            print("-->#EDIT")
                    elif box_items[0].hex() =="27":
                        box_items[0]=b"\xcc\x81"  #комбинируемый знак ударения (Combining Acute Accent), который в стандарте Unicode имеет код U+0301 (́).
                        if args.verbose:
                            print("-->", "sym: \"{}\", code: \"{}\", ##EDIT".format(match.group(1).decode("utf-8"), match.group(1).hex()))
                        else:
                            print("-->#EDIT")
                    elif box_items[0].hex() =="3d":
                        box_items[0]=b"\xcc\x84" #U+0305 — комбинируемую надчеркивающую черту
                        if args.verbose:
                            print("-->", "sym: \"{}\", code: \"{}\", ##EDIT".format(match.group(1).decode("utf-8"), match.group(1).hex()))
                        else:
                            print("-->#EDIT")
                    else:
                        if args.verbose:
                            print("-->","sym: \"{}\", code: \"{}\"".format(match.group(1).decode("utf-8"), match.group(1).hex()))

                    new_box_line=b" ".join(box_items)+b"\n"
                    out_file.write(new_box_line)
