import os
import re
import shutil
import subprocess
import logging
from typing import Dict, Any
from core.config import settings
from core.security.secret_masker import redact_secrets

logger = logging.getLogger(__name__)


class RepoCloneService:
    """
    Handles local git clone, pull, fetch, and branch checkout operations
    using installation tokens for GitHub App authentication.
    """

    @classmethod
    def get_workspace_dir(cls, project_id: str, repo_name: str) -> str:
        base_dir = os.path.abspath(os.path.join(settings.WORKSPACE_ROOT, project_id))
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, repo_name)

    @classmethod
    def _sanitize_url_for_logging(cls, url: str) -> str:
        """Redacts token credentials from git clone URLs before logging."""
        if "x-access-token:" in url:
            return re.sub(r"x-access-token:[^@]+@", "x-access-token:***REDACTED***@", url)
        return url

    @classmethod
    def clone_or_pull(cls, project_id: str, repo_name: str, git_url: str, token: str = "") -> str:
        target_dir = cls.get_workspace_dir(project_id, repo_name)

        auth_url = git_url
        if token and "github.com" in git_url:
            auth_url = git_url.replace("https://github.com/", f"https://x-access-token:{token}@github.com/")

        safe_url = cls._sanitize_url_for_logging(auth_url)

        if os.path.exists(os.path.join(target_dir, ".git")):
            logger.info(f"[RepoCloneService] Repository already cloned at {target_dir}. Running git pull...")
            try:
                subprocess.run(["git", "pull"], cwd=target_dir, capture_output=True, check=True, text=True)
            except Exception as e:
                logger.warning(f"[RepoCloneService] git pull warning for {safe_url}: {redact_secrets(str(e))}")
        else:
            logger.info(f"[RepoCloneService] Cloning repository {safe_url} to {target_dir}...")
            try:
                subprocess.run(["git", "clone", auth_url, target_dir], capture_output=True, check=True, text=True)
            except Exception as e:
                logger.error(f"[RepoCloneService] git clone failed for {safe_url}: {redact_secrets(str(e))}")
                # Create directory fallback for local testing
                os.makedirs(target_dir, exist_ok=True)

        return target_dir
