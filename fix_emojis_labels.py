#!/usr/bin/env python3
"""Fix emoji uses in PlantUML labels according to Rule #25"""
import re

file_path = r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\doc\guidelines-illustrated.md'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace patterns
replacements = [
    # is/not patterns
    (r'is \(❌ non\) not \(✅ oui\)', r'is (non) not (oui)'),

    # then patterns
    (r'then \(✅ oui\)', r'then (oui)'),
    (r'then \(❌ oui\)', r'then (oui)'),
    (r'then \(❌ non\)', r'then (non)'),

    # else patterns
    (r'else \(✅ oui\)', r'else (oui)'),
    (r'else \(❌ oui\)', r'else (oui)'),
    (r'else \(✅ non\)', r'else (non)'),
    (r'else \(❌ non\)', r'else (non)'),
    (r'else \(❌ erreur\)', r'else (erreur)'),
]

# Apply all replacements
for old_pattern, new_pattern in replacements:
    content = re.sub(old_pattern, new_pattern, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed emoji uses in labels")
