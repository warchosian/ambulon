## 0.5.1 (2026-01-07)

### Feat

- ajout des fonctions de traitement OCR par dossier et PDF

### Fix

- **packaging**: Embed config data and fix NameError issues to ensure reliable build and execution
- améliorer la détection des répertoires dans le module OCR
- améliorer la détection du mode de traitement OCR
- corrige la gestion des dossiers et fichiers dans le module OCR

### Refactor

- améliorer la détection du type de chemin d'entrée pour l'OCR
- corriger la détection du mode de traitement OCR (dossier/fichier)
- améliorer la détection et la gestion des chemins d'entrée pour l'OCR

## 0.4.0 (2025-12-15)

### Feat

- ajouter les modules img2pdf et compress-pdf à Ambulon
- ajout de scripts de test avancés pour le serveur MCP
- ajout de tests d'intégration complets pour le serveur MCP Ambulon
- corriger les tests d'OCR et de scan pour améliorer la robustesse
- Ajouter une structure complète de tests unitaires avec pytest
- ajout du module de configuration pour Ambulon
- ajouter le fichier de configuration JSON au package Poetry
- ajout de la gestion de configuration MCP et de l'export de configuration Claude
- intégrer le serveur MCP comme module Ambulon
- intégrer l'option `--no-increment` dans le serveur MCP pour le scan
- ajouter une vérification pour empêcher l'écrasement de répertoires lors de la numérisation
- ajout de l'option --no-increment pour désactiver l'auto-incrémentation des noms de fichiers
- ajout de l'auto-incrémentation pour les fichiers de scan
- Migrer le serveur MCP de Dyag vers Ambulon
- intégrer le serveur MCP pour Ambulon avec support des outils de scan et OCR
- ajouter un serveur MCP pour les outils dyag avec des fonctionnalités avancées
- améliore l'interface CLI d'Ambulon avec une aide détaillée et des modules disponibles
- intégrer le module OCR dans l'interface CLI d'Ambulon
- ajouter le module OCR pour le traitement d'images

### Fix

- ajouter la fonction setup_logging dans le module cli
- Ajouter la gestion du cas sans incrémentation dans le nommage des fichiers
- corriger l'initialisation de la variable output_file dans le mode de scan standard
- corriger la gestion des chemins de sortie dans le module de scan
- importer Path depuis pathlib pour vérifier l'existence du script de test
- corriger les tests et dépendances pour améliorer la compatibilité
- gérer l'aide et corriger l'encodage des messages de configuration
- améliorer la gestion du mode simulation de scan avec des informations détaillées
- corrige la gestion des erreurs de scan et d'OCR pour les fichiers vides
- ajouter le champ capabilities manquant dans InitializationOptions
- supprimer l'appel de get_capabilities() dans l'initialisation du serveur MCP
- corrige l'utilisation de false par False en Python

### Refactor

- modifier la logique d'incrémentation des noms de fichiers par défaut

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
