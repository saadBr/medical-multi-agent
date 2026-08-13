import asyncio
import json

from backend.app.state import MedicalState
from backend.app.tools.mcp_client import get_medical_tools


async def call_mcp_tool(
    severity: str,
    warning_signs: list[str],
) -> dict:
    """Load and invoke the MCP tool in its own event loop."""

    tools = await get_medical_tools()

    care_tool = next(
        tool
        for tool in tools
        if tool.name == "recommend_interim_care"
    )

    raw_result = await care_tool.ainvoke(
        {
            "severity": severity,
            "warning_signs": warning_signs,
        }
    )

    if isinstance(raw_result, list):
        text_block = next(
            block["text"]
            for block in raw_result
            if block.get("type") == "text"
        )
        return json.loads(text_block)

    return raw_result


def run_mcp_tool(
    severity: str,
    warning_signs: list[str],
) -> dict:
    """Run the asynchronous MCP operation inside a worker thread."""

    return asyncio.run(
        call_mcp_tool(severity, warning_signs)
    )


async def interim_care_agent(state: MedicalState) -> dict:
    """Generate interim care without blocking the ASGI event loop."""

    summary = state["diagnostic_summary"]

    interim_care = await asyncio.to_thread(
        run_mcp_tool,
        summary["severity"],
        summary["warning_signs"],
    )

    return {"interim_care": interim_care}