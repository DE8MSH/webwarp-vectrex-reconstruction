#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

KNOWN = {
    "webwarp": {
        "size": 8192,
        "sha256": "57ced92fb0646aa4e0ccf1a03ac1d8d001a48f9ebef9b719d4812dde2ec6f19b",
        "label": "Web Warp (1983) Vectrex cartridge ROM",
    },
    "bios": {
        "size": 4096,
        "sha256": "480cd76805efe1c87e2412d494ed03918049d7bb9da3b97a5647b768c3468eac",
        "label": "Vectrex BIOS dump used during reverse engineering",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(path: Path, kind: str) -> bool:
    ref = KNOWN[kind]
    data_size = path.stat().st_size
    digest = sha256(path)
    ok = data_size == ref["size"] and digest == ref["sha256"]

    print(ref["label"])
    print(f"  file:   {path}")
    print(f"  size:   {data_size} bytes (expected {ref['size']})")
    print(f"  sha256: {digest}")
    print(f"  result: {'OK' if ok else 'MISMATCH'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify local Web Warp/Vectrex ROM dumps by SHA-256.")
    ap.add_argument("rom", type=Path, help="Web Warp cartridge ROM")
    ap.add_argument("--bios", type=Path, help="optional Vectrex BIOS dump")
    ns = ap.parse_args()

    ok = verify(ns.rom, "webwarp")
    if ns.bios is not None:
        ok = verify(ns.bios, "bios") and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
