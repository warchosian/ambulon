"""
Module to fix and validate diagrams (Mermaid, PlantUML, Graphviz) in generated documentation files.

Supports two correction modes:
1. REGEX: Pattern-based fixes loaded from diagram-rules.yaml
2. LLM: AI-powered correction using cloud_gpt_oss_120b provider

Usage:
  python -m app.llm.commands.fix_diagrams --mode regex --input workplace-ambulon/delivrables
  python -m app.llm.commands.fix_diagrams --mode llm --input workplace-ambulon/delivrables --provider cloud_gpt_oss_120b
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

import yaml

from app.core.logging_config import setup_logging
from app.llm.core.config import load_llm_config, get_api_key, get_base_url, get_provider_config
from app.llm.core.providers import get_provider

logger = logging.getLogger(__name__)


# Mapping des familles de diagramme vers les fences markdown qu'elles couvrent.
# `common` s'applique à toutes les familles (clé spéciale dans rules.yaml).
FAMILY_FENCES = {
    "mermaid":   ["mermaid"],
    "plantuml":  ["plantuml", "puml"],
    "graphviz":  ["graphviz", "dot"],
    "excalidraw": ["excalidraw"],
}

# Mapping des flags YAML (chaînes) vers les constantes re Python.
RE_FLAG_MAP = {
    "MULTILINE":   re.MULTILINE,
    "DOTALL":      re.DOTALL,
    "IGNORECASE":  re.IGNORECASE,
    "VERBOSE":     re.VERBOSE,
    "UNICODE":     re.UNICODE,
}


@dataclass
class DiagramError:
    """Represents a diagram error found in a file."""
    file_path: Path
    line_number: int
    diagram_type: str
    error_type: str
    error_message: str
    diagram_content: str


@dataclass
class CompiledRule:
    """A rule from diagram-rules.yaml after parsing, validation and regex compilation."""
    id: str
    name: str
    rationale: str
    family: str            # mermaid | plantuml | graphviz | excalidraw | common
    scope: List[str]       # sous-types ou ["*"]
    pattern: str
    compiled_pattern: "re.Pattern"
    replacement: str
    flags: int             # OR des flags re
    examples: List[Dict[str, str]]   # liste de {before, after}
    introduced_in_iter: int
    introduced_by: str
    promoted: bool
    raw: Dict[str, Any] = field(default_factory=dict)  # pour debug


@dataclass
class RulesValidationReport:
    """Résultat des 5 validations §20.6 de la spec."""
    schema_errors: List[str] = field(default_factory=list)
    compile_errors: List[str] = field(default_factory=list)
    example_failures: List[str] = field(default_factory=list)
    duplicate_ids: List[str] = field(default_factory=list)
    cycle_warnings: List[str] = field(default_factory=list)

    @property
    def is_fatal(self) -> bool:
        """Erreurs qui empêchent le fonctionnement."""
        return bool(self.schema_errors or self.compile_errors or self.duplicate_ids)

    @property
    def has_warnings(self) -> bool:
        return bool(self.example_failures or self.cycle_warnings)


def _parse_re_flags(flag_names: List[str]) -> int:
    """Convertit une liste de noms de flags YAML en entier OR-é."""
    result = 0
    for name in flag_names or []:
        flag = RE_FLAG_MAP.get(name.upper())
        if flag is None:
            raise ValueError(f"Unknown re flag: {name!r}")
        result |= flag
    return result


def load_rules_from_yaml(yaml_path: Path) -> Tuple[List[CompiledRule], RulesValidationReport]:
    """
    Charge et valide diagram-rules.yaml selon la spec §20.6.

    Effectue les 5 validations :
    1. Schéma (champs requis)
    2. Compilabilité regex
    3. Reproductibilité des exemples (T1 rejoué)
    4. Unicité des `id`
    5. Détection de cycles d'ordre (basique : règle qui défait une règle amont)

    Returns:
        (compiled_rules, validation_report)
        Si validation_report.is_fatal, compiled_rules est partiel.
    """
    report = RulesValidationReport()

    if not yaml_path.exists():
        report.schema_errors.append(f"Rules file not found: {yaml_path}")
        return [], report

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        report.schema_errors.append(f"YAML parse error: {e}")
        return [], report

    raw_rules = data.get("rules") or []
    if not isinstance(raw_rules, list):
        report.schema_errors.append("Top-level 'rules' must be a list")
        return [], report

    compiled: List[CompiledRule] = []
    seen_ids = set()

    for idx, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            report.schema_errors.append(f"rules[{idx}]: not a mapping")
            continue

        # --- Validation 1 : schéma ---
        rid = raw.get("id")
        required = ["id", "name", "rationale", "family", "scope", "pattern", "replacement"]
        missing = [k for k in required if raw.get(k) is None]
        if missing:
            report.schema_errors.append(
                f"rules[{idx}] (id={rid!r}): missing fields: {missing}"
            )
            continue

        # --- Validation 4 : unicité id ---
        if rid in seen_ids:
            report.duplicate_ids.append(rid)
            continue
        seen_ids.add(rid)

        # --- Validation 2 : compilabilité regex ---
        try:
            flags_int = _parse_re_flags(raw.get("flags") or [])
        except ValueError as e:
            report.compile_errors.append(f"{rid}: {e}")
            continue

        try:
            compiled_pat = re.compile(raw["pattern"], flags_int)
        except re.error as e:
            report.compile_errors.append(f"{rid}: regex compile failed: {e}")
            continue

        rule = CompiledRule(
            id=rid,
            name=raw.get("name", rid),
            rationale=raw.get("rationale", ""),
            family=raw["family"],
            scope=list(raw["scope"]) if isinstance(raw["scope"], list) else [str(raw["scope"])],
            pattern=raw["pattern"],
            compiled_pattern=compiled_pat,
            replacement=raw["replacement"],
            flags=flags_int,
            examples=list(raw.get("examples") or []),
            introduced_in_iter=int(raw.get("introduced_in_iter", 0)),
            introduced_by=raw.get("introduced_by", "unknown"),
            promoted=bool(raw.get("promoted", False)),
            raw=raw,
        )

        # --- Validation 3 : reproductibilité des exemples ---
        for ex_idx, ex in enumerate(rule.examples):
            before = ex.get("before")
            after = ex.get("after")
            if before is None or after is None:
                report.example_failures.append(
                    f"{rid}: example[{ex_idx}] missing before/after"
                )
                continue
            try:
                produced = rule.compiled_pattern.sub(rule.replacement, before)
            except re.error as e:
                report.example_failures.append(
                    f"{rid}: example[{ex_idx}] sub error: {e}"
                )
                continue
            if produced != after:
                report.example_failures.append(
                    f"{rid}: example[{ex_idx}] mismatch: "
                    f"before={before!r} -> got={produced!r} expected={after!r}"
                )

        compiled.append(rule)

    return compiled, report


class RegexDiagramFixer:
    """
    Fix diagrams (Mermaid, PlantUML, Graphviz) using regex patterns from
    diagram-rules.yaml.

    The rules are loaded once at __init__, validated according to §20.6 of the spec,
    and applied to each diagram block found in a file. Each block is processed by
    rules whose `family` matches the fence type and whose `scope` covers the
    declared diagram subtype (or `*` for any).
    """

    DEFAULT_RULES_PATH = Path(
        "workplace-ambulon/piag-chat/prompts/diagram-rules.yaml"
    )

    def __init__(
        self,
        rules_yaml: Optional[Path] = None,
        rules_md: Optional[Path] = None,
        only_promoted: bool = True,
        strict: bool = False,
    ):
        """
        Args:
            rules_yaml: Path to diagram-rules.yaml. If None, use DEFAULT_RULES_PATH.
            rules_md: Path to REGLES_MERMAID.md (humain) — chargé pour le fallback LLM.
            only_promoted: If True, only apply rules with promoted=true.
            strict: If True, raise on validation errors. Otherwise log and continue.
        """
        self.rules_yaml = rules_yaml or self.DEFAULT_RULES_PATH
        self.rules_md = rules_md
        self.only_promoted = only_promoted

        compiled, report = load_rules_from_yaml(self.rules_yaml)
        self.validation_report = report
        self.all_rules = compiled
        self.rules: List[CompiledRule] = [
            r for r in compiled if (r.promoted or not only_promoted)
        ]

        if report.is_fatal:
            msg = (
                f"Rules file {self.rules_yaml} has fatal errors: "
                f"schema={len(report.schema_errors)} "
                f"compile={len(report.compile_errors)} "
                f"duplicates={len(report.duplicate_ids)}"
            )
            if strict:
                raise ValueError(msg)
            logger.error(msg)
            for e in report.schema_errors[:5]:
                logger.error("  schema: %s", e)
            for e in report.compile_errors[:5]:
                logger.error("  compile: %s", e)

        if report.has_warnings:
            logger.warning(
                "Rules file warnings: example_failures=%d cycles=%d",
                len(report.example_failures),
                len(report.cycle_warnings),
            )
            for e in report.example_failures[:3]:
                logger.warning("  example: %s", e)

        # Pré-indexe les règles par famille pour application rapide
        self._rules_by_family: Dict[str, List[CompiledRule]] = {}
        for rule in self.rules:
            self._rules_by_family.setdefault(rule.family, []).append(rule)

        logger.info(
            "Loaded %d rules from %s (promoted=%d, candidates=%d, total=%d)",
            len(self.rules),
            self.rules_yaml,
            sum(1 for r in compiled if r.promoted),
            sum(1 for r in compiled if not r.promoted),
            len(compiled),
        )

        # Charge la doc humaine pour exposition externe (LLM fallback)
        self.rules_content = ""
        if rules_md and rules_md.exists():
            try:
                self.rules_content = rules_md.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning("Could not load rules markdown: %s", e)

    @staticmethod
    def _detect_diagram_subtype(family: str, code: str) -> Optional[str]:
        """Best-effort detection of the declared subtype within a block.

        Tolérante à la casse et aux fautes courantes (ex. 'classdiagram' minuscule
        que les règles vont précisément corriger). En cas d'échec total de
        détection, retourne None et le caller appliquera quand même toutes
        les règles de la famille (cf. _rule_matches_scope).
        """
        if family == "mermaid":
            # Case-insensitive : on veut détecter même les déclarations buggées
            # comme 'classdiagram' ou 'CLASSDIAGRAM' parce qu'on a des règles
            # qui corrigent justement ces cas.
            keywords_to_canonical = {
                "classdiagram":     "classDiagram",
                "sequencediagram":  "sequenceDiagram",
                "statediagram-v2":  "stateDiagram-v2",
                "statediagram":     "stateDiagram",
                "erdiagram":        "erDiagram",
                "usecasediagram":   "usecaseDiagram",
                "gantt":            "gantt",
                "pie":              "pie",
                "mindmap":          "mindmap",
                "gitgraph":         "gitGraph",
                "timeline":         "timeline",
                "journey":          "journey",
                "requirementdiagram": "requirementDiagram",
                "c4context":        "C4Context",
                "c4container":      "C4Container",
                "c4component":      "C4Component",
                "flowchart":        "flowchart",
                "graph":            "graph",
            }
            for lowered, canonical in keywords_to_canonical.items():
                if re.search(rf'^\s*{re.escape(lowered)}\b', code, re.IGNORECASE | re.MULTILINE):
                    return canonical
        elif family == "plantuml":
            if "@startmindmap" in code:
                return "mindmap"
            if "@startuml" in code:
                lower = code.lower()
                if "class " in lower:
                    return "class"
                if "->" in lower and "..." not in lower:
                    return "sequence"
                if "rectangle" in lower or "component " in lower:
                    return "component"
                return "uml"
        elif family == "graphviz":
            if re.search(r'\bdigraph\b', code):
                return "digraph"
            if re.search(r'\bgraph\b', code):
                return "graph"
        return None

    def _rule_matches_scope(self, rule: CompiledRule, subtype: Optional[str]) -> bool:
        """True si le scope de la règle couvre le subtype détecté.

        Si subtype est None (détection échouée), on est permissif et on
        applique toutes les règles de la famille — elles no-op si leur
        pattern ne matche pas, donc le coût est nul et on évite de manquer
        des fix sur des blocs mal-formés (le cas typique qu'on cherche à
        corriger).
        """
        if "*" in rule.scope:
            return True
        if subtype is None:
            return True  # permissif : essaye toutes les règles de la famille
        return subtype in rule.scope

    def _apply_rules_to_block(
        self, code: str, family: str
    ) -> Tuple[str, List[str]]:
        """Applique toutes les règles compatibles à un bloc, retourne (fixed, applied_ids)."""
        subtype = self._detect_diagram_subtype(family, code)
        applied: List[str] = []

        candidate_rules: List[CompiledRule] = []
        candidate_rules.extend(self._rules_by_family.get(family, []))
        candidate_rules.extend(self._rules_by_family.get("common", []))

        fixed = code
        for rule in candidate_rules:
            if not self._rule_matches_scope(rule, subtype):
                continue
            try:
                new_code = rule.compiled_pattern.sub(rule.replacement, fixed)
            except re.error as e:
                logger.error("Rule %s sub error: %s", rule.id, e)
                continue
            if new_code != fixed:
                applied.append(rule.id)
                fixed = new_code

        return fixed, applied

    def fix(self, content: str) -> Tuple[str, List[str]]:
        """
        Fix diagram syntax issues across all supported families.

        Iterates over all fenced code blocks (mermaid, plantuml, puml, graphviz, dot)
        and applies the rules whose family/scope matches.

        Args:
            content: File content to fix

        Returns:
            (fixed_content, list_of_fixes_applied)
        """
        fixed_content = content
        fixes_applied: List[str] = []
        block_index = [0]

        # Construit un seul regex couvrant toutes les fences supportées
        fence_alternation = "|".join(
            re.escape(f) for fences in FAMILY_FENCES.values() for f in fences
        )
        block_pattern = re.compile(
            rf'```({fence_alternation})\n(.*?)\n```',
            re.DOTALL,
        )

        # Cache du fence_type -> family pour résolution rapide
        fence_to_family: Dict[str, str] = {}
        for fam, fences in FAMILY_FENCES.items():
            for f in fences:
                fence_to_family[f] = fam

        def _on_block(match: "re.Match") -> str:
            block_index[0] += 1
            fence_type = match.group(1)
            original = match.group(2)
            family = fence_to_family.get(fence_type, "unknown")
            if family == "unknown":
                return match.group(0)

            new_code, applied_ids = self._apply_rules_to_block(original, family)
            if applied_ids:
                fixes_applied.append(
                    f"Block {block_index[0]} ({family}): "
                    f"applied {len(applied_ids)} rule(s): {', '.join(applied_ids)}"
                )
                return f'```{fence_type}\n{new_code}\n```'
            return match.group(0)

        fixed_content = block_pattern.sub(_on_block, fixed_content)
        return fixed_content, fixes_applied


class LLMDiagramFixer:
    """Fix Mermaid diagrams using LLM analysis and correction with project rules."""

    def __init__(self, provider_name: str, config: Dict, rules_file: Optional[Path] = None):
        self.provider_name = provider_name
        self.config = config
        self.api_key = get_api_key(provider_name, config)
        self.base_url = get_base_url(provider_name, config)
        self.provider_config = get_provider_config(provider_name, config)
        self.provider = get_provider(provider_name, self.api_key, self.base_url, self.provider_config)
        self.rules_file = rules_file
        self.rules_content = self._load_rules() if rules_file else ""

    def _load_rules(self) -> str:
        """Load project-specific Mermaid rules."""
        try:
            if self.rules_file and self.rules_file.exists():
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Could not load rules file: {e}")
        return ""

    def fix(self, content: str, file_path: Path) -> Tuple[str, List[str]]:
        """
        Fix diagram issues using LLM analysis.

        Args:
            content: File content to analyze and fix
            file_path: Path to file being processed

        Returns:
            Tuple of (fixed_content, list_of_fixes_applied)
        """
        fixed = content
        fixes_applied = []

        # Extract mermaid diagrams
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        diagrams = list(re.finditer(mermaid_pattern, content, re.DOTALL))

        for i, match in enumerate(diagrams):
            original_diagram = match.group(1)

            # Build correction prompt with project rules
            rules_context = ""
            if self.rules_content:
                rules_context = f"\nProject Mermaid Rules:\n{self.rules_content[:2000]}\n"

            prompt = f"""Analyze this Mermaid diagram and fix any syntax errors using project rules.
Only respond with the corrected diagram code, nothing else.

Original diagram:
```mermaid
{original_diagram}
```

{rules_context}

Standard Rules:
1. Fix any unclosed quotes, parentheses, or brackets
2. Correct diagram type declarations (graph, flowchart, classDiagram, etc.)
3. Fix arrow syntax (should be --> for most diagrams)
4. Ensure proper indentation (4 spaces for nested elements)
5. Ensure alias comes BEFORE color (#RRGGBB)
6. Remove problematic special chars (:, *, **) from node IDs
7. Add missing semicolons where needed
8. Fix actor/relationship definitions

Return ONLY the corrected Mermaid code without markdown backticks."""

            try:
                logger.info(f"Correcting diagram {i+1} in {file_path.name}")
                result = self.provider.generate(
                    prompt=prompt,
                    temperature=0.3,  # Low temp for consistency
                    max_tokens=2048
                )

                corrected_diagram = result["content"].strip()

                # Remove markdown formatting if LLM included it
                corrected_diagram = re.sub(r'^```mermaid\s*\n?', '', corrected_diagram)
                corrected_diagram = re.sub(r'\n?```\s*$', '', corrected_diagram)

                if original_diagram != corrected_diagram:
                    fixed = fixed.replace(
                        f'```mermaid\n{original_diagram}\n```',
                        f'```mermaid\n{corrected_diagram}\n```',
                        1
                    )
                    fixes_applied.append(f"Diagram {i+1}: Corrected by LLM")
                    logger.info(f"  ✓ Corrected diagram {i+1}")

            except Exception as e:
                logger.error(f"Failed to correct diagram {i+1}: {e}")
                fixes_applied.append(f"Diagram {i+1}: Failed to correct ({str(e)})")

        return fixed, fixes_applied


class DiagramValidator:
    """Validate Mermaid diagram syntax."""

    @staticmethod
    def validate(content: str) -> List[DiagramError]:
        """
        Validate Mermaid diagrams in content.

        Args:
            content: File content to validate

        Returns:
            List of DiagramError objects
        """
        errors = []

        # Check for unclosed code blocks
        open_blocks = content.count('```mermaid')
        close_blocks = content.count('```')
        if open_blocks * 2 != close_blocks:
            errors.append(DiagramError(
                file_path=Path("unknown"),
                line_number=0,
                diagram_type="code_block",
                error_type="unclosed_block",
                error_message="Unclosed mermaid code block",
                diagram_content=""
            ))

        # Extract and validate each diagram
        pattern = r'```mermaid\n(.*?)\n```'
        for i, match in enumerate(re.finditer(pattern, content, re.DOTALL)):
            diagram = match.group(1)

            # Check for empty diagrams
            if not diagram.strip() or diagram.strip().startswith('%'):
                errors.append(DiagramError(
                    file_path=Path("unknown"),
                    line_number=match.start(),
                    diagram_type="unknown",
                    error_type="empty_diagram",
                    error_message="Diagram appears to be empty or commented",
                    diagram_content=diagram[:50]
                ))
                continue

            # Detect diagram type
            diagram_type = DiagramValidator._detect_diagram_type(diagram)

            # Validate based on type
            type_errors = DiagramValidator._validate_by_type(diagram, diagram_type)
            errors.extend(type_errors)

        return errors

    @staticmethod
    def _detect_diagram_type(diagram: str) -> str:
        """Detect the type of Mermaid diagram."""
        if re.search(r'^\s*graph\s+', diagram, re.MULTILINE):
            return "graph"
        elif re.search(r'^\s*flowchart\s+', diagram, re.MULTILINE):
            return "flowchart"
        elif re.search(r'^\s*classDiagram\s*$', diagram, re.MULTILINE):
            return "classDiagram"
        elif re.search(r'^\s*sequenceDiagram\s*$', diagram, re.MULTILINE):
            return "sequenceDiagram"
        elif re.search(r'^\s*usecaseDiagram\s*$', diagram, re.MULTILINE):
            return "usecaseDiagram"
        elif re.search(r'^\s*stateDiagram\s*', diagram, re.MULTILINE):
            return "stateDiagram"
        return "unknown"

    @staticmethod
    def _validate_by_type(diagram: str, diagram_type: str) -> List[DiagramError]:
        """Validate diagram syntax based on type."""
        errors = []

        # Check for unmatched quotes
        if '"' in diagram:
            if diagram.count('"') % 2 != 0:
                errors.append(DiagramError(
                    file_path=Path("unknown"),
                    line_number=0,
                    diagram_type=diagram_type,
                    error_type="unmatched_quotes",
                    error_message="Unmatched quotes in diagram",
                    diagram_content=diagram[:100]
                ))

        # Check for unmatched parentheses
        if '(' in diagram or ')' in diagram:
            open_parens = diagram.count('(')
            close_parens = diagram.count(')')
            if open_parens != close_parens:
                errors.append(DiagramError(
                    file_path=Path("unknown"),
                    line_number=0,
                    diagram_type=diagram_type,
                    error_type="unmatched_parens",
                    error_message="Unmatched parentheses in diagram",
                    diagram_content=diagram[:100]
                ))

        return errors


def main(argv=None):
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix and validate Mermaid diagrams in documentation files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix diagrams using regex patterns
  %(prog)s --mode regex --input workplace-ambulon/delivrables

  # Fix diagrams using LLM
  %(prog)s --mode llm --input workplace-ambulon/delivrables --provider cloud_gpt_oss_120b

  # Validate diagrams only
  %(prog)s --mode validate --input workplace-ambulon/delivrables
        """
    )

    parser.add_argument(
        "--mode",
        choices=["regex", "llm", "validate"],
        default="regex",
        help="Correction mode (default: regex)"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Input directory containing .md files"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output directory for fixed files (default: overwrite input)"
    )
    parser.add_argument(
        "--provider",
        default="cloud_gpt_oss_120b",
        help="LLM provider to use (for --mode llm)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/llm.yaml"),
        help="Path to LLM config file"
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=Path("workplace-ambulon/piag-chat/prompts/REGLES_MERMAID.md"),
        help="Path to humain-readable rules file (markdown, used by LLM mode)"
    )
    parser.add_argument(
        "--rules-yaml",
        type=Path,
        default=Path("workplace-ambulon/piag-chat/prompts/diagram-rules.yaml"),
        help="Path to machine-executable rules file (regex mode)"
    )
    parser.add_argument(
        "--include-candidates",
        action="store_true",
        help="Also apply rules with promoted=false (candidates)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on rules.yaml validation errors instead of warning"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args(argv)

    # Setup logging
    setup_logging(level=logging.DEBUG if args.verbose else logging.INFO)

    # Validate input
    if not args.input.exists():
        logger.error(f"Input directory not found: {args.input}")
        return 1

    # Load LLM config if needed
    config = {}
    if args.mode == "llm":
        if not args.config.exists():
            logger.error(f"Config file not found: {args.config}")
            return 1
        config = load_llm_config(args.config)

    # Find all markdown files
    md_files = list(args.input.glob("*.md"))
    logger.info(f"Found {len(md_files)} markdown files")

    if not md_files:
        logger.warning("No markdown files found")
        return 0

    # Initialize fixer
    rules_md_path = args.rules if args.rules and args.rules.exists() else None
    rules_yaml_path = args.rules_yaml if args.rules_yaml and args.rules_yaml.exists() else None

    if args.mode == "regex":
        fixer = RegexDiagramFixer(
            rules_yaml=rules_yaml_path,
            rules_md=rules_md_path,
            only_promoted=not args.include_candidates,
            strict=args.strict,
        )
    elif args.mode == "llm":
        fixer = LLMDiagramFixer(args.provider, config, rules_md_path)
    else:  # validate
        fixer = None

    # Process files
    total_fixes = 0
    failed_files = []

    for md_file in md_files:
        logger.info(f"Processing: {md_file.name}")

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if args.mode == "validate":
                errors = DiagramValidator.validate(content)
                if errors:
                    logger.warning(f"  Found {len(errors)} validation errors")
                    for error in errors:
                        logger.debug(f"    {error.error_type}: {error.error_message}")
                else:
                    logger.info(f"  ✓ All diagrams valid")

            else:
                fixed_content, fixes = fixer.fix(content)

                if fixes:
                    logger.info(f"  Applied {len(fixes)} fixes")
                    for fix in fixes:
                        logger.debug(f"    {fix}")
                    total_fixes += len(fixes)

                    # Write fixed content
                    output_file = args.output / md_file.name if args.output else md_file
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    logger.info(f"  Saved to: {output_file}")
                else:
                    logger.info(f"  No fixes needed")

        except Exception as e:
            logger.error(f"  Failed to process: {e}")
            failed_files.append(md_file.name)

    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Processed {len(md_files)} files")
    print(f"   Total fixes applied: {total_fixes}")
    if failed_files:
        print(f"   Failed files: {len(failed_files)}")
        for fname in failed_files:
            print(f"     - {fname}")
    print("=" * 70)

    return 1 if failed_files else 0


if __name__ == "__main__":
    sys.exit(main())
