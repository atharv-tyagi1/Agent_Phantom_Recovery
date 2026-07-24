import pytest
from core.tools.github_pr import CreatePullRequestTool


@pytest.mark.asyncio
async def test_create_pull_request_tool():
    tool = CreatePullRequestTool()
    res = await tool.execute(
        installation_token="mock_token",
        full_name="agent-phantom/demo-repo",
        title="fix: autonomous patch",
        body="Verified by GLM 5.2 Reviewer",
        head="phantom/patch-1"
    )
    assert res["success"] is True
    assert "PR #" in res["output"]
