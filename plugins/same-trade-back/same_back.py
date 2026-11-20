"""Send the same one back: runs a game's built-in trade host with its partner replaced by the
mirror (sameback_mirror.py), so the console's Pokemon comes back to it in the same trade."""
import argparse
import sys


def build_parser():
    ap = argparse.ArgumentParser(
        description="Trade a Pokemon and receive the same one back in that trade.",
        allow_abbrev=False)
    ap.add_argument("--same-back-launcher", required=True, metavar="SCRIPT",
                    help="the game's built-in trade host, bin/NAME.py; every other argument goes to it")
    ap.add_argument("--same-back-game", default="", metavar="GAME", help="the game's catalog key")
    # Declared so the app passes them (pokeldn.app.command.build); they go on to the host.
    ap.add_argument("--keys", default=None, metavar="FILE", help="prod.keys, passed to the host")
    ap.add_argument("--capture", default=None, metavar="FILE", help="a capture file, passed to the host")
    return ap


def main(argv=None):
    args, rest = build_parser().parse_known_args(argv)
    for flag, value in (("--keys", args.keys), ("--capture", args.capture)):
        if value:
            rest += [flag, value]
    if "--online" not in rest:
        rest.append("--online")
    from pokeldn.online import session
    from pokeldn.plugins import run_launcher

    import sameback_mirror
    sameback_mirror.install(session)
    return run_launcher(args.same_back_launcher, rest)


if __name__ == "__main__":
    sys.exit(main())
