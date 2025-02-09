# src/config.py
import os
import sys
import configparser

def prompt_for_github_repo():
    """
    Prompt the user for a GitHub repository URL.
    """
    repo_url = input(
        "No repository configured. Please enter your GitHub repository URL (e.g., https://github.com/username/repository.git): "
    ).strip()
    if not repo_url.startswith("https://github.com/"):
        print("Invalid repository URL. It should start with 'https://github.com/'. Exiting.")
        sys.exit(1)
    return repo_url

def prompt_for_openai_key():
    """
    Prompt the user for an OpenAI API key.
    """
    api_key = input("OPENAI_API_KEY is not configured. Please enter your OpenAI API key: ").strip()
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)
    return api_key

def load_config():
    CONFIG_FILE = "config.ini"
    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_FILE):
        # Create a new configuration structure
        config["repository"] = {}
        config["api_keys"] = {}
    else:
        config.read(CONFIG_FILE)
    return config, CONFIG_FILE

def save_config(config, config_file):
    with open(config_file, "w") as f:
        config.write(f)

def get_config():
    config, config_file = load_config()

    # --- Handle repository configuration ---
    if "repository" not in config or "url" not in config["repository"] or "local_path" not in config["repository"]:
        repo_url = prompt_for_github_repo()
        # Derive the repository name from the URL (strip off ".git" if present)
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        # Define the local clone path in the user's Documents folder (Linux)
        local_repo_path = os.path.join(os.path.expanduser("~"), "Documents", repo_name)
        config["repository"] = {"url": repo_url, "local_path": local_repo_path}
        save_config(config, config_file)
        print(f"Repository configuration saved to {config_file}")
    else:
        repo_url = config["repository"]["url"]
        local_repo_path = config["repository"]["local_path"]

    # --- Handle OpenAI API key configuration ---
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        if "api_keys" in config and "openai" in config["api_keys"]:
            openai_api_key = config["api_keys"]["openai"]
            os.environ["OPENAI_API_KEY"] = openai_api_key
        else:
            openai_api_key = prompt_for_openai_key()
            config.setdefault("api_keys", {})["openai"] = openai_api_key
            save_config(config, config_file)
            os.environ["OPENAI_API_KEY"] = openai_api_key

    return {
        "repo_url": repo_url,
        "local_repo_path": local_repo_path,
        "openai_api_key": openai_api_key,
        "config": config,
        "config_file": config_file,
    }

if __name__ == "__main__":
    cfg = get_config()
    print("Configuration loaded:")
    print(f"  Repository URL: {cfg['repo_url']}")
    print(f"  Local Path: {cfg['local_repo_path']}")
    print(f"  OpenAI API Key: {cfg['openai_api_key'][:4]}...")  # Do not print full key
