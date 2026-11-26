"""Builder for Bielson Pallet Town 6v6 Lv.70 Battle Event (FireRed & LeafGreen: BPRE, BPGE, BPRF, BPGF)."""
import struct

from pokeldn import gifts
from pokeldn.frlg.gift.ereader_trainer import TrainerMon, VisitingTrainer, personality_for
from pokeldn.frlg.rom import buffer_script as bs, builds, native_script, special_names
from pokeldn.frlg.text import charmap

import bielson_stubs as stubs

BASE = 0x0203FC00
CODE_ADDR = BASE + 16
SCRIPT_ADDR = BASE + 320
DATA_ADDR = BASE + 692
BACKUP_ADDR = BASE + 1008

MAGIC = 0x4C454942    # "BIEL" little-endian
SUCCESS = 0x4249454C  # "BIEL" big-endian status
STATE_VAR = 0x40FE
PENDING = 0xB101
CLAIMED = 0xB102

W = lambda n: struct.pack("<I", n & 0xFFFFFFFF)
H = lambda n: struct.pack("<H", n & 0xFFFF)

# Verified ROM function tables for English & French Switch builds (rev 0x0A).
# LeafGreen shares FireRed's addresses below 0x0807CF68; StartSpecialBattle sits in the -0x28 segment.
BUILD_FUNCTIONS = {
    "BPRE": {
        "StartSpecialBattle": 0x080EA021,
        "CreateBattleTowerMon": 0x0804184D,
        "GetObjectEventIdByLocalIdAndMap": 0x08061705,
        "ObjectEventSetGraphicsId": 0x08062805,
        "ClearRamScript": 0x0806D461,
    },
    "BPGE": {
        "StartSpecialBattle": 0x080E9FF9,
        "CreateBattleTowerMon": 0x0804184D,
        "GetObjectEventIdByLocalIdAndMap": 0x08061705,
        "ObjectEventSetGraphicsId": 0x08062805,
        "ClearRamScript": 0x0806D461,
    },
    "BPRF": {
        "StartSpecialBattle": 0x080EA401,
        "CreateBattleTowerMon": 0x080417A1,
        "GetObjectEventIdByLocalIdAndMap": 0x08061861,
        "ObjectEventSetGraphicsId": 0x08062961,
        "ClearRamScript": 0x0806D5C5,
    },
    "BPGF": {
        "StartSpecialBattle": 0x080EA3D9,
        "CreateBattleTowerMon": 0x080417A1,
        "GetObjectEventIdByLocalIdAndMap": 0x08061861,
        "ObjectEventSetGraphicsId": 0x08062961,
        "ClearRamScript": 0x0806D5C5,
    },
}

SUPPORTED_CODES = tuple(BUILD_FUNCTIONS)

# Gen 3 legal Lv. 70 competitive 6-Pokemon roster (Typhlosion has Hidden Power Grass 70 IVs).
# (nickname, gba_species, nature, item_id, moves, evs_hp_atk_def_spe_spa_spd, ivs)
TEAM_SPEC = (
    ("TYPHLOSION", 157, "timid", 215, (126, 53, 9, 237), (4, 0, 0, 252, 252, 0), (31, 30, 31, 31, 30, 31)),
    ("SWELLOW", 305, "adamant", 186, (38, 332, 98, 211), (4, 252, 0, 252, 0, 0), 31),
    ("JIRACHI", 409, "timid", 200, (347, 94, 85, 8), (4, 0, 0, 252, 252, 0), 31),
    ("AIPOM", 190, "jolly", 217, (332, 38, 247, 280), (4, 252, 0, 252, 0, 0), 31),
    ("LAPRAS", 131, "modest", 200, (57, 58, 85, 109), (252, 0, 0, 4, 252, 0), 31),
    ("GENGAR", 94, "timid", 141, (85, 8, 7, 202), (4, 0, 0, 252, 252, 0), 31),
)

DIALOGUES = {
    "en": {
        "intro": "BIELSON: I am Bielson!\n6-on-6 battle, Level 70?",
        "lost": "BIELSON: Great battle!\nYour team is healed. Try again!",
        "won_again": "BIELSON: You won again!\nThe prize was already given.",
        "fail": ("Event unavailable.", "Restart without boosts."),
    },
    "pt": {
        "intro": "BIELSON: Sou o Bielson!\nBatalha 6 contra 6, nivel 70?",
        "lost": "BIELSON: Boa batalha!\nSeu time esta curado. Tente de novo!",
        "won_again": "BIELSON: Voce venceu!\nO premio ja foi entregue.",
        "fail": ("Evento indisponivel.", "Reinicie sem boosts."),
    },
}


def build_team() -> tuple[tuple[TrainerMon, ...], bytes]:
    mons = tuple(
        TrainerMon(
            species=species,
            nickname=nick,
            level=70,
            moves=moves,
            held_item=item,
            evs=evs,
            ivs=ivs,
            personality=personality_for(nature, ot_id=0xB1E15001),
            ot_id=0xB1E15001,
            pp_bonuses=255,
        )
        for nick, species, nature, item, moves, evs, ivs in TEAM_SPEC
    )
    visitor = VisitingTrainer(
        name="BIEL",
        trainer_class="red",
        party=mons[:3],
        greeting=("hello",),
        farewell_player_won=("wow",),
        farewell_player_lost=("hello",),
        trainer_id=0xB1E15001,
    ).pack()
    event_data = visitor[:52] + b"".join(m.pack() for m in mons)
    return mons, event_data


class _FieldScript:
    def __init__(self, base: int):
        self.base = base
        self.data = bytearray()
        self.labels: dict[str, int] = {}
        self.refs: list[tuple[int, str]] = []

    def label(self, name: str):
        self.labels[name] = self.base + len(self.data)

    def emit(self, raw: bytes):
        self.data += raw

    def ptr(self, name: str):
        self.refs.append((len(self.data), name))
        self.emit(bytes(4))

    def go(self, name: str):
        self.emit(b"\x05")
        self.ptr(name)

    def branch(self, cond: int, name: str):
        self.emit(bytes((6, cond)))
        self.ptr(name)

    def compare(self, var: int, val: int):
        self.emit(b"\x21" + H(var) + H(val))

    def setvar(self, var: int, val: int):
        self.emit(b"\x16" + H(var) + H(val))

    def msg(self, name: str, kind: int = 4):
        self.emit(b"\x0F\x00")
        self.ptr(name)
        self.emit(bytes((9, kind)))

    def native(self, addr: int):
        self.emit(b"\x23" + W(addr | 1))

    def special(self, name: str):
        self.emit(b"\x25" + H(special_names.index(name)))

    def resolve(self) -> bytes:
        for at, name in self.refs:
            self.data[at:at + 4] = W(self.labels[name])
        return bytes(self.data)


def _patch_u32(buf: bytearray, offset: int, value: int) -> None:
    buf[offset:offset + 4] = W(value)


def build_event_blob(cart_code: str, *, dialogue: str = "en") -> tuple[bytes, dict]:
    if cart_code not in BUILD_FUNCTIONS:
        raise ValueError(f"Unsupported cartridge {cart_code!r}; supported: {', '.join(SUPPORTED_CODES)}")
    if dialogue not in DIALOGUES:
        raise ValueError(f"Unknown dialogue {dialogue!r}")

    build = builds.BUILDS[cart_code]
    funcs = BUILD_FUNCTIONS[cart_code]
    text = DIALOGUES[dialogue]
    _mons, event_data = build_team()

    einfo = stubs.EVENT_CODE
    eoff = einfo["offsets"]
    code = bytearray(bytes.fromhex(einfo["hex"]))
    _patch_u32(code, eoff["getobj"], funcs["GetObjectEventIdByLocalIdAndMap"])
    _patch_u32(code, eoff["objects"], 0x02036E34)
    _patch_u32(code, eoff["setgfx"], funcs["ObjectEventSetGraphicsId"])
    _patch_u32(code, eoff["sb2ptr"], build.sb2ptr)
    _patch_u32(code, eoff["var8004"], 0x020370BC)
    _patch_u32(code, eoff["startbattle"], funcs["StartSpecialBattle"])
    _patch_u32(code, eoff["party"], 0x02024028)
    _patch_u32(code, eoff["makemon"], funcs["CreateBattleTowerMon"])

    look = CODE_ADDR + einfo["entries"]["look"]
    start = CODE_ADDR + einfo["entries"]["start"]
    restore = CODE_ADDR + einfo["entries"]["restore"]

    s = _FieldScript(SCRIPT_ADDR)
    s.native(look)
    s.compare(STATE_VAR, PENDING)
    s.branch(1, "reward")
    s.msg("intro", 5)
    s.compare(0x800D, 0)
    s.branch(1, "exit")
    s.emit(b"\x68")
    s.special("HealPlayerParty")
    s.native(start)
    s.emit(b"\x27")
    s.native(restore)
    s.special("HealPlayerParty")
    s.emit(b"\x26" + H(0x800D) + H(special_names.index("GetBattleOutcome")))
    s.compare(0x800D, 1)
    s.branch(5, "loss")
    s.compare(STATE_VAR, CLAIMED)
    s.branch(1, "again")
    s.setvar(STATE_VAR, PENDING)
    s.label("reward")
    s.setvar(0x8000, 1)
    s.setvar(0x8001, 1)
    s.emit(b"\x09\x00")
    s.compare(0x800D, 0)
    s.branch(1, "exit")
    s.setvar(STATE_VAR, CLAIMED)
    s.go("exit")
    s.label("loss")
    s.msg("lost")
    s.go("exit")
    s.label("again")
    s.msg("won_again")
    s.label("exit")
    s.emit(b"\x6C\x02")

    for key in ("intro", "lost", "won_again"):
        s.label(key)
        s.emit(b"\xFE".join(charmap.encode(line) for line in text[key].split("\n")) + b"\xFF")

    field = s.resolve()
    assert len(code) <= SCRIPT_ADDR - CODE_ADDR
    assert len(field) <= DATA_ADDR - SCRIPT_ADDR, (len(field), DATA_ADDR - SCRIPT_ADDR)
    assert DATA_ADDR + len(event_data) <= BACKUP_ADDR

    blob = bytearray(1024)
    blob[:16] = struct.pack("<4I", MAGIC, 1024, SCRIPT_ADDR, 0)
    blob[16:16 + len(code)] = code
    blob[SCRIPT_ADDR - BASE:SCRIPT_ADDR - BASE + len(field)] = field
    blob[DATA_ADDR - BASE:DATA_ADDR - BASE + len(event_data)] = event_data
    checksum = (-sum(struct.unpack("<256I", blob))) & 0xFFFFFFFF
    blob[12:16] = W(checksum)

    meta = {
        "look": look,
        "start": start,
        "restore": restore,
        "script": SCRIPT_ADDR,
        "data": DATA_ADDR,
        "backup": BACKUP_ADDR,
        "code_len": len(code),
        "field_len": len(field),
        "event_data": event_data,
    }
    return bytes(blob), meta


def build_install_payloads(cart_code: str, *, dialogue: str = "en") -> tuple[dict[str, bytes], dict]:
    build = builds.BUILDS[cart_code]
    blob, meta = build_event_blob(cart_code, dialogue=dialogue)

    linfo = stubs.LOADER_CODE
    loff = linfo["offsets"]
    loader = bytearray(bytes.fromhex(linfo["hex"]))
    _patch_u32(loader, loff["result"], 0x020370CC)
    _patch_u32(loader, loff["intr"], build.intr_vblank)
    _patch_u32(loader, loff["original"], build.vblank_intr | 1)
    _patch_u32(loader, loff["sb2ptr"], build.sb2ptr)
    loader_bytes = bytes(loader)

    fail_lines = DIALOGUES[dialogue]["fail"]
    ram = (
        b"\xB8" + W(0x08000000) + b"\x6A\x5A"
        + native_script.stage(loader_bytes, address=0x0201C000)
        + native_script.callnative_at(0x0201C000)
        + b"\x21" + H(0x800D) + H(1) + bytes((6, 1)) + W(SCRIPT_ADDR)
    )
    failure_at = len(ram) + 5 + 5
    ram += (
        b"\xBD" + W(0x08000000 + failure_at) + b"\x66\x6D\x68\x6C\x02"
        + charmap.encode(fail_lines[0]) + b"\xFE" + charmap.encode(fail_lines[1]) + b"\xFF"
    )
    assert len(ram) <= 995, len(ram)

    iinfo = stubs.INSTALLER_CODE
    ioff = iinfo["offsets"]
    inst = bytearray(bytes.fromhex(iinfo["hex"]))
    code_word = int.from_bytes(cart_code.encode("ascii"), "little")
    _patch_u32(inst, ioff["cart_code"], code_word)
    _patch_u32(inst, ioff["initram"], build.callable_function("InitRamScript"))
    _patch_u32(inst, ioff["script_size"], len(ram))

    code = bytes(inst) + ram
    if len(code) % 4:
        code += bytes(4 - len(code) % 4)
    assert len(code) <= 1024, len(code)

    lead1 = bs.build_save_write(blob[:900], block="sav2", offset=0xB20)
    lead2 = bs.build_save_write(blob[900:], block="sav2", offset=0xB20 + 900)
    meta.update(blob=blob, loader=loader_bytes, ram_script=ram)
    return {"buffer_lead_1": lead1, "buffer_lead_2": lead2, "buffer_code": code}, meta


def build_remove_payload(cart_code: str) -> bytes:
    if cart_code not in BUILD_FUNCTIONS:
        raise ValueError(f"Unsupported cartridge {cart_code!r}")
    rinfo = stubs.REMOVER_CODE
    roff = rinfo["offsets"]
    rem = bytearray(bytes.fromhex(rinfo["hex"]))
    code_word = int.from_bytes(cart_code.encode("ascii"), "little")
    _patch_u32(rem, roff["cart_code"], code_word)
    _patch_u32(rem, roff["clear_func"], BUILD_FUNCTIONS[cart_code]["ClearRamScript"])
    return bytes(rem)


def build_install_gift(*, dialogue: str = "en", version: str = "any") -> gifts.Gift:
    variants = {}
    for code in SUPPORTED_CODES:
        if version in ("firered", "leafgreen") and builds.BUILDS[code].version != version:
            continue
        data, _ = build_install_payloads(code, dialogue=dialogue)
        variants[code] = gifts.Variant(data, {"buffer_expect": SUCCESS})
    return gifts.Gift("frlg", "Bielson - Pallet Town 6v6 Lv.70", variants)


def build_remove_gift(*, version: str = "any") -> gifts.Gift:
    variants = {}
    for code in SUPPORTED_CODES:
        if version in ("firered", "leafgreen") and builds.BUILDS[code].version != version:
            continue
        variants[code] = gifts.Variant(
            {"buffer_code": build_remove_payload(code)},
            {"buffer_expect": SUCCESS},
        )
    return gifts.Gift("frlg", "Remove Bielson Pallet Town Event", variants)
