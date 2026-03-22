import os
import shutil

for root, dirs, files in os.walk('src'):
    if '__pycache__' in dirs:
        cache_path = os.path.join(root, '__pycache__')
        print(f'Removing: {cache_path}')
        shutil.rmtree(cache_path)
        dirs.remove('__pycache__')

print('Cache cleared!')
