"""Core cloning logic for GitLab projects."""
import subprocess
from pathlib import Path

def clone_repository(repo_url_suffix: str, base_clone_dir: Path, username: str, token: str):
    """
    Clones a single GitLab repository.

    Args:
        repo_url_suffix (str): The repository URL path (e.g., 'group/project.git').
        base_clone_dir (Path): The local directory to clone into.
        username (str): The GitLab username for authentication.
        token (str): The GitLab personal access token.

    Yields:
        A dictionary with status updates.
    """
    try:
        # Clean up URL prefix if present
        repo_url_clean = repo_url_suffix
        if repo_url_clean.startswith('https://'):
            repo_url_clean = repo_url_clean[8:]
        elif repo_url_clean.startswith('http://'):
            repo_url_clean = repo_url_clean[7:]

        parts = repo_url_clean.split('/', 1)
        if len(parts) < 2:
            yield {"status": "error", "message": f"Invalid repository URL format: {repo_url_suffix}"}
            return

        domain, path_in_gitlab = parts
        authenticated_url = f"https://{username}:{token}@{domain}/{path_in_gitlab}"
        
        repo_name = Path(repo_url_clean).stem
        target_path = base_clone_dir / repo_name

        if target_path.exists():
            yield {
                "status": "skipped",
                "message": f"Repository '{repo_name}' already exists at '{target_path}'.",
                "repo_name": repo_name,
                "target_path": str(target_path),
            }
            return

        display_url = f"https://{domain}/{path_in_gitlab}"
        yield {"status": "cloning", "message": f"Cloning '{repo_name}' from '{display_url}'..."}

        result = subprocess.run(
            ["git", "clone", authenticated_url, str(target_path)],
            check=True,
            capture_output=True,
            text=True,
            shell=True  # For Windows compatibility
        )
        
        yield {
            "status": "success",
            "message": f"Successfully cloned '{repo_name}'.",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "repo_name": repo_name,
            "target_path": str(target_path),
        }

    except subprocess.CalledProcessError as e:
        yield {
            "status": "error",
            "message": f"Error cloning '{repo_name}': {e}",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "repo_name": repo_name,
        }
    except FileNotFoundError:
        yield {"status": "error", "message": "Error: 'git' command not found. Please ensure Git is installed and in your PATH."}
    except Exception as e:
        yield {"status": "error", "message": f"An unexpected error occurred: {e}"}
