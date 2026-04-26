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
- [ ] Google Business API kota aktifleşmesi (bekleniyor)
- [ ] Netlify'a GOOGLE_PLACES_API_KEY env ekleme
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
- [ ] Google Business API kota aktifleşmesini bekle (1-24 saat)
- [ ] Netlify environment variable: GOOGLE_PLACES_API_KEY ekle
- [ ] pg_cron ile saatlik otomatik yorum kontrolü kur
- [ ] Edge function'ı manuel test et (kota gelince)

## Deploy

```bash
git add .
git commit -m "açıklama"
git push origin main
# Netlify otomatik deploy yapar
```

## Lisans

Tüm hakları saklıdır. Gala Kokoreç Eminönü.
