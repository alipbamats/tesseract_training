shopt -s nullglob

for file in *.png; do
    echo "Processing: $file, ${file%.*}"
    # Your command here, e.g., cat "$file"
    tesseract $file ${file%.*} --psm 6 -l rus lstm.train
done

