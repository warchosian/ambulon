"""
WikiSI website scraper with recursive crawling capabilities.

This module provides the WikiSIScraper class for scraping WikiSI websites
with configurable crawling depth, filtering, and output options.
"""

import os
import re
import time
import json
import logging
import hashlib
from pathlib import Path
from typing import Optional, List, Set, Dict, Any
from urllib.parse import urljoin, urlparse, urlunparse
from datetime import datetime
from collections import deque

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    requests = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import yaml
except ImportError:
    yaml = None

try:
    from urllib.robotparser import RobotFileParser
except ImportError:
    RobotFileParser = None

logger = logging.getLogger(__name__)


class WikiSIScraper:
    """WikiSI website scraper with recursive crawling capabilities."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the scraper with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.visited_urls: Set[str] = set()
        self.failed_urls: Dict[str, str] = {}
        self.downloaded_files: List[Dict[str, Any]] = []

        # Setup session
        self.session = self._create_session()

        # Parse base URL
        self.base_url = config['site']['base_url']
        self.base_domain = urlparse(self.base_url).netloc

        # Setup robots.txt parser
        self.robots_parser = None
        if config['advanced'].get('respect_robots_txt', True):
            self._setup_robots_parser()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        if requests is None:
            logger.error("requests library is required. Install with: pip install requests")
            raise ImportError("requests library is required. Install with: pip install requests")

        session = requests.Session()

        # Setup retry strategy
        max_retries = self.config['advanced'].get('max_retries', 3)
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Setup headers
        headers = self.config.get('headers', {})
        session.headers.update(headers)

        # Setup authentication
        auth_config = self.config.get('authentication', {})
        auth_type = auth_config.get('type', 'none')

        if auth_type == 'basic':
            username = auth_config.get('username', '')
            password = auth_config.get('password', '')
            if username and password:
                from requests.auth import HTTPBasicAuth
                session.auth = HTTPBasicAuth(username, password)

        elif auth_type == 'bearer':
            token = auth_config.get('token', '')
            if token:
                session.headers['Authorization'] = f'Bearer {token}'

        return session

    def _setup_robots_parser(self):
        """Setup robots.txt parser."""
        if RobotFileParser is None:
            logger.warning("robotparser not available, robots.txt will be ignored")
            return

        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            self.robots_parser = RobotFileParser()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Could not load robots.txt: {e}")
            self.robots_parser = None

    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        if self.robots_parser is None:
            return True

        try:
            user_agent = self.config['headers'].get('User-Agent', '*')
            return self.robots_parser.can_fetch(user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and normalizing path."""
        parsed = urlparse(url)
        # Remove fragment
        normalized = urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, '')
        )
        return normalized

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled based on filters."""
        filters = self.config['filters']

        # Check same domain
        if filters.get('same_domain_only', True):
            url_domain = urlparse(url).netloc
            if url_domain != self.base_domain:
                return False

        # Check exclude patterns
        exclude_patterns = filters.get('exclude_patterns', [])
        for pattern in exclude_patterns:
            if re.search(pattern, url):
                logger.debug(f"URL excluded by pattern '{pattern}': {url}")
                return False

        # Check include patterns
        include_patterns = filters.get('include_patterns', [])
        if include_patterns:
            matched = False
            for pattern in include_patterns:
                if re.search(pattern, url):
                    matched = True
                    break
            if not matched:
                logger.debug(f"URL not matching include patterns: {url}")
                return False

        # Check file extension
        path = urlparse(url).path
        if path:
            allowed_extensions = filters.get('allowed_extensions', ['.html', '.htm'])
            # If URL has an extension, check if it's allowed
            if '.' in path.split('/')[-1]:
                ext = '.' + path.split('.')[-1].lower()
                if ext not in allowed_extensions:
                    logger.debug(f"URL extension not allowed: {url}")
                    return False

        return True

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename to be filesystem-safe."""
        # Replace invalid characters
        safe = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
        # Remove multiple underscores
        safe = re.sub(r'_+', '_', safe)
        # Limit length
        if len(safe) > 200:
            safe = safe[:200]
        return safe.strip('_')

    def _get_output_path(self, url: str) -> Path:
        """Generate output file path for a given URL."""
        output_dir = Path(self.config['output']['directory'])
        preserve_structure = self.config['output'].get('preserve_structure', True)
        filename_format = self.config['output'].get('filename_format', 'sanitized')

        parsed = urlparse(url)

        if preserve_structure:
            # Preserve directory structure
            path_parts = parsed.path.strip('/').split('/')

            # Handle empty path (root page)
            if not path_parts or path_parts == ['']:
                filename = 'index.html'
                dir_path = output_dir
            else:
                # Last part is filename, rest is directory structure
                filename = path_parts[-1] if path_parts[-1] else 'index.html'
                dir_parts = path_parts[:-1] if len(path_parts) > 1 else []

                # Sanitize directory parts
                safe_dirs = [self._sanitize_filename(d) for d in dir_parts]
                dir_path = output_dir / Path(*safe_dirs) if safe_dirs else output_dir

            # Ensure filename has .html extension
            if not filename.endswith(('.html', '.htm')):
                filename += '.html'

            # Sanitize filename
            if filename_format == 'sanitized':
                filename = self._sanitize_filename(filename)
            elif filename_format == 'hash':
                ext = Path(filename).suffix
                hash_name = hashlib.md5(url.encode()).hexdigest()
                filename = f"{hash_name}{ext}"

            return dir_path / filename

        else:
            # Flat structure
            if filename_format == 'hash':
                filename = hashlib.md5(url.encode()).hexdigest() + '.html'
            else:
                # Use path as filename
                filename = parsed.path.strip('/').replace('/', '_')
                if not filename:
                    filename = 'index.html'
                elif not filename.endswith(('.html', '.htm')):
                    filename += '.html'
                filename = self._sanitize_filename(filename)

            return output_dir / filename

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page and return its content."""
        try:
            # Check robots.txt
            if not self._can_fetch(url):
                logger.warning(f"Blocked by robots.txt: {url}")
                return None

            # Make request
            timeout = self.config['site'].get('timeout', 30)
            verify_ssl = self.config['advanced'].get('verify_ssl', True)

            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout, verify=verify_ssl)
            response.raise_for_status()

            # Check content length
            max_size = self.config['advanced'].get('max_file_size_mb', 50) * 1024 * 1024
            content_length = int(response.headers.get('Content-Length', 0))
            if max_size > 0 and content_length > max_size:
                logger.warning(f"File too large ({content_length} bytes): {url}")
                return None

            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            self.failed_urls[url] = str(e)
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            self.failed_urls[url] = str(e)
            return None

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML content."""
        if BeautifulSoup is None:
            logger.error("BeautifulSoup4 is required. Install with: pip install beautifulsoup4")
            raise ImportError("BeautifulSoup4 is required. Install with: pip install beautifulsoup4")

        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []

            # Find all <a> tags with href
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                # Normalize
                normalized_url = self._normalize_url(absolute_url)
                links.append(normalized_url)

            return links

        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []

    def _save_page(self, url: str, content: str) -> bool:
        """Save page content to file."""
        try:
            output_path = self._get_output_path(url)

            # Create parent directories
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved: {output_path}")

            # Track downloaded file
            self.downloaded_files.append({
                'url': url,
                'path': str(output_path),
                'size': len(content),
                'timestamp': datetime.now().isoformat()
            })

            return True

        except Exception as e:
            logger.error(f"Error saving {url}: {e}")
            return False

    def scrape(self, start_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Start scraping from the given URL.

        Args:
            start_url: Starting URL (defaults to base_url from config)

        Returns:
            Dictionary with scraping statistics
        """
        if start_url is None:
            start_url = self.base_url

        # Normalize start URL
        start_url = self._normalize_url(start_url)

        max_depth = self.config['site'].get('max_depth', -1)
        delay = self.config['site'].get('delay', 1.0)

        # Queue: (url, depth)
        queue = deque([(start_url, 0)])

        logger.info(f"Starting scrape from: {start_url}")
        logger.info(f"Max depth: {max_depth if max_depth >= 0 else 'unlimited'}")

        start_time = datetime.now()

        while queue:
            url, depth = queue.popleft()

            # Check if already visited
            if url in self.visited_urls:
                continue

            # Check depth limit
            if max_depth >= 0 and depth > max_depth:
                logger.debug(f"Skipping (max depth reached): {url}")
                continue

            # Check if valid URL
            if not self._is_valid_url(url):
                continue

            # Mark as visited
            self.visited_urls.add(url)

            # Fetch page
            content = self._fetch_page(url)
            if content is None:
                continue

            # Save page
            self._save_page(url, content)

            # Extract links for further crawling
            if max_depth < 0 or depth < max_depth:
                links = self._extract_links(content, url)
                for link in links:
                    if link not in self.visited_urls:
                        queue.append((link, depth + 1))

            # Delay between requests
            if delay > 0 and queue:
                time.sleep(delay)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Generate statistics
        stats = {
            'start_url': start_url,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'pages_visited': len(self.visited_urls),
            'pages_downloaded': len(self.downloaded_files),
            'pages_failed': len(self.failed_urls),
            'total_size_bytes': sum(f['size'] for f in self.downloaded_files)
        }

        # Save metadata
        if self.config['output'].get('save_metadata', True):
            self._save_metadata(stats)

        return stats

    def _save_metadata(self, stats: Dict[str, Any]):
        """Save scraping metadata to JSON file."""
        try:
            output_dir = Path(self.config['output']['directory'])
            metadata_path = output_dir / 'scrape_metadata.json'

            metadata = {
                'config': self.config,
                'statistics': stats,
                'downloaded_files': self.downloaded_files,
                'failed_urls': self.failed_urls
            }

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.info(f"Metadata saved: {metadata_path}")

        except Exception as e:
            logger.error(f"Error saving metadata: {e}")


def load_config(cli_config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration for the WikiSI scraper from YAML file with environment variable substitution.

    Hierarchy:
    1. CLI arguments (handled by caller, then merged into this config)
    2. YAML file
    3. Environment variables (substituted in YAML or directly taken if no YAML value)
    4. Default values

    Args:
        cli_config_path: Path to configuration file provided via CLI.

    Returns:
        Configuration dictionary.
    """
    # Default configuration
    config = {
        'site': {
            'base_url': os.getenv('WIKISI_BASE_URL', 'https://wikisi.example.gouv.fr'),
            'max_depth': int(os.getenv('WIKISI_MAX_DEPTH', '-1')),
            'delay': float(os.getenv('WIKISI_DELAY', '1.0')),
            'timeout': int(os.getenv('WIKISI_TIMEOUT', '30'))
        },
        'filters': {
            'include_patterns': [],
            'exclude_patterns': [],
            'allowed_extensions': ['.html', '.htm'],
            'same_domain_only': True
        },
        'output': {
            'directory': os.getenv('WIKISI_OUTPUT_DIR', './wikisi-downloaded'),
            'preserve_structure': True,
            'save_metadata': True,
            'filename_format': 'sanitized'
        },
        'headers': {
            'User-Agent': os.getenv('WIKISI_USER_AGENT', 'Ambulon WikiSI Scraper/1.0'),
            'Accept-Language': os.getenv('WIKISI_ACCEPT_LANGUAGE', 'fr-FR,fr;q=0.9')
        },
        'authentication': {
            'type': os.getenv('WIKISI_AUTH_TYPE', 'none'),
            'username': os.getenv('WIKISI_USERNAME', ''),
            'password': os.getenv('WIKISI_PASSWORD', ''),
            'token': os.getenv('WIKISI_TOKEN', '')
        },
        'advanced': {
            'max_retries': int(os.getenv('WIKISI_MAX_RETRIES', '3')),
            'respect_robots_txt': os.getenv('WIKISI_RESPECT_ROBOTS_TXT', 'true').lower() == 'true',
            'verify_ssl': os.getenv('WIKISI_VERIFY_SSL', 'true').lower() == 'true',
            'threads': int(os.getenv('WIKISI_THREADS', '1')),
            'max_file_size_mb': int(os.getenv('WIKISI_MAX_FILE_SIZE_MB', '50'))
        },
        'logging': {
            'level': os.getenv('WIKISI_LOG_LEVEL', 'info'),
            'log_to_file': os.getenv('WIKISI_LOG_TO_FILE', 'true').lower() == 'true',
            'log_file': os.getenv('WIKISI_LOG_FILE', './wikisi-scraper.log')
        }
    }

    # Load from YAML if specified (CLI path takes precedence)
    yaml_config_path_resolved: Optional[Path] = None
    if cli_config_path:
        yaml_config_path_resolved = Path(cli_config_path)
    else:
        # Try default config paths if no CLI path provided
        default_paths = [
            Path('config/wikisi.yaml'),
            Path('./wikisi.yaml'),
            Path(os.path.expanduser('~/.ambulon/wikisi.yaml'))
        ]
        for path in default_paths:
            if path.exists():
                yaml_config_path_resolved = path
                break
    
    if yaml_config_path_resolved and yaml_config_path_resolved.exists():
        if yaml is None:
            logger.warning("PyYAML not installed, cannot load YAML config. Install with: pip install pyyaml")
        else:
            try:
                with open(yaml_config_path_resolved, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()

                # Substitute environment variables in YAML (e.g., ${VAR:-default})
                def replace_env_var(match):
                    var_expr = match.group(1)
                    if ':-' in var_expr:
                        var_name, default_value = var_expr.split(':-', 1)
                        return os.getenv(var_name, default_value)
                    else:
                        return os.getenv(var_expr, '')

                yaml_content = re.sub(r'\$\{\s*([^}]+?)\s*\}', replace_env_var, yaml_content)

                loaded_yaml_config = yaml.safe_load(yaml_content)
                if loaded_yaml_config:
                    # Merge YAML config over defaults/env vars
                    # Recursive merge for nested dictionaries
                    def deep_merge(target, source):
                        for k, v in source.items():
                            if k in target and isinstance(target[k], dict) and isinstance(v, dict):
                                target[k] = deep_merge(target[k], v)
                            else:
                                target[k] = v
                        return target
                    
                    config = deep_merge(config, loaded_yaml_config)
                    logger.info(f"Loaded configuration from {yaml_config_path_resolved}")
                
            except Exception as e:
                logger.error(f"Error loading config from '{yaml_config_path_resolved}': {e}")
    elif cli_config_path: # Config path was provided via CLI but didn't exist
        logger.warning(f"Config file '{cli_config_path}' not found, using defaults and environment variables.")
    else: # No config path provided and no default found
        logger.info("No specific config file found or provided, using defaults and environment variables.")

    return config
