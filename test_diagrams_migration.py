#!/usr/bin/env python3
"""
Test script to verify the diagrams module migration is working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core types
        from app.diagrams.core import (
            DiagramType,
            ConversionMethod,
            DiagramBlock,
            ConversionResult,
            Violation,
        )
        print("  ✓ Core types imported")
        
        # Core functions
        from app.diagrams.core import (
            extract_diagram_blocks,
            get_diagram_stats,
            convert_plantuml,
            convert_mermaid,
            convert_graphviz,
            clean_svg_content,
            PlantUMLChecker,
            extract_diagrams_to_files,
            markdown_to_html_basic,
            wrap_html_document,
        )
        print("  ✓ Core functions imported")
        
        # Public API
        from app.diagrams import (
            process_markdown_to_html,
            diagram2svg4md_cli,
            md2html_cli,
        )
        print("  ✓ Public API imported")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_diagram_detection():
    """Test diagram detection."""
    print("\nTesting diagram detection...")
    
    from app.diagrams.core import extract_diagram_blocks, get_diagram_stats
    
    content = """# Test Document

```plantuml
@startuml
A -> B
@enduml
```

Some text

```mermaid
graph TD
    A --> B
```
"""
    
    diagrams = extract_diagram_blocks(content)
    stats = get_diagram_stats(diagrams)
    
    if stats['total'] == 2 and stats['plantuml'] == 1 and stats['mermaid'] == 1:
        print("  ✓ Diagram detection working")
        return True
    else:
        print(f"  ✗ Diagram detection failed: {stats}")
        return False


def test_markdown_conversion():
    """Test markdown to HTML conversion."""
    print("\nTesting markdown conversion...")
    
    from app.diagrams.core import markdown_to_html_basic
    
    content = """# Heading

**Bold** and *italic* text.

```python
print("hello")
```
"""
    
    html = markdown_to_html_basic(content)
    
    if '<h1 id="heading">Heading</h1>' in html and '<strong>Bold</strong>' in html:
        print("  ✓ Markdown conversion working")
        return True
    else:
        print(f"  ✗ Markdown conversion failed")
        print(f"    Output: {html[:200]}...")
        return False


def test_backward_compatibility():
    """Test backward compatibility shims."""
    print("\nTesting backward compatibility...")
    
    try:
        # Old imports should still work
        from app.processing.core.diagram_extractor import isolate_diagrams_logic
        print("  ✓ processing.diagram_extractor shim working")
        
        from app.encoding.core.plantuml_checker import PlantUMLChecker
        print("  ✓ encoding.plantuml_checker shim working")
        
        from app.conversion.commands.md2html import process_markdown_to_html
        print("  ✓ conversion.md2html shim working")
        
        return True
    except Exception as e:
        print(f"  ✗ Backward compatibility failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Diagrams Module Migration Test")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Diagram Detection", test_diagram_detection()))
    results.append(("Markdown Conversion", test_markdown_conversion()))
    results.append(("Backward Compatibility", test_backward_compatibility()))
    
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
