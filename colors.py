#!/usr/bin/env python3
"""
Update HTML files with alchemical/esoteric color scheme.
Run this script in the directory containing the three HTML files.
"""

import re
from pathlib import Path

# Alchemical color palette
COLOR_MAP = {
    # Backgrounds
    r'var\(--color-background-primary\)': '#211d19',
    r'var\(--color-background-secondary\)': '#1c1812',
    r'var\(--color-background-danger\)': '#5c2a2a',
    r'var\(--color-background-info\)': '#2a4f5e',
    r'var\(--color-background-warning\)': '#664d2a',
    
    # Text
    r'var\(--color-text-primary\)': '#f5e8c7',
    r'var\(--color-text-secondary\)': '#d4c9a8',
    r'var\(--color-text-tertiary\)': '#a89f8a',
    
    # Borders
    r'var\(--color-border-tertiary\)': '#3f3a32',
    r'var\(--color-border-secondary\)': '#3f3a32',
    r'var\(--color-border-primary\)': '#d4af37',
    
    # Old specific hex colors -> new palette
    '#D3D1C7': '#6b6659',   # Neutral / Neither
    '#B5D4F4': '#3e7a8c',   # True / Teal
    '#F7C1C1': '#8c2f2f',   # False / Crimson
    '#FAC775': '#b38b2e',   # Both / Amber
    '#BA7517': '#b38b2e',   # Knowledge ordering
    '#0F6E56': '#3e7a8c',   # Truth ordering
    '#888780': '#3f3a32',   # Lines
    '#5F5E5A': '#3f3a32',
    '#A32D2D': '#8c2f2f',
    '#854F0B': '#b38b2e',
    '#2C2C2A': '#0f0c08',
    '#444441': '#a89f8a',
}

def replace_colors(content: str) -> str:
    """Apply all color replacements."""
    for old, new in COLOR_MAP.items():
        content = re.sub(re.escape(old), new, content, flags=re.IGNORECASE)
    
    # Add CSS variables at the top of <style> if not present
    if ':root' not in content:
        root_css = """:root {
  --bg-primary: #0f0c08;
  --bg-secondary: #1c1812;
  --bg-card: #211d19;
  --text-primary: #f5e8c7;
  --text-secondary: #d4c9a8;
  --text-tertiary: #a89f8a;
  --accent-gold: #d4af37;
  --truth-teal: #3e7a8c;
  --false-crimson: #8c2f2f;
  --both-amber: #b38b2e;
  --neither-stone: #6b6659;
  --border: #3f3a32;
}
"""
        content = re.sub(r'(<style[^>]*>)', r'\1\n' + root_css, content, count=1)
    
    # General body/background fixes
    content = re.sub(r'background:\s*var\(--color-background-primary\)', 'background:var(--bg-card)', content)
    content = re.sub(r'color:\s*var\(--color-text-primary\)', 'color:var(--text-primary)', content)
    content = re.sub(r'border:\s*0\.5px solid var\(--color-border-tertiary\)', 'border:1px solid var(--border)', content)
    
    return content

def main():
    files = [
        "belnap_bilattice_probability.html",
        "scalar_field_symmetry_breaking_lattice.html",
        "four_five_logic_physics.html"
    ]
    
    for filename in files:
        path = Path(filename)
        if not path.exists():
            print(f"⚠️  File not found: {filename}")
            continue
        
        print(f"Updating {filename}...")
        content = path.read_text(encoding='utf-8')
        updated = replace_colors(content)
        
        # Backup original
        path.with_suffix('.html.bak').write_text(content, encoding='utf-8')
        
        # Write updated
        path.write_text(updated, encoding='utf-8')
        print(f"✅ Updated {filename}")
    
    print("\n🎉 All files updated with alchemical color scheme!")
    print("   Dark parchment background, gold accents, teal/crimson tones.")

if __name__ == "__main__":
    main()