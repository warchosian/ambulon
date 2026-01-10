"""
WikiSI Website Scraper - Ambulon

Aspire récursivement un site WikiSI et télécharge toutes les pages HTML.
Supporte la configuration via YAML, variables d'environnement et arguments CLI.

Hiérarchie de configuration:
1. Arguments CLI (priorité la plus haute)
2. Fichier YAML
3. Variables d'environnement
4. Valeurs par défaut

Exemple:
    ambulon wikisi-scrape --url https://wikisi.example.fr --output ./data
    ambulon wikisi-scrape --config config/wikisi.yaml --verbose
"""

import os
import sys
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


class WikiSIScraper:
    """WikiSI website scraper with recursive crawling capabilities."""

    def __init__(self, config: Dict[str, Any], verbose: bool = False):
        """
        Initialize the scraper with configuration.

        Args:
            config: Configuration dictionary
            verbose: Enable verbose logging
        """
        self.config = config
        self.verbose = verbose
        self.visited_urls: Set[str] = set()
        self.failed_urls: Dict[str, str] = {}
        self.downloaded_files: List[Dict[str, Any]] = []

        # Setup logging
        self._setup_logging()

        # Setup session
        self.session = self._create_session()

        # Parse base URL
        self.base_url = config['site']['base_url']
        self.base_domain = urlparse(self.base_url).netloc

        # Setup robots.txt parser
        self.robots_parser = None
        if config['advanced'].get('respect_robots_txt', True):
            self._setup_robots_parser()

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config['logging'].get('level', 'info').upper()

        # Configure logger
        self.logger = logging.getLogger('WikiSIScraper')
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level, logging.INFO))
        console_format = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler
        if self.config['logging'].get('log_to_file', False):
            log_file = self.config['logging'].get('log_file', 'wikisi-scraper.log')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        if requests is None:
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
            self.logger.warning("robotparser not available, robots.txt will be ignored")
            return

        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            self.robots_parser = RobotFileParser()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            self.logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            self.logger.warning(f"Could not load robots.txt: {e}")
            self.robots_parser = None

    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        if self.robots_parser is None:
            return True

        try:
            user_agent = self.config['headers'].get('User-Agent', '*')
            return self.robots_parser.can_fetch(user_agent, url)
        except Exception as e:
            self.logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and normalizing path."""
        parsed = urlparse(url)
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # No fragment
        ))
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
                self.logger.debug(f"URL excluded by pattern '{pattern}': {url}")
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
                self.logger.debug(f"URL not matching include patterns: {url}")
                return False

        # Check file extension
        path = urlparse(url).path
        if path:
            allowed_extensions = filters.get('allowed_extensions', ['.html', '.htm'])
            # If URL has an extension, check if it's allowed
            if '.' in path.split('/')[-1]:
                ext = '.' + path.split('.')[-1].lower()
                if ext not in allowed_extensions:
                    self.logger.debug(f"URL extension not allowed: {url}")
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
                self.logger.warning(f"Blocked by robots.txt: {url}")
                return None

            # Make request
            timeout = self.config['site'].get('timeout', 30)
            verify_ssl = self.config['advanced'].get('verify_ssl', True)

            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout, verify=verify_ssl)
            response.raise_for_status()

            # Check content length
            max_size = self.config['advanced'].get('max_file_size_mb', 50) * 1024 * 1024
            content_length = int(response.headers.get('Content-Length', 0))
            if max_size > 0 and content_length > max_size:
                self.logger.warning(f"File too large ({content_length} bytes): {url}")
                return None

            return response.text

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            self.failed_urls[url] = str(e)
            return None

        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            self.failed_urls[url] = str(e)
            return None

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML content."""
        if BeautifulSoup is None:
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
            self.logger.error(f"Error extracting links: {e}")
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

            self.logger.info(f"Saved: {output_path}")

            # Track downloaded file
            self.downloaded_files.append({
                'url': url,
                'path': str(output_path),
                'size': len(content),
                'timestamp': datetime.now().isoformat()
            })

            return True

        except Exception as e:
            self.logger.error(f"Error saving {url}: {e}")
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

        self.logger.info(f"Starting scrape from: {start_url}")
        self.logger.info(f"Max depth: {max_depth if max_depth >= 0 else 'unlimited'}")

        start_time = datetime.now()

        while queue:
            url, depth = queue.popleft()

            # Check if already visited
            if url in self.visited_urls:
                continue

            # Check depth limit
            if max_depth >= 0 and depth > max_depth:
                self.logger.debug(f"Skipping (max depth reached): {url}")
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

            self.logger.info(f"Metadata saved: {metadata_path}")

        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable substitution.

    Hierarchy:
    1. CLI arguments (handled by caller)
    2. YAML file
    3. Environment variables (substituted in YAML)
    4. Default values

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    # Default configuration
    default_config = {
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
            'User-Agent': 'Ambulon WikiSI Scraper/1.0',
            'Accept-Language': 'fr-FR,fr;q=0.9'
        },
        'authentication': {
            'type': os.getenv('WIKISI_AUTH_TYPE', 'none'),
            'username': os.getenv('WIKISI_USERNAME', ''),
            'password': os.getenv('WIKISI_PASSWORD', ''),
            'token': os.getenv('WIKISI_TOKEN', '')
        },
        'advanced': {
            'max_retries': 3,
            'respect_robots_txt': True,
            'verify_ssl': True,
            'threads': 1,
            'max_file_size_mb': 50
        },
        'logging': {
            'level': os.getenv('WIKISI_LOG_LEVEL', 'info'),
            'log_to_file': True,
            'log_file': './wikisi-scraper.log'
        }
    }

    # Load from YAML if specified
    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"Warning: Config file '{config_path}' not found, using defaults", file=sys.stderr)
            return default_config

        if yaml is None:
            print("Warning: PyYAML not installed, cannot load YAML config. Install with: pip install pyyaml", file=sys.stderr)
            return default_config

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_content = f.read()

            # Substitute environment variables in YAML
            def replace_env_var(match):
                var_expr = match.group(1)
                # Handle ${VAR:-default} syntax
                if ':-' in var_expr:
                    var_name, default_value = var_expr.split(':-', 1)
                    return os.getenv(var_name, default_value)
                else:
                    return os.getenv(var_expr, '')

            yaml_content = re.sub(r'\$\{([^}]+)\}', replace_env_var, yaml_content)

            yaml_config = yaml.safe_load(yaml_content)

            # Merge with defaults (YAML overrides defaults)
            def deep_merge(base, override):
                result = base.copy()
                for key, value in override.items():
                    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = deep_merge(result[key], value)
                    else:
                        result[key] = value
                return result

            return deep_merge(default_config, yaml_config)

        except Exception as e:
            print(f"Error loading config from '{config_path}': {e}", file=sys.stderr)
            return default_config

    return default_config


def scrape_wikisi(
    url: Optional[str] = None,
    output_dir: Optional[str] = None,
    config_path: Optional[str] = None,
    max_depth: Optional[int] = None,
    delay: Optional[float] = None,
    verbose: bool = False
) -> int:
    """
    Scrape WikiSI website.

    Args:
        url: Starting URL (overrides config)
        output_dir: Output directory (overrides config)
        config_path: Path to config file
        max_depth: Maximum crawl depth (overrides config)
        delay: Delay between requests (overrides config)
        verbose: Enable verbose logging

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Check dependencies
    missing_deps = []
    if requests is None:
        missing_deps.append('requests')
    if BeautifulSoup is None:
        missing_deps.append('beautifulsoup4')
    if yaml is None:
        missing_deps.append('pyyaml')

    if missing_deps:
        print(f"Error: Missing required dependencies: {', '.join(missing_deps)}", file=sys.stderr)
        print(f"Install with: pip install {' '.join(missing_deps)}", file=sys.stderr)
        return 1

    try:
        # Load configuration
        if config_path is None:
            # Try default config paths
            default_paths = [
                'config/wikisi.yaml',
                './wikisi.yaml',
                os.path.expanduser('~/.ambulon/wikisi.yaml')
            ]
            for path in default_paths:
                if Path(path).exists():
                    config_path = path
                    break

        config = load_config(config_path)

        # Override with CLI arguments (highest priority)
        if url:
            config['site']['base_url'] = url
        if output_dir:
            config['output']['directory'] = output_dir
        if max_depth is not None:
            config['site']['max_depth'] = max_depth
        if delay is not None:
            config['site']['delay'] = delay
        if verbose:
            config['logging']['level'] = 'debug'

        # Validate base URL
        if not config['site']['base_url'] or config['site']['base_url'] == 'https://wikisi.example.gouv.fr':
            print("Error: Please configure base_url in config file or provide --url argument", file=sys.stderr)
            return 1

        # Create scraper
        scraper = WikiSIScraper(config, verbose=verbose)

        # Start scraping
        stats = scraper.scrape()

        # Print summary
        print("\n" + "="*60)
        print("SCRAPING COMPLETED")
        print("="*60)
        print(f"Start URL:        {stats['start_url']}")
        print(f"Duration:         {stats['duration_seconds']:.2f} seconds")
        print(f"Pages visited:    {stats['pages_visited']}")
        print(f"Pages downloaded: {stats['pages_downloaded']}")
        print(f"Pages failed:     {stats['pages_failed']}")
        print(f"Total size:       {stats['total_size_bytes'] / 1024:.2f} KB")
        print(f"Output directory: {config['output']['directory']}")
        print("="*60)

        if stats['pages_failed'] > 0:
            print(f"\nWarning: {stats['pages_failed']} pages failed to download")
            print("Check the log file for details")

        return 0

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error: Scraping failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1
