# Web Warp / Web Wars — reverse-engineering map

This document is a compact working map for the native reconstruction. Addresses refer to the 8192-byte cartridge ROM (`$0000-$1FFF`). Semantic names are reconstruction names, not original source labels.

## Cartridge / boot

- `$0000` cartridge header: `g GCE 1983`, title-music pointer `$1E87`, title `WEB WARP`
- `$001D` cartridge entry and hidden programmer-credit gate
- hidden credits at `$11D5`: William Hawkins, Duncan Muirhead, Patrick King, GT 1983
- hidden gate uses Vectrex buttons 1+2+4

## Main loop

The per-frame order reconstructed from the cartridge is:

1. `Wait_Recal`
2. `Do_Sound`
3. button read
4. joystick sampler `$1CDF`
5. render/update frame `$0437`
6. shot/death `$0B3F`
7. player movement `$0B9A`
8. bonus/high score `$0B14`
9. Guardians/Creature/Portal `$0CE1`
10. Dragon shot `$1028`
11. web-line spawn `$0F54`
12. sound engine `$1D2A`
13. deterministic web-motion script `$1078`
14. player angle `$0FBF`
15. world transforms `$0C75`
16. BIOS counters
17. Capture Rod `$0FCE`
18. Cosmic Dragon trigger `$1104`
19. Trophy Room 2 check `$0100`

## Corrected major functions

| Address | Reconstruction name | Meaning |
|---|---|---|
| `$0100` | `WW_CheckTrophyRoom2` | original `$20`/20 bug check |
| `$0239` | `WW_InitGameAndWeb` | motion tables, speed, initial web |
| `$0437` | `WW_RenderAndAdvanceFrame` | central renderer/state advancement |
| `$08CF` | `WW_DrawTransformedWebVector` | direct VIA transformed foreground-web routine; largest remaining fidelity item |
| `$094F` | `WW_BuildDrawDisplacement` | camera/object draw displacement |
| `$0976/$0979` | depth update | rounded 8x8/16-bit depth math |
| `$099F` | `WW_RenderTrophyRoom` | Trophy Room renderer |
| `$0A54` | `WW_UpdateCosmicDragon` | Dragon update |
| `$0B14` | bonus/high score | extra lives + high score |
| `$0B3F` | player fire/death | 9-shot pool, cooldown 8 |
| `$0BBF` | lateral movement core | continuous motion across seven web segments |
| `$0C75` | transform all | Hawk, six Drones, Creature, Portal |
| `$0CC0` | transform coordinate | BIOS Rise/Run fixed-point rotation |
| `$0CE1` | Guardian/Creature/Portal update | principal world-object logic |
| `$0F1E` | collision | 3-axis threshold check returning Carry |
| `$0F54` | `WW_SpawnWebLine` | web-line allocator, not enemy spawn |
| `$0FBF` | player angle | seven-value table + web angle |
| `$0FCE` | Capture Rod | 13-frame rod timer / Creature capture |
| `$1028` | Dragon shot | projectile + 5x7 hit test |
| `$106A/$1078` | web script | initialize/update deterministic `$191C` motion script |
| `$10A9` | Portal spawn | separate Trophy Room entrance object |
| `$1104` | Dragon trigger | Cosmic Dragon activation |
| `$1D2A` | sound engine | music/SFX dispatch |

## Object/RAM map

- `$C900` initial 3-byte moving web-line record
- `$C903-$C91A` eight recycled 3-byte web-line records
- `$C94F-$C9BA` exactly six 18-byte Guardian Drone records
- `$C9BB-$C9CC` current Fantasy Creature, separate from Guardians
- `$C9CD...` Cosmic Dragon
- `$C9DE...` Hawk King/player record
- `$C9F0` capture-pending state
- `$C9F1-$CA41` exactly nine 9-byte blaster-shot records
- `$CB22...` Trophy Room portal, separate from Creature
- `$CAD6/$CAE1` player 1/player 2 score/display state

## Web geometry

`$1177` is the base U/semicircle mode-vector list. Its cumulative vertices are used to construct the seven web segments and the runtime movement tables.

The game uses one initial web-line record plus eight recycled records. A record starts at depth `$0280`; its depth grows using speed-dependent integer multiplication. Ring spacing comes from `$118F` and uses the active speed.

The visible web motion is **not random**. `$191C` is a fixed sequence of 7-byte records:

- duration
- signed 16-bit delta A
- signed 16-bit delta B
- signed 16-bit web-angle/base delta

`$1078` advances through the records and loops at the zero-duration terminator.

Hawk lateral movement does not make the web camera follow the Hawk. Hawk orientation is separately derived from `directionIndex >> 2` plus the current web-angle state.

After the normal moving ring pool is drawn, the original renderer performs another web pass at fixed scale `$E0` and calls `$08CF`. V8 approximates this foreground continuation, but `$08CF` itself is still the main target for a bit/beam-faithful port.

## Player / movement

The seven player/web orientation values at `$18BB` are:

`+17, +13, +7, 0, -7, -13, -17`

Runtime tables derived from the web segment deltas provide different movement granularity:

- Hawk: delta x8 -> 32 steps per segment
- Guardians: delta x16 -> 16 steps per segment
- Creature: delta x32 -> 8 steps per segment

The native reconstruction keeps these as fixed-width integer world coordinates before final raster display mapping.

## Original vector assets

- `$111C` Trophy Room entrance portal
- `$112C` patterned X-cross
- `$1145` player explosion dot list
- `$1177` web semicircle/U
- `$11B9` Guardian Drone star/mine
- `$1225` 40 pointers = 20 Creature/Trophy species x two frames
- `$1986` Hawk King animation pointer sequence
- `$1AAE` Cosmic Dragon animation pointer sequence
- `$1BCA` Dragon head
- `$1BD7` Dragon shot
- `$1BE9` Trophy Room hexagon
- `$1BF7` Trophy Room layout

The ROM decoder in `tools/web_warp_rom_decoder.py` extracts the supported vector lists into `web_warp_vectors.json` from a local cartridge dump.

## Capture / Trophy Room

Button 3 activates the Capture Rod for `$0D` frames. Capture checks Creature depth proximity and a BIOS `Obj_Hit` gate. Successful capture scores 325 and enables the later Portal sequence.

Entering the portal increments Trophy progression and scores 750.

The original cartridge contains a documented code bug at `$0100`: it compares the count to hexadecimal `$20` (32 decimal) where the intended threshold was apparently decimal 20. The reconstruction can preserve the original behavior or use the fixed threshold.

## Scoring / lives

Packed-decimal score constants at `$1163`:

- Guardian: 75 base points plus speed bonus
- Creature capture: 325
- Trophy Room entry: 750

Starting lives: 5.

ROM bonus thresholds at `$18F2`:

`25000, 50000, 100000, 250000, 500000, 999999`

## Sound

The custom event engine begins around `$1D2A`; the jump/data table is at `$1EF1`. Known event bits from call sites include:

- `$08` blaster fire
- `$10` Cosmic Dragon activation/attack
- `$20` Guardian destroyed
- `$40` Hawk King hit/death
- `$80` successful Capture Rod hit

Exact AY-3-8912 reproduction remains future work.

## Current fidelity boundary

V8 already uses original vector assets, ROM-derived integer world movement, BIOS Rise/Run rotation math, `$094F` displacement reconstruction, the speed/ring pool, deterministic web script and fixed-$E0 foreground continuation.

It is deliberately **not** labelled cycle-perfect or 1:1 yet. The most important remaining visual task is an instruction-by-instruction abstraction of `$08CF` into beam commands, followed by exact Guardian state transitions and sound synthesis.
