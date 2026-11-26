"""Gen 3 QoL Pack launcher script."""
import argparse
from pathlib import Path
import sys

PLUGIN_ID = "gfaraujosousa.gen3-qol-pack"


def build_parser():
    ap = argparse.ArgumentParser(
        description="Install R-toggle turbo and/or reusable Key-Item Rare Candy in FireRed, LeafGreen and Emerald.",
        allow_abbrev=False,
    )
    ap.add_argument("--game-target", choices=("frlg", "emerald"), default="frlg",
                    help="Target game family: frlg (FireRed/LeafGreen) or emerald (Emerald / Emerald Swap).")
    ap.add_argument("--frlg-version", choices=("any", "firered", "leafgreen"), default="any",
                    help="Restrict FRLG hosting to FireRed, LeafGreen, or allow both.")
    ap.add_argument("--turbo", action="store_true", default=False,
                    help="Enable R-toggle fast-forward.")
    ap.add_argument("--speed", type=int, choices=(2, 3, 4, 6, 8), default=8,
                    help="Target speed multiplier when R-toggle turbo is ON.")
    ap.add_argument("--rare-candy", action="store_true", default=False,
                    help="Place a reusable Rare Candy into a free Key Items slot.")
    ap.add_argument("--mom-restore", action="store_true", default=False,
                    help="Bind persistent turbo restore after soft reset/reboot (Mom in Pallet Town on FRLG; 2F Mystery Gift Delivery Man on Emerald).")
    ap.add_argument("--language", default="english", help="Cartridge language advertised on the link.")
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
    if not args.turbo and not args.rare_candy:
        print("Error: enable at least one option (--turbo or --rare-candy).", file=sys.stderr)
        return 2

    from pokeldn import gifts
    from pokeldn.plugins import data_folder, run_launcher

    import gen3qol_builder as builder

    if args.game_target == "emerald":
        builder.install_emerald_buffer_code_support()
        gift = builder.build_emerald_gift(
            turbo=args.turbo, speed=args.speed, rare_candy=args.rare_candy,
            mom_restore=args.mom_restore,
        )
    else:
        gift = builder.build_frlg_gift(
            version=args.frlg_version,
            turbo=args.turbo,
            speed=args.speed,
            rare_candy=args.rare_candy,
            mom_restore=args.mom_restore,
        )

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
    if args.game_target == "emerald":
        host_args += ["--version", "emerald", "--expect-console", "emerald"]
    else:
        if args.frlg_version in ("firered", "leafgreen"):
            host_args += ["--version", args.frlg_version, "--expect-console", args.frlg_version]
        else:
            host_args += ["--version", "firered"]
        if args.language and not args.language.startswith("{"):
            host_args += ["--language", args.language]

    if args.keys:
        host_args += ["--keys", args.keys]
    if args.capture:
        host_args += ["--capture", args.capture]
    host_args += rest

    print(f"[gen3-qol-pack] Hosting: {gift.name} (expected status: 0x514F4C38)")
    return run_launcher("bin/frlg_mg_host.py", host_args)


if __name__ == "__main__":
    sys.exit(main())
