"""
Weather MCP Server (weather-mcp) – port 3003.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-mcp")

WEATHER: dict[str, dict[str, dict]] = {
    "barcelona": {
        "january": {"hi": 13, "lo": 5, "cond": "Cool & cloudy", "rain": 5, "rec": "indoor"},
        "february": {"hi": 14, "lo": 6, "cond": "Cool & cloudy", "rain": 4, "rec": "indoor"},
        "march": {"hi": 16, "lo": 8, "cond": "Mild", "rain": 5, "rec": "mixed"},
        "april": {"hi": 18, "lo": 10, "cond": "Warm & sunny", "rain": 6, "rec": "outdoor"},
        "may": {"hi": 21, "lo": 14, "cond": "Warm & sunny", "rain": 5, "rec": "outdoor"},
        "june": {"hi": 25, "lo": 18, "cond": "Hot & sunny", "rain": 3, "rec": "outdoor"},
        "july": {"hi": 28, "lo": 21, "cond": "Hot & sunny", "rain": 2, "rec": "outdoor"},
        "august": {"hi": 28, "lo": 21, "cond": "Hot & humid", "rain": 4, "rec": "outdoor"},
        "september": {"hi": 26, "lo": 18, "cond": "Warm", "rain": 5, "rec": "outdoor"},
        "october": {"hi": 22, "lo": 14, "cond": "Mild", "rain": 7, "rec": "mixed"},
        "november": {"hi": 17, "lo": 9, "cond": "Cool", "rain": 6, "rec": "indoor"},
        "december": {"hi": 14, "lo": 6, "cond": "Cool", "rain": 5, "rec": "indoor"},
    },
    "paris": {
        "january": {"hi": 7, "lo": 2, "cond": "Cold & grey", "rain": 10, "rec": "indoor"},
        "march": {"hi": 12, "lo": 4, "cond": "Cool", "rain": 9, "rec": "mixed"},
        "june": {"hi": 23, "lo": 13, "cond": "Warm & pleasant", "rain": 7, "rec": "outdoor"},
        "july": {"hi": 25, "lo": 15, "cond": "Hot & sunny", "rain": 6, "rec": "outdoor"},
        "september": {"hi": 21, "lo": 12, "cond": "Warm", "rain": 7, "rec": "outdoor"},
        "december": {"hi": 7, "lo": 3, "cond": "Cold & grey", "rain": 10, "rec": "indoor"},
    },
    "tokyo": {
        "january": {"hi": 10, "lo": 2, "cond": "Cold & dry", "rain": 4, "rec": "indoor"},
        "april": {"hi": 19, "lo": 10, "cond": "Warm – cherry blossom!", "rain": 10, "rec": "outdoor"},
        "july": {"hi": 30, "lo": 23, "cond": "Hot & humid", "rain": 10, "rec": "mixed"},
        "october": {"hi": 22, "lo": 14, "cond": "Cool & pleasant", "rain": 9, "rec": "outdoor"},
    },
    "new york": {
        "january": {"hi": 4, "lo": -3, "cond": "Cold & snowy", "rain": 10, "rec": "indoor"},
        "april": {"hi": 17, "lo": 7, "cond": "Mild & rainy", "rain": 11, "rec": "mixed"},
        "july": {"hi": 30, "lo": 21, "cond": "Hot & humid", "rain": 9, "rec": "outdoor"},
        "october": {"hi": 18, "lo": 10, "cond": "Cool – fall foliage", "rain": 8, "rec": "outdoor"},
    },
    "marrakech": {
        "january": {"hi": 18, "lo": 6, "cond": "Mild & sunny", "rain": 4, "rec": "outdoor"},
        "april": {"hi": 25, "lo": 12, "cond": "Warm & pleasant", "rain": 4, "rec": "outdoor"},
        "july": {"hi": 38, "lo": 21, "cond": "Extremely hot", "rain": 0, "rec": "indoor"},
        "october": {"hi": 27, "lo": 14, "cond": "Warm & pleasant", "rain": 4, "rec": "outdoor"},
    },
}

def _find(dest: str):
    k = dest.strip().lower()
    for d in WEATHER:
        if k in d or d in k:
            return d
    return None

def _nearest_month(dest_data: dict, month: str):
    if month in dest_data:
        return month, dest_data[month]
    months_order = ["january","february","march","april","may","june",
                    "july","august","september","october","november","december"]
    idx = months_order.index(month) if month in months_order else 0
    available = sorted(dest_data.keys(), key=lambda m: abs(months_order.index(m) - idx))
    nearest = available[0]
    return nearest, dest_data[nearest]


@mcp.tool()
def get_weather(destination: str, month: str) -> str:
    """Get typical weather for a destination during a specific month.
    Returns temperature, conditions, rain days, and activity recommendation."""
    d = _find(destination)
    if not d:
        return f"No weather data for '{destination}'. Available: {', '.join(WEATHER.keys())}"
    m = month.strip().lower()
    actual_m, w = _nearest_month(WEATHER[d], m)
    note = f" (using nearest data: {actual_m.title()})" if actual_m != m else ""
    return (
        f"Weather in {d.title()} – {m.title()}{note}:\n"
        f"  Temperature: {w['lo']}°C – {w['hi']}°C\n"
        f"  Conditions: {w['cond']}\n"
        f"  Rainy days: {w['rain']}\n"
        f"  Recommendation: {w['rec']} activities"
    )


@mcp.tool()
def get_best_months(destination: str) -> str:
    """Get best months to visit a destination based on weather."""
    d = _find(destination)
    if not d:
        return f"No weather data for '{destination}'."
    scored = []
    for m, w in WEATHER[d].items():
        s = {"outdoor": 3, "mixed": 2, "indoor": 1}[w["rec"]] * 10 - w["rain"]
        scored.append((m, s, w))
    scored.sort(key=lambda x: x[1], reverse=True)
    lines = [f"  • {m.title()}: {w['lo']}–{w['hi']}°C, {w['cond']}" for m, _, w in scored[:3]]
    return f"Best months for {d.title()}:\n" + "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=3003)
