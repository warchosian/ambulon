"""
Module to fix and validate Mermaid diagrams in generated documentation files.

Supports two correction modes:
1. REGEX: Pattern-based fixes for common Mermaid syntax errors
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
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from app.core.logging_config import setup_logging
from app.llm.core.config import load_llm_config, get_api_key, get_base_url, get_provider_config
from app.llm.core.providers import get_provider

logger = logging.getLogger(__name__)


@dataclass
class DiagramError:
    """Represents a diagram error found in a file."""
    file_path: Path
    line_number: int
    diagram_type: str
    error_type: str
    error_message: str
    diagram_content: str


class RegexDiagramFixer:
    """Fix Mermaid diagrams using regex patterns and project rules."""

    def __init__(self, rules_file: Optional[Path] = None):
        self.patterns = [
            # Fix unclosed code blocks (critical)
            (r'(```mermaid\n[^`]+?)(?!```)\n(?=\n[^`]|$)', r'\1\n```\n'),
            # Fix classdiagram errors: classdiagram; → classDiagram and classdiagram → classDiagram
            (r'\bclassdiagram\b', r'classDiagram'),
            (r'classdiagram;', r'classDiagram'),
            # Remove PlantUML package syntax from classDiagram (Mermaid doesn't support packages)
            (r'^\s*package\s+[\w.]+\s*\{\s*$', r''),  # Remove package declarations
            (r'^\s*\}\s*$', r''),  # Remove closing braces from packages
            # Clean up multiple blank lines created by package removal
            (r'\n\s*\n\s*\n', r'\n\n'),  # Replace 3+ newlines with 2
            # Fix graph type declarations with semicolons: graph TB; → graph TB
            (r'\b(graph|flowchart)\s+(TB|LR|TD|BT|RL|DLR|TBL);', r'\1 \2'),
            # Fix end statements with semicolons: end; → end
            (r'\bend;', r'end'),
            # Fix CSS stroke-width syntax: stroke-width_2px → stroke-width:2px
            (r'stroke-width_(\d+)px', r'stroke-width:\1px'),
            # Fix missing semicolons at end of lines (skip diagram keywords)
            # This pattern intentionally left simpler - avoid matching declaration lines
            # Only apply to non-keyword lines (like method/property definitions)
            (r'^(?!(?:graph|flowchart|Graph|Flowchart|classDiagram|classdiagram|sequenceDiagram|stateDiagram|gantt|pie|mindmap|---)\b)(\w+)\s*\n(?=\s{4,})', r'\1;\n'),
            # Fix unclosed strings in quotes
            (r'(".*?)(?<!\\)"(?!")(?!.*")', r'\1"'),
            # Fix arrow syntax variations
            (r'(\w+)\s*--+>\s*(\w+)', r'\1 --> \2'),
            (r'(\))\s*--+>\s*\(', r'\1 --> \('),
            # Fix actor definitions
            (r'actor\s+"([^"]+)"\s+as\s+(\w+)', r'actor \1 as \2'),
            # Fix color before alias (Mermaid rule: alias before color)
            (r'([\w\s"]+)\s+#([0-9A-Fa-f]{6})\s+as\s+(\w+)',
             r'\1 as \3 #\2'),
            # Fix missing colons in init blocks
            (r"%%\{init:\s*\{([^}]+)\}\}", r"%%{init: {\1}}%%"),
            # Fix graph/flowchart lowercase (but NOT classDiagram which should be camelCase)
            (r'\b(Graph|FlowChart|GRAPH|FLOWCHART)\b',
             lambda m: 'graph' if m.group(1).lower().startswith('graph') else 'flowchart'),
            # Remove problematic special chars from node IDs (Mermaid rule)
            (r'(\w+):(\w+)', r'\1_\2'),  # Replace : with _
            # Fix empty diagram blocks
            (r'```mermaid\s*\n\s*```', r'```mermaid\n%% Empty diagram - TODO: Add content\n```'),
        ]
        self.rules_file = rules_file
        self.rules_content = self._load_rules() if rules_file else ""

    def _load_rules(self) -> str:
        """Load Mermaid rules from file if available."""
        try:
            if self.rules_file and self.rules_file.exists():
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Could not load rules file: {e}")
        return ""

    def fix(self, content: str) -> Tuple[str, List[str]]:
        """
        Fix diagram syntax issues using regex patterns.

        Args:
            content: File content to fix

        Returns:
            Tuple of (fixed_content, list_of_fixes_applied)
        """
        fixed = content
        fixes_applied = []
        block_count = 0

        # Process each mermaid block and apply fixes
        def fix_mermaid_block(match):
            nonlocal block_count, fixes_applied
            block_count += 1
            original = match.group(1)
            fixed_block = original

            # Apply regex patterns
            for pattern, replacement in self.patterns:
                if callable(replacement):
                    fixed_block = re.sub(pattern, replacement, fixed_block, flags=re.MULTILINE)
                else:
                    fixed_block = re.sub(pattern, replacement, fixed_block, flags=re.MULTILINE)

            # Track applied fixes
            if original != fixed_block:
                fixes_applied.append(f"Block {block_count}: Fixed diagram syntax")
                return f'```mermaid\n{fixed_block}\n```'
            return match.group(0)

        # Apply fixes to all mermaid blocks
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        fixed = re.sub(mermaid_pattern, fix_mermaid_block, fixed, flags=re.DOTALL)

        return fixed, fixes_applied


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
        default=Path("workplace-ambulon/piag-chat/prompts/REGLES_MERMAID.mmd.md"),
        help="Path to project Mermaid rules file"
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
    rules_file = args.rules if hasattr(args, 'rules') and args.rules.exists() else None

    if args.mode == "regex":
        fixer = RegexDiagramFixer(rules_file)
    elif args.mode == "llm":
        fixer = LLMDiagramFixer(args.provider, config, rules_file)
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
