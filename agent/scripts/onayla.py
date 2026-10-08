#!/usr/bin/env python3
"""Taslak dosyasındaki `durum: onay` blokları ornekler.md'ye (eğitim seti) ve cevaplanan.json'a işler.
`durum: red` olanlar sadece cevaplanan.json'a girer (tekrar üretilmesin).
Kullanım: python3 agent/scripts/onayla.py agent/cevaplar/taslak-2026-10-08.md"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DONE = os.path.join(REPO, "agent", "cevaplar", "cevaplanan.json")
ORNEK = os.path.join(REPO, "agent", "ornekler.md")
BLOCK = re.compile(r"### (?P<id>\w+) · (?P<yazar>.+?) · (?P<puan>\d)★ · (?P<tarih>.*?)\n> (?P<yorum>.*?)\n(?:dil: .*?\n)?cevap: ?(?P<cevap>.*?)\n(?:duygu: .*?\n)?durum: (?P<durum>\w+)", re.S)


def parse(text):
    return [m.groupdict() for m in BLOCK.finditer(text)]


def main():
    if "--test" in sys.argv:
        t = "### abc123 · Ali · 5★ · 2 gün önce\n> süper\ndil: tr\ncevap: sağ olun — Gala Kokoreç Ekibi\nduygu: positive\ndurum: onay\n"
        b = parse(t); assert b and b[0]["id"] == "abc123" and b[0]["durum"] == "onay", b
        print("ok"); return
    blocks = parse(open(sys.argv[1], encoding="utf-8").read())
    done = json.load(open(DONE)) if os.path.exists(DONE) else []
    seen = {d["id"] for d in done}
    n_onay = n_red = 0
    with open(ORNEK, "a", encoding="utf-8") as f:
        for b in blocks:
            if b["durum"] not in ("onay", "red") or b["id"] in seen:
                continue
            done.append({"id": b["id"], "yazar": b["yazar"], "puan": int(b["puan"]), "durum": b["durum"], "cevap": b["cevap"] if b["durum"] == "onay" else None})
            if b["durum"] == "onay":
                f.write(f"\n## {b['puan']}★\n> {b['yorum']}\ncevap: {b['cevap']}\n"); n_onay += 1
            else:
                n_red += 1
    json.dump(done, open(DONE, "w"), ensure_ascii=False, indent=1)
    print(f"onay: {n_onay}, red: {n_red} → ornekler.md ve cevaplanan.json güncellendi")


if __name__ == "__main__":
    main()
