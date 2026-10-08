-- ============================================
-- Gala Kokorec - Agentic Review Auto-Responder
-- Supabase Migration
-- ============================================

-- 1. Reviews tablosu
CREATE TABLE IF NOT EXISTS gala_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  google_review_id TEXT UNIQUE NOT NULL,
  author_name TEXT,
  author_photo_url TEXT,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review_text TEXT DEFAULT '',
  review_date TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'new'
    CHECK (status IN ('new', 'processing', 'replied', 'failed', 'skipped')),
  reply_text TEXT,
  replied_at TIMESTAMPTZ,
  error_message TEXT,
  sentiment TEXT CHECK (sentiment IN ('positive', 'negative', 'mixed', 'neutral')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Settings tablosu (API keyler ve config)
CREATE TABLE IF NOT EXISTS gala_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  description TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Audit log
CREATE TABLE IF NOT EXISTS gala_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  review_id UUID REFERENCES gala_reviews(id),
  action TEXT NOT NULL,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Indexler
CREATE INDEX IF NOT EXISTS idx_gala_reviews_status ON gala_reviews(status);
CREATE INDEX IF NOT EXISTS idx_gala_reviews_created ON gala_reviews(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_gala_reviews_google_id ON gala_reviews(google_review_id);

-- 5. Updated_at trigger
CREATE OR REPLACE FUNCTION gala_update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_gala_reviews_updated ON gala_reviews;
CREATE TRIGGER trigger_gala_reviews_updated
  BEFORE UPDATE ON gala_reviews
  FOR EACH ROW EXECUTE FUNCTION gala_update_updated_at();

-- 6. Row Level Security
ALTER TABLE gala_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE gala_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE gala_audit_log ENABLE ROW LEVEL SECURITY;

-- Service role tam erisim (edge function icin)
CREATE POLICY "Service role full access" ON gala_reviews
  FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access" ON gala_settings
  FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access" ON gala_audit_log
  FOR ALL USING (auth.role() = 'service_role');

-- 7. Baslangic ayarlari
INSERT INTO gala_settings (key, value, description) VALUES
  ('google_client_id', '', 'Google OAuth Client ID'),
  ('google_client_secret', '', 'Google OAuth Client Secret'),
  ('google_refresh_token', '', 'Google OAuth Refresh Token'),
  ('google_account_id', '', 'Google Business Account ID (auto-detected)'),
  ('google_location_id', '', 'Google Business Location ID (auto-detected)'),
  ('openrouter_api_key', '', 'OpenRouter API Key'),
  ('openrouter_model', 'anthropic/claude-sonnet-4-20250514', 'OpenRouter model ID'),
  ('agent_system_prompt', 'Sen Gala Kokoreç Eminönü''nün sosyal medya yöneticisisin. Müşteri yorumlarına Türkçe, samimi ve profesyonel cevaplar yaz. Kural: Kısa (1-3 cümle), samimi, doğal Türkçe. Pozitif yorumlara teşekkür et, negatif yorumlara anlayışlı ol ve geri gelmelerini iste. Asla İngilizce kullanma. Restoran: Gala Kokoreç, Eminönü Kutucu Sokak No:21, 1970''ten beri hizmet veriyor.', 'Agent system prompt'),
  ('cron_enabled', 'true', 'Otomatik yorum kontrolü aktif mi'),
  ('cron_interval_minutes', '60', 'Kontrol sıklığı (dakika)')
ON CONFLICT (key) DO NOTHING;

-- 8. RPC: Yeni yorumlari getir
CREATE OR REPLACE FUNCTION gala_get_new_reviews()
RETURNS SETOF gala_reviews AS $$
  SELECT * FROM gala_reviews WHERE status = 'new' ORDER BY created_at ASC;
$$ LANGUAGE sql SECURITY DEFINER;

-- 9. RPC: Istatistikler
CREATE OR REPLACE FUNCTION gala_get_review_stats()
RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'total', COUNT(*),
    'new', COUNT(*) FILTER (WHERE status = 'new'),
    'replied', COUNT(*) FILTER (WHERE status = 'replied'),
    'failed', COUNT(*) FILTER (WHERE status = 'failed'),
    'avg_rating', ROUND(AVG(rating)::numeric, 1)
  ) INTO result FROM gala_reviews;
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
