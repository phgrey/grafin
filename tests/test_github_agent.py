import pytest
from graphin.agents.github_agent import GitHubAgent, github_agent_node


def test_github_agent_flow_operations():
    agent = GitHubAgent(repo="phgrey/grafin", default_branch="main")

    # Create branch
    b_res = agent.create_branch("feature/test-1")
    assert b_res["status"] == "success"
    assert b_res["branch_name"] == "feature/test-1"

    # Commit files
    c_res = agent.commit_files(
        branch_name="feature/test-1",
        file_changes={"test.py": "print('hello')"},
        commit_message="feat: add test.py",
    )
    assert c_res["status"] == "success"
    assert "test.py" in c_res["files_committed"]

    # Create Pull Request
    pr_res = agent.create_pull_request(
        title="Test PR",
        body="PR description",
        head_branch="feature/test-1",
        base_branch="main",
    )
    assert pr_res["status"] == "success"
    pr_num = pr_res["pr_number"]

    # Review and Merge PR
    m_res = agent.review_and_merge_pr(pr_number=pr_num, reviewer_role="admin", action="approve")
    assert m_res["status"] == "success"
    assert m_res["merged"] is True


def test_github_agent_node_callable():
    initial_state = {
        "classified_chunks": [{"section_title": "Implement Feature X"}],
        "saved_results": [],
    }

    res = github_agent_node(initial_state)
    assert "github_flow_data" in res
    assert res["github_flow_data"]["branch_name"].startswith("feature/")
    assert len(res["saved_results"]) == 1
