# Tests unitaires du module TOC

Ce répertoire contient les tests unitaires pour les fonctionnalités de Table des Matières (TOC) d'Ambulon.

## Structure

```
tests/unit/toc/
├── __init__.py                      # Package marker
├── conftest.py                      # Fixtures pytest partagées
├── README.md                        # Ce fichier
├── test_markdown_toc_generator.py   # Tests pour add-toc4md
├── test_markdown_itoc.py            # Tests pour add-itoc4md
└── test_markdown_to_html.py         # Tests pour md2html-diagrams
```

## Couverture des tests

### test_markdown_toc_generator.py
- `extract_headings()` - Extraction des titres
- `generate_id()` - Génération d'IDs uniques
- `generate_toc_markdown()` - Génération de TOC en Markdown
- `add_anchors_to_headings()` - Ajout d'ancres HTML
- `remove_existing_toc()` - Suppression de TOC existante
- `is_toc_heading()` - Détection des titres de TOC
- `add_toc_to_markdown_logic()` - Logique complète add-toc4md

### test_markdown_itoc.py
- `extract_headings_with_positions()` - Extraction avec positions
- `add_backlinks_to_headings()` - Ajout de backlinks (↑)
- `remove_existing_backlinks()` - Suppression de backlinks
- `detect_itoc_links()` - Détection des liens existants
- `add_toc_backlinks_logic()` - Logique complète add-itoc4md

### test_markdown_to_html.py
- `generate_toc()` - Génération de TOC HTML
- `markdown_to_html_basic()` - Conversion Markdown → HTML
- `wrap_html_document()` - Enveloppement document HTML
- Positionnement de la TOC
- Gestion du marqueur `[TOC]`

## Exécution des tests

### Méthode 1: Script batch (Windows)

```cmd
tools\run_toc_tests.bat
```

### Méthode 2: Script Python (tous OS)

```bash
python tools/run_toc_tests.py
```

### Méthode 3: Directement avec pytest

```bash
# Tous les tests du module TOC
python -m pytest tests/unit/toc/ -v

# Un fichier spécifique
python -m pytest tests/unit/toc/test_markdown_toc_generator.py -v

# Un test spécifique
python -m pytest tests/unit/toc/test_markdown_toc_generator.py::TestExtractHeadings -v

# Avec couverture
python -m pytest tests/unit/toc/ --cov=src/app/toc --cov-report=html
```

## Scénarios de tests critiques

Les tests couvrent ces scénarios essentiels:

1. **Non-duplication de TOC**
   - `test_skip_existing_toc` - Skip si TOC existe
   - `test_force_replace_toc` - Remplacement avec --force
   - `test_no_duplicate_on_rerun` - Pas de duplication au re-lancement

2. **Positionnement correct**
   - `test_toc_position_after_h1` - TOC après H1 et métadonnées
   - `test_toc_replaces_toc_marker` - Remplacement de [TOC]

3. **Exclusion des titres de TOC**
   - `test_exclude_toc_headings` - Pas de "Table des matières" dans la TOC
   - `test_no_backlinks_on_toc_heading` - Pas de backlink sur le titre TOC

4. **Workflow complet**
   - `test_workflow_toc_then_itoc` - add-toc4md puis add-itoc4md
   - `test_no_duplicate_backlinks_on_rerun` - Pas de duplication des backlinks

## Ajouter un nouveau test

```python
# Dans le fichier de test approprié

class TestMaNouvelleFonctionnalite:
    """Tests pour ma nouvelle fonctionnalité"""
    
    def test_cas_nominal(self):
        """Description du test"""
        # Arrange
        input_data = "..."
        
        # Act
        result = ma_fonction(input_data)
        
        # Assert
        assert result == "attendu"
    
    def test_cas_limite(self, tmp_path):
        """Test avec fichier temporaire"""
        fichier = tmp_path / "test.md"
        fichier.write_text("contenu", encoding='utf-8')
        
        result = ma_fonction(fichier)
        
        assert result == 0
```

## Maintenance

Quand vous modifiez le code TOC:

1. **Ajoutez un test** pour la nouvelle fonctionnalité
2. **Vérifiez** que tous les tests passent: `python tools/run_toc_tests.py`
3. **Vérifiez** les cas limites (fichiers vides, gros fichiers, etc.)

## Ressources

- [Documentation pytest](https://docs.pytest.org/)
- [Guide des fixtures pytest](https://docs.pytest.org/en/stable/fixture.html)
