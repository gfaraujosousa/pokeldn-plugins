"""Gen 3 QoL Pack: R-button toggle turbo (up to 8x) + reusable Key-Item Rare Candy
for FireRed, LeafGreen (all 12 Switch builds, with persistent Mom restore) and Emerald
(including Emerald Swap)."""
from pokeldn.app.catalog import GAMES
from pokeldn.plugins import Field, Tool

SCRIPT = "gen3qol_run.py"

SPEED_CHOICES = (
    ("8", "Up to 8x (7 extra passes)"),
    ("6", "Up to 6x (5 extra passes)"),
    ("4", "Up to 4x (3 extra passes)"),
    ("3", "Up to 3x (2 extra passes)"),
    ("2", "Up to 2x (1 extra pass)"),
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
        "Keep at least one free slot in Key Items (if Rare Candy is enabled). No existing Key Item is ever overwritten.",
        "Restart the game cleanly without other RAM boosts active.",
        "Title screen: Mystery Gift, Wonder Cards, Friend. Wait on the search screen.",
        "Start here, then pick POKELDN. Confirm 0x514F4C38 MATCHES in the Session log.",
        "Continue your save and save normally. Tap R to toggle turbo ON/OFF; use Key Items > Rare Candy to level up.",
        ("After closing or soft-resetting FireRed/LeafGreen, talk to Mom in Pallet Town to re-enable R-toggle turbo without the ESP32. Key-Item Rare Candy stays in your save permanently.", ("--game-target", "frlg")),
        ("After closing or soft-resetting Emerald, talk to the Mystery Gift delivery man on 2F of any Pokemon Center to re-enable R-toggle turbo (and heal your party) without the ESP32. Key-Item Rare Candy stays in your save permanently.", ("--game-target", "emerald")),
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
        Field("--turbo", "R-toggle turbo", "switch", default=True,
              help="Tap R once to toggle fast-forward ON/OFF (no need to hold R). Uses scanline budget and lag/fade guards."),
        Field("--speed", "Turbo speed", "choice", default="8", choices=SPEED_CHOICES,
              help="Target speed multiplier when R-toggle turbo is ON."),
        Field("--rare-candy", "Reusable Key-Item Rare Candy", "switch", default=True,
              help="Places one encrypted Rare Candy into a free Key Items slot. RemoveBagItem only deducts from the regular Items pocket."),
        Field("--mom-restore", "Restore turbo after soft reset / reboot", "switch", default=True,
              help="FRLG: binds Mom in Pallet Town. Emerald: installs a Wonder Card and binds the Mystery Gift delivery man on 2F of any Pokemon Center (also heals your party)."),
        Field("--language", "Cartridge language", "choice", default="{gba_language}", choices=GBA_LANGUAGES,
              hidden=True, help="Set to Japanese only for Japanese FireRed/LeafGreen cartridges."),
        Field("--channel", "Channel", "choice", default="11", choices=CHANNELS, hidden=True,
              help="Wireless channel hosted by the board."),
    )
    return Tool(
        "gen3-qol-pack",
        "QoL Pack: R-toggle turbo & Key Rare Candy",
        SCRIPT,
        "Install R-toggle fast-forward (up to 8x) and/or a reusable Rare Candy in Key Items "
        "for FireRed, LeafGreen (all 12 Switch builds) and Emerald (including Emerald Swap), "
        "with persistent restore after soft reset or reboot.",
        steps,
        fields=fields,
        fixed=("--ot", "{ot}", "--id", "{tid}:{sid}"),
    )


def _rse_tool() -> Tool:
    steps = (
        "Keep at least one free slot in Key Items (if Rare Candy is enabled). No existing Key Item is ever overwritten.",
        "Restart Emerald cleanly without other RAM boosts active.",
        "Title screen: Mystery Gift, Wonder Cards, Friend. Wait on the search screen.",
        "Start here, then pick POKELDN. Confirm 0x514F4C38 MATCHES in the Session log.",
        "Continue your save and save normally. Tap R to toggle turbo ON/OFF; use Key Items > Rare Candy to level up.",
        "After closing or soft-resetting Emerald, talk to the Mystery Gift delivery man on 2F of any Pokemon Center to re-enable R-toggle turbo (and heal your party) without the ESP32. Send QoL Pack last if you also install ticket Wonder Cards.",
    )
    fields = (
        Field("--turbo", "R-toggle turbo", "switch", default=True,
              help="Tap R once to toggle fast-forward ON/OFF in overworld and battles (no need to hold R)."),
        Field("--speed", "Turbo speed", "choice", default="8", choices=SPEED_CHOICES,
              help="Target speed multiplier when R-toggle turbo is ON."),
        Field("--rare-candy", "Reusable Key-Item Rare Candy", "switch", default=True,
              help="Places one encrypted Rare Candy into a free Key Items slot (permanent in your save)."),
        Field("--mom-restore", "Delivery man (2F) restores turbo after soft reset", "switch", default=True,
              help="Installs a QoL Wonder Card and binds the Mystery Gift delivery man on 2F of any Pokemon Center to reinstall R-toggle turbo after a soft reset or restart, while also healing your party."),
        Field("--channel", "Channel", "choice", default="11", choices=CHANNELS, hidden=True,
              help="Wireless channel hosted by the board."),
    )
    return Tool(
        "rse-qol-pack",
        "QoL Pack: R-toggle turbo & Key Rare Candy (Emerald)",
        SCRIPT,
        "Install R-toggle fast-forward (up to 8x) with persistent 2F Delivery Man restore and/or "
        "a reusable Rare Candy in Key Items for Emerald (including Emerald Swap). Ruby and "
        "Sapphire have no wireless Mystery Gift.",
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
