#!/bin/bash

# Script to generate resources.md with dynamic file listing

RESOURCES_DIR="resources"
OUTPUT_FILE="resources_list.md"

# Start fresh by overwriting the file each time
echo "## Available resources" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Check if resources directory exists
if [ ! -d "$RESOURCES_DIR" ]; then
    echo "⚠️ Resources directory not found." >> $OUTPUT_FILE
    exit 1
fi

# Count and list HTML files
html_files=$(find $RESOURCES_DIR -name "*.html" | wc -l)

if [ $html_files -eq 0 ]; then
    echo "No HTML files found in resources directory." >> $OUTPUT_FILE
else
    # List all HTML files with relative paths
    find $RESOURCES_DIR -name "*.html" | sort | while read file; do
        filename=$(basename "$file" .html)

        # Convert filename to sentence case for link text
        link_text=$(echo "$filename" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')

        relative_path="${file#./}"  # Remove leading ./ if present
        echo "- [$link_text]($relative_path)" >> $OUTPUT_FILE
    done
fi

echo "" >> $OUTPUT_FILE
echo "*Last generated: $(date)*" >> $OUTPUT_FILE

echo "✅ Resources list generated: $OUTPUT_FILE"
