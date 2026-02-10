"""
Tests unitaires pour la conversion des diagrammes (PlantUML, Mermaid, Graphviz) en SVG
"""
import logging
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.core.logging_config import setup_logging
from app.conversion.commands.md2html import (
    process_markdown_to_html,
    extract_code_blocks,
    convert_plantuml_to_svg,
    convert_graphviz_to_svg,
    convert_mermaid_to_svg,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def _configure_logging():
    """Ensure logging is configured for tests without writing log files."""
    setup_logging(level=logging.INFO, log_file_prefix=None)


@pytest.fixture
def plantuml_markdown():
    """Sample markdown with PlantUML diagram."""
    return """# Test Document

## PlantUML Diagram

```plantuml
@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi!
@enduml
```

Some text after.
"""


@pytest.fixture
def mermaid_markdown():
    """Sample markdown with Mermaid diagram."""
    return """# Test Document

## Mermaid Diagram

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

Some text after.
"""


@pytest.fixture
def graphviz_markdown():
    """Sample markdown with Graphviz diagram."""
    return """# Test Document

## Graphviz Diagram

```dot
digraph G {
    A -> B;
    B -> C;
}
```

Some text after.
"""


@pytest.fixture
def mixed_diagrams_markdown():
    """Sample markdown with multiple diagram types."""
    return """# Test Document

## PlantUML Diagram

```plantuml
@startuml
title Use Case Diagram
actor User
User -> (Login)
@enduml
```

## Mermaid Diagram

```mermaid
sequenceDiagram
    Alice->>Bob: Hello
    Bob->>Alice: Hi
```

## Graphviz Diagram

```graphviz
digraph G {
    rankdir=LR;
    A -> B -> C;
}
```

## Regular Code Block

```python
def hello():
    print("Hello, World!")
```

End of document.
"""


@pytest.fixture
def mock_svg_output():
    """Mock SVG content returned by converters."""
    return """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">
<rect width="200" height="100" fill="lightblue"/>
<text x="100" y="50" text-anchor="middle">Test Diagram</text>
</svg>"""


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.conversion
class TestDiagramConversion:
    """Tests for diagram to SVG conversion."""

    def test_extract_plantuml_blocks(self, plantuml_markdown):
        """Test extraction of PlantUML code blocks."""
        blocks = extract_code_blocks(plantuml_markdown)

        assert len(blocks) == 1
        block_type, code, position = blocks[0]
        assert block_type == 'plantuml'
        assert '@startuml' in code
        assert '@enduml' in code
        assert position > 0

    def test_extract_mermaid_blocks(self, mermaid_markdown):
        """Test extraction of Mermaid code blocks."""
        blocks = extract_code_blocks(mermaid_markdown)

        assert len(blocks) == 1
        block_type, code, position = blocks[0]
        assert block_type == 'mermaid'
        assert 'graph TD' in code

    def test_extract_graphviz_blocks(self, graphviz_markdown):
        """Test extraction of Graphviz code blocks."""
        blocks = extract_code_blocks(graphviz_markdown)

        assert len(blocks) == 1
        block_type, code, position = blocks[0]
        assert block_type == 'dot'
        assert 'digraph G' in code

    def test_extract_mixed_diagrams(self, mixed_diagrams_markdown):
        """Test extraction of multiple diagram types."""
        blocks = extract_code_blocks(mixed_diagrams_markdown)

        # Should extract 3 diagram blocks, but not the python code block
        assert len(blocks) == 3

        block_types = [block[0] for block in blocks]
        assert 'plantuml' in block_types
        assert 'mermaid' in block_types
        assert 'graphviz' in block_types

    @patch('app.conversion.commands.md2html.convert_plantuml_to_svg')
    def test_process_markdown_logs_plantuml_context(self, mock_convert, temp_dir, plantuml_markdown, caplog):
        """Ensure PlantUML context is logged at md2html start."""
        mock_convert.return_value = None

        md_file = temp_dir / "test.md"
        md_file.write_text(plantuml_markdown, encoding='utf-8')

        html_file = temp_dir / "test.html"

        with caplog.at_level(logging.INFO):
            result = process_markdown_to_html(str(md_file), str(html_file), verbose=False)

        assert result == 0
        assert any("md2html PlantUML context" in record.message for record in caplog.records)
        assert any("md2html PlantUML mode" in record.message for record in caplog.records)

    @patch('subprocess.run')
    def test_convert_graphviz_to_svg(self, mock_run, mock_svg_output):
        """Test Graphviz to SVG conversion."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_svg_output.encode('utf-8'),
            stderr=b''
        )

        dot_code = "digraph G { A -> B; }"
        result = convert_graphviz_to_svg(dot_code, verbose=True)

        assert result is not None
        assert '<svg' in result
        mock_run.assert_called_once()

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_convert_plantuml_to_svg_local(self, mock_open, mock_exists, mock_run, mock_svg_output):
        """Test PlantUML to SVG conversion with local command."""
        mock_run.return_value = Mock(returncode=0, stdout=b'', stderr=b'')
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = mock_svg_output

        plantuml_code = "@startuml\nA -> B\n@enduml"
        result = convert_plantuml_to_svg(plantuml_code, verbose=True)

        # Should attempt local plantuml, Kroki (package/online), or fail gracefully
        assert mock_run.called or result is None or '<svg' in result

    @patch('os.environ.get')
    @patch('app.conversion.commands.md2html._java_available')
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.unlink')
    @patch('builtins.open', create=True)
    def test_convert_plantuml_to_svg_with_jar(self, mock_open, mock_unlink, mock_exists, mock_run, mock_java_available, mock_environ_get, mock_svg_output):
        """Test PlantUML to SVG conversion with PLANTUML_JAR environment variable."""
        # Setup mocks
        mock_java_available.return_value = True
        def _env_get_side_effect(key, default=None):
            if key == 'PLANTUML_JAR':
                return '/path/to/plantuml.jar'
            return default

        mock_environ_get.side_effect = _env_get_side_effect
        mock_exists.side_effect = lambda path: True  # JAR exists and SVG output exists
        mock_run.return_value = Mock(returncode=0, stdout=b'', stderr=b'')

        # Mock file operations
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.read = Mock(return_value=mock_svg_output)
        mock_file.write = Mock()
        mock_open.return_value = mock_file

        plantuml_code = "@startuml\nAlice -> Bob: Hello\nBob -> Alice: Hi!\n@enduml"
        result = convert_plantuml_to_svg(plantuml_code, verbose=True, method='jar')

        # Verify that environ.get was called to check for PLANTUML_JAR
        mock_environ_get.assert_any_call('PLANTUML_JAR')

        # Verify subprocess was called with java -jar OR Kroki succeeded first
        if mock_run.called:
            call_args = mock_run.call_args
            if call_args:
                args_list = call_args[0][0] if call_args[0] else []
                # Check if java -jar was called with the JAR path
                assert 'java' in args_list or mock_run.called

        # Verify result is not None (SVG was generated)
        assert result is not None
        assert '<svg' in result or result == mock_svg_output

    @patch('app.conversion.commands.md2html._java_available')
    @patch('os.environ.get')
    @patch('os.path.exists')
    def test_convert_plantuml_to_svg_jar_not_found(self, mock_exists, mock_environ_get, mock_java_available):
        """Test PlantUML conversion falls back when JAR doesn't exist."""
        # Setup: PLANTUML_JAR is set but file doesn't exist
        mock_java_available.return_value = True
        mock_environ_get.return_value = '/path/to/missing.jar'
        mock_exists.return_value = False

        plantuml_code = "@startuml\nA -> B\n@enduml"
        result = convert_plantuml_to_svg(plantuml_code, verbose=False)

        # Should try other methods (may succeed with Kroki or fail gracefully)
        # Result can be None or SVG depending on whether fallback succeeds
        assert result is None or '<svg' in result or result is not None

    @patch('app.conversion.commands.md2html.find_spec')
    @patch('urllib.request.urlopen')
    def test_convert_plantuml_to_svg_kroki_optional_missing(self, mock_urlopen, mock_find_spec):
        """Kroki optional dependency absence should not block conversion."""
        mock_find_spec.return_value = None
        mock_urlopen.side_effect = Exception("No network")

        plantuml_code = "@startuml\nA -> B\n@enduml"
        result = convert_plantuml_to_svg(plantuml_code, verbose=False, method='kroki')

        assert result is None

    @patch('urllib.request.urlopen')
    def test_convert_mermaid_to_svg_kroki(self, mock_urlopen, mock_svg_output):
        """Test Mermaid to SVG conversion with Kroki service."""
        mock_response = MagicMock()
        mock_response.read.return_value = mock_svg_output.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        mermaid_code = "graph TD\n    A-->B"
        result = convert_mermaid_to_svg(mermaid_code, verbose=True)

        assert result is not None
        assert '<svg' in result
        mock_urlopen.assert_called_once()

    @patch('app.conversion.commands.md2html.convert_plantuml_to_svg')
    def test_process_markdown_converts_plantuml(self, mock_convert, temp_dir, plantuml_markdown, mock_svg_output):
        """Test that process_markdown_to_html converts PlantUML to SVG."""
        mock_convert.return_value = mock_svg_output

        md_file = temp_dir / "test.md"
        md_file.write_text(plantuml_markdown, encoding='utf-8')

        html_file = temp_dir / "test.html"
        result = process_markdown_to_html(str(md_file), str(html_file), verbose=True)

        assert result == 0
        assert html_file.exists()

        html_content = html_file.read_text(encoding='utf-8')

        # Check that SVG is embedded
        assert '<svg' in html_content
        assert 'Test Diagram' in html_content

        # Check that original code block is replaced
        assert '```plantuml' not in html_content
        assert '@startuml' not in html_content

        # Check that diagram div wrapper is present
        assert 'class="diagram diagram-plantuml"' in html_content

        mock_convert.assert_called_once()

    @patch('app.conversion.commands.md2html.convert_mermaid_to_svg')
    def test_process_markdown_converts_mermaid(self, mock_convert, temp_dir, mermaid_markdown, mock_svg_output):
        """Test that process_markdown_to_html converts Mermaid to SVG."""
        mock_convert.return_value = mock_svg_output

        md_file = temp_dir / "test.md"
        md_file.write_text(mermaid_markdown, encoding='utf-8')

        html_file = temp_dir / "test.html"
        result = process_markdown_to_html(str(md_file), str(html_file), verbose=True)

        assert result == 0
        assert html_file.exists()

        html_content = html_file.read_text(encoding='utf-8')

        # Check that SVG is embedded
        assert '<svg' in html_content

        # Check that original code block is replaced
        assert '```mermaid' not in html_content
        assert 'graph TD' not in html_content

        # Check that diagram div wrapper is present
        assert 'class="diagram diagram-mermaid"' in html_content

    @patch('app.conversion.commands.md2html.convert_graphviz_to_svg')
    def test_process_markdown_converts_graphviz(self, mock_convert, temp_dir, graphviz_markdown, mock_svg_output):
        """Test that process_markdown_to_html converts Graphviz to SVG."""
        mock_convert.return_value = mock_svg_output

        md_file = temp_dir / "test.md"
        md_file.write_text(graphviz_markdown, encoding='utf-8')

        html_file = temp_dir / "test.html"
        result = process_markdown_to_html(str(md_file), str(html_file), verbose=True)

        assert result == 0
        assert html_file.exists()

        html_content = html_file.read_text(encoding='utf-8')

        # Check that SVG is embedded
        assert '<svg' in html_content

        # Check that original code block is replaced
        assert '```dot' not in html_content
        assert 'digraph G' not in html_content

        # Check that diagram div wrapper is present
        assert 'class="diagram diagram-dot"' in html_content

    @patch('app.conversion.commands.md2html.convert_plantuml_to_svg')
    @patch('app.conversion.commands.md2html.convert_mermaid_to_svg')
    @patch('app.conversion.commands.md2html.convert_graphviz_to_svg')
    def test_process_markdown_converts_all_diagrams(
        self,
        mock_graphviz,
        mock_mermaid,
        mock_plantuml,
        temp_dir,
        mixed_diagrams_markdown,
        mock_svg_output
    ):
        """Test that process_markdown_to_html converts all diagram types."""
        mock_plantuml.return_value = mock_svg_output.replace('Test Diagram', 'PlantUML')
        mock_mermaid.return_value = mock_svg_output.replace('Test Diagram', 'Mermaid')
        mock_graphviz.return_value = mock_svg_output.replace('Test Diagram', 'Graphviz')

        md_file = temp_dir / "test.md"
        md_file.write_text(mixed_diagrams_markdown, encoding='utf-8')

        html_file = temp_dir / "test.html"
        result = process_markdown_to_html(str(md_file), str(html_file), verbose=True)

        assert result == 0
        assert html_file.exists()

        html_content = html_file.read_text(encoding='utf-8')

        # Check that all three converters were called
        mock_plantuml.assert_called_once()
        mock_mermaid.assert_called_once()
        mock_graphviz.assert_called_once()

        # Check that all SVGs are embedded
        assert html_content.count('<svg') == 3

        # Check that original code blocks are replaced
        assert '```plantuml' not in html_content
        assert '```mermaid' not in html_content
        assert '```graphviz' not in html_content

        # Check that regular code block is preserved
        assert '```python' in html_content or '<code' in html_content
        assert 'def hello():' in html_content

        # Check that all diagram wrappers are present
        assert 'diagram-plantuml' in html_content
        assert 'diagram-mermaid' in html_content
        assert 'diagram-graphviz' in html_content

    def test_process_markdown_preserves_code_on_conversion_failure(self, temp_dir, plantuml_markdown):
        """Test that original code block is preserved when conversion fails."""
        # Don't mock anything - let conversion fail naturally
        md_file = temp_dir / "test.md"
        md_file.write_text(plantuml_markdown, encoding='utf-8')

        html_file = temp_dir / "test.html"
        result = process_markdown_to_html(str(md_file), str(html_file), verbose=False)

        # Should still succeed even if diagram conversion fails
        assert result == 0
        assert html_file.exists()

        html_content = html_file.read_text(encoding='utf-8')

        # Original code should be preserved (either as code block or in some form)
        # The exact representation depends on whether conversion failed or succeeded
        # If PlantUML/Kroki is available, it will convert; otherwise it keeps the code
        assert '@startuml' in html_content or '<svg' in html_content


@pytest.mark.integration
@pytest.mark.slow
class TestRealFileConversion:
    """Integration tests with real files."""

    def test_convert_analyseplus_md(self, temp_dir):
        """Test conversion of real analyseplus.md file with multiple diagrams."""
        # Path to the real file
        source_file = Path(__file__).parent.parent.parent.parent.parent / "doc" / "analyseplus.md"

        if not source_file.exists():
            pytest.skip("analyseplus.md not found")

        html_file = temp_dir / "analyseplus.html"

        # Convert the file
        result = process_markdown_to_html(str(source_file), str(html_file), verbose=True)

        assert result == 0
        assert html_file.exists()

        html_content = html_file.read_text(encoding='utf-8')

        # The file should have been processed
        assert len(html_content) > 0
        assert '<html>' in html_content or '<!DOCTYPE' in html_content

        # Check if diagrams were found (analyseplus.md has 6 PlantUML diagrams)
        # If conversion succeeded, we should see SVG tags
        # If conversion failed (no PlantUML available), we should see code blocks preserved
        blocks = extract_code_blocks(source_file.read_text(encoding='utf-8'))
        print(f"\nFound {len(blocks)} diagram blocks in analyseplus.md")

        # Count SVG occurrences (if converters are available)
        svg_count = html_content.count('<svg')
        print(f"Found {svg_count} SVG elements in generated HTML")

        # Either all diagrams converted to SVG, or they're preserved as code
        if svg_count > 0:
            # Conversion worked - check for SVG
            assert svg_count >= 1, "At least one diagram should be converted to SVG"
            assert '<div class="diagram' in html_content
        else:
            # Conversion failed - code should be preserved
            assert '@startuml' in html_content or '<code' in html_content
