import os
import glob

def replace_in_files():
    files = glob.glob('frontend/src/**/*.tsx', recursive=True)
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace hardcoded brand text colors with adaptive ones
        content = content.replace('text-brand-900', 'text-brand-900 dark:text-brand-100')
        content = content.replace('text-brand-800', 'text-brand-800 dark:text-brand-200')
        content = content.replace('text-brand-700', 'text-brand-700 dark:text-brand-300')
        content = content.replace('text-brand-600', 'text-brand-600 dark:text-brand-400')
        
        # Fix inputs that have dark text but no background specification, or just give them standard text
        # Actually, let's fix bg-surface-100 borders and text
        # If an input has bg-surface-100, it will have light text natively if it doesn't specify text color.
        # But some inputs specify text-content-700, which is adaptive.

        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

replace_in_files()
