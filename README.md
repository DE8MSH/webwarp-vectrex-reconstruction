# Web Warp / Web Wars — Vectrex native reconstruction

Work-in-progress native Python reconstruction of **Web Warp / Web Wars (Vectrex, 1983)** based on reverse engineering of the original cartridge code and Vectrex BIOS behavior.

The goal is a faithful vector-native reimplementation, not sprite emulation and not a Motorola 6809 emulator.

## Status

Current main build: **V8** (`webwarp.py`).

Implemented/reconstructed so far includes:

- 3:4 portrait Vectrex-style display
- original ROM vector models for Hawk King, Guardian Drones, creatures/trophies, portal and Cosmic Dragon
- deterministic `$191C` web/camera motion script
- original 3-byte moving web-line pool and speed-dependent spacing
- foreground web continuation corresponding to the separate fixed-`$E0` web render pass
- Vectrex BIOS Rise/Run rotation table and integer transform math
- reconstructed `$094F` draw-displacement path
- continuous Hawk movement using ROM-derived 16-bit web motion tables
- six Guardian slots and nine blaster shots
- Capture Rod timing and major collision/score rules
- Trophy Room / Trophy Room 2 behavior, including an option for the original `$20` bug
- hidden programmer-credit screen

This is **not yet claimed to be cycle-perfect or 1:1**. The largest remaining visual fidelity item is the cartridge's `$08CF` direct VIA transformed-web routine, plus some enemy-state and audio details.

## ROM files are intentionally not included

This repository does **not** contain the original Web Warp cartridge ROM, Vectrex BIOS, or extracted ROM vector JSON. Supply dumps you are legally entitled to use.

### Known reference hashes

The exact files used for this reverse-engineering work were:

| File | Size | SHA-256 |
|---|---:|---|
| Web Warp (1983) cartridge ROM | 8192 bytes | `57ced92fb0646aa4e0ccf1a03ac1d8d001a48f9ebef9b719d4812dde2ec6f19b` |
| Vectrex BIOS dump | 4096 bytes | `480cd76805efe1c87e2412d494ed03918049d7bb9da3b97a5647b768c3468eac` |

Verify your files with:

```bash
python3 verify_rom.py "Web Warp (1983).vec" \
  --bios "Vectrex BIOS (1982)(5).vec"
```

A mismatching hash does not automatically prove a dump is bad — there may be other BIOS revisions or cartridge revisions — but it means it is **not byte-identical to the files this reconstruction was developed against**.

## Setup

On Debian/Ubuntu/Linux Mint, use a virtual environment rather than `--break-system-packages`:

```bash
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Generate the local vector asset JSON

The JSON is derived from the cartridge ROM and therefore is not committed. Generate it from your own ROM:

```bash
python3 tools/web_warp_rom_decoder.py "Web Warp (1983).vec"
```

This creates:

```text
web_warp_vectors.json
```

beside the ROM.

## Run

```bash
python3 webwarp.py \
  --rom "Web Warp (1983).vec" \
  --vectors "web_warp_vectors.json" \
  --bios "Vectrex BIOS (1982)(5).vec"
```

Self-test:

```bash
python3 webwarp.py \
  --rom "Web Warp (1983).vec" \
  --vectors "web_warp_vectors.json" \
  --bios "Vectrex BIOS (1982)(5).vec" \
  --self-test
```

Optional final analogue display calibration:

```bash
--beam-gain 1.0
```

The gameplay math remains in original-style integer/Vectrex units; beam gain affects only the final desktop raster mapping.

## Controls

- **Left / Right** — move Hawk King across the Web of Fantasy
- **Up / Down** — speed
- **Space / 4** — fire
- **C / 3** — Capture Rod
- **1 / Z**, **2 / X** — Vectrex buttons 1/2
- **F1** — debug information
- **F2** — original Trophy Room bug / fixed behavior
- **P** — pause
- **Esc** — quit

On the title screen, holding Vectrex buttons **1 + 2 + 4** exposes the hidden programmer-credit screen.

## Reverse-engineering tools

`tools/web_warp_rom_decoder.py`
: Extracts tables and mode-vector lists from a local 8192-byte cartridge dump and writes `web_warp_vectors.json`.

`tools/web_warp_labels_v3.py`
: Ghidra labeling script containing corrected semantic names for major functions, RAM objects, vector tables and gameplay structures.

`docs/reverse_engineering.md`
: Current static reverse-engineering notes and ROM map.

## Repository policy

Do not commit:

- cartridge ROM dumps
- Vectrex BIOS dumps
- locally extracted `web_warp_vectors*.json`

They are covered by `.gitignore` on purpose.

## Project direction

The next major fidelity step is to port cartridge routine `$08CF` instruction-by-instruction into abstract vector-beam commands. That should remove the remaining approximation in the longitudinal foreground web geometry.
