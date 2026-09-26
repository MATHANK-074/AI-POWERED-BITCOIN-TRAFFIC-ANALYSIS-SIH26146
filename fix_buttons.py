import os
import glob
import re

def fix_buttons():
    files = glob.glob('frontend/src/**/*.tsx', recursive=True)
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace button text colors where background is dark (brand-600, purple-600, etc)
        content = re.sub(r'(bg-[a-z]+-600[^>]*?text-brand-900.*?)(["\'])', lambda m: m.group(1).replace('text-brand-900 dark:text-brand-100', 'text-white') + m.group(2), content)
        content = re.sub(r'(bg-[a-z]+-600[^>]*?text-brand-900.*?)(["\'])', lambda m: m.group(1).replace('text-brand-900', 'text-white') + m.group(2), content)

        # Cases where text-content-700 is inside dark buttons
        content = re.sub(r'(bg-[a-z]+-600[^>]*?text-content-700.*?)(["\'])', lambda m: m.group(1).replace('text-content-700', 'text-white') + m.group(2), content)

        # Fix specific tables to use text-content-700 instead of brand colors for data
        content = content.replace('text-brand-600 dark:text-brand-400', 'text-brand-600 dark:text-brand-400')
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

fix_buttons()
