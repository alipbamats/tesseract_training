#Создание box файла из изображения
 tesseract 8.png  8 -l rus --tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata/ makebox

 for i in *.png; do tesseract $i  ${i%.*} -l rus --tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata/ makebox; done

