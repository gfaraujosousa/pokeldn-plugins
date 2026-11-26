"""Bielson Battle Event (Pallet Town): FRLG-only plugin installing (or safely removing) a persistent
6v6 Level 70 custom trainer battle on the Pallet Town south NPC, rewarding 1 Master Ball once per save."""
from pokeldn.plugins import Field, Tool

SCRIPT = "bielson_run.py"

CHANNELS = (("11", "11"), ("1", "1"), ("6", "6"))


def tool() -> Tool:
    steps = (
        "Back up your save first. Supported builds: English & French FireRed and LeafGreen (BPRE, BPGE, BPRF, BPGF).",
        "Save in Pallet Town and restart the game cleanly without other RAM boosts active.",
        "Title screen: Mystery Gift, Wonder Cards, Friend. Wait on the search screen.",
        "Start here, then pick POKELDN. Confirm 0x4249454C MATCHES in the Session log.",
        ("Continue your save and talk to the man walking in southern Pallet Town (near the water) to battle Bielson's Lv. 70 team of six and earn a Master Ball.", ("--action", "install")),
        ("Restart the game to restore the NPC's original appearance, then save to keep the removal. Your Master Ball and reward progress are preserved.", ("--action", "remove")),
    )
    fields = (
        Field("--action", "Action", "choice", default="install",
              choices=(("install", "Install Bielson battle event"),
                       ("remove", "Remove Bielson battle event")),
              help="Install binds Bielson to the Pallet Town south NPC; Remove clears the binding safely."),
        Field("--dialogue", "NPC dialogue language", "choice", default="en",
              choices=(("en", "English"), ("pt", "Portuguese (original)")),
              when=("--action", "install"),
              help="Language of Bielson's overworld dialogue lines."),
        Field("--frlg-version", "Cartridge", "choice", default="any",
              choices=(("any", "Auto (FireRed or LeafGreen)"),
                       ("firered", "FireRed only"),
                       ("leafgreen", "LeafGreen only")),
              help="Optionally restrict the host to FireRed or LeafGreen."),
        Field("--channel", "Channel", "choice", default="11", choices=CHANNELS, hidden=True,
              help="Wireless channel hosted by the board."),
    )
    return Tool(
        "bielson-pallet-battle",
        "Bielson Battle Event (Pallet Town)",
        SCRIPT,
        "Challenge Bielson's 6-Pokemon Lv. 70 team in Pallet Town (FireRed & LeafGreen). "
        "Heals before and after, awards 1 Master Ball once per save, supports rematches, and "
        "restores any existing visiting trainer record.",
        steps,
        fields=fields,
        fixed=("--ot", "{ot}", "--id", "{tid}:{sid}"),
    )


def register(api):
    api.add_tool("frlg", tool())
