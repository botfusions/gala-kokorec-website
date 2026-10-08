#!/usr/bin/env python3
"""Sitedeki /api/reviews uç noktasından yorumları çeker, cevaplanmamış olanları JSON basar.
Hermes --monitor-script olarak çalışır: çıktı değişmezse ajan uyanmaz.
ponytail: Places API son 5 yorumu verir; Business Profile API onayı gelince kaynağı oraya çevir."""
import glob, hashlib, json, os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DONE = os.path.join(REPO, "agent", "cevaplar", "cevaplanan.json")
URL = os.environ.get("GALA_REVIEWS_URL", "https://galakokoreceminonu.com/api/reviews")


def review_id(r):
    if r.get("_id"):
        return r["_id"]
    return hashlib.md5(f"{r['author']}|{r['text']}".encode()).hexdigest()[:12]


def pending(reviews, done_ids):
    out = []
    for r in reviews:
        rid = review_id(r)
        if rid in done_ids:
            continue
        item = {"id": rid, "yazar": r["author"], "puan": r["rating"], "yorum": r.get("text", "")}
        if r.get("google_review_id"):
            item["google_review_id"] = r["google_review_id"]
        if r.get("yorum_tarihi"):
            item["yorum_tarihi"] = r["yorum_tarihi"]
        out.append(item)
    return sorted(out, key=lambda x: x["id"])


def composio(tool, arguments):
    body = json.dumps({"connected_account_id": os.environ["COMPOSIO_CONNECTED_ACCOUNT"],
                       "user_id": os.environ["COMPOSIO_USER_ID"], "arguments": arguments}).encode()
    req = urllib.request.Request(f"https://backend.composio.dev/api/v3/tools/execute/{tool}", data=body,
                                 headers={"x-api-key": os.environ["COMPOSIO_API_KEY"], "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    if not d.get("successful"):
        sys.exit(f"composio hata ({tool}): {d.get('error')}")
    return d["data"]


def gmail_reviews(done_ids):
    """Composio üzerinden cenk@galakokoreceminonu.com kutusundaki Google yorum bildirimlerini çeker.
    Ayrıştırmayı ajan yapar: her mail tek 'yorum' alanı olarak ham metinle gider, id = Gmail messageId.
    ponytail: Google bildirim şablonu değişse bile regex kırılmaz; ajan metni okur."""
    d = composio("GMAIL_FETCH_EMAILS", {"query": os.environ.get("GALA_GMAIL_QUERY", "from:businessprofile-noreply@google.com subject:(yorum yaptı OR review) newer_than:30d"),
                                       "max_results": 20, "include_payload": False})
    out = []
    for lst in d.get("messages", []):
        mid = lst.get("messageId")
        if not mid or mid in done_ids:
            continue
        m = composio("GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", {"message_id": mid, "format": "full"})  # liste çağrısı yalnızca önizleme verir
        raw = m.get("subject", "") + "\n" + (m.get("messageText") or "")
        text = re.sub(r"[\u200b\u200c\u200d\u00a0\s]+", " ", re.sub(r"<https?://[^>]+>", " ", raw)).strip()
        text = text.split("Yorumu yanıtla")[0].split("Reply to review")[0].strip()[:1500]  # mail kuyruğundaki HTML/footer atılır
        link = re.search(r"https://business\.google\.com/n/\d+/reviews/[A-Za-z0-9_-]+", m.get("messageText") or "")
        grid = link.group(0).rsplit("/", 1)[1] if link else None
        if grid and grid in done_ids or grid and any(o.get("google_review_id") == grid for o in out):
            continue  # aynı yorumun ikinci bildirimi
        out.append({"author": "mail:" + mid, "rating": 0, "text": text, "_id": grid or mid, "google_review_id": grid,
                    "yorum_tarihi": (m.get("messageTimestamp") or lst.get("messageTimestamp") or "")[:10]})
    return out


def main():
    if "--test" in sys.argv:
        rs = [{"author": "A", "rating": 5, "text": "x"}, {"author": "B", "rating": 1, "text": "y"}]
        p = pending(rs, {review_id(rs[0])})
        assert [x["yazar"] for x in p] == ["B"], p
        assert review_id(rs[0]) == review_id({"author": "A", "text": "x"})
        assert pending([{"author": "mail:m1", "rating": 0, "text": "t", "_id": "m1"}], {"m1"}) == []
        print("ok"); return
    done = set()
    if os.path.exists(DONE):
        done = {d["id"] for d in json.load(open(DONE))}
    for f in glob.glob(os.path.join(REPO, "agent", "cevaplar", "taslak-*.md")):  # taslağı yazılmış, onay bekleyen
        done |= set(re.findall(r"^### (\S+) ·", open(f, encoding="utf-8").read(), re.M))
    if os.environ.get("GALA_SOURCE") == "supabase":
        # Business Profile API onayı gelince: edge function gala_reviews'a yazar, buradan okuruz (status=new)
        req = urllib.request.Request(
            os.environ["SUPABASE_URL"] + "/rest/v1/gala_reviews?status=eq.new&select=google_review_id,author_name,rating,review_text&order=review_date.desc",
            headers={"apikey": os.environ["SUPABASE_SERVICE_KEY"], "Authorization": "Bearer " + os.environ["SUPABASE_SERVICE_KEY"]})
        rows = json.load(urllib.request.urlopen(req, timeout=20))
        reviews = [{"author": r["author_name"], "rating": r["rating"], "text": r["review_text"] or ""} for r in rows]
    elif os.environ.get("GALA_SOURCE") == "gmail":
        reviews = gmail_reviews(done)
    else:
        reviews = json.load(urllib.request.urlopen(URL, timeout=20))["reviews"]
    print(json.dumps({"bekleyen_yorumlar": pending(reviews, done)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
