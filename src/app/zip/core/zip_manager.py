"""
ZIP Archive Manager with AES-256 encryption support.

Uses pyzipper for secure password-protected archives.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import fnmatch

try:
    import pyzipper
except ImportError:
    raise ImportError(
        "pyzipper is required for ZIP operations. "
        "Install it with: pip install pyzipper"
    )

logger = logging.getLogger(__name__)


class ZipManager:
    """
    Manages ZIP archive creation and extraction with AES-256 encryption.

    Examples:
        >>> manager = ZipManager()
        >>> # Create encrypted archive
        >>> manager.create_archive(
        ...     sources=[Path("docs/")],
        ...     output=Path("docs.zip"),
        ...     password="secret123"
        ... )
        >>> # Extract archive
        >>> manager.extract_archive(
        ...     archive=Path("docs.zip"),
        ...     output_dir=Path("extracted/"),
        ...     password="secret123"
        ... )
    """

    def __init__(self):
        """Initialize ZIP manager."""
        pass

    def create_archive(
        self,
        sources: List[Path],
        output: Path,
        password: Optional[str] = None,
        compression_level: int = 6,
        exclude_patterns: Optional[List[str]] = None,
        recursive: bool = True
    ) -> Path:
        """
        Create a ZIP archive from files and directories.

        Args:
            sources: List of files/directories to archive
            output: Output ZIP file path
            password: Optional password for AES-256 encryption
            compression_level: Compression level 0-9 (default: 6)
            exclude_patterns: List of glob patterns to exclude (e.g., "*.pyc")
            recursive: Include subdirectories recursively (default: True)

        Returns:
            Path to the created archive

        Raises:
            FileNotFoundError: If source doesn't exist
            ValueError: If compression level is invalid
        """
        if compression_level < 0 or compression_level > 9:
            raise ValueError("Compression level must be between 0 and 9")

        exclude_patterns = exclude_patterns or []

        # Resolve output path
        output = output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating archive: {output}")

        # Collect files to archive
        files_to_archive: List[tuple[Path, str]] = []

        for source in sources:
            source = Path(source).resolve()

            if not source.exists():
                raise FileNotFoundError(f"Source not found: {source}")

            if source.is_file():
                # Single file
                arcname = source.name
                if not self._is_excluded(arcname, exclude_patterns):
                    files_to_archive.append((source, arcname))
                    logger.debug(f"Adding file: {arcname}")
            elif source.is_dir():
                # Directory
                if recursive:
                    for file_path in source.rglob("*"):
                        if file_path.is_file():
                            arcname = str(file_path.relative_to(source.parent))
                            if not self._is_excluded(arcname, exclude_patterns):
                                files_to_archive.append((file_path, arcname))
                                logger.debug(f"Adding file: {arcname}")
                else:
                    for file_path in source.iterdir():
                        if file_path.is_file():
                            arcname = str(file_path.relative_to(source.parent))
                            if not self._is_excluded(arcname, exclude_patterns):
                                files_to_archive.append((file_path, arcname))
                                logger.debug(f"Adding file: {arcname}")

        if not files_to_archive:
            logger.warning("No files to archive")
            return output

        # Create ZIP archive
        with pyzipper.AESZipFile(
            output,
            'w',
            compression=pyzipper.ZIP_DEFLATED,
            compresslevel=compression_level,
            encryption=pyzipper.WZ_AES if password else None
        ) as zipf:
            if password:
                zipf.setpassword(password.encode('utf-8'))
                logger.info(f"Archive will be encrypted with AES-256")

            for file_path, arcname in files_to_archive:
                zipf.write(file_path, arcname)

        file_count = len(files_to_archive)
        file_size = output.stat().st_size / 1024  # KB
        logger.info(f"Archive created: {file_count} files, {file_size:.1f} KB")

        return output

    def extract_archive(
        self,
        archive: Path,
        output_dir: Path,
        password: Optional[str] = None
    ) -> List[Path]:
        """
        Extract a ZIP archive.

        Args:
            archive: Path to ZIP file
            output_dir: Destination directory
            password: Optional password for encrypted archives

        Returns:
            List of extracted file paths

        Raises:
            FileNotFoundError: If archive doesn't exist
            RuntimeError: If password is incorrect or archive is corrupted
        """
        archive = Path(archive).resolve()
        output_dir = Path(output_dir).resolve()

        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive}")

        logger.info(f"Extracting archive: {archive}")
        logger.info(f"Destination: {output_dir}")

        output_dir.mkdir(parents=True, exist_ok=True)

        extracted_files: List[Path] = []

        try:
            with pyzipper.AESZipFile(archive, 'r') as zipf:
                if password:
                    zipf.setpassword(password.encode('utf-8'))

                # Extract all files
                for member in zipf.namelist():
                    zipf.extract(member, output_dir)
                    extracted_path = output_dir / member
                    extracted_files.append(extracted_path)
                    logger.debug(f"Extracted: {member}")

        except RuntimeError as e:
            if "Bad password" in str(e) or "password required" in str(e).lower():
                raise RuntimeError(
                    "Incorrect password or password required for this archive"
                ) from e
            raise RuntimeError(f"Failed to extract archive: {e}") from e

        logger.info(f"Extracted {len(extracted_files)} files")

        return extracted_files

    def list_contents(
        self,
        archive: Path,
        password: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List contents of a ZIP archive without extracting.

        Args:
            archive: Path to ZIP file
            password: Optional password for encrypted archives

        Returns:
            List of dictionaries with file information:
                - filename: str
                - file_size: int (bytes)
                - compress_size: int (bytes)
                - date_time: tuple (year, month, day, hour, min, sec)

        Raises:
            FileNotFoundError: If archive doesn't exist
            RuntimeError: If password is incorrect
        """
        archive = Path(archive).resolve()

        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive}")

        logger.info(f"Listing contents: {archive}")

        contents: List[Dict[str, Any]] = []

        try:
            with pyzipper.AESZipFile(archive, 'r') as zipf:
                if password:
                    zipf.setpassword(password.encode('utf-8'))

                for info in zipf.infolist():
                    contents.append({
                        'filename': info.filename,
                        'file_size': info.file_size,
                        'compress_size': info.compress_size,
                        'date_time': info.date_time,
                        'is_dir': info.is_dir()
                    })

        except RuntimeError as e:
            if "Bad password" in str(e) or "password required" in str(e).lower():
                raise RuntimeError(
                    "Incorrect password or password required for this archive"
                ) from e
            raise

        logger.info(f"Archive contains {len(contents)} items")

        return contents

    @staticmethod
    def _is_excluded(filename: str, exclude_patterns: List[str]) -> bool:
        """
        Check if filename matches any exclude pattern.

        Args:
            filename: Filename to check
            exclude_patterns: List of glob patterns

        Returns:
            True if filename should be excluded
        """
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False
