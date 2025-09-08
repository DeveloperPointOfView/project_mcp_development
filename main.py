"""
Mini Pokédex Lite - FastMCP 2.0 Resources Demo (Async Version)

This demo teaches MCP resources by providing a simple Pokédex interface.
It demonstrates:
- Static resource listing with @mcp.resource (async)
- Dynamic resource templates with URI parameters (async)
- External API integration with PokeAPI (async httpx)
- Error handling and JSON responses
- Proper async/await patterns

Usage:
    python main.py

MCP Resources provided:
- poke://pokemon/1 (Bulbasaur)
- poke://pokemon/4 (Charmander) 
- poke://pokemon/7 (Squirtle)
- poke://pokemon/{id} (Any Pokémon by ID)
"""

import sys
import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError

app = FastMCP(name="mini-pokedex-lite")


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)  # <- STDERR only


STARTERS = {"1": "bulbasaur", "4": "charmander", "7": "squirtle"}


@app.resource("poke://starters")
async def list_starters() -> dict:
    return {
        "starters": [
            {"id": pid, "name": name.capitalize(), "uri": f"poke://pokemon/{pid}"}
            for pid, name in STARTERS.items()
        ],
        "total": len(STARTERS),
    }


@app.resource("poke://pokemon/{pokemon_id_or_name}")
async def get_pokemon(pokemon_id_or_name: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id_or_name}")
        if r.status_code == 404:
            raise ResourceError(f"Pokémon '{pokemon_id_or_name}' not found")
        r.raise_for_status()
        data = r.json()
        return {
            "id": data["id"],
            "name": data["name"].capitalize(),
            "height": data["height"] / 10,
            "weight": data["weight"] / 10,
            "types": [t["type"]["name"] for t in data["types"]],
            "abilities": [a["ability"]["name"] for a in data["abilities"]],
            "base_stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            "sprite": data["sprites"]["front_default"],
            "api_url": f"https://pokeapi.co/api/v2/pokemon/{pokemon_id_or_name}",
        }


@app.resource("poke://types/{type_name}")
async def get_pokemon_by_type(type_name: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"https://pokeapi.co/api/v2/type/{type_name}")
        if r.status_code == 404:
            raise ResourceError(f"Type '{type_name}' not found")
        r.raise_for_status()
        data = r.json()
        pokemon_list = data["pokemon"][:10]
        return {
            "type": type_name.capitalize(),
            "type_id": data["id"],
            "pokemon_count": len(data["pokemon"]),
            "showing": len(pokemon_list),
            "pokemon": [
                {
                    "name": p["pokemon"]["name"].capitalize(),
                    "uri": f"poke://pokemon/{p['pokemon']['name']}",
                }
                for p in pokemon_list
            ],
        }


if __name__ == "__main__":
    # Human-readable logs go to STDERR:
    log("🔥 Pokédex STDIO server starting…")
    log("🎯 Try: poke://starters, poke://pokemon/1, poke://types/fire")
    app.run()  # STDIO transport
