#!/usr/bin/env python
"""Test MCP server md2html integration"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dyag.mcp_server import MCPServer


def test_list_tools():
    """Test that md2html tool is listed."""
    print("=" * 60)
    print("TEST 1: List Tools")
    print("=" * 60)

    server = MCPServer()
    request = {
        "method": "tools/list",
        "params": {}
    }

    response = server.handle_request(request)
    tools = response.get("tools", [])

    print(f"\nFound {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description'][:60]}...")

    # Check if md2html is in the list
    md2html_tool = next((t for t in tools if t["name"] == "dyag_md2html"), None)

    if md2html_tool:
        print("\n[OK] SUCCESS: dyag_md2html tool found!")
        print(f"\nTool details:")
        print(f"  Name: {md2html_tool['name']}")
        print(f"  Description: {md2html_tool['description']}")
        print(f"  Required params: {md2html_tool['inputSchema']['required']}")
        return True
    else:
        print("\n[FAILED] FAILED: dyag_md2html tool not found!")
        return False


def test_md2html_conversion():
    """Test md2html conversion via MCP."""
    print("\n" + "=" * 60)
    print("TEST 2: Convert Markdown to HTML via MCP")
    print("=" * 60)

    server = MCPServer()

    # Use an existing test file
    test_md = "examples/test-graphviz/graphviz_tools.md"
    output_html = "examples/test-graphviz/graphviz_tools.mcp.html"

    request = {
        "method": "tools/call",
        "params": {
            "name": "dyag_md2html",
            "arguments": {
                "markdown": test_md,
                "output": output_html,
                "verbose": True,
                "standalone": True
            }
        }
    }

    print(f"\nConverting: {test_md}")
    print(f"Output: {output_html}")
    print("-" * 60)

    response = server.handle_request(request)

    if "error" in response:
        print(f"\n[FAILED] FAILED: {response['error']['message']}")
        return False

    if response.get("isError"):
        print(f"\n[FAILED] FAILED: {response['content'][0]['text']}")
        return False

    print(f"\n[OK] SUCCESS!")
    print(f"Response: {response['content'][0]['text']}")

    # Verify file was created
    if Path(output_html).exists():
        size = Path(output_html).stat().st_size
        print(f"\nGenerated file: {output_html} ({size:,} bytes)")
        return True
    else:
        print(f"\n[FAILED] FAILED: Output file not created!")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCP Server - md2html Integration Tests")
    print("=" * 60)

    results = []

    # Test 1: List tools
    results.append(("List Tools", test_list_tools()))

    # Test 2: Convert markdown
    results.append(("Convert Markdown", test_md2html_conversion()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "[OK] PASSED" if passed else "[FAILED] FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(r[1] for r in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
    else:
        print("[FAILED] SOME TESTS FAILED")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
