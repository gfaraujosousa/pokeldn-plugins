"""Builders for Gen 3 QoL Pack (all 12 FRLG Switch builds + Emerald / Emerald Swap)."""
import struct

from pokeldn import gifts
from pokeldn.frlg.gift.stamp_rally import MysteryGiftDistribution
from pokeldn.frlg.gift.wonder_card import build_wonder_card
from pokeldn.frlg.rom import buffer_script as bs, builds, native_script as ns, special_names
from pokeldn.frlg.rom.resident_stubs import STUBS as RESIDENT_STUBS

import gen3qol_stubs as stubs

BASE = 0x0203FC00
SUCCESS_QOL8 = 0x514F4C38  # "QOL8"
REFUSED = 0xBAD0BAD0
BUDGET = 228
FRAMES_ADDR = 0x0203FF80
KEPT_STATUS_SCRATCH = 0x0203FBB4


def _patch_u32(buf: bytearray, offset: int, value: int) -> None:
    buf[offset:offset + 4] = struct.pack("<I", value & 0xFFFFFFFF)


def build_frlg_turbo_hook(build: builds.Build, *, speed: int = 8) -> tuple[bytes, bytes, dict]:
    """-> (resident hook blob, saved PKR2 blob for SaveBlock2+0xB20, metadata) for one FRLG build."""
    extra_passes = max(1, min(7, int(speed) - 1))
    tinfo = stubs.FRLG_TOGGLE
    toff = tinfo["offsets"]
    wrapper = bytearray(bytes.fromhex(tinfo["hex"]))
    n = len(wrapper)

    help_addr = build.ewram.get("help", bs.HELP_R_DISABLED)
    turbo, entry, orig = bs.resident_blob(
        "turbo-lite",
        build=build,
        field=0,
        battle=0,
        extra=0,
        hold=0,
        help=help_addr,
        budget=BUDGET,
        frames=FRAMES_ADDR,
    )
    sym = RESIDENT_STUBS["turbo-lite"][2]
    _patch_u32(wrapper, toff["gmain"], build.gmain)
    _patch_u32(wrapper, toff["field"], BASE + n + sym["p_field"])
    _patch_u32(wrapper, toff["battle"], BASE + n + sym["p_battle"])
    _patch_u32(wrapper, toff["entry"], BASE + n + entry + 1)
    _patch_u32(wrapper, toff["extra_passes"], extra_passes)

    blob = bytes(wrapper) + turbo
    assert len(blob) % 4 == 0 and BASE + len(blob) < FRAMES_ADDR, (len(blob), hex(BASE + len(blob)))
    head = struct.pack("<IIIHH", bs.RESIDENT_SAVE_MAGIC, len(blob), BASE, 0, n + orig)
    saved = head + blob
    checksum = sum(struct.unpack("<" + "I" * (len(saved) // 4), saved)) & 0xFFFFFFFF
    saved += struct.pack("<I", checksum)
    meta = {
        "wrapper_size": n,
        "hook_size": len(blob),
        "state": BASE + toff["state"],
        "field_literal": BASE + n + sym["p_field"],
        "battle_literal": BASE + n + sym["p_battle"],
        "original_literal": BASE + n + orig,
        "help_addr": help_addr,
        "entry": BASE,
        "extra_passes": extra_passes,
        "budget": BUDGET,
    }
    return blob, saved, meta


def build_frlg_mom_script(build: builds.Build) -> tuple[bytes, bytes]:
    """-> (Mom RAM script bytes, non-mutating install-kept ARM+Thumb blob) for one FRLG build.
    Redirects install-kept's Thumb status output to free EWRAM so the checksummed RAM script body
    is never modified at runtime."""
    kept = bytearray(bs.build_install_kept(build=build))
    adr = int.from_bytes(kept[8:10], "little")
    assert (adr & 0xF800) == 0xA000, hex(adr)
    scratch = 12 + (adr & 0xFF) * 4
    assert kept[scratch:scratch + 4] == bytes(4)
    kept[8:10] = struct.pack("<H", 0x4800 | (adr & 0xFF))
    kept[scratch:scratch + 4] = struct.pack("<I", KEPT_STATUS_SCRATCH)
    kept_bytes = bytes(kept)

    tail = (
        b"\x25" + struct.pack("<H", special_names.index("HealPlayerParty"))
        + b"\x2F" + struct.pack("<H", ns.SE_SUCCESS)
        + b"\x30\x02"
    )
    ram = ns.build_body_script(kept_bytes[bs.INSTALL_KEPT_THUMB_ENTRY:], tail, build=build)
    return ram, kept_bytes


def build_frlg_payloads(
    build: builds.Build,
    *,
    turbo: bool = True,
    speed: int = 8,
    rare_candy: bool = True,
    mom_restore: bool = True,
) -> tuple[dict[str, bytes], dict]:
    """-> (gift data dict with buffer_code / optional buffer_lead_1, metadata) for one FRLG build."""
    if not turbo and not rare_candy:
        raise ValueError("Enable at least one option: R-toggle turbo or Key-Item Rare Candy.")

    code_word = int.from_bytes(build.game_code.encode("ascii"), "little")
    pinfo = stubs.FRLG_PREPARE
    poff = pinfo["offsets"]

    if not turbo:
        # Rare Candy only: single buffer_code stage (no saved hook, no Mom script)
        prep = bytearray(bytes.fromhex(pinfo["hex"]))
        _patch_u32(prep, poff["cart_code"], code_word)
        _patch_u32(prep, poff["give_candy"], 1)
        _patch_u32(prep, poff["saved_size"], 0)
        return {"buffer_code": bytes(prep)}, {"mode": "candy-only"}

    blob, saved, meta = build_frlg_turbo_hook(build, speed=speed)
    prep = bytearray(bytes.fromhex(pinfo["hex"]))
    _patch_u32(prep, poff["cart_code"], code_word)
    _patch_u32(prep, poff["give_candy"], 1 if rare_candy else 0)
    _patch_u32(prep, poff["saved_size"], len(saved))
    prep_code = bytes(prep) + saved
    assert len(prep_code) <= 1024, len(prep_code)

    ram, kept = build_frlg_mom_script(build)
    finfo = stubs.FRLG_FINISH
    foff = finfo["offsets"]
    fin = bytearray(bytes.fromhex(finfo["hex"]))
    _patch_u32(fin, foff["cart_code"], code_word)
    _patch_u32(fin, foff["check_candy"], 1 if rare_candy else 0)
    _patch_u32(fin, foff["bind_mom"], 1 if mom_restore else 0)
    _patch_u32(fin, foff["ram_offset"], len(kept))
    _patch_u32(fin, foff["ram_size"], len(ram) if mom_restore else 0)
    _patch_u32(fin, foff["initram"], build.callable_function("InitRamScript"))

    final_code = bytes(fin) + kept + (ram if mom_restore else b"")
    if len(final_code) % 4:
        final_code += b"\x00" * (4 - len(final_code) % 4)
    assert len(final_code) <= 1024, len(final_code)

    meta.update({
        "mode": "full" if (turbo and rare_candy) else "turbo-only",
        "mom_restore": mom_restore,
        "ram_script": ram,
        "kept_code": kept,
        "saved_blob": saved,
        "hook_blob": blob,
    })
    return {"buffer_lead_1": prep_code, "buffer_code": final_code}, meta


def build_frlg_gift(
    *,
    version: str = "any",
    turbo: bool = True,
    speed: int = 8,
    rare_candy: bool = True,
    mom_restore: bool = True,
) -> gifts.Gift:
    parts = []
    if turbo:
        parts.append(f"R {speed}x")
    if rare_candy:
        parts.append("Key Rare Candy")
    if turbo and mom_restore:
        parts.append("Mom Restore")
    name = "FRLG QoL: " + " + ".join(parts)

    variants = {}
    for code, build in builds.BUILDS.items():
        if version in ("firered", "leafgreen") and build.version != version:
            continue
        data, _ = build_frlg_payloads(
            build, turbo=turbo, speed=speed, rare_candy=rare_candy, mom_restore=mom_restore,
        )
        variants[code] = gifts.Variant(data, {"buffer_expect": SUCCESS_QOL8})
    return gifts.Gift("frlg", name, variants)


# Verified Emerald Swap (pokeemerald_switch, all 10 Latin carts) addresses below 0x081E0000.
EMERALD_SWAP = {
    "gmain": 0x030023C0,
    "intr_check": 0x030023DC,
    "vblank_intr": 0x08000730,
    "cb1_overworld": 0x0808644C,
    "cb2_overworld": 0x080864A4,
    "battle_cb1": 0x0803A528,
    "battle_cb2": 0x08038A58,
    "palette_fade": 0x02037FD4,
    "run_text": 0x08004770,
    "printers": 0x020201B0,
    # Signature literals inside CB2_Overworld / overworld.o verified by installer before writing RAM
    "sig_pal_at": 0x080864CC,
    "sig_gmain_at": 0x080864D8,
    # Verified InitRamScript, SaveWonderCard & SaveBlock1 pointer across all 10 Emerald Swap builds
    "sb1ptr": 0x03005EAC,
    "initram": 0x08099744,
    "initram_sb1_at": 0x080997A8,
    "ram_script_magic_off": 0x372C,
    "save_wonder_card": 0x0801B6EC,
    "save_wc_sb1_at": 0x0801B738,
    "save_wc_card_off": 0x000033F0,
    "ram_jump_scratch": 0x0203FB80,
    "heal_special": 0,  # gSpecials[0] = HealPlayerParty
}


def build_emerald_wonder_card(*, speed: int = 8) -> bytes:
    """-> 332-byte Wonder Card so the Delivery Man spawns on 2F of every Pokemon Center."""
    card = build_wonder_card(
        flag_id=1008,
        icon_species=25,
        title="QOL PACK",
        subtitle=f"R-TOGGLE {int(speed)}X TURBO",
        body=(
            "Talk to the delivery man on 2F",
            "of any POKéMON CENTER to restore",
            "R-toggle fast-forward after reset.",
        ),
        footer1="Tap R to toggle turbo ON/OFF.",
        footer2="Reusable anytime after soft reset.",
    )
    assert len(card) == 332, len(card)
    return card


def build_emerald_turbo_hook(*, speed: int = 8) -> tuple[bytes, dict]:
    """-> (R-toggle wrapper + pokeldn turbo-lite bytes, metadata) for Emerald Swap."""
    extra_passes = max(1, min(7, int(speed) - 1))
    tinfo = stubs.FRLG_TOGGLE
    toff = tinfo["offsets"]
    wrapper = bytearray(bytes.fromhex(tinfo["hex"]))
    n = len(wrapper)

    em = EMERALD_SWAP
    turbo_raw, _digest, sym = RESIDENT_STUBS["turbo-lite"]
    turbo = bytearray(turbo_raw)
    literals = {
        "original": em["vblank_intr"] | 1,
        "intr_check": em["intr_check"],
        "run_text": em["run_text"] | 1,
        "extra": 0,
        "frames": FRAMES_ADDR,
        "printers": em["printers"],
        "field": 0,
        "battle": 0,
        "gmain": em["gmain"],
        "cb1_overworld": em["cb1_overworld"] | 1,
        "cb2_overworld": em["cb2_overworld"] | 1,
        "cb1_battle": em["battle_cb1"] | 1,
        "cb2_battle": em["battle_cb2"] | 1,
        "palette_fade": em["palette_fade"],
        "hold": 0,
        "help": 0,  # Emerald has no Help System
        "budget": BUDGET,
    }
    for key, value in literals.items():
        _patch_u32(turbo, sym[f"p_{key}"], value)

    entry = sym["turbo_hook"]
    orig = sym["p_original"]
    _patch_u32(wrapper, toff["gmain"], em["gmain"])
    _patch_u32(wrapper, toff["field"], BASE + n + sym["p_field"])
    _patch_u32(wrapper, toff["battle"], BASE + n + sym["p_battle"])
    _patch_u32(wrapper, toff["entry"], BASE + n + entry + 1)
    _patch_u32(wrapper, toff["extra_passes"], extra_passes)

    blob = bytes(wrapper) + bytes(turbo)
    assert len(blob) % 4 == 0 and BASE + len(blob) < FRAMES_ADDR
    meta = {
        "base": BASE,
        "extra_passes": extra_passes,
        "state": BASE + toff["state"],
        "field_literal": BASE + n + sym["p_field"],
        "battle_literal": BASE + n + sym["p_battle"],
        "original_literal": BASE + n + orig,
        "hook_size": len(blob),
    }
    return blob, meta


def build_emerald_mom_assets(hook_len: int) -> tuple[bytes, dict]:
    """-> (packed ram_assets for EMERALD_TURBO_INSTALLER, metadata).
    Layout:
      [0..35]   36-byte ram-jump trampoline targeting SaveBlock1.ramScript.data.script + 232
      [36..49]  14-byte callnative + HealPlayerParty + playse SE_SUCCESS + waitse + release + end
      [50..51]  2-byte alignment pad (skipped by installer before word-copying restore stub)
      [52..]    EMERALD_MOM_RESTORE Thumb stub (p_intr_vblank patched at install time)
    """
    em = EMERALD_SWAP
    prologue_size = 2  # lock (0x6A), faceplayer (0x5A) emitted before setptr loop
    tail = (
        ns.callnative_at(em["ram_jump_scratch"], thumb=True)
        + b"\x25" + struct.pack("<H", em["heal_special"])
        + b"\x2F" + struct.pack("<H", ns.SE_SUCCESS)
        + b"\x30\x6C\x02"  # waitse, release, end
    )
    assert len(tail) == 14
    prefix_size = prologue_size + 36 * ns.SETPTR_SIZE + len(tail)
    assert prefix_size == 232 and prefix_size % 4 == 0
    tail_padded = tail + b"\x00\x00"

    ram_jump = ns.stub(
        ns.TRAMPOLINE_STUB,
        sb1ptr=em["sb1ptr"],
        magic=em["ram_script_magic_off"],
        entry=(4 + prefix_size) | 1,
    )
    assert len(ram_jump) == 36

    minfo = stubs.EMERALD_MOM_RESTORE
    moff = minfo["offsets"]
    mom_stub = bytearray(bytes.fromhex(minfo["hex"]))
    _patch_u32(mom_stub, moff["blob_len"], hook_len)
    _patch_u32(mom_stub, moff["intr_vblank"], 0)

    ram_total = prefix_size + len(mom_stub) + hook_len
    assert ram_total <= ns.MAX_RAM_SCRIPT_SIZE, (ram_total, ns.MAX_RAM_SCRIPT_SIZE)
    assets = ram_jump + tail_padded + bytes(mom_stub)
    assert len(assets) % 4 == 0
    return assets, {
        "ram_jump": ram_jump,
        "tail": tail,
        "mom_stub_size": len(mom_stub),
        "mom_intr_off": moff["intr_vblank"],
        "prefix_size": prefix_size,
        "ram_script_size": ram_total,
    }


def build_emerald_payloads(
    *,
    turbo: bool = True,
    speed: int = 8,
    rare_candy: bool = True,
    mom_restore: bool = True,
) -> tuple[dict[str, bytes], dict]:
    """-> (gift data dict, metadata) for Emerald (including Emerald Swap)."""
    if not turbo and not rare_candy:
        raise ValueError("Enable at least one option: R-toggle turbo or Key-Item Rare Candy.")

    candy_code = bytes.fromhex(stubs.EMERALD_CANDY_ARM)
    if not turbo:
        return {"buffer_code": candy_code}, {"mode": "candy-only"}

    em = EMERALD_SWAP
    hook, meta = build_emerald_turbo_hook(speed=speed)

    pinfo = stubs.EMERALD_PREPARE
    poff = pinfo["offsets"]
    prep = bytearray(bytes.fromhex(pinfo["hex"]))
    _patch_u32(prep, poff["give_candy"], 1 if rare_candy else 0)
    _patch_u32(prep, poff["stage_len"], len(hook))
    prep_code = bytes(prep) + hook
    assert len(prep_code) <= 1024, len(prep_code)

    card_code = None
    card_bytes = None
    if mom_restore:
        card_bytes = build_emerald_wonder_card(speed=speed)
        cinfo = stubs.EMERALD_SAVE_CARD
        coff = cinfo["offsets"]
        save_c = bytearray(bytes.fromhex(cinfo["hex"]))
        _patch_u32(save_c, coff["save_wc"], em["save_wonder_card"] | 1)
        _patch_u32(save_c, coff["save_wc_sb1_at"], em["save_wc_sb1_at"])
        _patch_u32(save_c, coff["sb1ptr_exp"], em["sb1ptr"])
        _patch_u32(save_c, coff["card_off_exp"], em["save_wc_card_off"])
        card_code = bytes(save_c) + card_bytes
        assert len(card_code) <= 1024, len(card_code)

    ram_assets, ram_meta = build_emerald_mom_assets(len(hook))
    iinfo = stubs.EMERALD_TURBO_INSTALLER
    ioff = iinfo["offsets"]
    inst = bytearray(bytes.fromhex(iinfo["hex"]))
    _patch_u32(inst, ioff["blob_len"], len(hook))
    _patch_u32(inst, ioff["vbl_exp"], em["vblank_intr"] | 1)
    _patch_u32(inst, ioff["pal_at"], em["sig_pal_at"])
    _patch_u32(inst, ioff["pal_val"], em["palette_fade"])
    _patch_u32(inst, ioff["gmain_at"], em["sig_gmain_at"])
    _patch_u32(inst, ioff["gmain_val"], em["gmain"])
    _patch_u32(inst, ioff["check_candy"], 1 if rare_candy else 0)
    _patch_u32(inst, ioff["bind_mom"], 1 if mom_restore else 0)
    _patch_u32(inst, ioff["initram"], em["initram"] | 1)
    _patch_u32(inst, ioff["initram_sb1_at"], em["initram_sb1_at"])
    _patch_u32(inst, ioff["sb1ptr_exp"], em["sb1ptr"])
    _patch_u32(inst, ioff["mom_size"], ram_meta["mom_stub_size"])
    _patch_u32(inst, ioff["mom_intr_off"], ram_meta["mom_intr_off"])
    turbo_code = bytes(inst) + (ram_assets if mom_restore else b"")
    assert len(turbo_code) <= 1024, len(turbo_code)

    meta.update({
        "mode": "full" if (turbo and rare_candy) else "turbo-only",
        "mom_restore": mom_restore,
        "hook_blob": hook,
        "wonder_card": card_bytes,
        **ram_meta,
    })
    if card_code is not None:
        return {"buffer_lead_1": prep_code, "buffer_lead_2": card_code, "buffer_code": turbo_code}, meta
    return {"buffer_lead_1": prep_code, "buffer_code": turbo_code}, meta


def build_emerald_gift(
    *,
    turbo: bool = True,
    speed: int = 8,
    rare_candy: bool = True,
    mom_restore: bool = True,
) -> gifts.Gift:
    parts = []
    if turbo:
        parts.append(f"R {speed}x")
    if rare_candy:
        parts.append("Key Rare Candy")
    if turbo and mom_restore:
        parts.append("Delivery Man Restore")
    data, _ = build_emerald_payloads(
        turbo=turbo, speed=speed, rare_candy=rare_candy, mom_restore=mom_restore,
    )
    return gifts.Gift(
        "rse",
        "Emerald QoL: " + " + ".join(parts),
        {"emerald": gifts.Variant(data, {"buffer_expect": SUCCESS_QOL8})},
    )


def install_emerald_buffer_code_support() -> None:
    """Extends pokeldn.rse.gift_file & EmeraldPayload in this child process so bin/frlg_mg_host.py
    serves Emerald buffer_code gifts (CLI_RUN_BUFFER_SCRIPT) with BufferScriptHostApplication."""
    from pokeldn.frlg.gift import file as frlg_file
    from pokeldn.rse import gift_file as rse_file, gifts as rse_gifts

    orig_dist = rse_file.distribution

    def _distribution(variant):
        if "buffer_code" not in variant.data:
            return orig_dist(variant)
        d = frlg_file.distribution(variant)
        return MysteryGiftDistribution(
            card=None,
            ram_script=None,
            buffer_code=d.buffer_code,
            buffer_lead=d.buffer_lead,
            buffer_expect=d.buffer_expect,
            game=rse_file.TARGET,
        )

    rse_file.distribution = _distribution

    if not hasattr(rse_gifts.EmeraldPayload, "script"):
        rse_gifts.EmeraldPayload.script = property(
            lambda self: self.file.variants[rse_file.TARGET].options.get("buffer_decode", "imported-code")
        )
    if not hasattr(rse_gifts.EmeraldPayload, "expect"):
        rse_gifts.EmeraldPayload.expect = property(
            lambda self: self.file.variants[rse_file.TARGET].options.get("buffer_expect")
        )
