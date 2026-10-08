# Gala Kokoreç Eminönü - Web Sitesi

Gala Kokoreç'in resmi web sitesi. Eminönü Kutucu Sokak No:21'de 1970'den bu yana aynı adreste hizmet vermektedir.

## Canlı Site

- **GitHub**: https://github.com/botfusions/gala-kokorec-website
- **Netlify**: Otomatik deploy (GitHub push sonrası)

## Teknolojiler

- Tek sayfa statik HTML5
- CSS Custom Properties (dark theme)
- GSAP + ScrollTrigger (animasyonlar)
- Lenis (smooth scroll)
- Lucide Icons
- Google Fonts (Space Grotesk + Inter)
- Hero video döngüsü (MP4)
- Netlify Functions (Google Places API proxy)
- Supabase Edge Functions (agentic review responder)

## Site Bölümleri

| Bölüm | Açıklama |
|-------|----------|
| Navbar | SVG logo + navigasyon linkleri |
| Hero | Video döngüsü arka plan, 4.4 Google puanı, 19 yıl, çalışma saatleri |
| Menü | 6 ürün kartı (Yarım, Üç Çeyrek, Tam Kokoreç, Nohut Pilav, Tavuk Pilav, Midye Dolma) |
| Midye Dolma İnfografik | 4 özellik kartı + ürün görseli, tam ekran bölümlü tasarım |
| Hakkımızda | 19 yıldır aynı adreste vurgusu, 4 özellik (Taze, Hijyen, Adres, Çalışma Saatleri) |
| Yorumlar | Google Places API ile canlı yorumlar (Netlify function proxy) |
| Konum | Google Maps embed + iletişim bilgileri |
| Online Sipariş | Yemeksepeti, Getir, Trendyol linkleri |
| Footer | SVG logo + sosyal medya linkleri (Instagram, Facebook) |

## Google Business & Otomasyon

### Mimari

```
Site (Netlify)                    Backend (Supabase)
┌──────────────────┐              ┌─────────────────────────┐
│ index.html       │              │ gala_reviews            │
│ netlify/functions│              │ gala_settings           │
│   └─reviews.mjs  │──Places──▶  │ gala_audit_log          │
│                  │   API        │                         │
└──────────────────┘              │ Edge Function           │
                                  │  └─google-review-agent  │
                                  │     ├─ Google Business  │
                                  │     │   Profile API     │
                                  │     └─ OpenRouter LLM   │
                                  └─────────────────────────┘
```

### Supabase Tabloları

| Tablo | Açıklama |
|-------|----------|
| `gala_reviews` | Google yorumları + otomatik cevaplar |
| `gala_settings` | API keyler ve konfigürasyon |
| `gala_audit_log` | İşlem logları |

### Edge Function: google-review-agent

- Google Business Profile API'den yeni yorumları çeker
- OpenRouter (Gemini 2.5 Pro) ile Türkçe cevap üretir
- Cevabı Google'a geri gönderir
- Sonuçları gala_reviews tablosuna kaydeder

### Kurulum Durumu

- [x] Google Cloud Console — Places API + Business Profile API etkin
- [x] OAuth Desktop App credential oluşturuldu
- [x] OAuth refresh token alındı
- [x] Supabase tabloları oluşturuldu (gala_ prefix)
- [x] Edge function deploy edildi
- [x] OpenRouter API key kaydedildi
- [x] Siteye yorum bileşeni eklendi (Netlify function)
- [x] Netlify'a GOOGLE_PLACES_API_KEY env eklendi
- [x] Google Search Console site doğrulaması tamamlandı (DNS TXT)
- [x] Google site verification meta tag eklendi
- [ ] Google Business API erişim onayı (başvuru gönderildi, 3-14 iş günü)
- [ ] pg_cron ile otomatik yorum kontrolü

### Kritik Environment Variables

**Netlify:**
- `GOOGLE_PLACES_API_KEY` — Yorum gösterimi için

**Supabase gala_settings tablosu:**
- `google_client_id` ✅
- `google_client_secret` ✅
- `google_refresh_token` ✅
- `openrouter_api_key` ✅
- `openrouter_model` → `google/gemini-2.5-pro` ✅

## Yapılacaklar

### Web Sitesi
- [ ] Facebook linkini footer'a ekle
- [ ] Dosya isimlendirmeleri web standartlarına uygun hale getir (Türkçe karakter → ASCII)
- [ ] Sipariş platformu butonlarına doğrudan linkler (Yemeksepeti, Trendyol, Getir)
- [ ] Mobil uyumluluk kontrolü ve düzeltmeleri
- [ ] "Sizden Gelenler" bölümü (müşteri fotoğrafları)
- [ ] Hero video - mobilde performans optimizasyonu (poster image fallback)

### Google Business & Otomasyon
- [ ] Google Business API erişim onayını bekle (3-14 iş günü)
- [ ] pg_cron ile saatlik otomatik yorum kontrolü kur
- [ ] Edge function'ı manuel test et (onay gelince)

## Deploy

```bash
git add .
git commit -m "açıklama"
git push origin main
# Netlify otomatik deploy yapar
```

## Lisans

Tüm hakları saklıdır. Gala Kokoreç Eminönü.

## Google Yorum Cevap Ajanı (Hermes `gala` profili)

Kalite kapısı modeli: Cloudflare Clef (`cloudflare/clef`, OpenRouter `systemone` ucu, Jev uyumlu API). `JEV_MODEL=typesafe/jev-1.13` ile Jev'e dönülür. `cloudflare/clef-flash` testte 3/11 verdi, kullanma.

Bu klasöre bağlı Hermes profili 4 saatte bir (00, 04, 08, 12, 16, 20) cenk@galakokoreceminonu.com kutusundaki Google yorum bildirimlerini kontrol eder; yeni yorum varsa cevap taslağı yazar ve Jev ile denetler. Yeni mail yoksa ajan uyanmaz. Google'a hiçbir şey göndermez.

| Parça | Yer |
|---|---|
| Kimlik, ton, puan stratejisi | `agent/SOUL.md` |
| Onaylı örnekler (eğitim seti) | `agent/ornekler.md` |
| Günlük görev | `agent/prompts/gunluk-yorum-turu.md` |
| Yorum çekme (monitor script) | `agent/scripts/yorumlari_cek.py` → kopyası `~/.hermes/profiles/gala/scripts/gala_yorumlari_cek.py` |
| Taslaklar | `agent/cevaplar/taslak-YYYY-MM-DD.md` |
| Cevaplanan kayıt | `agent/cevaplar/cevaplanan.json` |

Onay döngüsü: taslak dosyasında `durum: bekliyor` → `onay` (cevabı düzeltebilirsin) ya da `red`, sonra:

```
python3 agent/scripts/onayla.py agent/cevaplar/taslak-2026-10-08.md
```

Jev kalite kapısı (OpenRouter üzerinden `typesafe/jev-1.13`, `OPENROUTER_API_KEY` env ya da `~/.hermes/profiles/gala/.env`; dil, özür, vaat, şablon, suçlama, detay, duygu + imza/cümle/emoji kontrolü), her bloğa `jev:` satırı yazar, `--dry` yalnız raporlar, `-v` ham olasılıkları basar:

```
python3 agent/scripts/jev_kontrol.py agent/cevaplar/taslak-2026-10-08.md
```

Etiketli vakalarla isabet ölçümü: `python3 agent/scripts/jev_kontrol.py --test agent/tests/jev_vakalar.md`

Onaylanan cevap `ornekler.md`'ye girer, ajan bir sonraki turda ondan öğrenir.

Cevabı Google'a yapıştırınca `agent/cevaplar/yorum-cevaplari.xlsx` içindeki "Google'a yazıldı" kolonuna tarih yaz. Sonraki 4 saatlik turda (ya da elle `python3 agent/scripts/yorumlari_cek.py --okundu <google_yorum_id>`) o yorumun bildirim maili Gmail'de okundu olur. Elle çalıştırmak için `hermes -p gala cron run e96b34cf3433`.
Google Business Profile API onayı gelince onaylanan cevapları gönderme adımı eklenecek.
