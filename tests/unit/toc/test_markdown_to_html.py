"""
Tests unitaires pour markdown_to_html.py (module diagrams)
Couvre: generate_toc, markdown_to_html_basic pour md2html-diagrams
"""

import pytest
from src.app.diagrams.core.markdown_to_html import (
    generate_toc,
    markdown_to_html_basic,
    wrap_html_document,
    is_toc_heading,
)


class TestIsTocHeading:
    """Tests pour is_toc_heading()"""
    
    @pytest.mark.parametrize("text", [
        "Table des matières",
        "TABLE DES MATIÈRES",
        "Table of Contents",
        "Sommaire",
        "SOMMAIRE",
    ])
    def test_recognizes_toc(self, text):
        """Reconnaît les variantes de TOC"""
        assert is_toc_heading(text) is True
    
    @pytest.mark.parametrize("text", [
        "Introduction",
        "Conclusion",
        "Tableau de données",
    ])
    def test_rejects_non_toc(self, text):
        """Rejette les non-TOC"""
        assert is_toc_heading(text) is False


class TestGenerateToc:
    """Tests pour generate_toc()"""
    
    def test_basic_toc_generation(self):
        """Génération basique de TOC"""
        content = """# Titre Principal
## Section 1
### Subsection 1.1
## Section 2
# Autre Titre
"""
        toc = generate_toc(content, skip_h1=True)
        
        assert '<nav class="table-of-contents"' in toc
        assert "<h2>Table des matières</h2>" in toc
        assert '<a href="#section-1">Section 1</a>' in toc
        assert '<a href="#subsection-11">Subsection 1.1</a>' in toc
        assert '<a href="#section-2">Section 2</a>' in toc
    
    def test_skip_h1_by_default(self):
        """Les H1 sont exclus par défaut"""
        content = """# Titre Principal
## Section 1
"""
        toc = generate_toc(content, skip_h1=True)
        
        assert "Titre Principal" not in toc
        assert "Section 1" in toc
    
    def test_include_h1_when_requested(self):
        """Inclure H1 quand demandé"""
        content = """# Titre Principal
## Section 1
"""
        toc = generate_toc(content, skip_h1=False)
        
        assert "Titre Principal" in toc
        assert "Section 1" in toc
    
    def test_normalize_levels_when_skipping_h1(self):
        """Normalisation des niveaux quand on skip H1"""
        content = """# Titre
## Section 1
### Subsection
"""
        toc = generate_toc(content, skip_h1=True)
        
        # Les H2 deviennent niveau 1 dans la TOC
        assert '<ul>' in toc
        # La structure doit être imbriquée correctement
        assert toc.count('<ul>') >= 1
    
    def test_exclude_toc_heading_itself(self):
        """Le titre 'Table des matières' ne doit pas être dans la TOC"""
        content = """# Document
## Table des matières
### Section 1
"""
        toc = generate_toc(content, skip_h1=True)
        
        assert "Table des matières" not in toc
        assert "Section 1" in toc
    
    def test_handle_explicit_ids(self):
        """Gestion des IDs explicites {#id}"""
        content = """# Titre
## Section {#ma-section}
"""
        toc = generate_toc(content, skip_h1=True)
        
        assert '<a href="#ma-section">Section</a>' in toc
    
    def test_empty_content(self):
        """Contenu sans titres"""
        assert generate_toc("") == ""
        assert generate_toc("Juste du texte") == ""
    
    def test_nested_structure(self):
        """Structure imbriquée correcte"""
        content = """# Titre
## A
### A1
### A2
## B
"""
        toc = generate_toc(content, skip_h1=True)
        
        # Vérifier la structure imbriquée
        assert '<ul>' in toc
        assert '</ul>' in toc
        assert '<li>' in toc
        assert '</li>' in toc
        
        # Les balises doivent être équilibrées
        assert toc.count('<ul>') == toc.count('</ul>')
        assert toc.count('<li>') == toc.count('</li>')


class TestMarkdownToHtmlBasic:
    """Tests pour markdown_to_html_basic()"""
    
    def test_basic_conversion(self):
        """Conversion basique"""
        content = """# Titre

## Section

Du texte **gras** et *italique*.
"""
        html = markdown_to_html_basic(content)
        
        assert '<h1 id="titre">Titre</h1>' in html
        assert '<h2 id="section">Section</h2>' in html
        assert '<strong>gras</strong>' in html
        assert '<em>italique</em>' in html
    
    def test_toc_marker_replacement(self):
        """Le marqueur [TOC] doit être remplacé"""
        content = """# Titre

[TOC]

## Section
"""
        html = markdown_to_html_basic(content)
        
        assert "[TOC]" not in html
        assert '<nav class="table-of-contents"' in html
        assert "Table des matières" in html
    
    def test_auto_toc_insertion(self):
        """Insertion auto de TOC si pas de marqueur"""
        content = """# Titre Principal

## Section 1

### Subsection

## Section 2
"""
        html = markdown_to_html_basic(content)
        
        # La TOC doit être présente
        assert '<nav class="table-of-contents"' in html
        
        # La TOC doit être après le H1
        h1_pos = html.find('<h1')
        toc_pos = html.find('<nav class="table-of-contents"')
        section1_pos = html.find('<h2 id="section-1">')
        
        assert h1_pos < toc_pos < section1_pos
    
    def test_toc_backlinks_option(self):
        """Option add_toc_backlinks"""
        content = """# Titre
## Section 1
"""
        html_with = markdown_to_html_basic(content, add_toc_backlinks=True)
        html_without = markdown_to_html_basic(content, add_toc_backlinks=False)
        
        assert '<a href="#table-of-contents"' in html_with
        assert '<a href="#table-of-contents"' not in html_without
    
    def test_table_conversion(self):
        """Conversion des tableaux"""
        content = """# Titre

| Col1 | Col2 |
|------|------|
| A    | B    |
| C    | D    |
"""
        html = markdown_to_html_basic(content)
        
        assert '<table>' in html
        assert '</table>' in html
        assert '<th>' in html
        assert '<td>' in html
    
    def test_code_block_conversion(self):
        """Conversion des blocs de code"""
        content = """# Titre

```python
def hello():
    pass
```
"""
        html = markdown_to_html_basic(content)
        
        assert '<pre><code' in html
        assert 'class="language-python"' in html
        assert '&lt;def hello():&gt;' not in html  # Doit être échappé
    
    def test_inline_code(self):
        """Conversion du code inline"""
        content = """# Titre

Utilisez `print()` pour afficher.
"""
        html = markdown_to_html_basic(content)
        
        assert '<code>print()</code>' in html
    
    def test_list_conversion(self):
        """Conversion des listes"""
        content = """# Titre

- Item 1
- Item 2
- Item 3
"""
        html = markdown_to_html_basic(content)
        
        assert '<ul>' in html
        assert '</ul>' in html
        assert '<li>Item 1</li>' in html
    
    def test_blockquote_conversion(self):
        """Conversion des citations"""
        content = """# Titre

> Une citation
> Sur plusieurs lignes
"""
        html = markdown_to_html_basic(content)
        
        assert '<blockquote>' in html
        assert '</blockquote>' in html
        assert 'Une citation' in html
    
    def test_horizontal_rule(self):
        """Conversion des lignes horizontales"""
        content = """# Titre

---

Texte
"""
        html = markdown_to_html_basic(content)
        
        assert '<hr>' in html
    
    def test_link_conversion(self):
        """Conversion des liens"""
        content = """# Titre

[Un lien](https://example.com)
[Lien interne](page.md)
"""
        html = markdown_to_html_basic(content)
        
        assert '<a href="https://example.com">Un lien</a>' in html
        assert '<a href="page.html">Lien interne</a>' in html  # .md -> .html
    
    def test_heading_with_explicit_id(self):
        """Titres avec ID explicite"""
        content = """# Titre {#mon-titre}
## Section {#ma-section}
"""
        html = markdown_to_html_basic(content)
        
        assert '<h1 id="mon-titre">Titre</h1>' in html
        assert '<h2 id="ma-section">Section</h2>' in html


class TestWrapHtmlDocument:
    """Tests pour wrap_html_document()"""
    
    def test_basic_wrapping(self):
        """Enveloppement basique"""
        content = "<h1>Titre</h1><p>Texte</p>"
        html = wrap_html_document(content, "Mon Titre")
        
        assert '<!DOCTYPE html>' in html
        assert '<html lang="fr">' in html
        assert '<title>Mon Titre</title>' in html
        assert '<h1>Titre</h1>' in html
        assert '<p>Texte</p>' in html
    
    def test_portrait_orientation_css(self):
        """CSS pour orientation portrait"""
        content = "<p>Test</p>"
        html = wrap_html_document(content, "Titre", page_orientation='portrait')
        
        assert 'max-width: 700px' in html
    
    def test_landscape_orientation_css(self):
        """CSS pour orientation paysage"""
        content = "<p>Test</p>"
        html = wrap_html_document(content, "Titre", page_orientation='landscape')
        
        assert 'max-width: 900px' in html
    
    def test_toc_styles(self):
        """Styles CSS pour la TOC"""
        content = "<p>Test</p>"
        html = wrap_html_document(content, "Titre")
        
        assert '.table-of-contents' in html
        assert '.back-to-toc' in html


class TestTocPositioning:
    """Tests pour le positionnement de la TOC"""
    
    def test_toc_after_h1_and_metadata(self):
        """TOC après H1 et métadonnées"""
        content = """# Titre Principal
**Version**: 1.0
**Date**: 2024

## Section 1
"""
        html = markdown_to_html_basic(content)
        
        # La TOC doit être entre le H1 et le premier H2
        h1_pos = html.find('<h1')
        toc_pos = html.find('<nav class="table-of-contents"')
        h2_pos = html.find('<h2')
        
        assert h1_pos < toc_pos < h2_pos
    
    def test_toc_at_toc_marker_position(self):
        """TOC à la position du marqueur [TOC]"""
        content = """# Titre

Premier paragraphe.

[TOC]

## Section 1
"""
        html = markdown_to_html_basic(content)
        
        # La TOC doit être après le premier paragraphe
        p_pos = html.find('<p>Premier paragraphe')
        toc_pos = html.find('<nav class="table-of-contents"')
        h2_pos = html.find('<h2')
        
        assert p_pos < toc_pos < h2_pos


class TestEdgeCases:
    """Cas limites"""
    
    def test_no_headings(self):
        """Document sans titres"""
        content = "Juste du texte sans titres."
        html = markdown_to_html_basic(content)
        
        assert '<nav class="table-of-contents"' not in html
    
    def test_only_h1(self):
        """Document avec seulement H1"""
        content = """# Titre

Du texte.
"""
        toc = generate_toc(content, skip_h1=True)
        assert toc == ""
    
    def test_deep_nesting(self):
        """Imbrication profonde"""
        content = """# Titre
## A
### A1
#### A1a
##### A1a1
"""
        toc = generate_toc(content, skip_h1=True)
        
        # Tous les niveaux doivent être présents
        assert "A" in toc
        assert "A1" in toc
        assert "A1a" in toc
        assert "A1a1" in toc
    
    def test_special_characters_in_headings(self):
        """Caractères spéciaux dans les titres"""
        content = """# Titre
## Café & Thé
## 100% Test
## Code: `variable`
"""
        toc = generate_toc(content, skip_h1=True)
        html = markdown_to_html_basic(content)
        
        assert "caf-th" in toc.lower() or "caf" in toc.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
