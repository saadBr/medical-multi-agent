from mcp.server.fastmcp import FastMCP


mcp = FastMCP("medical-care-server")


@mcp.tool()
def recommend_interim_care(
    severity: str,
    warning_signs: list[str],
) -> dict:
    """Provide cautious general interim guidance for an academic project."""

    if warning_signs or severity == "high":
        return {
            "urgency": "urgent",
            "recommendations": [
                "Seek prompt evaluation from a qualified healthcare professional.",
                "Do not delay care if symptoms worsen.",
            ],
        }

    return {
        "urgency": "routine",
        "recommendations": [
            "Rest and maintain hydration.",
            "Monitor symptoms for any worsening.",
            "Consult a healthcare professional if symptoms persist.",
        ],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")