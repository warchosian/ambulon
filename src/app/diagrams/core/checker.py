"""
Vérificateur de conformité des diagrammes PlantUML.

Vérifie la conformité aux règles définies dans doc/REGLES_PLANTUML.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from .detector import extract_diagram_blocks
from .base import DiagramType, Violation


class PlantUMLChecker:
    """
    Vérificateur de conformité PlantUML.
    
    Analyse un fichier Markdown et détecte les violations des règles
    de codage PlantUML définies dans la documentation du projet.
    """
    
    def __init__(self, file_path: Path | str):
        """
        Initialise le vérificateur.
        
        Args:
            file_path: Chemin vers le fichier Markdown à analyser
        """
        self.file_path = Path(file_path)
        self.content = self.file_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.violations: List[Violation] = []
        self._plantuml_blocks: Optional[List[Dict]] = None
    
    @property
    def plantuml_blocks(self) -> List[Dict]:
        """Lazy loading des blocs PlantUML."""
        if self._plantuml_blocks is None:
            self._plantuml_blocks = self._extract_plantuml_blocks()
        return self._plantuml_blocks
    
    def _extract_plantuml_blocks(self) -> List[Dict]:
        """
        Extrait tous les blocs PlantUML avec leurs numéros de ligne.
        
        Returns:
            Liste des blocs avec start, end, content
        """
        blocks = []
        in_block = False
        current_block = []
        start_line = 0
        
        for i, line in enumerate(self.lines, 1):
            if '```plantuml' in line:
                in_block = True
                start_line = i
                current_block = []
            elif in_block:
                if line.strip() == '```':
                    blocks.append({
                        'start': start_line,
                        'end': i,
                        'content': '\n'.join(current_block),
                        'lines': current_block
                    })
                    in_block = False
                else:
                    current_block.append(line)
        
        return blocks
    
    def check_all(self) -> List[Violation]:
        """
        Exécute toutes les vérifications.
        
        Returns:
            Liste des violations détectées
        """
        self.violations = []
        
        self._check_rule_21_22()  # @startuml/@enduml obligatoires
        self._check_rule_2_6()     # Ordre alias/couleur
        self._check_rule_23()      # Rectangles vides
        self._check_rule_24()      # Mindmaps
        self._check_rule_25()      # Emojis dans labels
        self._check_rule_26()      # Identification diagrammes
        self._check_rule_27()      # Commentaires problématiques
        self._check_rule_3()       # Listes à tirets
        self._check_rule_12()      # Bold dans notes
        self._check_rule_17()      # Caractères spéciaux
        
        return self.violations
    
    def _check_rule_21_22(self):
        """Règle #21-22 : Tous les blocs doivent avoir @startuml et @enduml."""
        for block in self.plantuml_blocks:
            content = block['content']
            
            has_start = '@startuml' in content or '@startmindmap' in content
            has_end = '@enduml' in content or '@endmindmap' in content
            
            if not has_start:
                self.violations.append(Violation(
                    rule_number="#21",
                    rule_name="@startuml obligatoire",
                    line_number=block['start'],
                    severity="erreur",
                    message="Bloc PlantUML sans @startuml ou @startmindmap",
                    code_snippet=content[:100]
                ))
            
            if not has_end:
                self.violations.append(Violation(
                    rule_number="#22",
                    rule_name="@enduml obligatoire",
                    line_number=block['start'],
                    severity="erreur",
                    message="Bloc PlantUML sans @enduml ou @endmindmap",
                    code_snippet=content[:100]
                ))
    
    def _check_rule_2_6(self):
        """Règle #2-6 : Ordre correct 'as alias' avant '#couleur'."""
        pattern = r'rectangle\s+"[^"]+"\s+#\w+\s+as\s+\w+'
        
        for block in self.plantuml_blocks:
            for i, line in enumerate(block['lines'], block['start'] + 1):
                if re.search(pattern, line):
                    self.violations.append(Violation(
                        rule_number="#2/#6",
                        rule_name="Ordre alias/couleur incorrect",
                        line_number=i,
                        severity="erreur",
                        message="L'alias doit être AVANT la couleur : 'as alias #COULEUR'",
                        code_snippet=line.strip()
                    ))
    
    def _check_rule_23(self):
        """Règle #23 : Rectangles avec braces doivent avoir au moins une ligne."""
        for block in self.plantuml_blocks:
            content = block['content']
            # Cherche rectangle ... { \n }
            pattern = r'rectangle\s+[^{]+\{\s*\n\s*\}'
            if re.search(pattern, content):
                self.violations.append(Violation(
                    rule_number="#23",
                    rule_name="Rectangle vide",
                    line_number=block['start'],
                    severity="erreur",
                    message="Rectangle avec braces vides. Ajouter au moins une ligne entre { et }",
                    code_snippet=""
                ))
    
    def _check_rule_24(self):
        """Règle #24 : Mindmaps doivent utiliser @startmindmap/@endmindmap."""
        for block in self.plantuml_blocks:
            content = block['content']
            
            # Si c'est une mindmap (contient des * pour hiérarchie)
            if re.search(r'^\s*\*+\s+\w+', content, re.MULTILINE):
                if '@startuml' in content and '@startmindmap' not in content:
                    self.violations.append(Violation(
                        rule_number="#24",
                        rule_name="Mindmap avec @startuml",
                        line_number=block['start'],
                        severity="erreur",
                        message="Les mindmaps doivent utiliser @startmindmap/@endmindmap",
                        code_snippet=""
                    ))
    
    def _check_rule_25(self):
        """Règle #25 : Pas d'emojis dans les labels is/then/else/not."""
        emoji_pattern = r'[✅❌🚀💡⚠️]'
        label_patterns = [
            r'is\s*\([^)]*[✅❌🚀💡⚠️][^)]*\)',
            r'then\s*\([^)]*[✅❌🚀💡⚠️][^)]*\)',
            r'else\s*\([^)]*[✅❌🚀💡⚠️][^)]*\)',
            r'not\s*\([^)]*[✅❌🚀💡⚠️][^)]*\)',
        ]
        
        for block in self.plantuml_blocks:
            for i, line in enumerate(block['lines'], block['start'] + 1):
                for pattern in label_patterns:
                    if re.search(pattern, line):
                        self.violations.append(Violation(
                            rule_number="#25",
                            rule_name="Emojis dans labels",
                            line_number=i,
                            severity="erreur",
                            message="Ne pas utiliser d'emojis dans les labels is/then/else/not",
                            code_snippet=line.strip()
                        ))
    
    def _check_rule_26(self):
        """Règle #26 : Identification diagrammes + éviter <figure markdown>."""
        # Vérifie présence de balises figure
        for i, line in enumerate(self.lines, 1):
            if '<figure markdown>' in line or '<figure>' in line:
                self.violations.append(Violation(
                    rule_number="#26",
                    rule_name="Utilisation de <figure>",
                    line_number=i,
                    severity="warning",
                    message="Éviter les balises <figure> (problèmes de compatibilité)",
                    code_snippet=line.strip()
                ))
        
        # Vérifie que chaque bloc a une légende
        for block in self.plantuml_blocks:
            end_line = block['end']
            has_figcaption = False
            
            for i in range(end_line, min(end_line + 4, len(self.lines))):
                if i < len(self.lines) and '<figcaption>' in self.lines[i]:
                    has_figcaption = True
                    break
            
            if not has_figcaption:
                self.violations.append(Violation(
                    rule_number="#26",
                    rule_name="Diagramme non identifié",
                    line_number=block['start'],
                    severity="warning",
                    message="Diagramme sans <figcaption>. Ajouter une légende après le bloc",
                    code_snippet=""
                ))
    
    def _check_rule_27(self):
        """Règle #27 : Pas de commentaires EVITER avec balises."""
        problematic_patterns = [
            r'<!--\s*EVITER\s*```',
            r'<!--\s*EVITER\s*<figure',
            r"'EVITER\s*<",
        ]
        
        for i, line in enumerate(self.lines, 1):
            for pattern in problematic_patterns:
                if re.search(pattern, line):
                    self.violations.append(Violation(
                        rule_number="#27",
                        rule_name="Commentaire problématique",
                        line_number=i,
                        severity="erreur",
                        message="Commentaire EVITER avec balises Markdown/HTML casse le rendu",
                        code_snippet=line.strip()
                    ))
    
    def _check_rule_3(self):
        """Règle #3 : Pas de listes à tirets dans rectangles imbriqués."""
        for block in self.plantuml_blocks:
            in_rectangle = False
            for i, line in enumerate(block['lines'], block['start'] + 1):
                if 'rectangle' in line and '{' in line:
                    in_rectangle = True
                if in_rectangle and re.match(r'\s*-\s+', line):
                    self.violations.append(Violation(
                        rule_number="#3",
                        rule_name="Liste à tirets dans rectangle",
                        line_number=i,
                        severity="warning",
                        message="Les listes à tirets dans rectangles peuvent causer des problèmes",
                        code_snippet=line.strip()
                    ))
                if '}' in line:
                    in_rectangle = False
    
    def _check_rule_12(self):
        """Règle #12 : Utiliser <b> au lieu de ** dans les notes."""
        for block in self.plantuml_blocks:
            in_note = False
            for i, line in enumerate(block['lines'], block['start'] + 1):
                if 'note ' in line:
                    in_note = True
                if in_note and '**' in line:
                    self.violations.append(Violation(
                        rule_number="#12",
                        rule_name="Bold ** dans note",
                        line_number=i,
                        severity="warning",
                        message="Utiliser <b>texte</b> au lieu de **texte** dans les notes",
                        code_snippet=line.strip()
                    ))
                if 'end note' in line:
                    in_note = False
    
    def _check_rule_17(self):
        """Règle #17 : Pas de caractères spéciaux non supportés."""
        special_chars = ['=>', '--', '->']  # Dans les noms, pas les flèches
        
        for block in self.plantuml_blocks:
            for i, line in enumerate(block['lines'], block['start'] + 1):
                # Ignore les lignes de flèches
                if re.match(r'\s*\[.*\]\s*[-=]>', line):
                    continue
                
                # Cherche dans les noms d'éléments
                if 'rectangle' in line or 'object' in line:
                    for char in special_chars:
                        if char in line:
                            self.violations.append(Violation(
                                rule_number="#17",
                                rule_name="Caractères spéciaux",
                                line_number=i,
                                severity="warning",
                                message=f"Caractère spécial '{char}' peut causer des problèmes",
                                code_snippet=line.strip()
                            ))
    
    def generate_report(self, output_path: Optional[Path | str] = None) -> str:
        """
        Génère un rapport Markdown des violations.
        
        Args:
            output_path: Chemin de sortie (défaut: fichier.violations.md)
            
        Returns:
            Chemin du rapport généré
        """
        if output_path is None:
            output_path = self.file_path.with_suffix('.violations.md')
        else:
            output_path = Path(output_path)
        
        lines = []
        lines.append(f"# Rapport de Conformité PlantUML\n")
        lines.append(f"**Fichier analysé** : `{self.file_path.name}`\n")
        lines.append(f"**Date** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**Blocs PlantUML trouvés** : {len(self.plantuml_blocks)}\n")
        lines.append(f"**Violations détectées** : {len(self.violations)}\n")
        lines.append("\n---\n")
        
        if not self.violations:
            lines.append("\n## ✅ Aucune violation détectée\n")
            lines.append("\nTous les blocs PlantUML respectent les règles définies.\n")
        else:
            # Groupe par règle
            violations_by_rule: Dict[str, List[Violation]] = {}
            for v in self.violations:
                key = f"{v.rule_number} - {v.rule_name}"
                violations_by_rule.setdefault(key, []).append(v)
            
            lines.append("\n## 📋 Résumé par Règle\n")
            for rule, viols in sorted(violations_by_rule.items()):
                count = len(viols)
                severity = viols[0].severity
                icon = "🔴" if severity == "erreur" else "🟡"
                lines.append(f"- {icon} **Règle {rule}** : {count} violation(s)\n")
            
            lines.append("\n---\n")
            lines.append("\n## 📝 Détails des Violations\n")
            
            for rule, viols in sorted(violations_by_rule.items()):
                lines.append(f"\n### Règle {rule}\n")
                for v in viols:
                    icon = "🔴" if v.severity == "erreur" else "🟡"
                    lines.append(f"\n{icon} **Ligne {v.line_number}** : {v.message}\n")
                    if v.code_snippet:
                        lines.append(f"```plantuml\n{v.code_snippet}\n```\n")
        
        lines.append("\n---\n")
        lines.append("\n## 📚 Références\n")
        lines.append("\nConsultez `doc/REGLES_PLANTUML.md` pour les détails de chaque règle.\n")
        
        report_content = ''.join(lines)
        output_path.write_text(report_content, encoding='utf-8')
        
        return str(output_path)


def check_plantuml_file(file_path: Path | str, output_report: Optional[Path | str] = None) -> tuple[int, int]:
    """
    Vérifie un fichier et génère un rapport.
    
    Args:
        file_path: Fichier à analyser
        output_report: Chemin du rapport (optionnel)
        
    Returns:
        Tuple (nombre_violations, nombre_erreurs_critiques)
    """
    checker = PlantUMLChecker(file_path)
    checker.check_all()
    
    if output_report or checker.violations:
        checker.generate_report(output_report)
    
    critical_count = sum(1 for v in checker.violations if v.severity == "erreur")
    
    return len(checker.violations), critical_count
