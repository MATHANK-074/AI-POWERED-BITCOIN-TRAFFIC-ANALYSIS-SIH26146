import os
import re

def replace_classes(content):
    content = re.sub(r'divide-slate-800(?:/60)?', 'divide-surface-300', content)
    content = re.sub(r'hover:text-cyan-300', 'hover:text-brand-500', content)
    content = re.sub(r'border-cyan-500/20', 'border-brand-200', content)
    return content

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                if file == 'Navbar.tsx':
                    continue
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = replace_classes(content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f'Updated {filepath}')

if __name__ == '__main__':
    process_directory('src/pages')
    process_directory('src/components')
