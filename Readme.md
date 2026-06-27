# Извлечение файлов из оригинальной модели

	combine_tessdata -u ~/tesseract_training/tessdata-main/tessdata-main/rus.traineddata ./rus_original/

# Создание box файла из изображения

	 tesseract 8.png  8 -l rus --tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata/ makebox

	 for i in *.png; do tesseract $i  ${i%.*} -l rus --tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata/ makebox; done
 
# Создать исходный .lstm файл

	combine_tessdata -e /usr/share/tesseract-ocr/4.00/tessdata/rus.traineddata ./rus.lstm

# Создать справочник символов из .box файлов

	$ unicharset_extractor  --output_unicharset train/avar.unicharset  --norm_mode 2 some_folder/*.box

# Создание начальной модели

	combine_lang_model \
			--input_unicharset avar.unicharset \
	  	--script_dir langdata_lstm  \
	  	--words langdata_lstm/avar/avar.wordlist \
  		--numbers langdata_lstm/avar/avar.numbers  \
	  	--puncs langdata_lstm/avar/avar.punc  \
	  	--output_dir avar_trained/ --lang avar

# Непосредственно обучение модели из полученных данных
	lstmtraining \
	  	--model_output out/ \
	  	--continue_from rus.lstm \
	  	--old_traineddata testdata_best/rus.traineddata \
	  	--traineddata avar_trained/avar/avar.traineddata \
	  	--train_listfile train/avar.training_files.txt \
	  	--eval_listfile eval/avar.training_files.txt  \
	  	--U avar.unicharset \
	  	--max_iterations 500

# Сборка результатов

	 lstmtraining \
		--stop_training \
  		--continue_from out/probability.checkpoint \
	  	--traineddata avar_trained/avar/avar.traineddata \
	  	--model_output out/avar.traineddata
# Каждое слово в верхний регистр
	 cat wordlist_lower.txt | sed -r "s/([а-я]{1})(.*)/\u\1\2/g" > wordlist_cap.txt
