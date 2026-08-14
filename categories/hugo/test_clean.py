filepath = './content/flexbox.md'  # Change to your test file

header_identifiers = ['{#header-container}', '{#head-container}']
footer_identifier = '{#footer-container}'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find end of front matter (--- lines)
front_matter_end = None
if lines and lines[0].strip() == '---':
    for idx in range(1, len(lines)):
        if lines[idx].strip() == '---':
            front_matter_end = idx
            break

content_start = (front_matter_end + 1) if front_matter_end is not None else 0
content_lines = lines[content_start:]

# Remove any lines containing header identifiers anywhere
content_lines = [line for line in content_lines if not any(idf in line for idf in header_identifiers)]

cleaned_lines = lines[:content_start] + content_lines

# Remove last line if it contains the footer identifier
if cleaned_lines and footer_identifier in cleaned_lines[-1]:
    cleaned_lines.pop()

output_path = './content/flexbox_cleaned.md'  # Output path
with open(output_path, 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print("Cleaned file saved to " + output_path)
