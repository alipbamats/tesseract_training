import argparse
import subprocess
import os
import shutil
from pathlib import Path
import re

parser = argparse.ArgumentParser(description="Tesseract results comparison program")

parser.add_argument("--textfile", required=True, type=str, help="Original text file")
parser.add_argument("--traineddata", required=True, type=str, help="Tesseract trained data folder")
parser.add_argument("--lang", required=True, type=str, help="Language name")
parser.add_argument("--fonts_dir", type= str, default="/usr/share/fonts/truetype/msttcorefonts/", help="Fonts location folder")
parser.add_argument("--font", type=str, default="Times New Roman",help="Font name")

args = parser.parse_args()

tmp_folder=Path("~tmp")
if os.path.exists(tmp_folder):
    shutil.rmtree(tmp_folder)
os.mkdir(tmp_folder)

result_file=tmp_folder/"compire"
try:
    # text2image  --text=Example.txt --outputbase=Example.png  --font="Times New Roman" --fonts_dir=/usr/share/fonts/truetype/msttcorefonts/
    shell_command = [
        "text2image",
        "--text={}".format(args.textfile),
        "--outputbase={}".format(result_file.as_posix()),
        "--font={}".format(args.font),
        "--fonts_dir={}".format(args.fonts_dir),
    ]
    process = subprocess.Popen(shell_command)
    process.wait()
except Exception as e:
    print("Error:",e)
    exit(-1)

try:
    # tesseract Example.tif  Example18 -l avar18 --tessdata-dir  ./
    shell_command = [
    "tesseract",
    "{}.tif".format(result_file.as_posix()),
    tmp_folder/args.lang,
    "-l", args.lang,
    "--tessdata-dir", args.traineddata
    ]
    process = subprocess.Popen(shell_command)
    process.wait()
except Exception as e:
    print("Error:",e)
    exit(-1)

cmp_textfile="{}.txt".format(tmp_folder/args.lang)
with open(cmp_textfile) as ocr_textfile, open(args.textfile) as textfile:
    ocr_text=ocr_textfile.read()
    ocr_text=ocr_text.strip()
    ocr_text=ocr_text.replace("\r","")
    ocr_text=ocr_text.replace("\n\n","\n")
    open(cmp_textfile,"w").write(ocr_text)
    text=textfile.read()
    text = text.replace("\r", "")
    text = text.replace("\n\n", "\n")

#git diff --word-diff-regex=. --no-index   Example.txt \~tmp/avar45.txt

try:
    shell_command = ["git", "diff", "--word-diff-regex=.", "--no-index", args.textfile,  cmp_textfile ]
    process = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    git_diff_txt=process.stdout.read()
    git_diff_txt=git_diff_txt.replace("[-\n-]\n","\n")
    open(tmp_folder/"diff.txt","w").write(git_diff_txt)
    diff_list=re.findall(r"\[-\S{1,2}-\]", git_diff_txt)
except Exception as e:
    print("Error:", e)
    exit(-1)
text=text.replace("\r","").replace("\n","")
avar_chars_list=re.findall(r"(гI|гъ|гь|кI|къ|кь|хI|хъ|хь|тI|чI|лъ|цI|ГI|Гъ|Гь|КI|Къ|Кь|ХI|Хъ|Хь|ТI|ЧI|Лъ|ЦI)", text)
print("Percentage of errors: {}%".format(len(diff_list)/len(text)*100))
print("Percentage of errors (avar): {}%".format(len(diff_list)/len(avar_chars_list)*100))
