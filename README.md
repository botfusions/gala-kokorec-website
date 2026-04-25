# Gala Kokoreç Web Sitesi - Güncelleme Notları

Bu dosya, proje üzerinde en son yapılan değişiklikleri ve gelecekte yapılacak düzenlemeleri takip etmek amacıyla oluşturulmuştur.

## 📌 Bugün Yapılan Geliştirmeler (Son Oturum)

1. **Menüye Sinematik Video Eklendi:**
   - Sitenin sahip olduğu MP4 formatındaki sinematik video (`Sinematik_Atmosfer_İçin_Video_Hazır.mp4`), **"Damak Zevkinize Göre"** başlığının hemen altına taşındı.
   - Videonun etrafına şık, koyu tonlarda (#1a1511) kalın bir çerçeve ve derinlik katan bir gölge (box-shadow) tasarımı yapıldı.
   - Video; kullanıcı sayfayı açtığında sessiz (`muted`), sürekli (`loop`) ve otomatik olarak (`autoplay`) çalışacak şekilde ayarlandı.

2. **Hero Bölümü Arka Planı Güncellendi:**
   - Sitenin en üstündeki karşılama (Hero) bölümünün arka planı, konsepte daha uygun olan statik görsel (`kokorec-ambiance.png`) ile değiştirilip eski haline getirildi.

3. **Eksik Menü Ürünleri ve Görselleri Tamamlandı:**
   - Menü alanındaki ürün listesine eksik olan şu kartlar dahil edildi:
     * **Tam Porsiyon Kokoreç** (Görsel: `haretli tam ekmek kokoreç.png`)
     * **Çeyrek Kokoreç** (Görsel: `çeyrek kokoreç.png`)
     * **Dürüm Kokoreç** (Görsel: `dürüm kokoreç.png`)
   - Mevcut ızgara (CSS Grid) yapısı bozulmadan öğeler entegre edildi.

---

## 📝 TO-DO / Yarın Yapılacaklar Listesi

* **Fiyatların Kaldırılması:** Menü öğelerinde yer alan tüm fiyat etiketleri siteden kaldırılacak.
* **Sosyal Medya Adresleri:** Sitenin uygun yerlerine (örneğin en alt kısma / footer) Facebook ve Instagram bağlantıları/adresleri eklenecek.
* **Google Business API Entegrasyonu:** Müşteri yorumlarını site üzerinde canlı göstermek için Google Business / Places API entegrasyonu yapılacak.
* **"Sizden Gelenler" Bölümü Oluşturulması:** Müşterilerin gönderdiği fotoğrafların sergileneceği "Sizden Gelen Resimler" adında özel bir bölüm eklenecek ve müşterilerin resim göndermesini rica eden bir çağrı metni yer alacak.
* **Dosya İsimlendirmeleri & SEO:** Resim dosyalarındaki Türkçe karakterler ve boşluklar web standartlarına uygun hale getirilecek (örn: `çeyrek kokoreç.png` -> `ceyrek-kokorec.png`).
* **Sipariş Linkleri:** Sipariş platformu butonlarına işletmenin doğrudan bağlantıları eklenecek.
* **Mobil Uyumluluk Kontrolü:** Son eklenen video ve yeni menü kartlarının mobilde (responsive) sorunsuz göründüğü teyit edilecek.
