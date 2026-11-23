#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""List barebox's initcalls in the order that start_barebox() runs them.

Usage: initcall-map.py BAREBOX_ELF

The debug markers (0009) show the number of the running initcall on the
screen, counted from 1. This prints "number function" for each of them, from
the ELF file of barebox proper: the table between __barebox_initcalls_start and
__barebox_initcalls_end holds 8-byte pointers, filled in by relative
relocations when the table itself is zero in the file.
"""
import struct
import sys


def main(path):
    d = open(path, "rb").read()
    assert d[:4] == b"\x7fELF" and d[4] == 2, "not a 64-bit ELF"
    (_, _, _, _, _, shoff, _, _, _, _, shentsize, shnum, shstrndx) = struct.unpack_from(
        "<HHIQQQIHHHHHH", d, 16)
    secs = []
    for i in range(shnum):
        (name, typ, flags, addr, off, size, link, info, align, entsize) = struct.unpack_from(
            "<IIQQQQIIQQ", d, shoff + i * shentsize)
        secs.append(dict(name=name, type=typ, addr=addr, off=off, size=size, link=link,
                         entsize=entsize))
    syms = {}
    funcs = []
    for s in secs:
        if s["type"] != 2:  # SHT_SYMTAB
            continue
        strtab = secs[s["link"]]
        for j in range(s["size"] // 24):
            name, info, other, shndx, value, size = struct.unpack_from(
                "<IBBHQQ", d, s["off"] + j * 24)
            end = d.index(b"\0", strtab["off"] + name)
            n = d[strtab["off"] + name:end].decode()
            syms[n] = value
            if info & 0xf == 2 and value:  # STT_FUNC
                funcs.append((value, n))
    funcs.sort()
    start, end = syms["__barebox_initcalls_start"], syms["__barebox_initcalls_end"]
    rela = {}
    for s in secs:
        if s["type"] == 4:  # SHT_RELA
            for j in range(s["size"] // 24):
                off, info, addend = struct.unpack_from("<QQq", d, s["off"] + j * 24)
                if start <= off < end:
                    rela[off] = addend
    sec = next(s for s in secs if s["addr"] <= start < s["addr"] + s["size"] and s["type"] == 1)
    import bisect
    keys = [v for v, _ in funcs]
    for k in range((end - start) // 8):
        addr = start + k * 8
        val = rela.get(addr)
        if val is None:
            val = struct.unpack_from("<Q", d, sec["off"] + addr - sec["addr"])[0]
        i = bisect.bisect_right(keys, val) - 1
        print(f"{k + 1:4d} {funcs[i][1] if i >= 0 else '?'} {val:#x}")


if __name__ == "__main__":
    main(sys.argv[1])
