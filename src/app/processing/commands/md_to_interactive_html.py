"""
Commande pour convertir un fichier Markdown en HTML interactif complet.

Workflow:
1. Ajoute TOC (add-toc4md)
2. Ajoute iTOC/backlinks (add-itoc4md)
3. Convertit en HTML (md2html-diagrams)
4. Rend interactif (make-html-interactive)

Usage:
    ambulon md-to-interactive-html mon-document.md
    
Produit:
    - mon-document-itoc.md (Markdown avec TOC et backlinks)
    - mon-document-itoc-interactive.html (HTML interactif final)
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional


def md_to_interactive_html(
    input_path: str,
    output_dir: Optional[str] = None,
    min_level: int = 2,
    max_level: int = 6,
    no_diagrams: bool = False,
    verbose: bool = False
) -> int:
    """
    Convert a Markdown file to an interactive HTML file with TOC and backlinks.
    
    Args:
        input_path: Path to input Markdown file
        output_dir: Optional output directory (default: same as input)
        min_level: Minimum heading level for TOC (default: 2)
        max_level: Maximum heading level for TOC (default: 6)
        no_diagrams: Skip diagram conversion (faster)
        verbose: Print detailed progress
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    input_file = Path(input_path).resolve()
    
    if not input_file.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        return 1
        
    if not input_file.is_file():
        print(f"Error: '{input_path}' is not a file.", file=sys.stderr)
        return 1
    
    # Determine output directory
    if output_dir:
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = input_file.parent
    
    base_name = input_file.stem
    toc_file = out_dir / f"{base_name}-toced.md"
    itoc_file = out_dir / f"{base_name}-itoced.md"
    html_file = out_dir / f"{base_name}-itoced.html"
    interactive_file = out_dir / f"{base_name}-interactive.html"
    
    try:
        # Step 1: Add TOC
        if verbose:
            print(f"[1/4] Adding TOC to {input_file.name}...")
            
        result = subprocess.run([
            sys.executable, '-m', 'app.toc.commands.add_toc4md',
            str(input_file),
            '-o', str(toc_file),
            '--min-level', str(min_level),
            '--max-level', str(max_level),
            '-v' if verbose else '-q'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error adding TOC: {result.stderr}", file=sys.stderr)
            return result.returncode
            
        if verbose:
            print(f"      Created: {toc_file.name}")
        
        # Step 2: Add iTOC (backlinks)
        if verbose:
            print(f"[2/4] Adding backlinks to {toc_file.name}...")
            
        result = subprocess.run([
            sys.executable, '-m', 'app.toc.commands.add_itoc4md',
            str(toc_file),
            '-o', str(itoc_file),
            '--min-level', str(min_level),
            '--max-level', str(max_level),
            '-v' if verbose else '-q'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error adding iTOC: {result.stderr}", file=sys.stderr)
            return result.returncode
        
        if verbose:
            print(f"      Created: {itoc_file.name}")
        
        # Step 3: Convert to HTML
        if verbose:
            print(f"[3/4] Converting to HTML...")
            
        cmd = [
            sys.executable, '-m', 'app.diagrams.commands.md2html',
            str(itoc_file),
            '-o', str(html_file)
        ]
        if no_diagrams:
            cmd.append('--no-convert-diagrams')
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error converting to HTML: {result.stderr}", file=sys.stderr)
            return result.returncode
            
        if verbose:
            print(f"      Created: {html_file.name}")
        
        # Step 4: Make interactive
        if verbose:
            print(f"[4/4] Augmenting HTML...")
        
        # Import and call directly
        from .add_augment import augment
        result = augment(
            input_path=str(html_file),
            output_path=str(augmented_file),
            verbose=verbose
        )
        
        if result != 0:
            print(f"Error making interactive (exit code: {result})", file=sys.stderr)
            return result
            
        if verbose:
            print(f"      Created: {augmented_file.name}")
        
        # Success summary
        print(f"\n[SUCCESS] Conversion complete!")
        print(f"  TOC Markdown:   {toc_file}")
        print(f"  iTOC Markdown:  {itoc_file}")
        print(f"  HTML:           {html_file}")
        print(f"  Augmented:      {augmented_file}")
        
        # File sizes
        toc_size = toc_file.stat().st_size
        itoc_size = itoc_file.stat().st_size
        html_size = html_file.stat().st_size
        augmented_size = augmented_file.stat().st_size
        
        print(f"\nFile sizes:")
        print(f"  {toc_file.name}: {toc_size:,} bytes")
        print(f"  {itoc_file.name}: {itoc_size:,} bytes")
        print(f"  {html_file.name}: {html_size:,} bytes")
        print(f"  {augmented_file.name}: {augmented_size:,} bytes")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv=None):
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert Markdown to interactive HTML with TOC and backlinks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.md
  %(prog)s document.md -o output_dir/
  %(prog)s document.md --min-level 2 --max-level 4
  %(prog)s document.md --no-diagrams  # Faster, skip diagram conversion
        """
    )
    
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: same as input)')
    parser.add_argument('--min-level', type=int, default=2, help='Minimum heading level (default: 2)')
    parser.add_argument('--max-level', type=int, default=6, help='Maximum heading level (default: 6)')
    parser.add_argument('--no-diagrams', action='store_true', help='Skip diagram conversion')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args(argv)
    
    return md_to_interactive_html(
        input_path=args.input,
        output_dir=args.output_dir,
        min_level=args.min_level,
        max_level=args.max_level,
        no_diagrams=args.no_diagrams,
        verbose=args.verbose
    )


if __name__ == '__main__':
    sys.exit(main())
