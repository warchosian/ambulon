"""
Command to convert HTML files to PDF while preserving hyperlinks and SVG vectors.

This module supports two rendering methods:
1. Chromium via Playwright (recommended, best SVG support)
2. wkhtmltopdf (fallback, older but works offline)

Features:
- Internal anchor links (TOC navigation)
- External hyperlinks
- CSS styling
- SVG diagrams (best with Chromium)
- Portrait and landscape orientations
"""

import sys
import shutil
import subprocess
import os
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def _find_wkhtmltopdf(custom_path: Optional[str] = None) -> Optional[str]:
    """
    Find wkhtmltopdf executable.
    
    Args:
        custom_path: Optional custom path to wkhtmltopdf executable
        
    Returns:
        Path to wkhtmltopdf executable or None if not found
    """
    # First check custom path if provided
    if custom_path:
        path = Path(custom_path)
        if path.exists():
            return str(path.resolve())
    
    # Try shutil.which (standard way)
    wk = shutil.which("wkhtmltopdf")
    if wk:
        return wk
    
    # Common Windows locations to check
    common_paths = [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\tools\wkhtmltopdf\bin\wkhtmltopdf.exe",
    ]
    
    # Check if wkhtmltopdf is in PATH via where command (Windows)
    try:
        result = subprocess.run(
            ["where", "wkhtmltopdf"],
            capture_output=True,
            text=True,
            shell=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0].strip()
    except Exception:
        pass
    
    # Check common paths
    for path in common_paths:
        if Path(path).exists():
            return path
    
    return None


def _get_wkhtmltopdf_version(executable_path: str) -> Optional[str]:
    """
    Get wkhtmltopdf version.
    
    Returns:
        Version string or None if failed
    """
    try:
        result = subprocess.run(
            [executable_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse version from output like "wkhtmltopdf 0.12.4 (with patched qt)"
            output = result.stdout.strip()
            if "wkhtmltopdf" in output.lower():
                parts = output.split()
                for part in parts:
                    if part[0].isdigit():
                        return part
        return None
    except Exception:
        return None


def _try_wkhtmltopdf(
    src: Path, 
    dst: Path, 
    orientation: str = 'portrait',
    verbose: bool = False,
    executable_path: Optional[str] = None
) -> int:
    """
    Try to convert HTML to PDF using wkhtmltopdf.
    
    Args:
        src: Source HTML file path
        dst: Destination PDF file path
        orientation: Page orientation
        verbose: Verbose output
        executable_path: Optional path to wkhtmltopdf executable
        
    Returns:
        0 on success, 1 on failure
    """
    wkhtmltopdf = executable_path or _find_wkhtmltopdf()
    
    if not wkhtmltopdf:
        if verbose:
            print("[ERROR] wkhtmltopdf not found.", file=sys.stderr)
        return 1
    
    # Get version for compatibility
    version = _get_wkhtmltopdf_version(wkhtmltopdf)
    if verbose:
        print(f"[INFO] wkhtmltopdf version: {version or 'unknown'}")
    
    if verbose:
        print(f"[INFO] Using wkhtmltopdf: {wkhtmltopdf}")
    
    try:
        # Build command with SVG support options
        # Note: wkhtmltopdf 0.12.4 has limited SVG support via QtWebKit
        cmd = [
            wkhtmltopdf,
            "--encoding", "utf-8",
            "--orientation",
            "Landscape" if orientation == "landscape" else "Portrait",
            "--enable-javascript",
            "--javascript-delay", "3000",  # Wait for SVG rendering
            "--no-stop-slow-scripts",
        ]
        
        # Add options for newer versions (0.12.6+)
        if version and version >= "0.12.6":
            cmd.extend(["--enable-local-file-access"])
        
        cmd.extend([str(src), str(dst)])
        
        if verbose:
            print(f"[INFO] Command: {' '.join(cmd)}")
        
        # Use shell=True on Windows for better compatibility with paths
        use_shell = sys.platform == 'win32'
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True, 
            shell=use_shell
        )
        
        if verbose and result.stdout:
            print(result.stdout)
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] wkhtmltopdf failed (exit code {e.returncode})", file=sys.stderr)
        if e.stderr:
            print(f"[ERROR] {e.stderr}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] wkhtmltopdf error: {e}", file=sys.stderr)
        return 1


def _try_chromium(
    input_file: Path,
    output_file: Path,
    orientation: str = 'portrait',
    verbose: bool = False
) -> int:
    """
    Try to convert HTML to PDF using Chromium via Playwright.
    
    Returns:
        0 on success, 1 on failure, -1 if Chromium not available
    """
    if not PLAYWRIGHT_AVAILABLE:
        if verbose:
            print("[INFO] Playwright not installed.")
        return -1
    
    try:
        if verbose:
            print("\n[INFO] Starting Chromium for PDF conversion...")
            print("[INFO] SVG diagrams will be preserved as vectors")
            print("[INFO] All hyperlinks will be preserved")

        with sync_playwright() as p:
            # Launch browser
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                if verbose:
                    print(f"[INFO] Chromium launch failed: {e}")
                return -1
                
            page = browser.new_page()

            # Load HTML file
            if verbose:
                print(f"[INFO] Loading HTML file...")

            page.goto(f'file:///{input_file.as_posix()}')

            # Wait for page to fully load
            page.wait_for_load_state('networkidle')
            
            # Wait for fonts to load
            page.wait_for_load_state('domcontentloaded')

            # Additional wait for SVG rendering (important!)
            if verbose:
                print("[INFO] Waiting for SVG rendering...")
            page.wait_for_timeout(3000)  # 3 seconds for SVG
            
            # Force any lazy-loaded SVGs to render by scrolling
            if verbose:
                print("[INFO] Scrolling to trigger lazy loading...")
            page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight);
                window.scrollTo(0, 0);
            """)
            page.wait_for_timeout(1000)  # Wait after scroll
            
            # Inject CSS to ensure SVGs are visible
            if verbose:
                print("[INFO] Ensuring SVG visibility...")
            page.add_style_tag(content="""
                svg {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    max-width: 100% !important;
                    height: auto !important;
                }
                .diagram svg, .diagram svg {
                    display: block !important;
                    margin: 20px auto !important;
                }
            """)
            page.wait_for_timeout(500)

            # Configure PDF options
            pdf_options = {
                'path': str(output_file),
                'format': 'A4',
                'print_background': True,
                'prefer_css_page_size': False,
                'margin': {
                    'top': '20mm',
                    'right': '20mm',
                    'bottom': '20mm',
                    'left': '20mm'
                }
            }

            # Set orientation
            if orientation == 'landscape':
                pdf_options['landscape'] = True

            # Generate PDF
            if verbose:
                print("[INFO] Generating PDF with vector SVG...")

            page.pdf(**pdf_options)
            browser.close()

        # Get file sizes for reporting
        input_size = input_file.stat().st_size
        output_size = output_file.stat().st_size

        print(f"\n[SUCCESS] PDF created (Chromium): {output_file}")
        print(f"[INFO] Input HTML: {input_size:,} bytes")
        print(f"[INFO] Output PDF: {output_size:,} bytes")
        print(f"[INFO] Orientation: {orientation}")
        print(f"[INFO] SVG diagrams preserved as vectors")
        print(f"[INFO] All hyperlinks preserved")

        return 0

    except Exception as e:
        error_msg = str(e).lower()
        
        # Check if it's a Chromium not found error
        if any(x in error_msg for x in [
            "executable doesn't exist",
            "browsertype.launch",
            "chromium",
            "could not find",
            "no such file"
        ]):
            if verbose:
                print(f"[INFO] Chromium not available: {e}")
            return -1
        else:
            # Other error, report it
            print(f"Error: Failed to convert with Chromium: {e}", file=sys.stderr)
            return 1


def convert_html_to_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    orientation: str = 'portrait',
    method: str = 'auto',
    wkhtmltopdf_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Convert HTML file to PDF while preserving hyperlinks and SVG vectors.

    Args:
        input_path: Path to input HTML file
        output_path: Optional path to output PDF file. If None, uses <input>.pdf
        orientation: Page orientation - 'portrait' or 'landscape' (default: 'portrait')
        method: Rendering method - 'auto', 'chromium', or 'wkhtmltopdf' (default: 'auto')
        wkhtmltopdf_path: Optional path to wkhtmltopdf executable
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_file = Path(input_path).resolve()

    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        return 1

    if not input_file.is_file():
        print(f"Error: '{input_path}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        output_file = input_file.parent / f"{input_file.stem}.pdf"
    else:
        output_file = Path(output_path).resolve()

    # Validate orientation
    if orientation not in ['portrait', 'landscape']:
        print(f"Error: Invalid orientation '{orientation}'. Must be 'portrait' or 'landscape'.", file=sys.stderr)
        return 1

    # Parse method
    method = method.lower()
    if method not in ['auto', 'chromium', 'wkhtmltopdf']:
        print(f"Error: Invalid method '{method}'. Must be 'auto', 'chromium', or 'wkhtmltopdf'.", file=sys.stderr)
        return 1

    if verbose:
        print(f"Processing: {input_file}")
        print(f"Output: {output_file}")
        print(f"Orientation: {orientation}")
        print(f"Method: {method}")

    # Suppress verbose Qt warnings on Windows
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
    
    # Try based on method preference
    if method == 'chromium':
        # Force Chromium
        chromium_result = _try_chromium(input_file, output_file, orientation, verbose)
        if chromium_result == 0:
            return 0
        elif chromium_result == -1:
            print("Error: Chromium browser not installed.", file=sys.stderr)
            print("\nNote: Playwright (Python package) is in the wheel,", file=sys.stderr)
            print("      but Chromium (browser binary) must be installed separately.", file=sys.stderr)
            print("\nInstall Chromium (~100 MB, one-time installation):", file=sys.stderr)
            print("  python -m playwright install chromium", file=sys.stderr)
            print("\nOr use wkhtmltopdf (limited SVG support):", file=sys.stderr)
            print("  ambulon html2pdf doc.html --method wkhtmltopdf", file=sys.stderr)
            return 1
        else:
            return 1
            
    elif method == 'wkhtmltopdf':
        # Force wkhtmltopdf
        wk_result = _try_wkhtmltopdf(input_file, output_file, orientation, verbose, wkhtmltopdf_path)
        if wk_result == 0:
            print(f"\n[SUCCESS] PDF created (wkhtmltopdf): {output_file}")
            # Warn about SVG limitations
            version = _get_wkhtmltopdf_version(wkhtmltopdf_path or _find_wkhtmltopdf() or "")
            if version and version < "0.12.6":
                print("\n[WARNING] wkhtmltopdf version < 0.12.6 detected.", file=sys.stderr)
                print("[WARNING] SVG diagrams may not render correctly.", file=sys.stderr)
                print("[WARNING] For better SVG support, use --method chromium or update wkhtmltopdf.", file=sys.stderr)
            return 0
        else:
            print("\nError: wkhtmltopdf conversion failed.", file=sys.stderr)
            if not wkhtmltopdf_path and not _find_wkhtmltopdf():
                print("\nwkhtmltopdf not found. Install it from:", file=sys.stderr)
                print("  https://wkhtmltopdf.org/downloads.html", file=sys.stderr)
            return 1
    
    else:  # method == 'auto'
        # Try Chromium first (better quality)
        chromium_result = _try_chromium(input_file, output_file, orientation, verbose)
        
        if chromium_result == 0:
            return 0
        
        # Chromium failed or not available, try wkhtmltopdf
        if verbose or chromium_result == -1:
            if chromium_result == -1:
                print("[INFO] Chromium not available, trying wkhtmltopdf...")
            else:
                print("[INFO] Chromium failed, trying wkhtmltopdf...")
        
        wk_result = _try_wkhtmltopdf(input_file, output_file, orientation, verbose, wkhtmltopdf_path)
        
        if wk_result == 0:
            print(f"\n[SUCCESS] PDF created (wkhtmltopdf): {output_file}")
            # Warn about SVG limitations
            version = _get_wkhtmltopdf_version(wkhtmltopdf_path or _find_wkhtmltopdf() or "")
            if version and version < "0.12.6":
                print("\n[WARNING] wkhtmltopdf version < 0.12.6 detected.", file=sys.stderr)
                print("[WARNING] SVG diagrams may not render correctly.", file=sys.stderr)
                print("[WARNING] For better SVG support, use --method chromium or update wkhtmltopdf.", file=sys.stderr)
            return 0
        
        # Both failed
        print("\nError: Failed to convert HTML to PDF.", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("  1. Install Chromium browser (recommended for SVG):", file=sys.stderr)
        print("     python -m playwright install chromium", file=sys.stderr)
        print("     (Note: Playwright package is in wheel, but browser is separate)", file=sys.stderr)
        print("\n  2. Or use wkhtmltopdf if installed:", file=sys.stderr)
        wk_path = _find_wkhtmltopdf(wkhtmltopdf_path)
        if wk_path:
            print(f"     Found: {wk_path}", file=sys.stderr)
        else:
            print("     Download from: https://wkhtmltopdf.org/downloads.html", file=sys.stderr)
        print("\n  3. For help: ambulon html2pdf --install-chromium", file=sys.stderr)
        
        # Show if wkhtmltopdf was found
        wk_path = _find_wkhtmltopdf(wkhtmltopdf_path)
        if wk_path:
            print(f"\n  [DEBUG] wkhtmltopdf found at: {wk_path}", file=sys.stderr)
            print(f"  [DEBUG] but conversion failed.", file=sys.stderr)
        else:
            print(f"\n  [DEBUG] wkhtmltopdf not found.", file=sys.stderr)
        
        return 1


def install_chromium_guide():
    """Print instructions for installing Chromium."""
    print("""
=== Installation de Chromium pour un meilleur support SVG ===

Le package Python Playwright est inclus dans la wheel.
Cependant, le navigateur Chromium (~100 MB) doit être installé séparément
car il ne peut pas être embarqué dans la wheel pour des raisons de taille.

Installation rapide (une seule fois par machine)
------------------------------------------------
    python -m playwright install chromium

Alternative : wkhtmltopdf (déjà présent sur votre système)
----------------------------------------------------------
    ambulon html2pdf document.html --method wkhtmltopdf
    
    Note: wkhtmltopdf a un support SVG limité.

Utilisation après installation
------------------------------
    ambulon html2pdf document.html --method chromium

Vérification
------------
    python -c "from playwright.sync_api import sync_playwright; print('OK')"
""")


def main():
    """Entry point for html2pdf command."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="""
        Convert HTML to PDF with SVG support.
        
        Supports two rendering methods:
        - Chromium (default, best SVG support, requires playwright)
        - wkhtmltopdf (fallback, older, limited SVG support)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect method (Chromium preferred, fallback to wkhtmltopdf)
  ambulon html2pdf document.html
  
  # Force Chromium (best for SVG diagrams)
  ambulon html2pdf document.html --method chromium
  
  # Force wkhtmltopdf
  ambulon html2pdf document.html --method wkhtmltopdf
  
  # Custom wkhtmltopdf path
  ambulon html2pdf document.html --method wkhtmltopdf --wkhtmltopdf-path "C:\\tools\\wkhtmltopdf.exe"
  
  # Landscape orientation with verbose output
  ambulon html2pdf document.html -r landscape --verbose

Notes:
  - wkhtmltopdf < 0.12.6 has LIMITED SVG support (diagrams may not appear)
  - For documents with PlantUML/Mermaid diagrams, use --method chromium
  - Playwright is INCLUDED in the wheel (no pip install needed)
  - To install Chromium browser: poetry run playwright install chromium
        """
    )
    
    parser.add_argument('input', help='Input HTML file')
    parser.add_argument('-o', '--output', help='Output PDF file (default: <input>.pdf)')
    parser.add_argument(
        '-r', '--orientation', 
        choices=['portrait', 'landscape'], 
        default='portrait', 
        help='Page orientation (default: portrait)'
    )
    parser.add_argument(
        '-m', '--method',
        choices=['auto', 'chromium', 'wkhtmltopdf'],
        default='auto',
        help='Rendering method: auto (try chromium first), chromium, or wkhtmltopdf (default: auto)'
    )
    parser.add_argument(
        '--wkhtmltopdf-path',
        help='Path to wkhtmltopdf executable (optional, for custom installation)'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--install-chromium', action='store_true', help='Show Chromium installation guide')
    
    args = parser.parse_args()
    
    if args.install_chromium:
        install_chromium_guide()
        return 0
    
    return convert_html_to_pdf(
        args.input,
        args.output,
        args.orientation,
        args.method,
        args.wkhtmltopdf_path,
        args.verbose
    )


if __name__ == '__main__':
    sys.exit(main())
