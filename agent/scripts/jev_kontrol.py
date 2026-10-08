#!/usr/bin/env python3
"""Jev kalite kapısı: taslak cevapları SOUL.md kurallarına göre denetler. Metin üretmez, yalnız yargılar.
Jev'e OpenRouter üzerinden gidilir (stdlib urllib). Anahtar: OPENROUTER_API_KEY (env, yoksa Hermes gala .env).
Kullanım:
  python3 agent/scripts/jev_kontrol.py agent/cevaplar/taslak-2026-10-08.md [--dry]
  python3 agent/scripts/jev_kontrol.py --test agent/tests/jev_vakalar.md
Her bloğa `durum:` satırının üstüne `jev: OK` ya da `jev: ihlal=özür(0.82),dil(0.71)` yazar."""
import json, time, os, re, sys, urllib.error, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from onayla import BLOCK  # aynı blok ayrıştırıcı

ENV_DOSYA = os.path.expanduser("~/.hermes/profiles/gala/.env")
# (uç nokta, model) — ilki 404 verirse ikincisi denenir (JEV-HANDOFF bölüm 10)
MODEL = os.environ.get("JEV_MODEL", "typesafe/jev-1.13")  # cloudflare/clef ve cloudflare/clef-flash de aynı uçta çalışır
UCLAR = [("https://openrouter.ai/api/v1/systemone", MODEL),
         ("https://openrouter.ai/api/alpha/decisions", "~typesafe/jev-latest")]
ESIK = 0.6  # noul > ESIK → ihlal
IMZA = "Gala Kokoreç Ekibi"
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF✀-➿❤]")
YASAK = re.compile(r"yapay zek[aâ]|\bbot\b|otomatik", re.I)

def aid(k):
    """Soru kimliği ASCII olmalı (Clef `^[A-Za-z0-9_.-]+$` ister); etiketler Türkçe kalır."""
    return k.translate(str.maketrans("öşçüğıÖŞÇÜĞİ", "oscugiOSCUGI"))


SORULAR = {
    "dil": {"q": "Is `cevap` written in the same language as `yorum`? Judge the grammar and common words of the sentences; ignore names of dishes, places and people such as 'kokoreç' or 'Eminönü'.",
            "t": "Both texts use the same language, e.g. an English review and an English reply.",
            "f": "The reply uses a different language than the review, e.g. a Turkish reply to an English review."},
    "vaat": {"q": "Does `cevap` promise the customer a discount, a gift, a free product, or a free next visit?",
             "t": "Any offer of something free or discounted: 'bir sonraki kokoreç bizden', 'ikram', 'indirim', 'on us', 'free'.",
             "f": "An invitation to come again without anything free or discounted."},
    "özür": {"q": "Does `cevap` contain an explicit apology that admits the business was at fault?",
             "t": "Phrases like 'özür dileriz', 'hatamız', 'kusura bakmayın', 'we apologize', 'our mistake'.",
             "f": "Only regret about the customer's experience, e.g. 'üzgünüz', 'üzülerek okuduk', 'sorry to hear', with no admission of fault."},
    "detay": {"q": "Does `cevap` refer to a concrete detail that the customer wrote in `yorum` (a dish, a place, a person, a timing, a complaint)?",
              "t": "The reply names something specific from the review.",
              "f": "The reply is generic and could be sent to any review."},
    "şablon": {"q": "Does `cevap` read like a robotic customer-service template?",
               "t": "Generic corporate address such as 'Değerli müşterimiz', 'Sayın müşterimiz', 'Dear valued customer', or boilerplate thanks with no personal touch.",
               "f": "A warm, specific reply written for this customer."},
    "suçlama": {"q": "Does the tone of `cevap` blame the customer or argue with them?",
                "t": "The reply says the customer is wrong, should have known better, or disputes their account in a defensive way.",
                "f": "The reply accepts the feedback calmly, even if it gives context like busy hours."},
}
DUYGU = {"positive": "Satisfied, praises the food or place", "negative": "Unhappy, complains with little or no praise",
         "mixed": "Both praise and a real complaint", "neutral": "Factual, no clear feeling"}


def anahtar():
    k = os.environ.get("OPENROUTER_API_KEY")
    if not k and os.path.exists(ENV_DOSYA):
        m = re.search(r"^OPENROUTER_API_KEY=[\"']?([^\"'\n]+)", open(ENV_DOSYA).read(), re.M)
        k = m and m.group(1).strip()
    return k or sys.exit("OPENROUTER_API_KEY yok (env ya da ~/.hermes/profiles/gala/.env).")


def jev_sor(key, state, questions):
    """Tek istek; ilk uç 404 verirse eskisini dener. Cevap: answers.<id>.noul / .choice / .confidence"""
    for i, (uc, model) in enumerate(UCLAR):
        body = json.dumps({"model": model, "state": state, "questions": questions}).encode()
        req = urllib.request.Request(uc, data=body, headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        for deneme in range(4):  # 5xx/429 (yoğunluk) için 3 yeniden deneme: 5s, 15s, 45s
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.loads(r.read())["answers"]
            except urllib.error.HTTPError as e:
                if e.code == 404 and i < len(UCLAR) - 1:
                    break
                if e.code in (429, 500, 502, 503, 529) and deneme < 3:
                    time.sleep(5 * 3 ** deneme); continue
                sys.exit(f"Jev {e.code}: {e.read()[:300].decode(errors='replace')}")


def parse(text):
    """Blok sözlükleri + testte kullanılacak `beklenen:` satırı (durum satırının hemen altında)."""
    out = []
    for m in BLOCK.finditer(text):
        b = m.groupdict(); b["_m"] = m
        nxt = text[m.end():].lstrip("\n").split("\n", 1)[0]
        b["beklenen"] = nxt[len("beklenen:"):].strip() if nxt.startswith("beklenen:") else None
        out.append(b)
    return out


def kod_kontrol(b):
    """Jev'e sorulmayan, kodla sayılan kurallar."""
    cevap, puan, ihlal = b["cevap"], int(b["puan"]), []
    if IMZA not in cevap:
        ihlal.append("imza")
    govde = cevap.split("—")[0] if IMZA in cevap else cevap
    # ponytail: cümle sayımı kaba — nokta/ünlem/soru ve emoji sınır sayılır, "vs." gibi kısaltmalar da böler
    n_cumle = len([p for p in re.split(r"[.!?…]+(?:\s|$)|" + EMOJI.pattern, govde) if p.strip()])
    if n_cumle > 3:
        ihlal.append(f"cümle({n_cumle})")
    n_emoji = len(EMOJI.findall(cevap))
    if n_emoji > 2 or (puan <= 2 and n_emoji > 0):
        ihlal.append(f"emoji({n_emoji})")
    if YASAK.search(cevap):
        ihlal.append("yasak_kelime")
    return ihlal


def jev_kontrol(key, b, ayrinti=False):
    """Tek istekte tüm Noul/Choice soruları; eşikleme ve puan politikası burada."""
    # imza sabit Türkçe; dil sorusunu şaşırtmasın diye state'e girmez (imza kontrolü kod_kontrol'de)
    state = {"yorum": b["yorum"].replace("\n> ", "\n"), "puan": int(b["puan"]), "cevap": b["cevap"].replace("— " + IMZA, "").strip()}
    sorular = {k: {"type": "noul", "instructions": {"question": v["q"], "inspect": ["yorum", "cevap"]},
                   "criteria": {"true": v["t"], "false": v["f"]}} for k, v in ((aid(k), v) for k, v in SORULAR.items())}
    sorular["duygu"] = {"type": "choice", "instructions": "What is the customer's overall sentiment in `yorum`?", "criteria": DUYGU}
    a = jev_sor(key, state, sorular)
    if ayrinti:
        print("   " + " ".join(f"{k}={a[aid(k)]['noul']:.2f}" for k in SORULAR) + f" duygu={a['duygu']['choice']}({a['duygu']['confidence']:.2f})")
    ihlal = []
    for k in SORULAR:
        p = a[aid(k)]["noul"]
        if k in ("dil", "detay"):  # olumlu soru; ihlal = olumsuz taraf
            p = 1 - p
        if k == "özür" and int(b["puan"]) > 2:  # özür yalnız 1-2★'da yasak
            continue
        if p > ESIK:
            ihlal.append(f"{k}({p:.2f})")
    d = a["duygu"]
    yazilan = (re.search(r"duygu: (\w+)", b["_m"].group(0)) or [None, None])[1]
    if yazilan and d["choice"] != yazilan and d["confidence"] > ESIK:
        ihlal.append(f"duygu({d['choice']} {d['confidence']:.2f})")
    return ihlal


def satir(ihlal):
    return "jev: OK" if not ihlal else "jev: ihlal=" + ",".join(ihlal)


def yaz(text, sonuc):
    """Her bloğa `durum:` üstüne jev satırı koyar; eski jev satırını değiştirir."""
    for b, ihlal in reversed(sonuc):
        m = b["_m"]; blk = re.sub(r"jev: .*\n", "", m.group(0))
        i = blk.rfind("durum:")
        text = text[:m.start()] + blk[:i] + satir(ihlal) + "\n" + blk[i:] + text[m.end():]
    return text


def main():
    key = anahtar()
    test, ayrinti = "--test" in sys.argv, "-v" in sys.argv
    yol = [a for a in sys.argv[1:] if not a.startswith("-")][0]
    text = open(yol, encoding="utf-8").read()
    bloklar = parse(text)
    sonuc, isabet = [], 0
    for b in bloklar:
        ihlal = kod_kontrol(b) + jev_kontrol(key, b, ayrinti)
        sonuc.append((b, ihlal))
        if test:
            bulunan = sorted(re.sub(r"\(.*?\)", "", x) for x in ihlal)
            beklenen = sorted(x for x in (b["beklenen"] or "").split(",") if x and x != "OK")
            ok = bulunan == beklenen; isabet += ok
            print(f"{'✓' if ok else '✗'} {b['id'][:12]:<12} {b['puan']}★ beklenen={','.join(beklenen) or 'OK':<14} bulunan={satir(ihlal)[5:]}")
        else:
            print(f"{b['id'][:12]:<12} {b['puan']}★ {satir(ihlal)[5:]}")
    if test:
        print(f"isabet: {isabet}/{len(bloklar)} ({100 * isabet // max(len(bloklar), 1)}%)")
    elif "--dry" not in sys.argv:
        open(yol, "w", encoding="utf-8").write(yaz(text, sonuc))
        print(f"{yol} güncellendi")


if __name__ == "__main__":
    main()
