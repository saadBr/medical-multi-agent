from backend.app.nodes.interim_care_agent import run_mcp_tool


def test_mcp_returns_routine_guidance_without_warning_signs():
    result = run_mcp_tool(
        severity="moderate",
        warning_signs=[],
    )

    assert result["urgency"] == "routine"
    assert len(result["recommendations"]) > 0


def test_mcp_returns_urgent_guidance_for_warning_signs():
    result = run_mcp_tool(
        severity="moderate",
        warning_signs=["chest pain"],
    )

    assert result["urgency"] == "urgent"
    assert len(result["recommendations"]) > 0