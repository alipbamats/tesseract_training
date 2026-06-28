import subprocess
import os
from pathlib import Path
import shutil
import hashlib


def clear_work_space(files: list):
    for file in files:
        if os.path.isfile(file):
            os.remove(file)
        if os.path.isdir(file):
            shutil.rmtree(file)
def get_files_by_extension(path: Path, extension: str) -> dict:
    files_dict = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith(extension):
                continue
            if root not in files_dict:
                files_dict[root] = []
            files_dict[root].append(file)

    return files_dict
def del_files_in_folder(path: Path):
    for file in os.listdir(path):
        file_path = path / file
        os.remove(file_path)
def create_unicharset(sources: Path, box_files_dir: Path):
    box_files = get_files_by_extension(path=sources, extension=".box")

    # Если не существует, то создаем директорию box_files_dir
    if not os.path.isdir(box_files_dir):
        os.mkdir(box_files_dir)

    # Копируем все *.box файлы в директорию box_files_dir
    for folder, files in box_files.items():
        for file in files:
            file_path = Path(folder) / file
            file_path_sha256 = hashlib.sha256(str(file_path).encode("utf-8")).hexdigest() + ".box"
            shutil.copy(Path(folder) / file, box_files_dir / file_path_sha256)

    shell_command = ['unicharset_extractor',
                     "--output_unicharset", "train/avar.unicharset",
                     "--norm_mode", "2", Path(box_files_dir / "*.box").as_posix()]

    process = subprocess.Popen(" ".join(shell_command), shell=True)
    process.wait()
def create_lstmf_files(sources: Path):
    box_files = get_files_by_extension(path=sources, extension=".box")
    for folder, files in box_files.items():
        for file in files:
            png_file_name= "{}.png".format(Path(file).stem)
            png_file_path = str(Path(folder)/png_file_name)
            box_file_path = str(Path(folder)/Path(file).stem)
            shell_command = ['tesseract',
                             "\'{}\'".format(png_file_path),
                             "\'{}\'".format(box_file_path),
                             "--psm", "6", "lstm.train"]
            process = subprocess.Popen(" ".join(shell_command), shell=True)
            process.wait()
def create_combine_lang_model(unicharset_file: Path, language_data: Path, out: Path, language: str):
    wordlist=language_data/language/"{}.wordlist".format(language)
    if not os.path.isfile(wordlist):
        print("Error: the file \"{}\" doesn't exist".format(wordlist))
        return
    numbers=language_data/language/"{}.numbers".format(language)
    if not os.path.isfile(numbers):
        print("Error: the file \"{}\" doesn't exist".format(numbers))
        return
    punc=language_data/language/"{}.punc".format(language)
    if not os.path.isfile(punc):
        print("Error: the file \"{}\" doesn't exist".format(punc))
        return

    if not os.path.isdir(out):
        os.mkdir(out)
    '''
    	combine_lang_model \
			--input_unicharset avar.unicharset \
	  	--script_dir langdata_lstm  \
	  	--words langdata_lstm/avar/avar.wordlist \
  		--numbers langdata_lstm/avar/avar.numbers  \
	  	--puncs langdata_lstm/avar/avar.punc  \
	  	--output_dir avar_trained/ --lang avar
    '''
    shell_command = ['combine_lang_model',
                     "--input_unicharset", str(unicharset_file),
                     "--script_dir", str(language_data),
                     "--words", str(wordlist),
                     "--numbers",str(numbers),
                     "--puncs", str(punc),
                     "--output_dir", str(out),
                     "--lang",str(language)]
    process = subprocess.Popen(" ".join(shell_command), shell=True)
    process.wait()
def train_model(sources: Path,
                out: Path,
                init_lstm: Path,
                old_traineddata: Path,
                traineddata: Path,
                unicharset_file: Path,
                train_files_list: Path,
                eval_files_list: Path,
                max_iterations: int = 500):

    lstmf_files=get_files_by_extension(sources, "lstmf")
    try:
        with open(train_files_list,"w") as train_file, open(eval_files_list,"w") as eval_file:
            for folder, files in lstmf_files.items():
                count = 0
                for file in files:
                    if count % 5 == 0:
                        eval_file.write(str(Path(folder) / file) + "\n")
                    else:
                        train_file.write(str(Path(folder) / file) + "\n")
                    count += 1
    except Exception as e:
        print("Error:",e)
        return
    if not os.path.isdir(out):
        os.mkdir(out)
    shell_command = ['lstmtraining',
                     "--model_output", str(out)+"/",
                     "--continue_from", str(init_lstm),
                     "--old_traineddata", str(old_traineddata),
                     "--traineddata", str(traineddata),
                     "--train_listfile", str(train_files_list),
                     "--eval_listfile", str(eval_files_list),
                     "--U", str(unicharset_file),
                     "--max_iterations", str(max_iterations)]
    print(" ".join(shell_command))
    process = subprocess.Popen(" ".join(shell_command), shell=True)
    process.wait()

lang="avar"
train_dir=Path(".")/"train"
box_files_dir = Path(".") / train_dir / "box"
unicharset_file = Path(".") / train_dir / "{}.unicharset".format(lang)
pre_trained=train_dir/"avar_trained"
sources=Path(".")/"sources"
language_data=train_dir/"langdata_lstm"
train_out_dir = train_dir/"out"
train_files_list_file=train_dir/"{}.train_files.txt".format(lang)
eval_files_list_file=train_dir/"{}.eval_files.txt".format(lang)

work_space_files=[str(box_files_dir),
                  str(unicharset_file),
                  str(pre_trained),
                  str(train_files_list_file),
                  str(eval_files_list_file),
                  str(train_out_dir)]

lstmf_files=get_files_by_extension(path=sources, extension=".lstmf")
for folder, files in lstmf_files.items():
    work_space_files.extend([str(Path(folder)/file) for file in files])

clear_work_space(files=work_space_files)
create_unicharset(sources=sources, box_files_dir=box_files_dir)
create_lstmf_files(sources=sources)
create_combine_lang_model(unicharset_file=unicharset_file,
                          language_data=language_data,
                          out=pre_trained,
                          language=lang)
train_model(sources=sources,
            out=train_out_dir,
            init_lstm=train_dir/"rus.lstm",
            old_traineddata=train_dir/"testdata_best"/"rus.traineddata",
            traineddata=pre_trained/lang/"{}.traineddata".format(lang),
            unicharset_file=unicharset_file,
            train_files_list=train_files_list_file,
            eval_files_list=eval_files_list_file)

