#!/usr/bin/env python
import yaml

with open('config/gitlab.yaml', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    print("=== Lignes 65-70 ===")
    for i, line in enumerate(lines[64:72], start=65):
        print(f'{i}: {repr(line)}')
    
    print('\n=== Parsing YAML ===')
    config = yaml.safe_load(content)
    repos = config.get('gitlab', {}).get('repositories', [])
    print(f'Nombre de repos trouvés: {len(repos)}')
    print('\nDerniers repos:')
    for r in repos[-5:]:
        print(f'  - {r}')
