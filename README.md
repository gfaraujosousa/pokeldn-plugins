# pokeldn plugins

Plugins for [pokeldn](https://github.com/Decryptu/pokeldn). They are not made, reviewed or supported by
pokeldn; report problems here.

## Install

In pokeldn, open **Plugins** (bottom of the side menu), go to **Sources** and add:

```
gfaraujosousa/pokeldn-plugins
```

Then install from **Browse**. Updates show up there too. You can also download a `.pokeplugin` from
[Releases](https://github.com/gfaraujosousa/pokeldn-plugins/releases) and drop it on **Plugins > Installed**.

Every package is signed with the key `D7GL-JWBM-QDCN-JUBT`. pokeldn shows that fingerprint on the install
screen; if it shows another one, don't install it.

## Send the same one back

Trade a Pokemon and get the very same one back in that trade. A Pokemon that evolves by trade
(Kadabra, Machoke, Graveler, Haunter, Boldore, Gurdurr...) evolves on your console in a single trade,
and you don't need a Pokemon to offer.

pokeldn's own **Send it back** takes two trades and needs a Pokemon of yours to hand over first. This
one does it in one.

Works in every game pokeldn hosts a trade for:

- FireRed & LeafGreen
- Ruby, Sapphire & Emerald
- Let's Go, Pikachu! & Let's Go, Eevee!
- Sword & Shield
- Brilliant Diamond & Shining Pearl
- Legends: Arceus
- Scarlet & Violet
- Legends: Z-A

### Use

1. Install the plugin and open your game in pokeldn's **Games** page.
2. Pick **Trade: send the same one back** and press Start.
3. On the console, join the trade the same way as for pokeldn's own trade host.
4. Offer the Pokemon you want back and confirm. It comes back in that trade. Offer another one to do it
   again, or press Stop.

On FireRed, LeafGreen, Ruby, Sapphire and Emerald the trade screen shows your own party on both sides;
pick the Pokemon and the same slot is picked back.

The Pokemon you get back is byte for byte the one you sent. Nothing is created or changed, and pokeldn
keeps a copy of what it received in its Received folder, like any trade.

### How it works

Each game's tool runs pokeldn's built-in trade host for that game in its online mode, where the host
offers whatever the far player's console offers. The plugin puts a partner in place of the far player
that always offers what your own console offered.

Needs pokeldn 0.66.8 or newer (plugin API 1.13).

## Source

`plugins/` holds each plugin's source as it is packed. Licensed under the GNU AGPL v3, like pokeldn.
