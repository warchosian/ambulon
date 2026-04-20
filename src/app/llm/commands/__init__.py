"""
CLI commands for LLM module.

Available commands:
- llm: Generate documents via LLM APIs (Kimi, ChatGPT, Claude)
- filter: Filter and reduce large code.md files
- summarize: Intelligently summarize code.md files using LLM
"""

from .llm import main as llm_main
from .filter import main as filter_main
from .summarize import main as summarize_main

__all__ = ['llm_main', 'filter_main', 'summarize_main']
