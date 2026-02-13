#!/usr/bin/env python3
"""
PlantUML Markdown Checker - Vérifie la conformité aux règles REGLES_PLANTUML.md

Génère un rapport Markdown listant toutes les violations de règles détectées.
"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Violation:
    """Représente une violation de règle"""
    rule_number: str
    rule_name: str
    line_number: int
    severity: str  # "erreur" ou "warning"
    message: str
    code_snippet: str = ""


class PlantUMLChecker:
    """Vérificateur de conformité PlantUML"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = self.file_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.violations: List[Violation] = []
        self.plantuml_blocks = self._extract_plantuml_blocks()

    def _extract_plantuml_blocks(self) -> List[Dict]:
        """Extrait tous les blocs PlantUML avec leurs numéros de ligne"""
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
                if '```' in line and line.strip() == '```':
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

    def check_all_rules(self):
        """Vérifie toutes les règles"""
        self.check_rule_21_22()  # @startuml/@enduml obligatoires
        self.check_rule_2_6()     # Ordre alias/couleur
        self.check_rule_23()      # Rectangles vides
        self.check_rule_24()      # Mindmaps
        self.check_rule_25()      # Emojis dans labels
        self.check_rule_26()      # Identification diagrammes
        self.check_rule_27()      # Commentaires problématiques
        self.check_rule_3()       # Listes à tirets
        self.check_rule_12()      # Bold dans notes
        self.check_rule_17()      # Caractères spéciaux

    def check_rule_21_22(self):
        """Règle #21-22 : Tous les blocs doivent avoir @startuml et @enduml"""
        for block in self.plantuml_blocks:
            content = block['content']

            if '@startuml' not in content and '@startmindmap' not in content:
                self.violations.append(Violation(
                    rule_number="#21",
                    rule_name="@startuml obligatoire",
                    line_number=block['start'],
                    severity="erreur",
                    message="Bloc PlantUML sans @startuml ou @startmindmap",
                    code_snippet=content[:100]
                ))

            if '@enduml' not in content and '@endmindmap' not in content:
                self.violations.append(Violation(
                    rule_number="#22",
                    rule_name="@enduml obligatoire",
                    line_number=block['start'],
                    severity="erreur",
                    message="Bloc PlantUML sans @enduml ou @endmindmap",
                    code_snippet=content[:100]
                ))

    def check_rule_2_6(self):
        """Règle #2-6 : Ordre correct "as alias" avant "#couleur" """
        pattern = r'rectangle\s+"[^"]+"\s+#\w+\s+as\s+\w+'

        for block in self.plantuml_blocks:
            for i, line in enumerate(block['lines'], block['start'] + 1):
                if re.search(pattern, line):
                    self.violations.append(Violation(
                        rule_number="#2/#6",
                        rule_name="Ordre alias/couleur incorrect",
                        line_number=i,
                        severity="erreur",
                        message="L'alias doit être AVANT la couleur : 'as alias #COULEUR' et non '#COULEUR as alias'",
                        code_snippet=line.strip()
                    ))

    def check_rule_23(self):
        """Règle #23 : Rectangles avec braces doivent avoir au moins une ligne"""
        # Pattern : rectangle ... { } sur même ligne ou lignes consécutives
        for block in self.plantuml_blocks:
            content = block['content']
            # Chercher rectangle ... { \n }
            pattern = r'rectangle\s+[^{]+\{\s*\n\s*\}'
            if re.search(pattern, content):
                self.violations.append(Violation(
                    rule_number="#23",
                    rule_name="Rectangle vide",
                    line_number=block['start'],
                    severity="erreur",
                    message="Rectangle avec braces vides. Ajouter au moins une ligne vide entre { et }",
                    code_snippet=""
                ))

    def check_rule_24(self):
        """Règle #24 : Mindmaps doivent utiliser @startmindmap/@endmindmap"""
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
                        message="Les mindmaps doivent utiliser @startmindmap/@endmindmap et non @startuml/@enduml",
                        code_snippet=""
                    ))

    def check_rule_25(self):
        """Règle #25 : Pas d'emojis dans les labels is/then/else/not"""
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

    def check_rule_26(self):
        """Règle #26 : Identification diagrammes + éviter <figure markdown>"""
        # Vérifier présence de <figure markdown>
        for i, line in enumerate(self.lines, 1):
            if '<figure markdown>' in line or '<figure>' in line:
                self.violations.append(Violation(
                    rule_number="#26",
                    rule_name="Utilisation de <figure>",
                    line_number=i,
                    severity="warning",
                    message="Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)",
                    code_snippet=line.strip()
                ))

        # Vérifier que chaque bloc PlantUML a une figcaption après
        for block in self.plantuml_blocks:
            end_line = block['end']
            # Chercher <figcaption> dans les 3 lignes suivantes
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

    def check_rule_27(self):
        """Règle #27 : Pas de commentaires EVITER avec balises"""
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

    def check_rule_3(self):
        """Règle #3 : Pas de listes à tirets dans rectangles imbriqués"""
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
                        message="Les listes à tirets dans rectangles peuvent causer des problèmes de rendu",
                        code_snippet=line.strip()
                    ))
                if '}' in line:
                    in_rectangle = False

    def check_rule_12(self):
        """Règle #12 : Utiliser <b> au lieu de ** dans les notes"""
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

    def check_rule_17(self):
        """Règle #17 : Pas de caractères spéciaux non supportés"""
        special_chars = ['=>', '--', '->']  # Dans les noms, pas les flèches
        for block in self.plantuml_blocks:
            for i, line in enumerate(block['lines'], block['start'] + 1):
                # Ignorer les lignes de flèches
                if re.match(r'\s*\[.*\]\s*[-=]>', line):
                    continue

                # Chercher dans les noms d'éléments
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

    def generate_report(self, output_path: str = None) -> str:
        """Génère un rapport Markdown des violations"""
        from datetime import datetime

        if output_path is None:
            output_path = self.file_path.with_suffix('.violations.md')

        report_lines = []
        report_lines.append(f"# Rapport de Conformité PlantUML\n")
        report_lines.append(f"**Fichier analysé** : `{self.file_path.name}`\n")
        report_lines.append(f"**Date** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append(f"**Blocs PlantUML trouvés** : {len(self.plantuml_blocks)}\n")
        report_lines.append(f"**Violations détectées** : {len(self.violations)}\n")
        report_lines.append("\n---\n")

        if not self.violations:
            report_lines.append("\n## ✅ Aucune violation détectée\n")
            report_lines.append("\nTous les blocs PlantUML respectent les règles définies.\n")
        else:
            # Grouper par règle
            violations_by_rule = {}
            for v in self.violations:
                key = f"{v.rule_number} - {v.rule_name}"
                if key not in violations_by_rule:
                    violations_by_rule[key] = []
                violations_by_rule[key].append(v)

            report_lines.append("\n## 📋 Résumé par Règle\n")
            for rule, viols in sorted(violations_by_rule.items()):
                count = len(viols)
                severity = viols[0].severity
                icon = "🔴" if severity == "erreur" else "🟡"
                report_lines.append(f"- {icon} **Règle {rule}** : {count} violation(s)\n")

            report_lines.append("\n---\n")
            report_lines.append("\n## 📝 Détails des Violations\n")

            for rule, viols in sorted(violations_by_rule.items()):
                report_lines.append(f"\n### Règle {rule}\n")
                for v in viols:
                    icon = "🔴" if v.severity == "erreur" else "🟡"
                    report_lines.append(f"\n{icon} **Ligne {v.line_number}** : {v.message}\n")
                    if v.code_snippet:
                        report_lines.append(f"```plantuml\n{v.code_snippet}\n```\n")

        report_lines.append("\n---\n")
        report_lines.append("\n## 📚 Références\n")
        report_lines.append("\nConsultez `doc/REGLES_PLANTUML.md` pour les détails de chaque règle.\n")

        report_content = ''.join(report_lines)

        if output_path:
            Path(output_path).write_text(report_content, encoding='utf-8')
            return output_path

        return report_content


def main():
    """Point d'entrée CLI"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python plantuml_checker.py <fichier.md> [rapport.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    checker = PlantUMLChecker(input_file)
    checker.check_all_rules()

    report_path = checker.generate_report(output_file)

    print(f"Analyse terminee : {len(checker.violations)} violations detectees")
    print(f"Rapport genere : {report_path}")

    # Retourner code d'erreur si violations critiques
    critical_count = sum(1 for v in checker.violations if v.severity == "erreur")
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == '__main__':
    main()
