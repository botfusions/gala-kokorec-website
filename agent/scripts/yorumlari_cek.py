#!/usr/bin/env python3
"""Sitedeki /api/reviews uç noktasından yorumları çeker, cevaplanmamış olanları JSON basar.
Hermes --monitor-script olarak çalışır: çıktı değişmezse ajan uyanmaz.
ponytail: Places API son 5 yorumu verir; Business Profile API onayı gelince kaynağı oraya çevir."""
import hashlib, json, os, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DONE = os.path.join(REPO, "agent", "cevaplar", "cevaplanan.json")
URL = os.environ.get("GALA_REVIEWS_URL", "https://galakokoreceminonu.com/api/reviews")


def review_id(r):
    return hashlib.md5(f"{r['author']}|{r['text']}".encode()).hexdigest()[:12]


def pending(reviews, done_ids):
    out = []
    for r in reviews:
        rid = review_id(r)
        if rid in done_ids:
            continue
        out.append({"id": rid, "yazar": r["author"], "puan": r["rating"], "yorum": r.get("text", "")})
    return sorted(out, key=lambda x: x["id"])


def main():
    if "--test" in sys.argv:
        rs = [{"author": "A", "rating": 5, "text": "x"}, {"author": "B", "rating": 1, "text": "y"}]
        p = pending(rs, {review_id(rs[0])})
        assert [x["yazar"] for x in p] == ["B"], p
        assert review_id(rs[0]) == review_id({"author": "A", "text": "x"})
        print("ok"); return
    done = set()
    if os.path.exists(DONE):
        done = {d["id"] for d in json.load(open(DONE))}
    data = json.load(urllib.request.urlopen(URL, timeout=20))
    print(json.dumps({"bekleyen_yorumlar": pending(data["reviews"], done)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
