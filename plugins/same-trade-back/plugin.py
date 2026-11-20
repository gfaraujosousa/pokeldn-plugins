"""Send the same one back: one tool per game that pokeldn hosts a trade for, each running that
game's own trade host with the mirror partner (same_back.py, sameback_mirror.py).

The tools are read from pokeldn's catalog when the plugin loads, so a game pokeldn adds a board trade
host for gets the tool too, with the host's own console steps, link code and version fields."""
from pokeldn.app.catalog import GAMES
from pokeldn.plugins import Tool

SCRIPT = "same_back.py"
NAME = "Trade: send the same one back"
SUMMARY = ("Trade any Pokemon and get the same one back in that trade, so one that evolves by trade "
           "evolves on your console. You need no Pokemon to offer and nothing comes from pokeldn.")
STEP = "Offer the Pokemon you want back: pokeldn offers you the same one, then confirm the trade."
# Fields that decide what we offer: the mirror offers the console's own Pokemon instead.
OFFER_FLAGS = {"--trade-back", "--online", "--online-code"}


def host_of(game):
    """-> the game's trade host over the board, or None."""
    for tool in game.tools:
        if tool.activity == "trade" and dict(tool.variant) == {"role": "host", "link": "board"}:
            return tool
    return None


def kept_fields(host):
    dropped = {f.key for f in host.fields if f.kind == "pokemon" or f.key in OFFER_FLAGS}
    kept = []
    for field in host.fields:
        if field.key in dropped:
            continue
        refers = {field.when[0] if field.when else "", field.unless, field.requires}
        if refers & dropped:
            continue
        kept.append(field)
    return tuple(kept)


def kept_steps(host, fields):
    """The host's console steps, less those that only show for a field this tool leaves out."""
    keys = {f.key for f in fields}
    steps = [s for s in host.steps if isinstance(s, str) or s[1][0] in keys]
    return (*steps, STEP)


def tool_for(game, host):
    fields = kept_fields(host)
    return Tool(f"same-back-{game.key}", NAME, SCRIPT, SUMMARY, kept_steps(host, fields), fields=fields,
                fixed=("--same-back-launcher", host.script, "--same-back-game", game.key, *host.fixed,
                       "--online"),
                radio=host.radio, joins=host.joins)


def tools():
    """-> (game key, Tool) for every game with a board trade host."""
    return [(game.key, tool_for(game, host)) for game in GAMES if (host := host_of(game))]


def register(api):
    for game, tool in tools():
        api.add_tool(game, tool)
