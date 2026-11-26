<div align="center">

# pokeldn plugins

**Mystery Gifts, legendary hunts, and link trades for [pokeldn](https://github.com/Decryptu/pokeldn).**

<p>
  <a href="#send-the-same-one-back"><img src="plugins/same-trade-back/icon.png" width="68" height="68" alt="Send the same one back"></a>
  <a href="#static-legendary-respawn-gen-3"><img src="plugins/gen3-legendary-respawn/icon.png" width="68" height="68" alt="Static Legendary Respawn"></a>
  <a href="#shiny-static-legendary-rng-gen-3"><img src="plugins/gen3-shiny-legendary-rng/icon.png" width="68" height="68" alt="Shiny Static Legendary RNG"></a>
  <a href="#gen-3-qol-pack-r-toggle-turbo--key-rare-candy"><img src="plugins/gen3-qol-pack/icon.png" width="68" height="68" alt="Gen 3 QoL Pack"></a>
  <a href="#bielson-battle-event-pallet-town"><img src="plugins/bielson-pallet-battle/icon.png" width="68" height="68" alt="Bielson Battle Event"></a>
</p>

[**Install**](#install) · [**Plugin catalog**](#plugin-catalog) · [**Releases**](https://github.com/gfaraujosousa/pokeldn-plugins/releases)

</div>

---

## Install

1. In **pokeldn**, open **Plugins → Sources**.
2. Add `gfaraujosousa/pokeldn-plugins`.
3. Open **Browse** and select **Install** next to the plugin you want. Available updates also appear in **Browse**.

To install by file, download a `.pokeplugin` from [Releases](https://github.com/gfaraujosousa/pokeldn-plugins/releases) and import it from **Plugins → Installed**.

> [!TIP]
> Check for **`D7GL-JWBM-QDCN-JUBT`** on the install confirmation screen. All releases in this repository use that signing key.

## Plugin Catalog

| Plugin | Games | What it does |
|---|---|---|
| [**Send the same one back**](#send-the-same-one-back) | All eight pokeldn trade games | Evolve a Pokémon by getting the one you offered back in a single trade. |
| [**Static Legendary Respawn**](#static-legendary-respawn-gen-3) | FireRed, LeafGreen, Emerald, Emerald Swap | Reset static encounters so you can battle or catch a legendary again. |
| [**Shiny Static Legendary RNG**](#shiny-static-legendary-rng-gen-3) | FireRed, LeafGreen, Emerald, Emerald Swap | Hunt a Method 1 shiny using your own trainer IDs. |
| [**Gen 3 QoL Pack**](#gen-3-qol-pack-r-toggle-turbo--key-rare-candy) | FireRed, LeafGreen, Emerald, Emerald Swap | Toggle up to **8×** speed with **R** and use a reusable Rare Candy from Key Items. |
| [**Bielson Battle Event**](#bielson-battle-event-pallet-town) | FireRed and LeafGreen (English and French Switch builds) | Challenge Bielson's Lv. 70 team in Pallet Town and earn a Master Ball. |

> [!IMPORTANT]
> Back up your save before trying a new Mystery Gift on your console.

> [!NOTE]
> **Emerald & Emerald Swap notes:**
> - **Ruby & Sapphire** have no Wireless Adapter Mystery Gift menu, so Gen 3 Mystery Gift tools target **FireRed**, **LeafGreen**, and **Emerald** (including **Emerald Swap**).
> - **Retail Switch Emerald Swap:** Verified live on a stock retail Switch (`BPGE`) receiving **Gen 3 QoL Pack `1.0.1`** over Mystery Gift (`39 s`). On streamed retail `emerald-swap` builds, wireless requires aligning Emerald's `&gSTWIStatus` IWRAM pointer to the host cartridge (`0x030030E0` on `BPRE`/`BPGE`, `0x03003030` on EU builds) — see [Decryptu/pokeldn-decrypt-plugins#3](https://github.com/Decryptu/pokeldn-decrypt-plugins/pull/3).
> - In packaged pokeldn releases where the RSE tab is hidden, each Gen 3 tool exposes a **Game** dropdown under **FireRed & LeafGreen**; when `POKELDN_PREVIEW=1` is enabled, dedicated tools also appear under **Ruby, Sapphire & Emerald**.

---

## Send the same one back

Trade any Pokemon and receive the exact same Pokemon back in that same trade. Pokemon that evolve by trade (Kadabra, Machoke, Graveler, Haunter, Boldore, Gurdurr, Phantump, etc.) evolve directly on your console in a single trade, with no offer Pokemon needed.

- **Works across every game pokeldn hosts a trade for:** FireRed & LeafGreen, Ruby/Sapphire/Emerald, Let's Go Pikachu/Eevee, Sword & Shield, Brilliant Diamond & Shining Pearl, Legends: Arceus, Scarlet & Violet, and Legends: Z-A.
- **Byte-for-byte identical:** Nothing is created or edited, and pokeldn saves a copy in its Received folder like any normal trade.

### How to use

1. Open your game on pokeldn's **Games** page and pick **Trade: send the same one back**.
2. Press **Start** and join the trade on your console as usual.
3. Offer the Pokemon you want back and confirm — it returns immediately in that trade.

<details>
<summary>How it works</summary>

Each game's tool runs pokeldn's built-in trade host in online mode and attaches a local mirror partner that echoes your console's own offer, confirmation, and (on Gen 3) party blocks and slot selection.

</details>

---

## Static Legendary Respawn (Gen 3)

Reset static legendary encounter flags and island puzzle counters so you can battle, capture, or shiny-hunt them again. Previously caught Pokemon in your party/PC and your Pokedex entries stay completely intact.

- **FireRed & LeafGreen (all 12 Switch builds):** Runs via native `CLI_RUN_BUFFER_SCRIPT` directly on SaveBlock1 — keeps your active Wonder Card and saved boosts untouched.
- **Emerald (including Emerald Swap):** Delivers a portable Wonder Card whose Pokemon Center 2F delivery man executes standard GBA script opcodes (`CLEARFLAG` / `SETFLAG` / `SETVAR`) — zero ROM addresses required.

### How to use

1. Save **outside** the legendary's room (or outside Birth Island / Faraway Island).
2. On pokeldn, pick **Respawn static legendaries**, choose your game and legendary (or **All**), and press **Start**.
3. On the console: **Mystery Gift > Wonder Cards > Friend**, then select **POKELDN**.
4. **FireRed / LeafGreen:** Continue your save, re-enter the legendary's map, and save.
5. **Emerald:** Continue your save, talk to the delivery man on **2F of any Pokemon Center**, then save (for Kyogre/Groudon, visit Weather Institute 2F afterward to trigger abnormal weather).

<details>
<summary>Supported static encounters (FireRed / LeafGreen & Emerald)</summary>

| Game | Available targets |
|---|---|
| **FireRed & LeafGreen** (EN, FR, DE, IT, ES, JP) | **All**, Articuno, Zapdos, Moltres, Mewtwo, Ho-Oh, Lugia, Deoxys (resets meteorite + triangle puzzle), Snorlax (Routes 12 & 16) |
| **Emerald / Emerald Swap** | **All**, Regirock, Regice, Registeel, Kyogre, Groudon, Rayquaza, Latias / Latios (Southern Island), Ho-Oh, Lugia, Deoxys (resets triangle puzzle), Mew (Faraway Island) |

</details>

---

## Shiny Static Legendary RNG (Gen 3)

Guarantees a legal **Method 1 shiny** static legendary under your save's own **TID/SID** without needing frame-perfect button presses.

- **Authentic encounter generation:** Advances `gRngValue` to the first upcoming state that yields a shiny PID for your trainer IDs immediately before the game's original encounter creator runs. The game itself generates the Pokemon, IVs, nature, and fateful encounter marker.
- **Covers both event and field legendaries:** Intercepts `CreateEnemyEventMon` (Ho-Oh, Lugia, Deoxys, Mew, Southern Island Latias/Latios) and `setwildbattle` (Articuno, Zapdos, Moltres, Mewtwo, Snorlax, Regirock, Regice, Registeel, Kyogre, Groudon, Rayquaza) — choose a specific target or **Any static legendary**.
- **Safety checks:** Refuses cleanly (`0xBAD0BAD0`) without writing RAM if the cartridge, revision, or ROM table signature does not match, or if another VBlank hook is active. Caps search at 262,144 states so it can never hang.

### How to use

1. Restart the game cleanly (do not combine with other RAM boosts in the same session).
2. Open **Shiny static legendary (RNG)**, choose your game and target legendary, and press **Start**.
3. On the console: **Mystery Gift > Wonder Cards > Friend**, pick **POKELDN**, and confirm `0x53484E59 MATCHES` in the log.
4. Continue your save and trigger the encounter normally (you must already have normal access to the island/location). Capture and save as usual.

<details>
<summary>Compatibility & verification notes</summary>

- Resident RAM hooks last until the game is closed or reset; saving does not write the hook into your save file.
- Verified under Unicorn ARMv4T (`TI925T`) emulation across FRLG builds and Emerald dynamic-discovery fixtures; back up your save before first console use.

</details>

---

## Gen 3 QoL Pack: R-Toggle Turbo & Key Rare Candy

> [!TIP]
> **Verified on retail hardware:** Confirmed working on a stock retail Switch on both FireRed/LeafGreen and **Emerald Swap** (with the `gSTWIStatus` alignment fix in [Decryptu/pokeldn-decrypt-plugins#3](https://github.com/Decryptu/pokeldn-decrypt-plugins/pull/3)).

Combines two practical quality-of-life tools into one configurable Mystery Gift session:

- **R-Toggle Turbo (2x / 3x / 4x / 6x / 8x):** Tap **R** once to toggle fast-forward ON or OFF (no need to hold the button). Starts OFF after install/restore, suppresses the R Help System on FRLG, and keeps scanline-budget (`228`), lag, and transition/fade guards active.
- **Reusable Key-Item Rare Candy:** Preflight-scans all 30 Key Item slots before writing anything, encrypts quantity `1` with your save's own encryption key, reuses an existing slot if already present (no duplicates), and refuses cleanly (`0xBAD0BAD0`) if Key Items is full — never overwriting any item or touching ordinary Rare Candies.
- **Turbo restore (FireRed & LeafGreen):** Saves the turbo hook in `SaveBlock2` (`filler_B20`) and binds Mom in Pallet Town so talking to her after any restart restores R-toggle turbo (and still heals your party) without needing the ESP32 again.
- **Turbo restore (Emerald):** With restore enabled, talk to the Mystery Gift delivery man on **2F of any Pokémon Center** after a restart.

### How to use

1. Keep at least **1 free slot in Key Items** (when Key-Item Rare Candy is enabled).
2. Restart the game cleanly without other RAM boosts active.
3. Open **QoL Pack: R-toggle turbo & Key Rare Candy**, choose your game, speed, and toggles, then press **Start**.
4. On the console: **Mystery Gift > Wonder Cards > Friend**, pick **POKELDN**, and confirm `0x514F4C38 MATCHES`.
5. Continue your save, verify the features, and save normally.

<details>
<summary>Persistence & Rare Candy notes</summary>

- **Key-Item Rare Candy** is permanent in the save on both FRLG and Emerald. Open **Key Items > Rare Candy > USE**. Because `RemoveBagItem` looks in the regular Items pocket, the unit in Key Items is not deducted (any normal Rare Candies in your Items pocket are consumed first if present).
- **After reboot:** On FireRed & LeafGreen (with Mom restore enabled), talk to Mom at home in Pallet Town to re-enable R-toggle turbo. On Emerald, talk to the Mystery Gift delivery man on **2F of any Pokémon Center** to restore turbo. The Key-Item Rare Candy stays in your save across restarts.
- Do not combine with other RAM boosts, shiny RNG hooks, or follower hooks in the same session.

</details>

---

## Bielson Battle Event (Pallet Town)

Adds a persistent **6-on-6 Level 70** boss battle against **Bielson** in Pallet Town for **FireRed & LeafGreen** (English & French Switch builds: `BPRE`, `BPGE`, `BPRF`, `BPGF`), plus a safe one-click **Remove** action.

- **Persistent overworld NPC:** Binds to the man walking in southern Pallet Town near the water; changes his sprite to Red when spoken to and offers a full 6v6 Lv. 70 single battle (supports both **English** and **Portuguese** dialogue).
- **Fair rules & reward:** Heals your party before and after the battle, awards **1 Master Ball once per save** (with full-bag pending retry — no need to win twice), allows unlimited rematches without duplicating the prize, and preserves any existing visiting trainer record across SaveBlock2 relocation.
- **Safe remover:** Select **Remove Bielson battle event** to clear the RAM script binding cleanly (verifies the Pallet Town `3/0/2` binding header before clearing and keeps your Master Ball / reward progress).

### How to use

1. Back up your save, save in **Pallet Town**, and restart the game without other RAM boosts active.
2. Open **Bielson Battle Event (Pallet Town)** under **FireRed & LeafGreen**, pick **Install** (or **Remove**) and dialogue language, then press **Start**.
3. On the console: **Mystery Gift > Wonder Cards > Friend**, pick **POKELDN**, and confirm `0x4249454C MATCHES`.
4. Continue your save and talk to the man in southern Pallet Town.

<details>
<summary>Bielson's Level 70 Gen 3 Team Roster</summary>

| Pokemon | Nature | Held Item | Moves |
|---|---|---|---|
| **Typhlosion** | Timid | Charcoal | Fire Blast / Flamethrower / ThunderPunch / Hidden Power Grass (70) |
| **Swellow** | Adamant | Choice Band | Double-Edge / Aerial Ace / Quick Attack / Steel Wing |
| **Jirachi** | Timid | Leftovers | Calm Mind / Psychic / Thunderbolt / Ice Punch |
| **Aipom** | Jolly | Silk Scarf | Aerial Ace / Double-Edge / Shadow Ball / Brick Break |
| **Lapras** | Modest | Leftovers | Surf / Ice Beam / Thunderbolt / Confuse Ray |
| **Gengar** | Timid | Lum Berry | Thunderbolt / Ice Punch / Fire Punch / Giga Drain |

</details>

---

## Requirements & Source

- Requires **pokeldn 0.66.8** or newer (plugin API `1.13`).
- Browse the current public source in [`plugins/`](plugins/).
- These community plugins are maintained here. [Report a plugin issue](https://github.com/gfaraujosousa/pokeldn-plugins/issues)
- Licensed under the **GNU AGPL v3** ([LICENSE](LICENSE)), like pokeldn.
