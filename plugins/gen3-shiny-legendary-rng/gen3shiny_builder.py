"""Builders for Shiny Static Legendary RNG (all 12 FRLG Switch builds + Emerald dynamic discovery)."""
import struct

from pokeldn import gifts
from pokeldn.frlg.gift.stamp_rally import MysteryGiftDistribution
from pokeldn.frlg.rom import builds

import gen3shiny_stubs as stubs

SUCCESS_SHNY = 0x53484E59  # "SHNY"
REFUSED = 0xBAD0BAD0

# (mode, GBA internal species id, label)
FRLG_TARGETS = {
    "any": ("both", 0, "Any Static Legendary"),
    "hooh": ("special", 250, "Ho-Oh"),
    "lugia": ("special", 249, "Lugia"),
    "deoxys": ("special", 410, "Deoxys"),
    "mewtwo": ("wild", 150, "Mewtwo"),
    "articuno": ("wild", 144, "Articuno"),
    "zapdos": ("wild", 145, "Zapdos"),
    "moltres": ("wild", 146, "Moltres"),
    "snorlax": ("wild", 143, "Snorlax"),
}

EMERALD_TARGETS = {
    "any": ("both", 0, "Any Static Legendary"),
    "hooh": ("special", 250, "Ho-Oh"),
    "lugia": ("special", 249, "Lugia"),
    "deoxys": ("special", 410, "Deoxys"),
    "mew": ("special", 151, "Mew"),
    "latias": ("special", 407, "Latias"),
    "latios": ("special", 408, "Latios"),
    "regirock": ("wild", 401, "Regirock"),
    "regice": ("wild", 402, "Regice"),
    "registeel": ("wild", 403, "Registeel"),
    "kyogre": ("wild", 404, "Kyogre"),
    "groudon": ("wild", 405, "Groudon"),
    "rayquaza": ("wild", 406, "Rayquaza"),
}


def _patch_u32(buf: bytearray, offset: int, value: int) -> None:
    buf[offset:offset + 4] = struct.pack("<I", value & 0xFFFFFFFF)


def build_frlg_payload(build: builds.Build, target: str) -> tuple[bytes, dict]:
    """-> (ARMv4T installer + Thumb resident hook bytes, metadata) for one FRLG cartridge build."""
    if target not in FRLG_TARGETS:
        raise ValueError(f"Unknown FRLG target {target!r}")
    mode, species_id, _label = FRLG_TARGETS[target]
    hinfo = stubs.FRLG_HOOKS[mode]
    iinfo = stubs.FRLG_INSTALLER
    base = hinfo["base"]
    hoff = hinfo["offsets"]
    ioff = iinfo["offsets"]

    var8000 = build.ewram.get("special_var_8000", 0x020370B4)
    var8004 = var8000 + 8

    hook = bytearray(bytes.fromhex(hinfo["hex"]))
    _patch_u32(hook, hoff["old_vblank"], build.vblank_intr | 1)
    _patch_u32(hook, hoff["ctx"], build.script_context)
    _patch_u32(hook, hoff["rng"], build.rng)
    _patch_u32(hook, hoff["sb2ptr"], build.sb2ptr)
    if "species_var" in hoff:
        _patch_u32(hook, hoff["species_var"], var8004)
    if "wanted_species" in hoff:
        _patch_u32(hook, hoff["wanted_species"], species_id)

    inst = bytearray(bytes.fromhex(iinfo["hex"]))
    code_word = int.from_bytes(build.game_code.encode("ascii"), "little")
    _patch_u32(inst, ioff["cart_code"], code_word)
    _patch_u32(inst, ioff["var_expected"], var8004)
    _patch_u32(inst, ioff["intr"], build.intr_vblank)
    _patch_u32(inst, ioff["original"], build.vblank_intr | 1)
    _patch_u32(inst, ioff["base"], base)
    _patch_u32(inst, ioff["blob_len"], len(hook))
    _patch_u32(inst, ioff["table_lit"], base + hoff["old_table"])
    _patch_u32(inst, ioff["old_spec_lit"], base + hoff["old_special"] if "old_special" in hoff else 0)
    _patch_u32(inst, ioff["old_wild_lit"], base + hoff["old_wild"] if "old_wild" in hoff else 0)
    _patch_u32(inst, ioff["wrap_spec"], (base + hoff["wrapper_special"]) | 1 if "wrapper_special" in hoff else 0)
    _patch_u32(inst, ioff["wrap_wild"], (base + hoff["wrapper_wild"]) | 1 if "wrapper_wild" in hoff else 0)

    payload = bytes(inst) + bytes(hook)
    assert len(payload) <= 1024, len(payload)
    meta = {
        "mode": mode,
        "species": species_id,
        "base": base,
        "table": hinfo["table"],
        "hook_offsets": hoff,
        "wrapper_special": (base + hoff["wrapper_special"]) if "wrapper_special" in hoff else None,
        "wrapper_wild": (base + hoff["wrapper_wild"]) if "wrapper_wild" in hoff else None,
    }
    return payload, meta


def build_frlg_gift(target: str, *, version: str = "any") -> gifts.Gift:
    if target not in FRLG_TARGETS:
        raise ValueError(f"Unknown FRLG target {target!r}")
    label = FRLG_TARGETS[target][2]
    variants = {}
    for code, build in builds.BUILDS.items():
        if version in ("firered", "leafgreen") and build.version != version:
            continue
        payload, _ = build_frlg_payload(build, target)
        variants[code] = gifts.Variant({"buffer_code": payload}, {"buffer_expect": SUCCESS_SHNY})
    return gifts.Gift("frlg", f"RNG Shiny {label} (FRLG)", variants)


def build_emerald_payloads(target: str) -> tuple[bytes, bytes, dict]:
    """-> (buffer_lead_1 stage payload, buffer_code dynamic installer, metadata) for Emerald."""
    if target not in EMERALD_TARGETS:
        raise ValueError(f"Unknown Emerald target {target!r}")
    mode, species_id, _label = EMERALD_TARGETS[target]
    hinfo = stubs.EMERALD_HOOKS[mode]
    iinfo = stubs.EMERALD_INSTALLER
    sinfo = stubs.EMERALD_STAGE
    base = hinfo["base"]
    hoff = hinfo["offsets"]
    ioff = iinfo["offsets"]

    hook = bytearray(bytes.fromhex(hinfo["hex"]))
    if "wanted_species" in hoff:
        _patch_u32(hook, hoff["wanted_species"], species_id)

    stage = bytearray(bytes.fromhex(sinfo["hex"]))
    _patch_u32(stage, sinfo["offsets"]["blob_len"], len(hook))
    lead1 = bytes(stage) + bytes(hook)
    assert len(lead1) <= 1024, len(lead1)

    inst = bytearray(bytes.fromhex(iinfo["hex"]))
    _patch_u32(inst, ioff["base"], base)
    _patch_u32(inst, ioff["blob_len"], len(hook))
    _patch_u32(inst, ioff["vbl_lit"], base + hoff["old_vblank"])
    _patch_u32(inst, ioff["ctx_lit"], base + hoff["ctx"])
    _patch_u32(inst, ioff["table_lit"], base + hoff["old_table"])
    _patch_u32(inst, ioff["spec_var_lit"], base + hoff["species_var"] if "species_var" in hoff else 0)
    _patch_u32(inst, ioff["old_spec_lit"], base + hoff["old_special"] if "old_special" in hoff else 0)
    _patch_u32(inst, ioff["old_wild_lit"], base + hoff["old_wild"] if "old_wild" in hoff else 0)
    _patch_u32(inst, ioff["rng_lit"], base + hoff["rng"])
    _patch_u32(inst, ioff["sb2_lit"], base + hoff["sb2ptr"])
    _patch_u32(inst, ioff["wrap_spec"], (base + hoff["wrapper_special"]) | 1 if "wrapper_special" in hoff else 0)
    _patch_u32(inst, ioff["wrap_wild"], (base + hoff["wrapper_wild"]) | 1 if "wrapper_wild" in hoff else 0)
    code = bytes(inst)
    assert len(code) <= 1024, len(code)

    meta = {
        "mode": mode,
        "species": species_id,
        "base": base,
        "table": hinfo["table"],
        "hook_offsets": hoff,
        "wrapper_special": (base + hoff["wrapper_special"]) if "wrapper_special" in hoff else None,
        "wrapper_wild": (base + hoff["wrapper_wild"]) if "wrapper_wild" in hoff else None,
    }
    return lead1, code, meta


def build_emerald_gift(target: str) -> gifts.Gift:
    if target not in EMERALD_TARGETS:
        raise ValueError(f"Unknown Emerald target {target!r}")
    label = EMERALD_TARGETS[target][2]
    lead1, code, _ = build_emerald_payloads(target)
    return gifts.Gift(
        "rse",
        f"RNG Shiny {label} (Emerald)",
        {"emerald": gifts.Variant(
            {"buffer_lead_1": lead1, "buffer_code": code},
            {"buffer_expect": SUCCESS_SHNY},
        )},
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
