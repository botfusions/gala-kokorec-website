# Cevap şablonları

Şablon iskelettir, kopyalanmaz. Ajan her cevapta `{detay}` yerine müşterinin yazdığı somut bir şeyi koyar
(ürün, servis, konum, kişi). Detay yoksa `{detay}` cümlesini atar. İmza her dilde aynen: "Gala Kokoreç Ekibi".
Yorum Türkçe ve İngilizce dışında bir dildeyse ajan şablonu o dile çevirir, yapıyı korur.

## Olumlu (5★)
**TR:** {İsim}, {detay} için teşekkürler! Sizi yine en taze kokoreçle bekliyoruz 😊 — Gala Kokoreç Ekibi
**EN:** Thank you, {Name}! Glad you enjoyed {detail}. See you again in Eminönü 😊 — Gala Kokoreç Ekibi

## Olumlu, davetli (4★)
**TR:** Değerlendirmeniz için sağ olun! {detay} notunuzu aldık, bir sonraki ziyarette 5 yıldızı hak etmek için çalışacağız 🙏 — Gala Kokoreç Ekibi
**EN:** Thanks for the review! We noted {detail}; next time we'll work to earn that fifth star 🙏 — Gala Kokoreç Ekibi

## Karışık (3★)
**TR:** {detay} konusundaki geri bildiriminiz bizim için değerli. Ustalarımızla paylaşacağız, yeniden ağırlamak isteriz — Gala Kokoreç Ekibi
**EN:** Your feedback on {detail} matters to us. We'll share it with our team and hope to host you again — Gala Kokoreç Ekibi

## Olumsuz (1-2★) — özür yok, hediye yok, telefon var
**TR:** {detay} yaşamanız bizi üzdü; bu, alıştığınız Gala kalitesi değil. Yoğun saatlerde böyle aksaklıklar olabiliyor. Detayı konuşmak isteriz: 0533 072 61 30 — Gala Kokoreç Ekibi
**EN:** We're sorry to hear about {detail}; that's not the Gala standard. Rush hours can cause slips like this. We'd like to talk it through: +90 533 072 61 30 — Gala Kokoreç Ekibi

## Olumsuz, haksız/şüpheli iddia (1★, metin yok ya da bizimle ilgisiz)
**TR:** Kayıtlarımızda böyle bir duruma rastlamadık. Ziyaretinizi doğrulayıp konuşmak isteriz: 0533 072 61 30 — Gala Kokoreç Ekibi
**EN:** We couldn't match this to any visit on our side. Happy to verify and talk: +90 533 072 61 30 — Gala Kokoreç Ekibi

## Sadece puan, metin yok
**5-4★ TR:** Puanınız için teşekkürler, tekrar bekleriz 😊 — Gala Kokoreç Ekibi
**5-4★ EN:** Thanks for the rating, see you again 😊 — Gala Kokoreç Ekibi
**1-3★ TR:** Deneyiminizi duymak isteriz: 0533 072 61 30 — Gala Kokoreç Ekibi
**1-3★ EN:** We'd like to hear what went wrong: +90 533 072 61 30 — Gala Kokoreç Ekibi

## Metin kesik geldiyse (mail bildirimi, `...` ile bitiyor)
Görünen kısımdaki detayı kullan. Kesilen kısım hakkında varsayım yapma.
