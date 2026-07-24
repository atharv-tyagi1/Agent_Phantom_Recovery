import time
import logging
import jwt
import httpx
from typing import Any, Dict, List, Optional
from core.config import settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """
    Unified GitHub REST API client supporting both:
    1. Identity Layer: GitHub OAuth (user authentication, profile, orgs)
    2. Automation Layer: GitHub App Installation Tokens (webhooks, repos, PRs, Checks)
    """

    GITHUB_API_BASE = "https://api.github.com"

    # ── Identity Layer: OAuth ────────────────────────────────────────────────

    @classmethod
    async def exchange_oauth_code(cls, code: str) -> Dict[str, Any]:
        """Exchange OAuth code for user access token."""
        url = "https://github.com/login/oauth/access_token"
        payload = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_OAUTH_REDIRECT_URI,
        }
        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code >= 400:
                logger.error(f"[GitHubClient] OAuth token exchange failed: {resp.text}")
                raise Exception(f"OAuth token exchange failed: {resp.text}")
            return resp.json()

    @classmethod
    async def get_authenticated_user(cls, user_access_token: str) -> Dict[str, Any]:
        """Fetch GitHub user profile using user access token."""
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{cls.GITHUB_API_BASE}/user", headers=headers)
            if resp.status_code >= 400:
                raise Exception(f"Failed to fetch user profile: {resp.text}")
            return resp.json()

    @classmethod
    async def list_user_orgs(cls, user_access_token: str) -> List[Dict[str, Any]]:
        """List GitHub organizations for user."""
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{cls.GITHUB_API_BASE}/user/orgs", headers=headers)
            if resp.status_code >= 400:
                return []
            return resp.json()

    # ── Automation Layer: GitHub App Installation Tokens ──────────────────────

    @classmethod
    def generate_app_jwt(cls) -> str:
        """Generate JWT for GitHub App authentication."""
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),  # Max 10 mins
            "iss": settings.GITHUB_APP_ID,
        }
        private_key = settings.GITHUB_APP_PRIVATE_KEY
        if not private_key and settings.GITHUB_APP_PRIVATE_KEY_PATH:
            try:
                with open(settings.GITHUB_APP_PRIVATE_KEY_PATH, "r") as f:
                    private_key = f.read()
            except Exception as e:
                logger.error(f"[GitHubClient] Failed to read private key file: {e}")

        if not private_key:
            # Placeholder JWT for development mock when private key isn't provided
            private_key = "placeholder_key"
            return "mock_jwt_token"

        return jwt.encode(payload, private_key, algorithm="RS256")

    @classmethod
    async def get_installation_access_token(cls, installation_id: int) -> str:
        """Fetch short-lived installation access token for automation."""
        app_jwt = cls.generate_app_jwt()
        if app_jwt == "mock_jwt_token":
            return f"mock_installation_token_{installation_id}"

        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"{cls.GITHUB_API_BASE}/app/installations/{installation_id}/access_tokens"

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers)
            if resp.status_code >= 400:
                raise Exception(f"Failed to fetch installation token: {resp.text}")
            return resp.json().get("token", "")

    @classmethod
    async def list_installation_repositories(cls, installation_token: str) -> List[Dict[str, Any]]:
        """List repositories accessible to the GitHub App installation."""
        if installation_token.startswith("mock_"):
            return [
                {
                    "id": 101,
                    "name": "demo-recovery-repo",
                    "full_name": "agent-phantom/demo-recovery-repo",
                    "html_url": "https://github.com/agent-phantom/demo-recovery-repo",
                    "default_branch": "main",
                }
            ]

        headers = {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{cls.GITHUB_API_BASE}/installation/repositories", headers=headers)
            if resp.status_code >= 400:
                return []
            return resp.json().get("repositories", [])

    # ── Automation Tools: PRs & Checks ────────────────────────────────────────

    @classmethod
    async def create_pull_request(
        cls,
        installation_token: str,
        full_name: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create a Pull Request on GitHub using an installation token."""
        if installation_token.startswith("mock_"):
            return {
                "id": 999,
                "number": 42,
                "html_url": f"https://github.com/{full_name}/pull/42",
                "state": "open",
            }

        headers = {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"{cls.GITHUB_API_BASE}/repos/{full_name}/pulls"
        payload = {"title": title, "body": body, "head": head, "base": base}

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                raise Exception(f"Failed to create PR: {resp.text}")
            return resp.json()

    @classmethod
    async def create_check_run(
        cls,
        installation_token: str,
        full_name: str,
        name: str,
        head_sha: str,
        status: str = "in_progress",
        conclusion: Optional[str] = None,
        output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create or update a GitHub Check Run."""
        if installation_token.startswith("mock_"):
            return {"id": 8888, "status": status, "conclusion": conclusion}

        headers = {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"{cls.GITHUB_API_BASE}/repos/{full_name}/check-runs"
        payload: Dict[str, Any] = {"name": name, "head_sha": head_sha, "status": status}
        if conclusion:
            payload["conclusion"] = conclusion
        if output:
            payload["output"] = output

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                logger.warning(f"[GitHubClient] Check run creation failed: {resp.text}")
                return {"id": 0, "status": status}
            return resp.json()
