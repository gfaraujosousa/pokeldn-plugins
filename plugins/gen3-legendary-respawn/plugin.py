"""Static Legendary Respawn (Gen 3): resets static encounter flags and puzzle variables in
FireRed, LeafGreen (all 12 Switch builds) and Emerald (including Emerald Swap)."""
from pokeldn.app.catalog import GAMES
from pokeldn.plugins import Field, Tool

SCRIPT = "gen3respawn_run.py"

FRLG_CHOICES = (
    ("all", "All FRLG static legendaries (Birds, Mewtwo, Ho-Oh, Lugia, Deoxys)"),
    ("mewtwo", "Mewtwo (Cerulean Cave)"),
    ("articuno", "Articuno (Seafoam Islands)"),
    ("zapdos", "Zapdos (Power Plant)"),
    ("moltres", "Moltres (Mt. Ember)"),
    ("hooh", "Ho-Oh (Navel Rock Summit)"),
    ("lugia", "Lugia (Navel Rock Base)"),
    ("deoxys", "Deoxys (Birth Island — resets meteorite & triangle puzzle)"),
    ("snorlax", "Snorlax (Route 12 & Route 16)"),
)

EMERALD_CHOICES = (
    ("all", "All Emerald static legendaries (Regis, Weather Trio, Lati, Ho-Oh, Lugia, Deoxys, Mew)"),
    ("regirock", "Regirock (Desert Ruins)"),
    ("regice", "Regice (Island Cave)"),
    ("registeel", "Registeel (Ancient Tomb)"),
    ("kyogre", "Kyogre (Marine Cave — resets abnormal weather)"),
    ("groudon", "Groudon (Terra Cave — resets abnormal weather)"),
    ("rayquaza", "Rayquaza (Sky Pillar Top)"),
    ("lati", "Latias / Latios (Southern Island)"),
    ("hooh", "Ho-Oh (Navel Rock Top)"),
    ("lugia", "Lugia (Navel Rock Bottom)"),
    ("deoxys", "Deoxys (Birth Island — resets triangle puzzle)"),
    ("mew", "Mew (Faraway Island)"),
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
        ("Save outside the legendary's room (or outside Birth Island) before starting.", ("--game-target", "frlg")),
        ("Title screen: Mystery Gift, Wonder Cards, Friend. Wait on the search screen.", ("--game-target", "frlg")),
        ("Start here, then pick POKELDN. Your active Wonder Card and saved boosts are kept.", ("--game-target", "frlg")),
        ("Continue your save, re-enter the legendary's map, and save to keep the respawn.", ("--game-target", "frlg")),
        ("In Emerald (including Emerald Swap), Mystery Gift unlocks after the Pokedex and writing LINK TOGETHER WITH ALL on a Poke Mart questionnaire.", ("--game-target", "emerald")),
        ("Title screen: Mystery Gift, Wonder Cards, Friend. Start here, then pick POKELDN.", ("--game-target", "emerald")),
        ("Continue your save and talk to the delivery man on 2F of any Pokemon Center to apply the respawn. For Kyogre/Groudon, visit Weather Institute 2F afterward.", ("--game-target", "emerald")),
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
        Field("--frlg-legendary", "Legendary", "choice", default="all", choices=FRLG_CHOICES,
              when=("--game-target", "frlg"),
              help="Which static encounter to respawn in FireRed or LeafGreen."),
        Field("--emerald-legendary", "Legendary", "choice", default="all", choices=EMERALD_CHOICES,
              when=("--game-target", "emerald"),
              help="Which static encounter to respawn in Emerald."),
        Field("--language", "Cartridge language", "choice", default="{gba_language}", choices=GBA_LANGUAGES,
              hidden=True, help="Set to Japanese only for Japanese FireRed/LeafGreen cartridges."),
        Field("--channel", "Channel", "choice", default="11", choices=CHANNELS, hidden=True,
              help="Wireless channel hosted by the board."),
    )
    return Tool(
        "gen3-legendary-respawn",
        "Respawn static legendaries",
        SCRIPT,
        "Reset encounter flags and puzzle counters for static legendaries in FireRed, LeafGreen "
        "and Emerald (including Emerald Swap). Already-caught Pokemon and Pokedex entries stay intact.",
        steps,
        fields=fields,
        fixed=("--ot", "{ot}", "--id", "{tid}:{sid}"),
    )


def _rse_tool() -> Tool:
    steps = (
        "Save outside the legendary's room (or outside Birth Island / Faraway Island) before starting.",
        "Title screen: Mystery Gift, Wonder Cards, Friend. (Unlock Mystery Gift with Pokedex + LINK TOGETHER WITH ALL on a Poke Mart questionnaire.)",
        "Start here, then pick POKELDN when it appears.",
        "Continue your save and talk to the delivery man on 2F of any Pokemon Center to apply the respawn. For Kyogre/Groudon, visit Weather Institute 2F afterward.",
    )
    fields = (
        Field("--emerald-legendary", "Legendary", "choice", default="all", choices=EMERALD_CHOICES,
              help="Which static encounter to respawn in Emerald. Ruby and Sapphire have no wireless Mystery Gift."),
        Field("--channel", "Channel", "choice", default="11", choices=CHANNELS, hidden=True,
              help="Wireless channel hosted by the board."),
    )
    return Tool(
        "rse-legendary-respawn",
        "Respawn static legendaries (Emerald)",
        SCRIPT,
        "Send a portable Emerald Wonder Card whose delivery man resets static legendary flags and "
        "puzzle counters. Works on every Emerald build including Emerald Swap.",
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
