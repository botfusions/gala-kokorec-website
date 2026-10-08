# HANDOFF — Gala Kokoreç yorum ajanı (güncelleme: 9 Ekim 2026)

## Durum özeti
Google yorum bildirimleri e-postadan alınır, Hermes `gala` profili cevap taslağı yazar, Clef taslağı denetler, Cenk onaylar, onaylı cevaplar örnek setine ve Excel'e işlenir. Google'a otomatik gönderim yok. Cenk cevapları Google Maps'e elle yapıştırır.

Akış:
```
Gmail (Composio) → yorumlari_cek.py → Hermes gala (Codex Luna, medium) → taslak-*.md
→ jev_kontrol.py (cloudflare/clef, OpenRouter) → Cenk: durum onay/red → onayla.py
→ ornekler.md + cevaplanan.json + yorum-cevaplari.xlsx
```

## Canlı bileşenler
| Parça | Değer |
|---|---|
| Site | https://galakokoreceminonu.com · Netlify `gala-kokorec-eminonu` · repo botfusions/gala-kokorec-website |
| Yorum API'si (site) | `/api/reviews` (Places API, son 5 yorum) |
| Hermes profili | `gala` · `~/.hermes/profiles/gala` · model openai-codex / gpt-5.6-luna / medium |
| Cron | `e96b34cf3433` · `0 */4 * * *` · monitor script (çıktı değişmezse ajan uyanmaz) · deliver local |
| Zamanlayıcı | Hermes ana gateway, launchd `ai.hermes.gateway`, KeepAlive açık. Terminale bağlı değil |
| Gmail kaynağı | Composio hesabı `ca_xwSbAp0pP7D7`, user_id `gala-kokorec`, kutu cenk@galakokoreceminonu.com |
| Karar modeli | `cloudflare/clef` (OpenRouter `/api/v1/systemone`). `typesafe/jev-1.13` de çalışır. `clef-flash` 3/11, kullanma |
| Anahtarlar | Yalnızca `~/.hermes/profiles/gala/.env` içinde: `COMPOSIO_*`, `GALA_SOURCE=gmail`, `OPENROUTER_API_KEY`, `HERMES_WRITE_SAFE_ROOT` |

## Dosyalar (repo)
- `AGENTS.md` — ajanın her koşuda okuma sırası
- `agent/SOUL.md` — kimlik, ton, dil kuralı, yasaklar, taslak blok formatı
- `agent/sablonlar.md` — olumlu/olumsuz şablon iskeletleri (TR/EN)
- `agent/ornekler.md` — onaylı cevaplar, eğitim seti (şu an 10 örnek)
- `agent/prompts/gunluk-yorum-turu.md` — cron görevi (taslak yaz → Clef kapısı → özet)
- `agent/scripts/yorumlari_cek.py` — kaynak seçici (`GALA_SOURCE`: boş=site, `gmail`, `supabase`)
- `agent/scripts/jev_kontrol.py` — kalite kapısı, `--test agent/tests/jev_vakalar.md` (11 vaka)
- `agent/scripts/onayla.py` — onay işleyici + Excel üretici
- `agent/cevaplar/` — `taslak-*.md`, `cevaplanan.json` (tek doğruluk kaynağı), `yorum-cevaplari.xlsx`

## Doğrulananlar
- Clef test seti 11/11, üç ölçümde kararlı. Jev ile aynı sonuç.
- Gmail kaynağı gerçek bildirim mailinden yorum ve Google yorum kimliğini çıkarıyor.
- Cron elle tetiklendi, Codex ile tamamlandı, taslak yazıldı.
- Excel'de 7 cevap var (5 Ekim'den 8 Ekim'e).
- Gece 00:00 OTOMATİK koşusu 9 Ekim'de çalıştı: `completed`, `last_status: ok`, `failure_streak: 0`. Yeni taslak dosyası oluşmadı. Koşu çıktısı açılmadı, Gmail'de gerçekten yeni yorum maili olmadığı kesinleşmedi.
- Mac uykuya geçmiyor (`pmset sleep 0`, caffeinate açık).

- Okundu eşlemesi: Excel'de "Google'a yazıldı" kolonu dolu satırların bildirim mailleri sonraki turda okundu olur (`okundu_senkron`). Mail okundu yapma Composio ile canlı doğrulandı (Oğuzhan'ın 2 maili). Excel okuyucu standart kütüphane, `openpyxl` gerektirmez.

## Doğrulanmayanlar
- Excel'den tetiklenen okundu akışı uçtan uca görülmedi: parça parça sınandı (Excel okuma + sahte işaretleyici, gerçek mail işaretleme elle). İlk gerçek tarih girişinde sonucu kontrol et.
- 04:00 ve sonraki otomatik koşular henüz izlenmedi. Yeni yorum gelince otomatik koşunun taslak yazdığı görülmedi.
- Cron içinde Clef adımı bir kez OpenRouter 529 hatası aldı. Yeniden deneme eklendi, canlı cron'da tekrar sınanmadı.
- `alpha/decisions` yedek ucu hiç tetiklenmedi.

## Sıradaki işler
1. **Takip:** 04:00 ve sonraki koşuları kontrol et (00:00 koşusu ok).
   ```
   hermes -p gala cron runs e96b34cf3433
   ```
   `jobs.json` içinde `last_status: ok` ve `failure_streak: 0` olmalı.
2. Cenk yeni taslakları onaylar, cevapları Google'a yapıştırır, Excel'in son kolonuna tarih yazar.
3. **Business Profile API onayı** (başvuru gitti, 3-14 iş günü). Gelince: `GALA_SOURCE=supabase`, edge function'ı çalıştır, onaylı cevapları Google'a gönderen adımı ekle. Tam yorum metni de o zaman gelir (mail bildirimi metni kısaltıyor).
4. **VPS (Coolify) — acele yok, henüz başlanmadı.** Taşırken çıkacak noktalar:
   - Codex girişi OAuth. VPS'te başsız giriş yöntemi çözülmeli.
   - `agent/SOUL.md` ve monitor script kopyası Mac yoluna bağlı (`/Users/cenktk/...`). `GALA_REPO` ortam değişkeni var, SOUL.md'deki yol elle değişmeli.
   - Taslaklar VPS diskinde kalır. Cenk'in onay yapabilmesi için repo'ya otomatik commit ya da küçük bir web arayüzü gerekir.
   - Profil klasörü ve `.env` taşınacak. Anahtarlar sohbet kaydına yazılmamalı.

## Tuzaklar
- Hermes betik için symlink kabul etmiyor. `yorumlari_cek.py` değişince şunu yap:
  ```
  cp agent/scripts/yorumlari_cek.py ~/.hermes/profiles/gala/scripts/gala_yorumlari_cek.py
  ```
  Sonra kopyadaki `REPO =` satırını Mac yoluna sabitle (`os.environ.get('GALA_REPO', '/Users/cenktk/Documents/open/gala-kokorec-website')`).
- Ajan bir kez taslak dosyasını baştan yazıp 5 bloğu sildi. Prompt'ta "yalnızca sona ekle" kuralı var. Dosyayı git'ten geri alabilirsin.
- Clef soru kimliklerinde Türkçe karakter kabul etmez. `jev_kontrol.py` içinde `aid()` çevirir.
- Gala profili medya'dan klonlandı. Yazma kökü `HERMES_WRITE_SAFE_ROOT` ile bu repoya çevrildi.
- Mail bildirimindeki yorum metni "..." ile kesik gelir. Ajan tahmin etmemeli.
- Bu klasöre özel Hermes profili var. Diğer profillere ve Composio hesaplarına dokunma.

## Git
Branch `main`, uzak ile senkron. Son kod commit'i `34f5770`. Commit mesajları Türkçe, `Co-Authored-By` satırıyla biter.
