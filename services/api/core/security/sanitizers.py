import os
import re
from fastapi import HTTPException, status


def sanitize_file_path(path: str, base_dir: str = "workspaces") -> str:
    """
    Prevents path traversal attacks by validating that resolved path stays within base_dir.
    """
    if not path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty path provided")

    abs_base = os.path.abspath(base_dir)
    target_path = os.path.abspath(os.path.join(abs_base, path))

    if not target_path.startswith(abs_base):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Path traversal attempt blocked"
        )
    return target_path


def sanitize_command(command: str) -> str:
    """
    Sanitizes command line inputs against shell injection characters.
    """
    forbidden_tokens = [";", "&&", "||", "`", "$(", "${", ">", "<", "\n"]
    for token in forbidden_tokens:
        if token in command:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Command contains forbidden character: {token}"
            )
    return command.strip()
