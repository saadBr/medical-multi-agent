import json

from backend.app.state import MedicalState
from backend.app.tools.mcp_client import get_medical_tools


async def interim_care_agent(state: MedicalState) -> dict:
    """Call the MCP tool and normalize its response."""

    tools = await get_medical_tools()

    care_tool = next(
        tool for tool in tools
        if tool.name == "recommend_interim_care"
    )

    summary = state["diagnostic_summary"]

    raw_result = await care_tool.ainvoke(
        {
            "severity": summary["severity"],
            "warning_signs": summary["warning_signs"],
        }
    )

    if isinstance(raw_result, list):
        text_block = next(
            block["text"]
            for block in raw_result
            if block.get("type") == "text"
        )
        interim_care = json.loads(text_block)
    else:
        interim_care = raw_result

    return {"interim_care": interim_care}