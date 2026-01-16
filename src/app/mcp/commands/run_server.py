"""
Command-line entry point for running the Ambulon MCP server.
"""
import argparse
import asyncio
import logging
import sys
from app.mcp.core.server import run_server, setup_logging

def main():
    """Main entry point for the MCP server command."""
    parser = argparse.ArgumentParser(
        description='Ambulon MCP Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples of use:
  %(prog)s           Start the MCP server
  %(prog)s --help    Show this help message
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    if args.verbose:
        logging.getLogger("ambulon-mcp").setLevel(logging.DEBUG)
    
    try:
        asyncio.run(run_server())
        return 0
    except KeyboardInterrupt:
        logging.getLogger("ambulon-mcp").info("MCP server stopped by user.")
        return 0
    except Exception as e:
        logging.getLogger("ambulon-mcp").error(f"Failed to start MCP server: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
