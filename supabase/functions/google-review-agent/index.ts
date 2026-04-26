// ============================================
// Gala Kokorec - Agentic Review Auto-Responder
// Supabase Edge Function (Deno)
// ============================================

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "authorization, content-type",
};

interface Review {
  name: string; // accounts/{account}/locations/{location}/reviews/{review}
  reviewId: string;
  reviewer: {
    displayName: string;
    profilePhotoUrl: string;
  };
  starRating: string;
  comment: string;
  createTime: string;
  updateTime: string;
}

interface Settings {
  [key: string]: string;
}

// --- Google OAuth ---
async function getAccessToken(
  clientId: string,
  clientSecret: string,
  refreshToken: string
): Promise<string> {
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Token refresh failed: ${err}`);
  }

  const data = await res.json();
  return data.access_token;
}

// --- Google Business Profile API ---
const ACCOUNTS_URL = "https://mybusinessaccountmanagement.googleapis.com/v1";
const INFO_URL = "https://mybusinessbusinessinformation.googleapis.com/v1";

async function googleFetch(url: string, token: string): Promise<any> {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Google API error (${res.status}): ${err}`);
  }
  return res.json();
}

async function detectAccountAndLocation(
  token: string
): Promise<{ account: string; location: string }> {
  const accountsData = await googleFetch(`${ACCOUNTS_URL}/accounts`, token);
  const account = accountsData.accounts?.[0]?.name;

  if (!account) throw new Error("Google Business hesabı bulunamadı");

  const locationsData = await googleFetch(
    `${INFO_URL}/${account}/locations?pageSize=10&readMask=name,title`,
    token
  );
  const location = locationsData.locations?.[0]?.name;

  if (!location) throw new Error("Google Business lokasyonu bulunamadı");

  return { account, location };
}

async function fetchReviews(
  token: string,
  account: string,
  location: string
): Promise<Review[]> {
  const data = await googleFetch(
    `${INFO_URL}/${location}/reviews?pageSize=50&orderBy=updateTime desc`,
    token
  );
  return data.reviews || [];
}

async function replyToReview(
  token: string,
  reviewName: string,
  comment: string
): Promise<any> {
  const res = await fetch(
    `${INFO_URL}/${reviewName}/reply`,
    {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ comment }),
    }
  );

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Reply failed: ${err}`);
  }

  return res.json();
}

// --- OpenRouter Agent ---
async function generateReply(
  apiKey: string,
  model: string,
  systemPrompt: string,
  authorName: string,
  rating: number,
  reviewText: string
): Promise<{ reply: string; sentiment: string }> {
  const starRating = "ONE_TWO_THREE_FOUR_FIVE".split("_")[rating - 1] || "FIVE";

  const messages = [
    {
      role: "system",
      content: systemPrompt,
    },
    {
      role: "user",
      content: `Bir müşteri yorum geldi. Lütfen bu yoruma uygun bir Türkçe cevap yaz.\n\nMüşteri: ${authorName}\nPuan: ${rating}/5\nYorum: "${reviewText || "(Yorum yazmamış, sadece puan vermiş)"}"\n\nJSON formatında cevap ver:\n{"reply": "cevabın buraya", "sentiment": "positive|negative|mixed|neutral"}`,
    },
  ];

  const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "HTTP-Referer": "https://galakokorec.com",
      "X-Title": "Gala Kokorec Review Agent",
    },
    body: JSON.stringify({
      model,
      messages,
      temperature: 0.7,
      max_tokens: 300,
      response_format: { type: "json_object" },
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`OpenRouter error (${res.status}): ${err}`);
  }

  const data = await res.json();
  const content = data.choices?.[0]?.message?.content || "";

  try {
    const parsed = JSON.parse(content);
    return {
      reply: parsed.reply || "Teşekkür ederiz!",
      sentiment: parsed.sentiment || "neutral",
    };
  } catch {
    return {
      reply: content.replace(/^"|"$/g, "") || "Teşekkür ederiz!",
      sentiment: "neutral",
    };
  }
}

// --- Helpers ---
function starRatingToNumber(rating: string): number {
  const map: Record<string, number> = {
    ONE: 1,
    TWO: 2,
    THREE: 3,
    FOUR: 4,
    FIVE: 5,
  };
  return map[rating] || 5;
}

// --- Main Agent Logic ---
async function runAgent(supabase: any) {
  console.log("[Agent] Starting review check...");

  // 1. Ayarlari yukle
  const { data: settingsData } = await supabase
    .from("gala_settings")
    .select("key, value");

  const settings: Settings = {};
  for (const row of settingsData || []) {
    settings[row.key] = row.value;
  }

  const required = [
    "google_client_id",
    "google_client_secret",
    "google_refresh_token",
    "openrouter_api_key",
  ];

  for (const key of required) {
    if (!settings[key]) {
      throw new Error(`Missing setting: ${key}`);
    }
  }

  // 2. Google access token al
  const accessToken = await getAccessToken(
    settings.google_client_id,
    settings.google_client_secret,
    settings.google_refresh_token
  );

  // 3. Account ve location tespit et (veya kaydedilmis degeri kullan)
  let account = settings.google_account_id;
  let location = settings.google_location_id;

  if (!account || !location) {
    const detected = await detectAccountAndLocation(accessToken);
    account = detected.account;
    location = detected.location;

    await supabase
      .from("gala_settings")
      .upsert([
        { key: "google_account_id", value: account },
        { key: "google_location_id", value: location },
      ]);
  }

  // 4. Yorumlari cek
  const reviews = await fetchReviews(accessToken, account, location);
  console.log(`[Agent] Fetched ${reviews.length} reviews from Google`);

  let newCount = 0;
  let repliedCount = 0;

  for (const review of reviews) {
    const reviewId = review.name;
    const rating = starRatingToNumber(review.starRating);

    // DB'de var mi kontrol et
    const { data: existing } = await supabase
      .from("gala_reviews")
      .select("id, status")
      .eq("google_review_id", reviewId)
      .single();

    if (existing) continue;

    newCount++;

    const { data: inserted } = await supabase
      .from("gala_reviews")
      .insert({
        google_review_id: reviewId,
        author_name: review.reviewer?.displayName || "Anonim",
        author_photo_url: review.reviewer?.profilePhotoUrl || "",
        rating,
        review_text: review.comment || "",
        review_date: review.createTime,
        status: "processing",
      })
      .select()
      .single();

    if (!inserted) continue;

    // Agent ile cevap uret
    try {
      const systemPrompt = settings.agent_system_prompt || `Sen Gala Kokoreç Eminönü'nün müşteri ilişkileri temsilcisisin. Google Maps yorumlarına Türkçe cevap yazıyorsun.

## Marka Profili
- İşletme: Gala Kokoreç, Eminönü Kutucu Sokak No:21, 1970'ten beri aynı adreste
- Ürünler: Kokoreç, midye dolma, nohut pilav, tavuk pilav
- Slogan: "Eminönü'nün Kokoreç Kralı"

## DİL TESPİTİ KURALI (ÇOK ÖNEMLİ)
- Müşterinin yorum hangi dilde yazılmışsa, cevabı AYNI DİLDE yaz
- Türkçe yorum → Türkçe cevap
- İngilizce yorum → İngilizce cevap
- Almanca yorum → Almanca cevap
- Rusça yorum → Rusça cevap
- Arapça yorum → Arapça cevap
- Diğer diller → İngilizce cevap (güvenli fallback)
- İmza her dilde "Gala Kokoreç Ekibi" kalır (marka adı değişmez)
- Tourist yorumlarında Eminönü'nün turistik konumunu vurgula

## Ton ve Dil Kuralları
- Profesyonel ama samimi bir dil kullan
- 1-2 cümle maksimum, kısa ve net ol
- Cevabın sonuna "Gala Kokoreç Ekibi" imzasını ekle
- Emoji kullanımı: Doğal, maksimum 1-2 adet (pozitif yorumlara 😊🙏 gibi, negatif yorumlara emoji koyma)

## PUANA GÖRE CEVAP STRATEJİSİ

### 5 Yıldız - Teşekkür
- Kısa teşekkür, memnuniyet vurgusu
- Tekrar bekleriz tarzı kapanış
- Örnek: "Yorumunuz için çok teşekkürler! Sizi her zaman en taze kokoreçle bekliyoruz 😊 — Gala Kokoreç Ekibi"

### 4 Yıldız - Teşekkür + Davet
- Teşekkür et, tekrar gelmeye davet et
- Örnek: "Değerlendirmeniz sağ olsun! Bir sonraki ziyaretinizde 5 yıldızı hak etmek için çalışıyoruz 🙏 — Gala Kokoreç Ekibi"

### 3 Yıldız - Empati + İyileştirme
- Geri bildirime değer ver, iyileştirme mesajı ver
- Örnek: "Geri bildiriminiz bizim için değerli. Deneyiminizi daha iyi hale getirmek için çalışıyoruz. Tekrar bekleriz — Gala Kokoreç Ekibi"

### 1-2 Yıldız - Savunma + Açıklama
- Tektar üzüntünü belirt AMA asla pes etme
- Durumu mantıklı şekilde açıkla, savun
- Sorunun geçici/özel bir durum olduğunu vurgula
- İletişim bilgisi ver: "Bize 0530 966 79 75'ten ulaşabilirsiniz"
- ASLA indirim, ücretsiz ürün veya hediye vaat etme
- ASLA özür dileme (empati göster ama suçlu kabul etme)
- Örnek: "Yaşadığınız durumun normal hizmet kalitemizin dışında olduğunu belirtmek isteriz. Yoğun saatlerde böyle durumlar olabiliyor. Detaylı konuşmak için bize 0530 966 79 75'ten ulaşabilirsiniz. — Gala Kokoreç Ekibi"

## KESİNLİKLE YASAK OLANLAR
- "Değerli müşterimiz", "sayın müşterimiz" gibi robotik ifadeler
- Yapay zeka kokan, şablon gibi cevaplar
- Emoji yağmuru (3'ten fazla emoji)
- İndirim, hediye, ücretsiz ürün teklifi
- "Yapay zeka", "bot", "otomatik" gibi kelimeler
- 3 cümleden uzun cevaplar
- Müşteriyi suçlayan veya kaba ton
- Yoruma farklı dilde cevap vermek (müşterinin dilinde yaz)

## JSON ÇIKTI FORMATI
Her cevap JSON formatında olmalı:
{"reply": "cevap metni burada — Gala Kokoreç Ekibi", "sentiment": "positive|negative|mixed|neutral"}`;

      const { reply, sentiment } = await generateReply(
        settings.openrouter_api_key,
        settings.openrouter_model || "google/gemini-2.5-pro",
        systemPrompt,
        review.reviewer?.displayName || "Müşteri",
        rating,
        review.comment || ""
      );

      // Google'a cevabi gonder
      await replyToReview(accessToken, reviewId, reply);

      // DB guncelle
      await supabase
        .from("gala_reviews")
        .update({
          status: "replied",
          reply_text: reply,
          replied_at: new Date().toISOString(),
          sentiment,
        })
        .eq("id", inserted.id);

      // Audit log
      await supabase.from("gala_audit_log").insert({
        review_id: inserted.id,
        action: "auto_replied",
        details: { reply, sentiment, rating },
      });

      repliedCount++;
      console.log(`[Agent] Replied to ${review.reviewer?.displayName}: "${reply.substring(0, 50)}..."`);

      // Rate limit: 2 saniye bekle
      await new Promise((r) => setTimeout(r, 2000));
    } catch (err) {
      console.error(`[Agent] Error processing review:`, err);

      await supabase
        .from("gala_reviews")
        .update({
          status: "failed",
          error_message: String(err),
        })
        .eq("id", inserted.id);

      await supabase.from("gala_audit_log").insert({
        review_id: inserted.id,
        action: "error",
        details: { error: String(err) },
      });
    }
  }

  console.log(`[Agent] Done. New: ${newCount}, Replied: ${repliedCount}`);

  return {
    total: reviews.length,
    new: newCount,
    replied: repliedCount,
    failed: newCount - repliedCount,
  };
}

// --- Edge Function Handler ---
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Authorization check
    const authHeader = req.headers.get("authorization");
    const cronSecret = Deno.env.get("CRON_SECRET");

    if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const result = await runAgent(supabase);

    return new Response(JSON.stringify({ success: true, result }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("[Agent] Fatal error:", err);
    return new Response(
      JSON.stringify({ success: false, error: String(err) }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
