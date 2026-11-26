"""Gift builders for Static Legendary Respawn (FireRed, LeafGreen & Emerald).

FRLG uses ARMv4T console code (`buffer_code`) operating directly on SaveBlock1 (`r2`): it works on
all 12 Switch cartridges without overwriting the player's Wonder Card or saved boosts.
Emerald uses a portable Wonder Card + RAM script (`CLEARFLAG` / `SETFLAG` / `SETVAR`) delivered by
the Pokemon Center 2F delivery man, requiring zero ROM addresses.
"""
import struct

from pokeldn import gifts
from pokeldn.frlg.gift.stamp_rally import MysteryGiftDistribution
from pokeldn.frlg.gift.wonder_card import build_wonder_card
from pokeldn.frlg.rom import builds
from pokeldn.rse import gift_file as rse_gift_file
from pokeldn.rse.scripts import END, FACEPLAYER, LOCK, RELEASE, SETFLAG, SETVAR, Script

import gen3respawn_stubs as stubs

OP_CLEARFLAG = 0x2A

# FireRed / LeafGreen SaveBlock1 flags and vars (verified against pret/pokefirered)
FRLG_SPECS = {
    "mewtwo": {
        "label": "Mewtwo",
        "clear": (0x081, 0x2BC),  # FLAG_HIDE_MEWTWO, FLAG_FOUGHT_MEWTWO
        "set": (),
        "vars": (),
        "answer": 150,
    },
    "articuno": {
        "label": "Articuno",
        "clear": (0x082, 0x2BE),  # FLAG_HIDE_ARTICUNO, FLAG_FOUGHT_ARTICUNO
        "set": (),
        "vars": (),
        "answer": 144,
    },
    "zapdos": {
        "label": "Zapdos",
        "clear": (0x05D, 0x2BF),  # FLAG_HIDE_ZAPDOS, FLAG_FOUGHT_ZAPDOS
        "set": (),
        "vars": (),
        "answer": 145,
    },
    "moltres": {
        "label": "Moltres",
        "clear": (0x052, 0x2BD),  # FLAG_HIDE_MOLTRES, FLAG_FOUGHT_MOLTRES
        "set": (),
        "vars": (),
        "answer": 146,
    },
    "hooh": {
        "label": "Ho-Oh",
        "clear": (0x09C, 0x2F3, 0x2F6),  # HIDE_HO_OH, FOUGHT_HO_OH, HO_OH_FLEW_AWAY
        "set": (),
        "vars": (),
        "answer": 250,
    },
    "lugia": {
        "label": "Lugia",
        "clear": (0x09B, 0x2F2, 0x2F5),  # HIDE_LUGIA, FOUGHT_LUGIA, LUGIA_FLEW_AWAY
        "set": (),
        "vars": (),
        "answer": 249,
    },
    "deoxys": {
        "label": "Deoxys",
        "clear": (0x09A, 0x2E4, 0x2F7, 0x848),  # HIDE_METEORITE, FOUGHT, FLEW_AWAY, AWAKENED
        "set": (0x099,),                        # HIDE_DEOXYS (stays hidden until triangle solved)
        "vars": (0x4026, 0x403E),               # STEP_COUNTER, INTERACTION_NUM
        "answer": 386,
    },
    "snorlax": {
        "label": "Snorlax (Routes 12 & 16)",
        "clear": (0x054, 0x080, 0x253),         # HIDE_R12, HIDE_R16, WOKE_UP_R12
        "set": (),
        "vars": (),
        "answer": 143,
    },
}

FRLG_ALL_KEYS = ("articuno", "zapdos", "moltres", "mewtwo", "hooh", "lugia", "deoxys")

# Emerald SaveBlock1 flags and vars (verified against pret/pokeemerald)
# Card flag_id sits in [1000, 1020) and the delivery script does not gate repeat use on it.
EMERALD_CARD_FLAG_ID = 1018

EMERALD_SPECS = {
    "regirock": {
        "label": "Regirock",
        "icon": 401,  # GBA internal SPECIES_REGIROCK
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1BB, 0x3A7),  # FLAG_DEFEATED_REGIROCK, FLAG_HIDE_REGIROCK
        "set": (),
        "vars": (),
        "note": "Desert Ruins is ready.",
    },
    "regice": {
        "label": "Regice",
        "icon": 402,  # SPECIES_REGICE
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1BC, 0x3A8),  # FLAG_DEFEATED_REGICE, FLAG_HIDE_REGICE
        "set": (),
        "vars": (0x403B, 0x403C, 0x403D),  # VAR_REGICE_STEPS_1..3
        "note": "Island Cave is ready.",
    },
    "registeel": {
        "label": "Registeel",
        "icon": 403,  # SPECIES_REGISTEEL
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1BD, 0x3A9),  # FLAG_DEFEATED_REGISTEEL, FLAG_HIDE_REGISTEEL
        "set": (),
        "vars": (),
        "note": "Ancient Tomb is ready.",
    },
    "kyogre": {
        "label": "Kyogre",
        "icon": 404,  # SPECIES_KYOGRE
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1BE, 0x30E),  # FLAG_DEFEATED_KYOGRE, FLAG_HIDE_MARINE_CAVE_KYOGRE
        "set": (),
        "vars": (0x4037, 0x4038, 0x4039),  # abnormal weather vars
        "note": "Visit Weather Institute 2F.",
    },
    "groudon": {
        "label": "Groudon",
        "icon": 405,  # SPECIES_GROUDON
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1BF, 0x30F),  # FLAG_DEFEATED_GROUDON, FLAG_HIDE_TERRA_CAVE_GROUDON
        "set": (),
        "vars": (0x4037, 0x4038, 0x4039),  # abnormal weather vars
        "note": "Visit Weather Institute 2F.",
    },
    "rayquaza": {
        "label": "Rayquaza",
        "icon": 406,  # SPECIES_RAYQUAZA
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1C0, 0x050),  # FLAG_DEFEATED_RAYQUAZA, FLAG_HIDE_SKY_PILLAR_TOP_RAYQUAZA_STILL
        "set": (),
        "vars": (),
        "note": "Sky Pillar Top is ready.",
    },
    "lati": {
        "label": "Latias / Latios",
        "icon": 407,  # SPECIES_LATIAS
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1C8, 0x1C9, 0x0CE),  # DEFEATED, CAUGHT, ENCOUNTERED_LATIAS_OR_LATIOS
        "set": (),
        "vars": (),
        "note": "Southern Island is ready.",
    },
    "hooh": {
        "label": "Ho-Oh",
        "icon": 250,
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x092, 0x1DC, 0x321),  # CAUGHT_HO_OH, DEFEATED_HO_OH, HIDE_HO_OH
        "set": (),
        "vars": (),
        "note": "Navel Rock Top is ready.",
    },
    "lugia": {
        "label": "Lugia",
        "icon": 249,
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x091, 0x1DD, 0x320),  # CAUGHT_LUGIA, DEFEATED_LUGIA, HIDE_LUGIA
        "set": (),
        "vars": (),
        "note": "Navel Rock Bottom is ready.",
    },
    "deoxys": {
        "label": "Deoxys",
        "icon": 410,  # SPECIES_DEOXYS
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1AC, 0x1AD, 0x2FC, 0x8D4),  # DEFEATED, BATTLED, HIDE_TRIANGLE, ROCK_COMPLETE
        "set": (0x2FB,),                        # FLAG_HIDE_DEOXYS
        "vars": (0x4034, 0x4035),               # VAR_DEOXYS_ROCK_STEP_COUNT, VAR_DEOXYS_ROCK_LEVEL
        "note": "Birth Island puzzle reset.",
    },
    "mew": {
        "label": "Mew",
        "icon": 151,
        "flag_id": EMERALD_CARD_FLAG_ID,
        "clear": (0x1C7, 0x1CA, 0x2CE),         # DEFEATED_MEW, CAUGHT_MEW, HIDE_MEW
        "set": (),
        "vars": (0x403A,),                      # VAR_FARAWAY_ISLAND_STEP_COUNTER
        "note": "Faraway Island is ready.",
    },
}

EMERALD_ALL_KEYS = (
    "regirock", "regice", "registeel", "kyogre", "groudon", "rayquaza",
    "lati", "hooh", "lugia", "deoxys", "mew",
)


def frlg_spec(key: str) -> dict:
    if key == "all":
        clear, set_, vars_ = [], [], []
        for k in FRLG_ALL_KEYS:
            spec = FRLG_SPECS[k]
            clear.extend(spec["clear"])
            set_.extend(spec["set"])
            vars_.extend(spec["vars"])
        return {
            "label": "All FRLG Static Legendaries",
            "clear": tuple(dict.fromkeys(clear)),
            "set": tuple(dict.fromkeys(set_)),
            "vars": tuple(dict.fromkeys(vars_)),
            "answer": 0x5253504E,  # "RSPN"
        }
    if key not in FRLG_SPECS:
        raise ValueError(f"Unknown FRLG legendary {key!r}")
    return FRLG_SPECS[key]


def emerald_spec(key: str) -> dict:
    if key == "all":
        clear, set_, vars_ = [], [], []
        for k in EMERALD_ALL_KEYS:
            spec = EMERALD_SPECS[k]
            clear.extend(spec["clear"])
            set_.extend(spec["set"])
            vars_.extend(spec["vars"])
        return {
            "label": "All Static Legendaries",
            "icon": 406,  # Rayquaza
            "flag_id": EMERALD_CARD_FLAG_ID,
            "clear": tuple(dict.fromkeys(clear)),
            "set": tuple(dict.fromkeys(set_)),
            "vars": tuple(dict.fromkeys(vars_)),
            "note": "All static encounters reset.",
        }
    if key not in EMERALD_SPECS:
        raise ValueError(f"Unknown Emerald legendary {key!r}")
    return EMERALD_SPECS[key]


def build_frlg_code(cart_code: str, key: str) -> tuple[bytes, int]:
    """-> (ARMv4T buffer_code bytes, expected u32 answer) for one FRLG cartridge."""
    spec = frlg_spec(key)
    base = bytes.fromhex(stubs.FRLG_RESPAWN_ARM)
    code_word = int.from_bytes(cart_code.encode("ascii"), "little")
    table = bytearray(struct.pack(
        "<5I", code_word, len(spec["clear"]), len(spec["set"]), len(spec["vars"]), spec["answer"],
    ))
    for flag in spec["clear"]:
        table += struct.pack("<H", flag)
    for flag in spec["set"]:
        table += struct.pack("<H", flag)
    for var in spec["vars"]:
        table += struct.pack("<H", var)
    if len(table) % 4:
        table += b"\x00" * (4 - len(table) % 4)
    payload = base + bytes(table)
    if len(payload) > 1024:
        raise ValueError(f"respawn payload too large ({len(payload)} bytes)")
    return payload, spec["answer"]


def build_frlg_gift(key: str, *, version: str = "any") -> gifts.Gift:
    """-> .pokegift covering all 12 FRLG Switch cartridges (or only firered/leafgreen)."""
    spec = frlg_spec(key)
    variants = {}
    for code, build in builds.BUILDS.items():
        if version in ("firered", "leafgreen") and build.version != version:
            continue
        payload, expect = build_frlg_code(code, key)
        variants[code] = gifts.Variant({"buffer_code": payload}, {"buffer_expect": expect})
    return gifts.Gift("frlg", f"Respawn {spec['label']}", variants)


def build_emerald_script(key: str) -> bytes:
    """-> portable Emerald RAM script bytes resetting the chosen legendary's flags and vars."""
    spec = emerald_spec(key)
    s = Script()
    s.op(LOCK)
    s.op(FACEPLAYER)
    for flag in spec["clear"]:
        s.op(OP_CLEARFLAG, flag)
    for flag in spec["set"]:
        s.op(SETFLAG, flag)
    for var in spec["vars"]:
        s.op(SETVAR, var, 0)
    s.vmessage(f"{spec['label']} respawned!\n{spec['note']}\fSave your game before\nre-entering the map.")
    s.op(RELEASE)
    s.op(END)
    return s.assemble()


def build_emerald_gift(key: str) -> gifts.Gift:
    """-> portable Emerald Wonder Card .pokegift (works on every Emerald build + Emerald Swap)."""
    spec = emerald_spec(key)
    script = build_emerald_script(key)
    card = build_wonder_card(
        flag_id=spec["flag_id"],
        icon_species=spec["icon"],
        title=f"RESPAWN {spec['label'].upper()}"[:32],
        subtitle="MYSTERY GIFT",
        body=(f"Resets {spec['label']}.", spec["note"]),
        footer1="Talk to the delivery man on",
        footer2="2F of a POKéMON CENTER.",
    )
    dist = MysteryGiftDistribution(card, script, game="emerald")
    return rse_gift_file.from_distribution(dist, name=f"Emerald Respawn: {spec['label']}")
