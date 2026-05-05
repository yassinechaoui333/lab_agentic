"""
Currency Converter MCP Server (currency-mcp) – port 3004.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("currency-mcp")

RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 154.50,
    "MAD": 10.05,
    "CAD": 1.37,
    "AUD": 1.55,
    "CHF": 0.88,
    "CNY": 7.24,
    "INR": 83.50,
    "BRL": 5.05,
    "MXN": 17.15,
    "KRW": 1340.0,
    "TRY": 32.50,
    "SEK": 10.85,
}


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another using current exchange rates."""
    src = from_currency.strip().upper()
    tgt = to_currency.strip().upper()
    if src not in RATES:
        return f"Unknown currency '{from_currency}'. Available: {', '.join(sorted(RATES.keys()))}"
    if tgt not in RATES:
        return f"Unknown currency '{to_currency}'. Available: {', '.join(sorted(RATES.keys()))}"
    usd = amount / RATES[src]
    result = usd * RATES[tgt]
    return (
        f"{amount:,.2f} {src} = {result:,.2f} {tgt}\n"
        f"(Rate: 1 {src} = {RATES[tgt] / RATES[src]:.4f} {tgt})"
    )


@mcp.tool()
def list_currencies() -> str:
    """List all supported currencies with their USD exchange rates."""
    lines = [f"  {code}: {rate}" for code, rate in sorted(RATES.items())]
    return "Supported currencies (rate per 1 unit in USD):\n" + "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=3004)
