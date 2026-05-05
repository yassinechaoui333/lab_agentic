"""
Travel Search MCP Server (travel-search-mcp)
Retrieves tourist attractions, landmarks, and activities for a given destination.
Runs on port 3001.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travel-search-mcp")

# --------------------------------------------------------------------------- #
#  Simulated destination database
# --------------------------------------------------------------------------- #
DESTINATIONS: dict[str, dict] = {
    "barcelona": {
        "country": "Spain",
        "currency": "EUR",
        "language": "Spanish / Catalan",
        "attractions": [
            "La Sagrada Familia",
            "Park Güell",
            "Casa Batlló",
            "La Rambla",
            "Gothic Quarter (Barri Gòtic)",
            "Camp Nou Stadium",
            "Barceloneta Beach",
            "Montjuïc Castle",
            "Picasso Museum",
            "Magic Fountain of Montjuïc",
        ],
        "activities": [
            "Walking tour of the Gothic Quarter",
            "Tapas and wine tasting in El Born",
            "Beach day at Barceloneta",
            "Day trip to Montserrat monastery",
            "Flamenco show in Ciutat Vella",
            "Cycling along the waterfront",
            "Visit the Boqueria Market",
            "Sunset at Bunkers del Carmel",
            "Kayaking along the coast",
            "Cooking class – traditional paella",
        ],
    },
    "paris": {
        "country": "France",
        "currency": "EUR",
        "language": "French",
        "attractions": [
            "Eiffel Tower",
            "Louvre Museum",
            "Notre-Dame Cathedral",
            "Arc de Triomphe",
            "Sacré-Cœur Basilica",
            "Musée d'Orsay",
            "Palace of Versailles",
            "Champs-Élysées",
            "Sainte-Chapelle",
            "Panthéon",
        ],
        "activities": [
            "Seine river cruise at sunset",
            "Explore Montmartre and artists' quarter",
            "Pastry tasting in Le Marais",
            "Visit the Catacombs of Paris",
            "Day trip to Versailles",
            "Picnic in Luxembourg Gardens",
            "Wine and cheese evening",
            "Moulin Rouge cabaret show",
            "Shopping at Galeries Lafayette",
            "Bike tour along the Seine",
        ],
    },
    "tokyo": {
        "country": "Japan",
        "currency": "JPY",
        "language": "Japanese",
        "attractions": [
            "Senso-ji Temple",
            "Tokyo Skytree",
            "Meiji Shrine",
            "Shibuya Crossing",
            "Tsukiji Outer Market",
            "Imperial Palace East Gardens",
            "Akihabara Electric Town",
            "Shinjuku Gyoen National Garden",
            "Tokyo Tower",
            "Odaiba & teamLab Borderless",
        ],
        "activities": [
            "Sushi-making class in Tsukiji",
            "Day trip to Mount Fuji / Hakone",
            "Explore Harajuku fashion district",
            "Traditional tea ceremony experience",
            "Sumo wrestling morning practice visit",
            "Robot Restaurant show in Shinjuku",
            "Cherry blossom viewing (seasonal)",
            "Karaoke night in Shibuya",
            "Visit the Ghibli Museum",
            "Ramen street food crawl",
        ],
    },
    "new york": {
        "country": "United States",
        "currency": "USD",
        "language": "English",
        "attractions": [
            "Statue of Liberty",
            "Central Park",
            "Empire State Building",
            "Times Square",
            "Brooklyn Bridge",
            "Metropolitan Museum of Art",
            "One World Observatory",
            "Broadway Theater District",
            "The High Line",
            "Grand Central Terminal",
        ],
        "activities": [
            "Broadway musical show",
            "Walk across Brooklyn Bridge at sunset",
            "Food tour in Chinatown & Little Italy",
            "Bike ride through Central Park",
            "Visit the 9/11 Memorial & Museum",
            "Explore street art in Bushwick",
            "Rooftop bar hopping in Manhattan",
            "Ferry ride to Staten Island (free!)",
            "Shopping on Fifth Avenue",
            "Jazz night in Greenwich Village",
        ],
    },
    "marrakech": {
        "country": "Morocco",
        "currency": "MAD",
        "language": "Arabic / French / Berber",
        "attractions": [
            "Jemaa el-Fnaa Square",
            "Majorelle Garden",
            "Bahia Palace",
            "Koutoubia Mosque",
            "Saadian Tombs",
            "Medina Souks",
            "El Badi Palace",
            "Menara Gardens",
            "Ben Youssef Madrasa",
            "Museum of Marrakech",
        ],
        "activities": [
            "Haggling in the Medina souks",
            "Traditional Moroccan hammam experience",
            "Cooking class – tagine and couscous",
            "Sunset camel ride in Agafay Desert",
            "Day trip to Ourika Valley & Atlas Mountains",
            "Mint tea ceremony on a riad rooftop",
            "Henna tattoo in Jemaa el-Fnaa",
            "Hot air balloon ride at sunrise",
            "Visit Berber villages",
            "Evening food tour of street stalls",
        ],
    },
}


@mcp.tool()
def search_destination(destination: str) -> str:
    """
    Search for tourist attractions, landmarks, and activities for a given
    destination city. Returns detailed information including country, currency,
    language, top attractions, and recommended activities.
    """
    key = destination.strip().lower()

    # Try partial match
    matched = None
    for k in DESTINATIONS:
        if key in k or k in key:
            matched = k
            break

    if matched is None:
        available = ", ".join(DESTINATIONS.keys())
        return (
            f"Destination '{destination}' not found in database. "
            f"Available destinations: {available}. "
            f"You can still provide general travel advice based on your knowledge."
        )

    info = DESTINATIONS[matched]
    attractions = "\n".join(f"  • {a}" for a in info["attractions"])
    activities = "\n".join(f"  • {a}" for a in info["activities"])

    return (
        f"=== {matched.title()} ({info['country']}) ===\n"
        f"Currency: {info['currency']}\n"
        f"Language: {info['language']}\n\n"
        f"Top Attractions:\n{attractions}\n\n"
        f"Recommended Activities:\n{activities}"
    )


@mcp.tool()
def list_available_destinations() -> str:
    """List all destinations available in the travel database."""
    destinations = []
    for name, info in DESTINATIONS.items():
        destinations.append(f"• {name.title()} ({info['country']})")
    return "Available Destinations:\n" + "\n".join(destinations)


if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=3001)
