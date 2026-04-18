"""
Document manager for aggregating source files and managing generation.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a loaded document."""
    path: Path
    content: str
    metadata: Dict[str, Any]


@dataclass
class GenerationMetadata:
    """Metadata about a generation request."""
    timestamp: str
    provider: str
    model: str
    input_files: List[str]
    prompt_file: str
    output_file: str
    tokens: Dict[str, int]
    duration_seconds: float
    streaming: bool
    success: bool
    error: Optional[str] = None


class DocumentManager:
    """
    Manages document loading, aggregation, and response saving.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DocumentManager.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        # Document settings
        doc_config = config.get("documents", {})
        self.separator = doc_config.get("separator", "\n\n---\n\n")
        self.include_metadata = doc_config.get("include_metadata", True)
        self.aggregation_template = doc_config.get("aggregation_template")
        self.allowed_extensions = doc_config.get("allowed_extensions", [".md", ".markdown", ".txt"])
        self.default_encoding = doc_config.get("default_encoding", "utf-8")

        # Output settings
        output_config = config.get("output", {})
        self.default_output = output_config.get("default_file", "response.md")
        self.create_output_dir = output_config.get("create_output_dir", True)
        self.save_metadata = output_config.get("save_metadata", True)
        self.metadata_filename = output_config.get("metadata_filename", "generation_metadata.json")

    def load_documents(self, file_paths: List[Path]) -> List[Document]:
        """
        Load multiple document files.

        Args:
            file_paths: List of file paths to load

        Returns:
            List of Document objects

        Raises:
            FileNotFoundError: If a file doesn't exist
            ValueError: If file has unsupported extension
        """
        documents = []

        for idx, file_path in enumerate(file_paths):
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Check extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                logger.warning(f"Skipping file with unsupported extension: {file_path}")
                continue

            # Read file
            try:
                with open(file_path, 'r', encoding=self.default_encoding) as f:
                    content = f.read()

                metadata = {
                    "index": idx,
                    "filename": file_path.name,
                    "size_bytes": file_path.stat().st_size,
                    "extension": file_path.suffix
                }

                doc = Document(path=file_path, content=content, metadata=metadata)
                documents.append(doc)

                logger.debug(f"Loaded document: {file_path.name} ({metadata['size_bytes']} bytes)")

            except UnicodeDecodeError as e:
                logger.error(f"Encoding error reading {file_path}: {e}")
                raise ValueError(f"Cannot read file {file_path}: encoding error. Try UTF-8.")

        logger.info(f"Loaded {len(documents)} documents")
        return documents

    def aggregate_content(self, documents: List[Document]) -> str:
        """
        Aggregate document contents into a single string.

        Args:
            documents: List of Document objects

        Returns:
            Aggregated content string
        """
        if not documents:
            raise ValueError("No documents to aggregate")

        parts = []

        for doc in documents:
            if self.aggregation_template and self.include_metadata:
                # Use template
                part = self.aggregation_template.format(
                    index=doc.metadata["index"] + 1,
                    filename=doc.metadata["filename"],
                    content=doc.content
                )
            elif self.include_metadata:
                # Default format with metadata
                part = f"# Document {doc.metadata['index'] + 1}: {doc.metadata['filename']}\n\n{doc.content}"
            else:
                # Content only
                part = doc.content

            parts.append(part)

        aggregated = self.separator.join(parts)
        logger.info(f"Aggregated {len(documents)} documents ({len(aggregated)} characters)")

        return aggregated

    def load_prompt(self, prompt_path: Path) -> str:
        """
        Load prompt from file.

        Args:
            prompt_path: Path to prompt file

        Returns:
            Prompt content

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, 'r', encoding=self.default_encoding) as f:
            prompt = f.read()

        logger.info(f"Loaded prompt: {prompt_path.name} ({len(prompt)} characters)")
        return prompt

    def save_response(
        self,
        content: str,
        output_path: Path,
        metadata: Optional[GenerationMetadata] = None
    ) -> None:
        """
        Save generated response to file.

        Args:
            content: Generated content
            output_path: Output file path
            metadata: Optional generation metadata
        """
        # Create output directory if needed
        if self.create_output_dir and not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created output directory: {output_path.parent}")

        # Save content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Saved response: {output_path} ({len(content)} characters)")

        # Save metadata if enabled
        if self.save_metadata and metadata:
            metadata_path = output_path.parent / self.metadata_filename

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(metadata), f, indent=2, ensure_ascii=False)

            logger.info(f"Saved metadata: {metadata_path}")

    def validate_inputs(
        self,
        input_files: List[Path],
        prompt_file: Path
    ) -> None:
        """
        Validate input files before processing.

        Args:
            input_files: List of input file paths
            prompt_file: Prompt file path

        Raises:
            ValueError: If validation fails
        """
        if not input_files:
            raise ValueError("No input files specified")

        if not prompt_file:
            raise ValueError("No prompt file specified")

        # Check prompt file
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        # Check input files
        missing_files = [f for f in input_files if not f.exists()]
        if missing_files:
            raise FileNotFoundError(f"Input files not found: {', '.join(str(f) for f in missing_files)}")

        logger.debug("Input validation passed")

    def create_metadata(
        self,
        provider: str,
        model: str,
        input_files: List[Path],
        prompt_file: Path,
        output_file: Path,
        tokens: Dict[str, int],
        duration: float,
        streaming: bool,
        success: bool,
        error: Optional[str] = None
    ) -> GenerationMetadata:
        """
        Create generation metadata.

        Args:
            provider: Provider name
            model: Model name
            input_files: Input file paths
            prompt_file: Prompt file path
            output_file: Output file path
            tokens: Token usage dict
            duration: Generation duration in seconds
            streaming: Whether streaming was used
            success: Whether generation succeeded
            error: Optional error message

        Returns:
            GenerationMetadata object
        """
        return GenerationMetadata(
            timestamp=datetime.now().isoformat(),
            provider=provider,
            model=model,
            input_files=[str(f) for f in input_files],
            prompt_file=str(prompt_file),
            output_file=str(output_file),
            tokens=tokens,
            duration_seconds=round(duration, 2),
            streaming=streaming,
            success=success,
            error=error
        )
