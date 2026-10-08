const PLACE_ID = "ChIJQe3kbFS5yhQRoCiMX0s4A04";
const FIELDS = "reviews,rating,user_ratings_total,name";
const CACHE_TTL = 3600;

let cached = null;
let cachedAt = 0;

export default async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
      },
    });
  }

  const apiKey = process.env.GOOGLE_PLACES_API_KEY;
  if (!apiKey) {
    return new Response(
      JSON.stringify({ error: "API key not configured" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  const now = Date.now();
  if (cached && now - cachedAt < CACHE_TTL * 1000) {
    return new Response(JSON.stringify(cached), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": `public, max-age=${CACHE_TTL}`,
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  try {
    const url = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${PLACE_ID}&fields=${FIELDS}&key=${apiKey}&language=tr`;
    const res = await fetch(url);
    const data = await res.json();

    if (data.status !== "OK") {
      return new Response(
        JSON.stringify({ error: data.status, message: data.error_message }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      );
    }

    const result = {
      rating: data.result.rating,
      total: data.result.user_ratings_total,
      name: data.result.name,
      reviews: (data.result.reviews || []).map((r) => ({
        author: r.author_name,
        photo: r.profile_photo_url,
        rating: r.rating,
        text: r.text,
        time: r.relative_time_description,
      })),
    };

    cached = result;
    cachedAt = now;

    return new Response(JSON.stringify(result), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": `public, max-age=${CACHE_TTL}`,
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ error: "fetch_failed", message: err.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};

export const config = { path: "/api/reviews" };
