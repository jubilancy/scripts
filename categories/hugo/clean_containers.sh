#!/bin/bash

find content/ -type f \( -name "*.md" -o -name "*.html" \) | while read file; do
  sed -i '' '/^::: *{#header-container} *:::/d' "$file"
  sed -i '' '/^::: *{#head-container} *:::/d' "$file"
  
  tac "$file" | sed -e '/^::: *{#footer-container} *:::/d' | tac > "$file.tmp" 
  mv "$file.tmp" "$file"

  echo "Cleaned $file"
done

echo "All content files cleaned!"

