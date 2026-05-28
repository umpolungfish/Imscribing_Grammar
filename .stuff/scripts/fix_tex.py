import re

with open('Frobenius_Structure_Proof.tex', 'r') as f:
    content = f.read()

# Fix unescaped \zeta and \xi in table headers - wrap in $...$
content = content.replace(r'\textbf{\zeta}', r'\textbf{$\zeta$}')
content = content.replace(r'\textbf{\xi}', r'\textbf{$\xi$}')

# Fix standalone \zeta and \xi in text that should be math mode
# Use simple string replace with careful handling
content = content.replace(r'\zeta $', r'$\zeta$')
content = content.replace(r'\xi $', r'$\xi$')
content = content.replace(r'\zeta ', r'$\zeta$ ')
content = content.replace(r'\xi ', r'$\xi$ ')

# Fix \rightarrow
content = content.replace(r'\rightarrow(', r'$\rightarrow$(')
content = content.replace(r'\rightarrow ', r'$\rightarrow$ ')

with open('Frobenius_Structure_Proof.tex', 'w') as f:
    f.write(content)

print("Done fixing")
