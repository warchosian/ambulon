## 0.3.0 (2025-12-15)

### Feat

- **Serveur MCP complet** pour intégration avec assistants IA (Claude, OpenRouter, Aider, Continue)
- **Module img2pdf** : Conversion d'images en PDF avec compression optionnelle
- **Module compress-pdf** : Compression de fichiers PDF existants
- **Système de configuration multi-assistants** avec installation automatique
- **Suite de tests complète** avec pytest et tests d'intégration
- **7 outils MCP disponibles** :
  - `scan_document` : Scanner un document avec NAPS2
  - `ocr_image` : OCR d'une image
  - `ocr_batch` : OCR en lot sur plusieurs images
  - `scan_with_ocr` : Scanner + OCR en une opération
  - `process_existing_scans` : Traiter des scans existants
  - `images_to_pdf` : Convertir images en PDF
  - `compress_pdf` : Compresser un PDF
- **Commandes de gestion** :
  - `ambulon config install` : Installation automatique pour assistants
  - `ambulon config status` : Statut des configurations
  - `ambulon config test` : Test du serveur MCP
  - `ambulon test mcp-live` : Tests en conditions réelles
- **Support multi-plateforme** (Windows, macOS, Linux)
- **Gestion avancée des chemins** de sortie sans auto-incrémentation par défaut

### Changed

- **Logique d'incrémentation inversée** : `--increment` pour activer l'auto-incrémentation
- **Interface CLI étendue** avec nouveaux modules
- **Amélioration du système de logging** avec encodage UTF-8
- **Tests robustes** avec gestion des erreurs d'encodage

### Fix

- **Gestion des chemins de sortie** dans le module de scan
- **Problèmes d'encodage Unicode** sur Windows
- **Initialisation des variables** dans les fonctions de scan
- **Compatibilité pytest** avec tests async

### Dependencies

- Ajout de **Pillow** pour le traitement d'images
- Ajout de **PyMuPDF** pour la manipulation PDF
- Ajout de **importlib-resources** pour l'accès aux ressources
- Ajout de **pytest-asyncio** pour les tests asynchrones

## 0.2.0 (2025-12-15)

### Feat

- intégration complète du module de scan TWAIN avec profils DPI et OCR
- mise à jour de la version vers 0.3.0 pour la nouvelle release de scan
- intégrer le module de scan complet dans Ambulon
- ajouter le module de scan de base pour Ambulon
- créer le fichier cli.py pour l'interface en ligne de commande d'Ambulon

### Fix

- nettoie la configuration Poetry et supprime les commentaires invalides
- corrige l'implémentation du CLI pour gérer la commande scan

### Refactor

- modifier la configuration des logs pour utiliser le répertoire logs

## 0.2.0a0 (2025-12-14)

### Feat

- initial commit
