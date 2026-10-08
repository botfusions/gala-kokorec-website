# Günlük yorum turu

1. `AGENTS.md`, `agent/SOUL.md`, `agent/sablonlar.md`, `agent/ornekler.md` dosyalarını oku. Cevabı puana uyan şablondan başlat, `{detay}` yerine yorumdaki somut şeyi koy.
2. Prompt'a eklenen "bekleyen yorumlar" JSON listesini al. Liste boşsa hiçbir dosya yazma, "bekleyen yorum yok" de ve bitir.
3. Yorum `yazar` alanı `mail:` ile başlıyorsa bu ham bir Google bildirim e-postasıdır: metinden yazar adını, yıldız sayısını ve yorum metnini sen çıkar; blokta gerçek yazar adını ve puanı kullan, id'yi aynen koru. Mailde yorum metni çoğu zaman `...` ile kesilmiştir; kesilen kısmı tahmin etme, görünen kısma ve puana göre yaz. Mail bir yorum bildirimi değilse (ör. haftalık özet) bloğu `durum: red` ile yaz.
3. Her yorum için SOUL.md'deki blok formatında bir taslak yaz. Sıra: JSON'daki sıra.
   Önce yorumun dilini tespit et, cevabı O DİLDE yaz. İngilizce yoruma Türkçe cevap yazmak hatadır. Bloğa `dil:` satırı ekle.
4. Blokları `agent/cevaplar/taslak-<bugün YYYY-MM-DD>.md` dosyasına yaz. Dosya varsa SADECE sonuna ekle (append). Dosyayı asla baştan yazma, mevcut blokları silme.
5. Jev kalite kapısını çalıştır: `python3 agent/scripts/jev_kontrol.py agent/cevaplar/taslak-<bugün>.md`. Betik her bloğa `jev:` satırı yazar. `jev: ihlal=...` alan bloğun cevabını ihlale göre bir kez yeniden yaz ve betiği tekrar çalıştır. İkinci denemede de ihlal kalırsa bırak, özette belirt.
6. Kısa özet ver: kaç yorum, kaç tanesi negatif, kaç Jev ihlali kaldı, dosya yolu.

Yapma: Google'a yazma, `cevaplanan.json`'a dokunma, `ornekler.md`'yi değiştirme.
