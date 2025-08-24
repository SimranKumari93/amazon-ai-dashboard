import { useEffect, useState } from "react";
import { 
  fetchSaleEvents, 
  fetchSentiment, 
  fetchComments, 
  generateInsights, 
  scrapeRedditData,
  fetchSubreddits 
} from "./api";
import SentimentChart from "./components/SentimentChart";
import CommentsTable from "./components/CommentsTable";
import InsightsPanel from "./components/InsightsPanel";

export default function App() {
  const [saleEvents, setSaleEvents] = useState([]);
  const [subreddits, setSubreddits] = useState([]);
  const [sentimentData, setSentimentData] = useState(null);
  const [commentsData, setCommentsData] = useState({ total: 0, rows: [] });
  const [insights, setInsights] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [keywords, setKeywords] = useState("amazon prime day");
  const [isScrapingLoading, setIsScrapingLoading] = useState(false);

  // Load initial data on component mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [events, subredditsList] = await Promise.all([
          fetchSaleEvents(),
          fetchSubreddits()
        ]);
        setSaleEvents(events);
        setSubreddits(subredditsList);
        
        // Load existing comments and sentiment
        await loadCommentsAndSentiment();
      } catch (err) {
        setError("Failed to load initial data: " + err.message);
      }
    };
    
    loadInitialData();
  }, []);

  const loadCommentsAndSentiment = async () => {
    try {
      const [sentiment, comments] = await Promise.all([
        fetchSentiment().catch(() => ({ distribution: [] })),
        fetchComments(100, 0, keywords).catch(() => ({ total: 0, rows: [] }))
      ]);
      
      setSentimentData(sentiment);
      setCommentsData(comments);
    } catch (err) {
      console.error("Error loading comments and sentiment:", err);
    }
  };

  const handleScrapeData = async () => {
    if (!keywords.trim()) {
      setError("Please enter keywords to search");
      return;
    }

    setIsScrapingLoading(true);
    setError("");
    
    try {
      const keywordsList = keywords.split(",").map(k => k.trim()).filter(k => k);
      await scrapeRedditData(keywordsList, 50, null);
      
      // Wait a bit then refresh data
      setTimeout(async () => {
        await loadCommentsAndSentiment();
        setIsScrapingLoading(false);
      }, 2000);
      
    } catch (err) {
      setError("Failed to scrape data: " + err.message);
      setIsScrapingLoading(false);
    }
  };

  const handleGenerateInsights = async () => {
    setLoading(true);
    setError("");
    
    try {
      const result = await generateInsights(100);
      setInsights(result.insights);
    } catch (err) {
      setError("Failed to generate insights: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeywordsChange = async (newKeywords) => {
    setKeywords(newKeywords);
    if (newKeywords.trim()) {
      // Refresh comments when keywords change
      try {
        const keywordsList = newKeywords.split(",").map(k => k.trim()).filter(k => k);
        const comments = await fetchComments(100, 0, keywordsList.join(","));
        setCommentsData(comments);
      } catch (err) {
        console.error("Error filtering comments:", err);
      }
    }
  };

  return (
    <div style={{ 
      maxWidth: 1200, 
      margin: "0 auto", 
      padding: "20px", 
      fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif" 
    }}>
      {/* Header */}
      <div style={{ marginBottom: "30px", textAlign: "center" }}>
        <h1 style={{ 
          fontSize: "2.5rem", 
          fontWeight: "bold", 
          color: "#1f2937",
          marginBottom: "8px"
        }}>
          Amazon Sale AI Dashboard
        </h1>
        <p style={{ 
          fontSize: "1.1rem", 
          color: "#6b7280",
          margin: 0
        }}>
          Real-time sentiment analysis from Reddit discussions about Amazon sales
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{ 
          padding: "12px 16px", 
          backgroundColor: "#fef2f2", 
          border: "1px solid #fecaca",
          borderRadius: "8px", 
          color: "#dc2626",
          marginBottom: "20px"
        }}>
          {error}
        </div>
      )}

      {/* Search and Scraping Section */}
      <div style={{ 
        marginBottom: "30px",
        padding: "24px",
        backgroundColor: "white",
        borderRadius: "12px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
      }}>
        <h2 style={{ 
          fontSize: "1.5rem", 
          fontWeight: "600", 
          color: "#1f2937",
          marginBottom: "16px",
          margin: "0 0 16px 0"
        }}>
          Search & Scrape Reddit Data
        </h2>
        
        <div style={{ marginBottom: "16px" }}>
          <label style={{ 
            display: "block", 
            fontSize: "1rem", 
            fontWeight: "500", 
            color: "#374151",
            marginBottom: "8px"
          }}>
            Keywords (comma separated):
          </label>
          <input 
            type="text"
            value={keywords}
            onChange={(e) => handleKeywordsChange(e.target.value)}
            placeholder="amazon prime day, black friday, cyber monday"
            style={{
              width: "100%",
              padding: "12px 16px",
              fontSize: "1rem",
              border: "1px solid #d1d5db",
              borderRadius: "8px",
              backgroundColor: "white",
              color: "#374151"
            }}
          />
        </div>
        
        <button 
          onClick={handleScrapeData}
          disabled={isScrapingLoading}
          style={{
            padding: "12px 24px",
            fontSize: "1rem",
            fontWeight: "500",
            color: "white",
            backgroundColor: isScrapingLoading ? "#9ca3af" : "#3b82f6",
            border: "none",
            borderRadius: "8px",
            cursor: isScrapingLoading ? "not-allowed" : "pointer"
          }}
        >
          {isScrapingLoading ? "Scraping..." : "Scrape Reddit Data"}
        </button>
        
        {subreddits.length > 0 && (
          <div style={{ marginTop: "12px", fontSize: "0.9rem", color: "#6b7280" }}>
            Searching in: {subreddits.slice(0, 5).join(", ")} {subreddits.length > 5 && `and ${subreddits.length - 5} more`}
          </div>
        )}
      </div>

      {/* Dashboard Content */}
      <div style={{ 
        display: "grid", 
        gap: "24px",
        gridTemplateColumns: "1fr"
      }}>
        {/* Sentiment Chart */}
        <div style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "24px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
        }}>
          <h2 style={{ 
            fontSize: "1.5rem", 
            fontWeight: "600", 
            color: "#1f2937",
            marginBottom: "16px",
            margin: "0 0 16px 0"
          }}>
            Sentiment Distribution
          </h2>
          <SentimentChart distribution={sentimentData?.distribution || []} />
        </div>

        {/* Comments Table */}
        <div style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "24px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
        }}>
          <h2 style={{ 
            fontSize: "1.5rem", 
            fontWeight: "600", 
            color: "#1f2937",
            marginBottom: "16px",
            margin: "0 0 16px 0"
          }}>
            Reddit Comments ({commentsData.total})
          </h2>
          <CommentsTable rows={commentsData.rows || []} />
        </div>

        {/* Insights Panel */}
        <div style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "24px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
        }}>
          <h2 style={{ 
            fontSize: "1.5rem", 
            fontWeight: "600", 
            color: "#1f2937",
            marginBottom: "16px",
            margin: "0 0 16px 0"
          }}>
            AI Insights
          </h2>
          <InsightsPanel 
            text={insights} 
            onGenerate={handleGenerateInsights} 
            loading={loading} 
          />
        </div>
      </div>

      {/* Sale Events Info */}
      {saleEvents.length > 0 && (
        <div style={{ 
          marginTop: "30px",
          padding: "20px",
          backgroundColor: "#f9fafb",
          borderRadius: "12px",
          border: "1px solid #e5e7eb"
        }}>
          <h3 style={{ 
            fontSize: "1.2rem", 
            fontWeight: "600", 
            color: "#1f2937",
            marginBottom: "12px",
            margin: "0 0 12px 0"
          }}>
            Available Sale Events
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {saleEvents.map((event) => (
              <span 
                key={event.slug}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "#3b82f6",
                  color: "white",
                  borderRadius: "20px",
                  fontSize: "0.9rem",
                  fontWeight: "500"
                }}
              >
                {event.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ 
        textAlign: "center", 
        padding: "20px 0", 
        borderTop: "1px solid #e5e7eb",
        color: "#6b7280",
        fontSize: "0.9rem",
        marginTop: "40px"
      }}>
        Amazon Sale AI Dashboard v2.0 - Powered by Reddit & Gemini AI
      </div>
    </div>
  );
}