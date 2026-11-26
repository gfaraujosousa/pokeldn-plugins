"""Shiny Static Legendary RNG (Gen 3): installs a resident VBlank + script-table hook in RAM
that seeks the next genuine Method 1 shiny gRngValue for the save's own TID/SID right before the
chosen static legendary is created by the game's original encounter routine."""
from pokeldn.app.catalog import GAMES
from pokeldn.plugins import Field, Tool

SCRIPT = "gen3shiny_run.py"

FRLG_CHOICES = (
    ("any", "Any static legendary (Birds, Mewtwo, Ho-Oh, Lugia, Deoxys, Snorlax)"),
    ("hooh", "Ho-Oh (Navel Rock Summit)"),
    ("lugia", "Lugia (Navel Rock Base)"),
    ("deoxys", "Deoxys (Birth Island)"),
    ("mewtwo", "Mewtwo (Cerulean Cave)"),
    ("articuno", "Articuno (Seafoam Islands)"),
    ("zapdos", "Zapdos (Power Plant)"),
    ("moltres", "Moltres (Mt. Ember)"),
    ("snorlax", "Snorlax (Route 12 & Route 16)"),
)

EMERALD_CHOICES = (
    ("any", "Any static legendary (Regis, Weather Trio, Lati, Ho-Oh, Lugia, Deoxys, Mew)"),
    ("mew", "Mew (Faraway Island)"),
    ("deoxys", "Deoxys (Birth Island)"),
    ("hooh", "Ho-Oh (Navel Rock Top)"),
    ("lugia", "Lugia (Navel Rock Bottom)"),
    ("rayquaza", "Rayquaza (Sky Pillar Top)"),
    ("kyogre", "Kyogre (Marine Cave)"),
    ("groudon", "Groudon (Terra Cave)"),
    ("regirock", "Regirock (Desert Ruins)"),
    ("regice", "Regice (Island Cave)"),
    ("registeel", "Registeel (Ancient Tomb)"),
    ("latias", "Latias (Southern Island)"),
    ("latios", "Latios (Southern Island)"),
)

CHANNELS = (("11", "11"), ("1", "1"), ("6", "6"))
GBA_LANGUAGES = (
    ("{gba_language}", "Same as Settings"),
    ("english", "English"),
    ("french", "French"),
    ("german", "German"),
    ("italian", "Italian"),
    ("spanish", "Spanish"),
    ("japanese", "Japanese"),
)


def _frlg_tool() -> Tool:
    steps = (
        "Restart the game cleanly without other RAM boosts active (resident RAM is shared).",
        "Title screen: Mystery Gift, Wonder Cards, Friend. Wait on the search screen.",
        "Start here, then pick POKELDN. Confirm 0x53484E59 MATCHES in the Session log.",
        "Continue your save and trigger the legendary encounter normally. The game's own routine creates a legal Method 1 shiny for your TID/SID.",
        "Stays in RAM until the game is closed or reset; capture and save normally.",
    )
    fields = (
        Field("--game-target", "Game", "choice", default="frlg",
              choices=(("frlg", "FireRed / LeafGreen (all 12 Switch builds)"),
                       ("emerald", "Emerald (including Emerald Swap)")),
              help="Choose FireRed / LeafGreen, or Emerald when playing through Emerald Swap. Ruby and Sapphire have no wireless Mystery Gift."),
        Field("--frlg-version", "Cartridge", "choice", default="any",
              choices=(("any", "Auto (FireRed or LeafGreen)"), ("firered", "FireRed only"), ("leafgreen", "LeafGreen only")),
              when=("--game-target", "frlg"),
              help="Optionally restrict the host to FireRed or LeafGreen."),
        Field("--frlg-legendary", "Legendary", "choice", default="any", choices=FRLG_CHOICES,
              when=("--game-target", "frlg"),
              help="Target static encounter in FireRed or LeafGreen."),
        Field("--emerald-legendary", "Legendary", "choice", default="any", choices=EMERALD_CHOICES,
              when=("--game-target", "emerald"),
              help="Target static encounter in Emerald."),
        Field("--language", "Cartridge language", "choice", default="{gba_language}", choices=GBA_LANGUAGES,
              hidden=True, help="Set to Japanese only for Japanese FireRed/LeafGreen cartridges."),
        Field("--channel", "Channel", "choice", default="11", choices=CHANNELS, hidden=True,
              help="Wireless channel hosted by the board."),
    )
    return Tool(
        "gen3-shiny-legendary-rng",
        "Shiny static legendary (RNG)",
        SCRIPT,
        "Seek the next legal Method 1 shiny gRngValue for your save's own TID/SID right before "
        "a static legendary generates. No button timing needed; works in FireRed, LeafGreen and "
        "Emerald (including Emerald Swap).",
        steps,
        fields=fields,
        fixed=("--ot", "{ot}", "--id", "{tid}:{sid}"),
    )


def _rse_tool() -> Tool:
    steps = (
        "Restart Emerald cleanly without other RAM boosts active.",
        "Title screen: Mystery Gift, Wonder Cards, Friend. Wait on the search screen.",
        "Start here, then pick POKELDN. Confirm 0x53484E59 MATCHES in the Session log.",
        "Continue your save and trigger the legendary encounter normally. The game creates a legal Method 1 shiny for your TID/SID.",
    )
    fields = (
        Field("--emerald-legendary", "Legendary", "choice", default="any", choices=EMERALD_CHOICES,
              help="Target static encounter in Emerald. Ruby and Sapphire have no wireless Mystery Gift."),
        Field("--channel", "Channel", "choice", default="11", choices=CHANNELS, hidden=True,
              help="Wireless channel hosted by the board."),
    )
    return Tool(
        "rse-shiny-legendary-rng",
        "Shiny static legendary (RNG, Emerald)",
        SCRIPT,
        "Install a dynamic-discovery RAM hook in Emerald (including Emerald Swap) that seeks the "
        "next legal Method 1 shiny gRngValue right before a static legendary generates.",
        steps,
        fields=fields,
        fixed=("--game-target", "emerald", "--ot", "{ot}", "--id", "{tid}:{sid}"),
    )


def tools():
    out = [("frlg", _frlg_tool())]
    if any(g.key == "rse" for g in GAMES):
        out.append(("rse", _rse_tool()))
    return out


def register(api):
    for game, tool in tools():
        api.add_tool(game, tool)
