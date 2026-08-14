#!/bin/bash

# Base content directory path
base_dir="/Users/elianatamrat/Desktop/myhugosite/content"

# List of folder names
folders=("favorite" "img" "links" "tools" "computer" "notes" "research")

for folder in "${folders[@]}"; do
  folder_path="$base_dir/$folder"
  mkdir -p "$folder_path"  # Ensure folder exists
  index_file="$folder_path/index.md"
  
  # Create index.md with Hugo front matter
  cat > "$index_file" <<EOF
---
title: "$folder"
date: $(date +"%Y-%m-%dT%H:%M:%S%z")
draft: false
---

# $folder

This is the index page for the $folder section.
EOF

  echo "Created $index_file"
done
