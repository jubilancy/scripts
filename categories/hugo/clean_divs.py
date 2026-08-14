import os

content_dir = './content'
id_strings = [
    '<div id="header-container"></div>',
    '<div id="head-container"></div>'
]

for root, dirs, files in os.walk(content_dir):
    for file in files:
        if file.endswith('.md') or file.endswith('.html'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            original_content = content
            for id_str in id_strings:
                content = content.replace(id_str, '')
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Cleaned {file_path}")

print("Finished cleaning content files.")
