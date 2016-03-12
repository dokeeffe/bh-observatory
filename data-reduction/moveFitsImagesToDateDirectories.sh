#!/usr/bin/env bash
BASE_DIR=/home/dokeeffe/Pictures


#Rename new to fits for any solved images
for file in *.new; do
    mv "$file" "'basename $file .new'.fits"
done

find . -maxdepth 1 -name "*.fits" | while IFS= read -r file
do 
    year="$(date -d "$(stat -c %y "$file")" +%Y)"
    month="$(date -d "$(stat -c %y "$file")" +%m)"
    day="$(date -d "$(stat -c %y "$file")" +%d)"
    echo "moving $file to  $year/$month/$day"

    ## Create the directories if they don't exist. The -p flag
    ## makes 'mkdir' create the parent directories as needed so
    ## you don't need to create $year explicitly.
    [[ ! -d "$BASE_DIR/$year/$month/$day" ]] && mkdir -p "$BASE_DIR/$year/$month/$day"; 

    ## Move the file
    mv "$file" "$BASE_DIR/$year/$month/$day"
done
