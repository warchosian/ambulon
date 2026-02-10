import re

# Test with 4 backticks wrapping content that has 3-backtick blocks
test_content = """````markdown
# Dyag

## Installation

```bash
poetry install
```

## Utilisation

```bash
dyag <commande> -h
```
````


### RELEASE_NOTES_v0.2.0-rc.1.md

<a id="RELEASE_NOTES_v0-2-0-rc-1-md"></a>

````markdown
# dyag v0.2.0-rc.1 Release Notes
````
"""

# Test the new pattern
pattern = r'(`{3,})([^\n`]*)\n(.*?)\1(?:\n|$)'
matches = list(re.finditer(pattern, test_content, re.DOTALL))

print(f'Found {len(matches)} matches\n')

for i, match in enumerate(matches, 1):
    backticks = match.group(1)
    lang = match.group(2)
    content = match.group(3)
    start_pos = match.start()
    end_pos = match.end()

    # Find line numbers
    lines_before_start = test_content[:start_pos].count('\n')
    lines_before_end = test_content[:end_pos].count('\n')

    print(f'Match {i}:')
    print(f'  Backticks: {len(backticks)}')
    print(f'  Language: "{lang}"')
    print(f'  Lines: {lines_before_start + 1} to {lines_before_end + 1}')
    print(f'  Content length: {len(content)} chars')
    print(f'  Content start: {repr(content[:80])}...')
    print()

# Check what's between matches
print('\nChecking gaps between matches:')
if len(matches) > 0:
    # Between matches
    for i in range(len(matches) - 1):
        gap_start = matches[i].end()
        gap_end = matches[i+1].start()
        gap = test_content[gap_start:gap_end]
        if gap.strip():
            print(f'Between match {i+1} and {i+2}:')
            print(repr(gap))
            print()
