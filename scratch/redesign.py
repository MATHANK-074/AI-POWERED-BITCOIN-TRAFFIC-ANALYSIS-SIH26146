import os
import re

def replace_classes(content):
    # Backgrounds
    content = re.sub(r'bg-slate-950/?\d*', 'bg-surface-50', content)
    content = re.sub(r'bg-slate-900/?\d*', 'bg-surface-100', content)
    content = re.sub(r'bg-slate-800/?\d*', 'bg-surface-200', content)
    content = re.sub(r'bg-slate-700/?\d*', 'bg-surface-300', content)
    
    # Texts
    content = re.sub(r'text-slate-100', 'text-content-700', content)
    content = re.sub(r'text-slate-200', 'text-brand-900', content)
    content = re.sub(r'text-white', 'text-brand-900', content)
    content = re.sub(r'text-slate-300', 'text-content-600', content)
    content = re.sub(r'text-slate-400', 'text-content-500', content)
    content = re.sub(r'text-slate-500', 'text-content-400', content)

    # Borders
    content = re.sub(r'border-slate-800/?\d*', 'border-surface-300', content)
    content = re.sub(r'border-slate-700/?\d*', 'border-surface-400', content)
    content = re.sub(r'border-slate-900/?\d*', 'border-surface-200', content)

    # Theme colors
    content = re.sub(r'cyan-400', 'brand-600', content)
    content = re.sub(r'cyan-500', 'brand-500', content)
    content = re.sub(r'cyan-600', 'brand-600', content)
    content = re.sub(r'cyan-900', 'brand-200', content)
    content = re.sub(r'cyan-950', 'brand-100', content)
    
    # Gradients
    content = re.sub(r'from-cyan-600', 'from-brand-600', content)
    content = re.sub(r'to-blue-600', 'to-brand-700', content)
    content = re.sub(r'hover:from-cyan-500', 'hover:from-brand-500', content)
    content = re.sub(r'hover:to-blue-500', 'hover:to-brand-600', content)
    
    # Specific semantic colors
    content = re.sub(r'text-emerald-400', 'text-verified-600', content)
    content = re.sub(r'bg-emerald-500/10', 'bg-verified-50', content)
    content = re.sub(r'border-emerald-500/20', 'border-verified-500', content)
    content = re.sub(r'emerald', 'verified', content)

    content = re.sub(r'text-rose-400', 'text-critical-600', content)
    content = re.sub(r'bg-rose-500/20', 'bg-critical-50', content)
    content = re.sub(r'border-rose-500/30', 'border-critical-500', content)
    content = re.sub(r'rose', 'critical', content)

    content = re.sub(r'text-amber-400', 'text-warning-600', content)
    content = re.sub(r'bg-amber-500/20', 'bg-warning-50', content)
    content = re.sub(r'border-amber-500/30', 'border-warning-500', content)
    content = re.sub(r'amber', 'warning', content)

    # Some Recharts / UI specific overrides
    content = re.sub(r'#0f172a', '#ffffff', content)
    content = re.sub(r'#334155', '#e2e8f0', content)
    content = re.sub(r'#f8fafc', '#0f172a', content)
    content = re.sub(r'#38bdf8', '#0284c7', content)
    content = re.sub(r'#94a3b8', '#475569', content)
    content = re.sub(r'#0284c7', '#0369a1', content)
    
    return content

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                if file in ['Header.tsx', 'Sidebar.tsx', 'App.tsx']:
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
