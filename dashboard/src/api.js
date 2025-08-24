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

// Get all sale events
export async function fetchSaleEvents() {
  const response = await fetch(`${API_BASE}/sale-events`);
  return handleResponse(response);
}

// Get all subreddits
export async function fetchSubreddits() {
  const response = await fetch(`${API_BASE}/subreddits`);
  return handleResponse(response);
}

// Get comments with optional keyword filtering
export async function fetchComments(limit = 100, offset = 0, keywords = null) {
  let url = `${API_BASE}/comments?limit=${limit}&offset=${offset}`;
  if (keywords) {
    url += `&keywords=${encodeURIComponent(keywords)}`;
  }
  const response = await fetch(url);
  return handleResponse(response);
}

// Get sentiment summary
export async function fetchSentiment() {
  const response = await fetch(`${API_BASE}/sentiment`);
  return handleResponse(response);
}

// Scrape Reddit data
export async function scrapeRedditData(keywords = null, maxPosts = 50, subreddits = null) {
  const response = await fetch(`${API_BASE}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      keywords: keywords,
      max_posts: maxPosts, 
      subreddits: subreddits 
    }),
  });
  return handleResponse(response);
}

// Generate insights
export async function generateInsights(maxComments = 100) {
  const response = await fetch(`${API_BASE}/insights`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ max_comments: maxComments }),
  });
  return handleResponse(response);
}