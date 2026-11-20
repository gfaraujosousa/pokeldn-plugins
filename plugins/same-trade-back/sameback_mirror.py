"""The mirror: a trade partner whose console always offers what ours offers.

A built-in host launcher trades with a far player through `pokeldn.online.session.partner()`: the
partner's offer is offered to our console, each side confirms once both consoles have, and on
FireRed / LeafGreen / Emerald the partner's party blocks and pick are replayed to ours. The mirror
answers every call with the console's own data, so the Pokemon the console offers comes back to it
in the same trade, byte for byte, and one that evolves by trade evolves there.

It keeps the surface `pokeldn.online.link.Partner` shows a launcher: `theirs()` with `offer`,
`accepted`, `withdrawn`, `done`, `refused` and `shared`, and `offer`, `withdraw`, `share`,
`accept`, `unaccept`, `refuse`, `done`, `close`. It has no `hear`: a host tells a gift made for its
receiver apart by that method, and the mirror is none.
"""
import threading

TAG = "[same-back]"


class Round:
    """What the mirror's console did this round, as `pokeldn.online.link.Round` keeps a partner's."""

    def __init__(self):
        self.offer = None
        self.accepted = False
        self.withdrawn = 0
        self.done = False
        self.refused = ""
        self.shared = {}


class Mirror:
    """A partner that is always paired and always offers back what the console offered."""

    validate = None             # the console's own records: nothing to check

    def __init__(self, game, log=print):
        self.game = game
        self.log = log
        self.state = "paired"
        self.round = 1
        self.lock = threading.RLock()
        self.current = Round()

    @property
    def paired(self):
        return self.state == "paired"

    def start(self, thread=True):
        self.log(f"{TAG} every trade offers the console's own Pokemon back")

    def close(self, reason="closed"):
        self.state = "closed"

    def tick(self):
        pass

    def theirs(self):
        with self.lock:
            return self.current

    def offer(self, record):
        with self.lock:
            self.current.offer, self.current.accepted, self.current.refused = bytes(record), False, ""
        self.log(f"{TAG} trade {self.round}: offering the console's Pokemon back")

    def withdraw(self):
        with self.lock:
            self.current.offer, self.current.accepted = None, False
            self.current.withdrawn += 1
            # A FireRed pick belongs to the offer it came with.
            self.current.shared.pop("pick", None)

    def share(self, key, data):
        with self.lock:
            self.current.shared[key] = bytes(data)

    def accept(self):
        with self.lock:
            self.current.accepted = True

    def unaccept(self):
        with self.lock:
            self.current.accepted = False

    def refuse(self, reason):
        self.log(f"{TAG} the host refused the console's Pokemon: {reason}")

    def done(self):
        """The console's trade completed: the next round starts empty, so its party blocks and offer
        are the console's new ones."""
        with self.lock:
            self.current.done = True
            self.round += 1
            self.current = Round()
        self.log(f"{TAG} trade {self.round - 1} complete; offer another Pokemon to trade it back too")


def install(session, log=print):
    """Makes `session.partner` (pokeldn.online.session) hand a host launcher run with --online a
    started Mirror instead of a far player. -> the replaced function."""
    original = session.partner

    def partner(game, args, code="", name="", log=log):
        if not getattr(args, "online", False):
            return original(game, args, code=code, name=name, log=log)
        mirror = Mirror(game, log=log)
        mirror.start()
        return mirror

    session.partner = partner
    return original
