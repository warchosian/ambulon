import os
import shutil
import sys

def clear_cache(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            print(f'Removing: {cache_path}')
            shutil.rmtree(cache_path)
            count += 1
            dirs.remove('__pycache__')
        # Also remove .pyc files
        for f in files:
            if f.endswith('.pyc'):
                pyc_path = os.path.join(root, f)
                os.remove(pyc_path)
                count += 1
    return count

# Clear src and tests directories
src_count = clear_cache('src')
tests_count = clear_cache('tests')

print(f'\nRemoved {src_count} cache items from src/')
print(f'Removed {tests_count} cache items from tests/')
print('All cache cleared!')
