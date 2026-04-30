#!/bin/bash
# generate_causalis_pdf.sh - Generate HTML + PDF from Causalis markdown with Mermaid diagrams

set -e

INPUT_FILE="workplace-ambulon/delivrables/causalis.dat_uml.mmd.gpt-oss_120b-cloud.md"
OUTPUT_DIR="doc/generated"
HTML_FILE="$OUTPUT_DIR/causalis.html"
PDF_FILE="$OUTPUT_DIR/causalis.pdf"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "Generating Causalis Documentation"
echo "========================================"
echo ""

# Check input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi

echo "Step 1: Converting Markdown to HTML (with Mermaid diagrams)..."
echo "Input:  $INPUT_FILE"
echo "Output: $HTML_FILE"

# Generate HTML with Pandoc and Mermaid filter
# If pandoc-mermaid-filter is not available, try with embedded script
if pandoc --version > /dev/null 2>&1; then
    if pandoc --filter pandoc-mermaid-filter "$INPUT_FILE" -o "$HTML_FILE" 2>/dev/null; then
        echo "✓ HTML generated successfully with Mermaid filter"
    else
        echo "⚠ Mermaid filter not available, using basic HTML generation..."
        pandoc "$INPUT_FILE" \
            --standalone \
            --toc \
            -o "$HTML_FILE"
        echo "✓ HTML generated (note: Mermaid diagrams may not be rendered)"
    fi
else
    echo "ERROR: Pandoc not found. Install with: apt-get install pandoc (Linux) or brew install pandoc (Mac)"
    exit 1
fi

echo ""
echo "Step 2: Checking HTML file size..."
HTML_SIZE=$(du -h "$HTML_FILE" | cut -f1)
echo "✓ HTML file size: $HTML_SIZE"

echo ""
echo "Step 3: Converting HTML to PDF..."

# Try multiple PDF generation tools
PDF_GENERATED=false

if command -v wkhtmltopdf &> /dev/null; then
    echo "Using wkhtmltopdf..."
    wkhtmltopdf "$HTML_FILE" "$PDF_FILE" 2>/dev/null && PDF_GENERATED=true
elif command -v weasyprint &> /dev/null; then
    echo "Using weasyprint..."
    weasyprint "$HTML_FILE" "$PDF_FILE" 2>/dev/null && PDF_GENERATED=true
elif command -v chromium &> /dev/null; then
    echo "Using Chromium..."
    chromium --headless --print-to-pdf="$PDF_FILE" "$HTML_FILE" 2>/dev/null && PDF_GENERATED=true
elif command -v google-chrome &> /dev/null; then
    echo "Using Google Chrome..."
    google-chrome --headless --print-to-pdf="$PDF_FILE" "$HTML_FILE" 2>/dev/null && PDF_GENERATED=true
else
    echo "WARNING: No PDF generation tool found"
    echo "Install one of: wkhtmltopdf, weasyprint, chromium, or google-chrome"
fi

if [ "$PDF_GENERATED" = true ]; then
    PDF_SIZE=$(du -h "$PDF_FILE" | cut -f1)
    echo "✓ PDF generated successfully: $PDF_SIZE"
else
    echo "⚠ PDF generation skipped (no tool available)"
fi

echo ""
echo "========================================"
echo "Generated Files:"
echo "========================================"
echo "HTML: $HTML_FILE"
if [ "$PDF_GENERATED" = true ]; then
    echo "PDF:  $PDF_FILE"
fi
echo ""
echo "Next steps:"
echo "1. Open HTML in browser to check diagram rendering:"
echo "   open $HTML_FILE"
echo "2. Check PDF for final output:"
if [ "$PDF_GENERATED" = true ]; then
    echo "   open $PDF_FILE"
fi
echo ""
echo "Note: If diagrames are missing or show errors in HTML,"
echo "it means there are syntax errors in the Mermaid diagram blocks."
echo "========================================"
