const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// Utility function to handle API responses
async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  const data = await response.json();
  return data.success ? data.data : data;
}

// Get all sale events with processing status
export async function fetchEvents() {
  const response = await fetch(`${API_BASE}/events`);
  return handleResponse(response);
}

// Get detailed data for a specific event
export async function fetchEventData(eventSlug) {
  const response = await fetch(`${API_BASE}/events/${eventSlug}`);
  return handleResponse(response);
}

// Process an event (scrape + analyze + insights)
export async function processEvent(eventSlug, keywords = null, maxPosts = 50, forceRefresh = false) {
  const response = await fetch(`${API_BASE}/events/${eventSlug}/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      event_slug: eventSlug,
      keywords: keywords,
      max_posts: maxPosts,
      force_refresh: forceRefresh
    }),
  });
  return handleResponse(response);
}

// Get processing status for an event
export async function fetchEventStatus(eventSlug) {
  const response = await fetch(`${API_BASE}/events/${eventSlug}/status`);
  return handleResponse(response);
}