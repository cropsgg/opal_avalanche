from __future__ import annotations

from typing import Iterable, List

from eth_utils import keccak


def para_hash(txt: str) -> bytes:
    canon = " ".join(txt.split()).strip().lower()
    return keccak(text=canon)


def merkle_root(hashes: Iterable[bytes]) -> bytes:
    level: List[bytes] = list(hashes)
    if not level:
        return b"\x00" * 32
    while len(level) > 1:
        nxt: List[bytes] = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i + 1] if i + 1 < len(level) else level[i]
            nxt.append(keccak(a + b))
        level = nxt
    return level[0]


