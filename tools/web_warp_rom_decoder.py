#!/usr/bin/env python3
"""
Web Warp (1983) ROM inspection / asset decoder.

Usage:
    python3 web_warp_rom_decoder.py "Web Warp (1983).vec"

No external Python packages required.

This is intentionally an archival/extraction tool, not an emulator.
It prints the cartridge header, score/difficulty tables, text, model pointers,
and decodes Vectrex mode-vector lists into relative line commands suitable for
a later Python vector renderer.
"""

from __future__ import annotations
from pathlib import Path
import sys
import json


def s8(v):
    return v - 256 if v & 0x80 else v


def be16(b, p):
    return (b[p] << 8) | b[p + 1]


def packed_bcd_word_to_int(v):
    # Web Warp score constants are stored as four decimal nibbles:
    # $0075 -> 75, $0325 -> 325, $0750 -> 750.
    digits = [
        (v >> 12) & 0xF,
        (v >> 8) & 0xF,
        (v >> 4) & 0xF,
        v & 0xF,
    ]
    if any(d > 9 for d in digits):
        raise ValueError(f"not packed BCD: ${v:04X}")
    return digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]


def ascii80(b, p):
    out = []
    while p < len(b):
        x = b[p]
        p += 1
        if x == 0x80:
            break
        out.append(chr(x) if 32 <= x < 127 else f"<{x:02X}>")
    return "".join(out), p


def decode_mode_vector(b, p, max_records=256):
    """
    Vectrex mode-list convention used heavily by Web Warp:
        mode, dy, dx
    with terminator mode == 0x01.

    mode $00 = move (beam blank)
    mode $FF = draw
    Other mode values are retained verbatim.
    """
    start = p
    x = y = 0
    commands = []
    for _ in range(max_records):
        mode = b[p]
        p += 1
        if mode == 0x01:
            return {
                "address": start,
                "end": p,
                "commands": commands,
            }
        dy = s8(b[p])
        dx = s8(b[p + 1])
        p += 2
        x2 = x + dx
        y2 = y + dy
        commands.append({
            "mode": mode,
            "dx": dx,
            "dy": dy,
            "from": [x, y],
            "to": [x2, y2],
            "draw": mode != 0,
        })
        x, y = x2, y2
    raise ValueError(f"unterminated/too-long vector list at ${start:04X}")


def main(path):
    b = Path(path).read_bytes()
    if len(b) != 0x2000:
        raise SystemExit(f"Expected 8192-byte ROM, got {len(b)} bytes")

    copyright_text, p = ascii80(b, 0)
    title_music = be16(b, p)
    p += 2
    text_hw = [b[p], b[p+1]]
    title_yx = [b[p+2], b[p+3]]
    p += 4
    title, p = ascii80(b, p)
    assert b[p] == 0

    score_table = [be16(b, 0x1163 + i * 2) for i in range(3)]
    angle_table = [s8(x) for x in b[0x18BB:0x18C2]]
    delay_table = list(b[0x118F:0x11A9])

    bonus = []
    p2 = 0x18F2
    for _ in range(6):
        s, p2 = ascii80(b, p2)
        bonus.append(s.strip())

    trophy_ptrs = [be16(b, 0x1225 + i * 2) for i in range(40)]
    player_ptrs = [be16(b, 0x1986 + i * 2) for i in range(8)]
    dragon_ptrs = [be16(b, 0x1AAE + i * 2) for i in range(8)]

    credits_raw = b[0x11D5:0x1225]
    promo = b[0x1F29:0x1FE9].rstrip(b"\x00").decode("ascii", errors="replace").strip()

    info = {
        "rom_size": len(b),
        "header": {
            "copyright_field": copyright_text,
            "title_music": f"${title_music:04X}",
            "text_hw": [f"${x:02X}" for x in text_hw],
            "title_yx": [f"${x:02X}" for x in title_yx],
            "title": title.rstrip(),
            "code_entry": "$001D",
        },
        "score_table": {
            "guardian_base": packed_bcd_word_to_int(score_table[0]),
            "creature_capture": packed_bcd_word_to_int(score_table[1]),
            "trophy_room_entry": packed_bcd_word_to_int(score_table[2]),
            "raw_words": [f"${x:04X}" for x in score_table],
        },
        "player_angle_table": angle_table,
        "web_line_delay_table": delay_table,
        "bonus_threshold_strings": bonus,
        "trophy_vector_pointers": [f"${x:04X}" for x in trophy_ptrs],
        "player_animation_pointers": [f"${x:04X}" for x in player_ptrs],
        "dragon_animation_pointers": [f"${x:04X}" for x in dragon_ptrs],
        "unused_promo_text": promo,
    }

    print(json.dumps(info, indent=2))

    # Decode all unique original line-mode assets referenced by the key tables.
    addresses = {
        0x111C: "trophy_room_portal",
        0x112C: "pattern_x_cross",
        0x1177: "web_semicircle",
        0x11B9: "guardian_drone",
        0x1BCA: "dragon_head",
        0x1CAE: "x_cross",
    }

    for i, ptr in enumerate(trophy_ptrs):
        addresses[ptr] = f"trophy_{i//2:02d}_frame_{i%2}"
    for i, ptr in enumerate(player_ptrs):
        addresses.setdefault(ptr, f"player_frame_ptrslot_{i}")
    for i, ptr in enumerate(dragon_ptrs):
        addresses.setdefault(ptr, f"dragon_frame_ptrslot_{i}")

    print("\nVECTOR LISTS")
    print("============")
    for ptr in sorted(addresses):
        try:
            vl = decode_mode_vector(b, ptr)
        except Exception as e:
            print(f"${ptr:04X} {addresses[ptr]}: decode failed: {e}")
            continue
        draws = sum(1 for c in vl["commands"] if c["draw"])
        moves = len(vl["commands"]) - draws
        print(f"${ptr:04X}-${vl['end']-1:04X}  {addresses[ptr]:28s} "
              f"records={len(vl['commands']):2d} draw={draws:2d} move={moves:2d}")

    # Save machine-readable vector extraction next to the ROM.
    extracted = {}
    for ptr in sorted(addresses):
        try:
            extracted[f"{ptr:04X}_{addresses[ptr]}"] = decode_mode_vector(b, ptr)
        except Exception:
            pass

    out = Path(path).with_name("web_warp_vectors.json")
    out.write_text(json.dumps(extracted, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 web_warp_rom_decoder.py <Web Warp ROM>")
    main(sys.argv[1])
