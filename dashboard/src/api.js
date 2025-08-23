const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchEvents() {
  const r = await fetch(`${API}/events`);
  if (!r.ok) throw new Error("Failed to load events");
  return r.json();
}

export async function fetchSentiment(slug) {
  const r = await fetch(`${API}/sentiment?slug=${encodeURIComponent(slug)}`);
  if (!r.ok) throw new Error("No sentiment for this event");
  return r.json();
}

export async function fetchComments(slug, limit=200, offset=0) {
  const r = await fetch(`${API}/comments?slug=${encodeURIComponent(slug)}&limit=${limit}&offset=${offset}`);
  if (!r.ok) throw new Error("Failed to load comments");
  return r.json();
}

export async function fetchInsights(slug, maxComments=200) {
  const r = await fetch(`${API}/insights`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ slug, max_comments: maxComments })
  });
  if (!r.ok) throw new Error("Failed to generate insights");
  return r.json();
}
