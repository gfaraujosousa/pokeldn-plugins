"""Bielson Battle Event (Pallet Town) launcher script (FireRed & LeafGreen only)."""
import argparse
from pathlib import Path
import sys

PLUGIN_ID = "gfaraujosousa.bielson-pallet-battle"


def build_parser():
    ap = argparse.ArgumentParser(
        description="Install or remove the Bielson 6v6 Lv.70 battle event in Pallet Town (FireRed & LeafGreen).",
        allow_abbrev=False,
    )
    ap.add_argument("--action", choices=("install", "remove"), default="install",
                    help="Install or safely remove the Bielson Pallet Town battle event.")
    ap.add_argument("--dialogue", choices=("en", "pt"), default="en",
                    help="NPC dialogue language when installing.")
    ap.add_argument("--frlg-version", choices=("any", "firered", "leafgreen"), default="any",
                    help="Restrict hosting to FireRed, LeafGreen, or allow both.")
    ap.add_argument("--channel", default="11", help="Wireless channel hosted by the board.")
    ap.add_argument("--ot", default="POKELDN", help="Trainer name for the link session.")
    ap.add_argument("--id", dest="trainer_id", default="12345:54321", help="TID:SID for the link session.")
    ap.add_argument("--keys", default=None, metavar="FILE", help="Switch keys file, passed to the host.")
    ap.add_argument("--capture", default=None, metavar="FILE", help="Optional capture file, passed to the host.")
    ap.add_argument("--export-gift", default=None, metavar="FILE",
                    help="Write the generated .pokegift to FILE and exit without starting the radio.")
    return ap


def main(argv=None):
    args, rest = build_parser().parse_known_args(argv)
    from pokeldn import gifts
    from pokeldn.plugins import data_folder, run_launcher

    import bielson_builder as builder

    if args.action == "remove":
        gift = builder.build_remove_gift(version=args.frlg_version)
    else:
        gift = builder.build_install_gift(dialogue=args.dialogue, version=args.frlg_version)

    if args.export_gift:
        out = Path(args.export_gift)
        gifts.save(out, gift)
        print(f"Saved {out}: {gift.name}")
        return 0

    folder = data_folder(PLUGIN_ID)
    folder.mkdir(parents=True, exist_ok=True)
    gift_path = folder / "active.pokegift"
    gifts.save(gift_path, gift)

    host_args = [
        "--live",
        "--gift-file", str(gift_path),
        "--ot", args.ot,
        "--id", args.trainer_id,
        "--channel", str(args.channel),
    ]
    if args.frlg_version in ("firered", "leafgreen"):
        host_args += ["--version", args.frlg_version, "--expect-console", args.frlg_version]
    else:
        host_args += ["--version", "firered"]
    if args.keys:
        host_args += ["--keys", args.keys]
    if args.capture:
        host_args += ["--capture", args.capture]
    host_args += rest

    print(f"[bielson-pallet-battle] Hosting: {gift.name} (expected status: 0x4249454C)")
    return run_launcher("bin/frlg_mg_host.py", host_args)


if __name__ == "__main__":
    sys.exit(main())
