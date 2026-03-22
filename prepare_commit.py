import subprocess
import sys

# Vérifier les fichiers modifiés
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print("Git status:")
print(result.stdout)

# Ajouter tous les fichiers modifiés
result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Erreur git add: {result.stderr}")
    sys.exit(1)

print("Fichiers ajoutés à l'index")

# Vérifier le statut
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print("\nFichiers staged:")
print(result.stdout)
