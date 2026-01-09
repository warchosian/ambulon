"""Module GitLab Clone - Clone des projets GitLab depuis la configuration."""
import yaml
from pathlib import Path
import subprocess
import sys

CONFIG_FILE = Path("config/gitlab.yaml")

def load_config():
    """Charge la configuration GitLab depuis le fichier YAML."""
    if not CONFIG_FILE.exists():
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
        print(f"Please create '{CONFIG_FILE}' based on '{CONFIG_FILE}.example'.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}")
            sys.exit(1)

def main():
    """
    Fonction principale - Clone les projets GitLab spécifiés dans config/gitlab.yaml.
    """
    config = load_config()
    gitlab_config = config.get("gitlab", {})

    token = gitlab_config.get("token")
    username = gitlab_config.get("username")
    base_clone_dir = Path(gitlab_config.get("base_clone_dir", "."))
    repositories = gitlab_config.get("repositories", [])

    if not all([token, username, base_clone_dir, repositories]):
        print("Error: Missing 'token', 'username', 'base_clone_dir', or 'repositories' in gitlab.yaml.")
        sys.exit(1)

    base_clone_dir.mkdir(parents=True, exist_ok=True)

    for repo_url_suffix in repositories:
        # Assuming the repo_url_suffix format is like "domain.com/group/project.git"
        # and we need to insert the token before the domain.
        # Example: gitlab-forge.din.developpement-durable.gouv.fr/snum/pnm3/produits/support/admin-ep/admin_ep.git
        parts = repo_url_suffix.split('/', 1) # Split only on the first slash
        if len(parts) < 2:
            print(f"Warning: Invalid repository URL format: {repo_url_suffix}. Skipping.")
            continue

        domain = parts[0]
        path_in_gitlab = parts[1]

        # Construct the authenticated URL
        # e.g., https://oauth2:glpat-token@gitlab.com/group/project.git
        authenticated_url = f"https://{username}:{token}@{domain}/{path_in_gitlab}"

        repo_name = Path(repo_url_suffix).stem # Gets 'admin_ep' from the example
        target_path = base_clone_dir / repo_name

        if target_path.exists():
            print(f"Repository '{repo_name}' already exists at '{target_path}'. Skipping.")
            continue

        print(f"Cloning '{repo_name}' from '{authenticated_url}' to '{target_path}'...")
        try:
            # Using shell=True for simpler command parsing on Windows, but be aware of security implications if inputs were not controlled.
            # Here, inputs are from config file, so it's relatively safe.
            result = subprocess.run(
                ["git", "clone", authenticated_url, str(target_path)],
                check=True,
                capture_output=True,
                text=True,
                shell=True # For Windows compatibility with git command
            )
            print(f"Successfully cloned '{repo_name}'.")
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning '{repo_name}': {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: 'git' command not found. Please ensure Git is installed and in your PATH.")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
