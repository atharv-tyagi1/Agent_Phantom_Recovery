import os
import subprocess
import logging
import uuid
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages workspace checkpoints via Git commits/stashes before mutating tool calls.
    Allows automated rollback if execution causes broken builds or corrupted files.
    """

    @staticmethod
    def create_checkpoint(workspace_path: str, label: str = "checkpoint") -> Optional[str]:
        if not os.path.exists(os.path.join(workspace_path, ".git")):
            logger.debug(f"[Checkpoint] No .git repo found at {workspace_path}. Skipping git checkpoint.")
            return None

        try:
            checkpoint_id = f"ckpt-{label}-{uuid.uuid4().hex[:6]}"
            # Add all current untracked / tracked changes
            subprocess.run(["git", "add", "."], cwd=workspace_path, capture_output=True, check=True)
            # Commit snapshot
            subprocess.run(
                ["git", "commit", "-m", f"Agent Phantom Checkpoint: {checkpoint_id}"],
                cwd=workspace_path,
                capture_output=True
            )
            # Get latest commit hash
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = res.stdout.strip()
            logger.info(f"[Checkpoint] Created checkpoint {commit_hash[:8]} for {workspace_path}")
            return commit_hash
        except Exception as e:
            logger.warning(f"[Checkpoint] Failed to create git checkpoint: {e}")
            return None

    @staticmethod
    def rollback_checkpoint(workspace_path: str, commit_hash: str) -> bool:
        if not os.path.exists(os.path.join(workspace_path, ".git")):
            logger.warning(f"[Checkpoint] Cannot rollback. No .git repo found at {workspace_path}.")
            return False

        try:
            # Reset hard to target commit hash
            subprocess.run(["git", "reset", "--hard", commit_hash], cwd=workspace_path, capture_output=True, check=True)
            # Clean untracked files
            subprocess.run(["git", "clean", "-fd"], cwd=workspace_path, capture_output=True, check=True)
            logger.info(f"[Checkpoint] Successfully rolled back {workspace_path} to {commit_hash[:8]}")
            return True
        except Exception as e:
            logger.error(f"[Checkpoint] Rollback failed to {commit_hash}: {e}")
            return False
