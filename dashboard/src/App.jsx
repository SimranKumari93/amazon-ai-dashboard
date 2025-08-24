import { useEffect, useState } from "react";
import { fetchEvents, fetchEventData, processEvent, fetchEventStatus } from "./api";

export default function App() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [eventData, setEventData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [error, setError] = useState("");
  const [keywords, setKeywords] = useState("amazon sale, amazon deals, amazon discount");

  // Load events on mount
  useEffect(() => {
    loadEvents();
  }, []);

  // Load event data when event is selected
  useEffect(() => {
    if (selectedEvent) {
      loadEventData(selectedEvent.slug);
    } else {
      setEventData(null);
    }
  }, [selectedEvent]);

  const loadEvents = async () => {
    try {
      setError("");
      const eventsData = await fetchEvents();
      setEvents(eventsData);
    } catch (err) {
      setError("Failed to load events: " + err.message);
    }
  };

  const loadEventData = async (eventSlug) => {
    try {
      setLoading(true);
      setError("");
      const data = await fetchEventData(eventSlug);
      console.log('Loaded event data:', data);
      setEventData(data);
    } catch (err) {
      console.log('Error loading event data:', err);
      // Always create default structure for UI to work
      const defaultData = { 
        event: { slug: eventSlug, is_processed: false, comments_count: 0 }, 
        comments: [], 
        sentiment_distribution: [], 
        insights: "" 
      };
      setEventData(defaultData);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeComments = async () => {
    if (!selectedEvent) return;

    try {
      setProcessing(true);
      setProcessingStep('scraping');
      setError("");
      
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);
      
      const response = await fetch(`http://localhost:8000/events/${selectedEvent.slug}/scrape-comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_slug: selectedEvent.slug,
          keywords: keywordList,
          max_posts: 50,
          force_refresh: false
        })
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to scrape comments');
      }
      
      // Reload event data
      await loadEventData(selectedEvent.slug);
      await loadEvents();
      
    } catch (err) {
      setError("Failed to scrape comments: " + err.message);
    } finally {
      setProcessing(false);
      setProcessingStep('');
    }
  };

  const handleAnalyzeSentiment = async () => {
    if (!selectedEvent) return;

    try {
      setProcessing(true);
      setProcessingStep('sentiment');
      setError("");
      
      const response = await fetch(`http://localhost:8000/events/${selectedEvent.slug}/analyze-sentiment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to analyze sentiment');
      }
      
      // Reload event data
      await loadEventData(selectedEvent.slug);
      await loadEvents();
      
    } catch (err) {
      setError("Failed to analyze sentiment: " + err.message);
    } finally {
      setProcessing(false);
      setProcessingStep('');
    }
  };

  const handleGenerateInsights = async () => {
    if (!selectedEvent) return;

    try {
      setProcessing(true);
      setProcessingStep('insights');
      setError("");
      
      const response = await fetch(`http://localhost:8000/events/${selectedEvent.slug}/generate-insights`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to generate insights');
      }
      
      // Reload event data
      await loadEventData(selectedEvent.slug);
      await loadEvents();
      
    } catch (err) {
      setError("Failed to generate insights: " + err.message);
    } finally {
      setProcessing(false);
      setProcessingStep('');
    }
  };

  const handleEventSelect = (event) => {
    setSelectedEvent(event);
    setError("");
  };

  const isEventProcessed = eventData?.event?.is_processed && 
                          eventData?.event?.sentiment_analyzed && 
                          eventData?.event?.insights_generated;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#ffffff', borderBottom: '1px solid #e5e7eb', padding: '24px 0' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1f2937', margin: '0 0 8px 0' }}>
            Amazon Sale AI Dashboard
          </h1>
          <p style={{ color: '#6b7280', margin: '0', fontSize: '1.1rem' }}>
            AI-powered sentiment analysis from Reddit discussions about Amazon sales
          </p>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 16px' }}>
        {/* Error Message */}
        {error && (
          <div style={{ 
            marginBottom: '24px', 
            padding: '16px', 
            backgroundColor: '#fef2f2', 
            border: '1px solid #fecaca', 
            borderRadius: '8px', 
            color: '#dc2626' 
          }}>
            {error}
          </div>
        )}

        {/* Event Selector */}
        <EventSelector 
          events={events}
          selectedEvent={selectedEvent}
          onEventSelect={handleEventSelect}
          keywords={keywords}
          onKeywordsChange={setKeywords}
          onScrapeComments={handleScrapeComments}
          onAnalyzeSentiment={handleAnalyzeSentiment}
          onGenerateInsights={handleGenerateInsights}
          processing={processing}
          processingStep={processingStep}
          isProcessed={isEventProcessed}
          eventData={eventData}
          hasSentimentAnalysis={eventData?.comments?.some(c => c.sentiment)}
        />

        {/* Main Content - Always show when event is selected */}
        {selectedEvent && (
          <div style={{ marginTop: '32px' }}>
            {/* Loading State */}
            {loading && (
              <div style={{ textAlign: 'center', padding: '48px 0' }}>
                <div style={{ 
                  display: 'inline-block',
                  width: '32px',
                  height: '32px',
                  border: '3px solid #e5e7eb',
                  borderTop: '3px solid #3b82f6',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                <p style={{ marginTop: '16px', color: '#6b7280' }}>Loading event data...</p>
              </div>
            )}

            {/* Processing State */}
            {processing && (
              <div style={{ 
                backgroundColor: '#eff6ff', 
                border: '1px solid #dbeafe', 
                borderRadius: '8px', 
                padding: '24px', 
                textAlign: 'center',
                marginBottom: '32px'
              }}>
                <div style={{ 
                  display: 'inline-block',
                  width: '24px',
                  height: '24px',
                  border: '3px solid #e5e7eb',
                  borderTop: '3px solid #3b82f6',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  marginBottom: '16px'
                }} />
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#1e40af', margin: '0 0 8px 0' }}>Processing Event</h3>
                <p style={{ color: '#3b82f6', margin: '0 0 16px 0' }}>
                  Scraping Reddit comments, analyzing sentiment, and generating insights...
                </p>
                <div style={{ fontSize: '0.875rem', color: '#6366f1' }}>
                  This may take 2-5 minutes depending on the amount of data
                </div>
              </div>
            )}

            {/* Main Dashboard Sections - Always visible when not loading */}
            {!loading && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
                {/* 1. Comments Section - FIRST */}
                <CommentsSection 
                  comments={eventData?.comments || []}
                  eventName={selectedEvent?.name || ""}
                  isProcessed={isEventProcessed}
                />

                {/* 2. Sentiment Distribution - SECOND */}
                <SentimentSection 
                  distribution={eventData?.sentiment_distribution || []}
                  isProcessed={isEventProcessed}
                />

                {/* 3. AI Insights - THIRD */}
                <InsightsSection 
                  insights={eventData?.insights || ""}
                  isProcessed={isEventProcessed}
                />
              </div>
            )}
          </div>
        )}

        {/* Welcome State */}
        {!selectedEvent && (
          <div style={{ textAlign: 'center', padding: '64px 0' }}>
            <div style={{ maxWidth: '448px', margin: '0 auto' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937', margin: '0 0 16px 0' }}>
                Select a Sale Event
              </h2>
              <p style={{ color: '#6b7280', lineHeight: '1.5' }}>
                Choose a sale event from the dropdown above to view Reddit sentiment analysis, 
                or process a new event to scrape fresh data.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer style={{ 
        backgroundColor: '#ffffff', 
        borderTop: '1px solid #e5e7eb', 
        marginTop: '64px',
        padding: '24px 0',
        textAlign: 'center',
        color: '#6b7280'
      }}>
        Amazon Sale AI Dashboard v2.0 - Powered by Reddit & Gemini AI
      </footer>

      {/* CSS for animations */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// Event Selector Component
function EventSelector({ 
  events, 
  selectedEvent, 
  onEventSelect, 
  keywords, 
  onKeywordsChange, 
  onScrapeComments,
  onAnalyzeSentiment,
  onGenerateInsights,
  processing, 
  processingStep,
  isProcessed, 
  eventData,
  hasSentimentAnalysis
}) {
  return (
    <div style={{ 
      backgroundColor: '#ffffff', 
      borderRadius: '12px', 
      border: '1px solid #e5e7eb',
      padding: '24px'
    }}>
      <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937', margin: '0 0 24px 0' }}>
        Event Selection & Processing
      </h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Event Selection */}
        <div>
          <label style={{ 
            display: 'block', 
            fontSize: '0.875rem', 
            fontWeight: '500', 
            color: '#374151',
            marginBottom: '8px'
          }}>
            Select Sale Event:
          </label>
          <select
            value={selectedEvent?.slug || ""}
            onChange={(e) => {
              const event = e.target.value 
                ? events.find(ev => ev.slug === e.target.value) 
                : null;
              onEventSelect(event);
            }}
            disabled={processing}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '1rem',
              backgroundColor: processing ? '#f3f4f6' : '#ffffff',
              color: '#374151'
            }}
          >
            <option value="">Choose an event...</option>
            {events.map((event) => (
              <option key={event.slug} value={event.slug}>
                {event.name} {event.is_processed ? '✓' : '○'}
              </option>
            ))}
          </select>
          
          {/* Event Status */}
          {selectedEvent && eventData && (
            <div style={{ 
              marginTop: '12px', 
              padding: '12px', 
              backgroundColor: '#f9fafb', 
              borderRadius: '8px'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>Status:</span>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    backgroundColor: isProcessed ? '#dcfce7' : '#fef3c7',
                    color: isProcessed ? '#166534' : '#92400e'
                  }}>
                    {isProcessed ? 'Processed' : 'Not Processed'}
                  </span>
                </div>
                {eventData.event?.comments_count > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                    <span>Comments:</span>
                    <span style={{ fontWeight: '500' }}>{eventData.event.comments_count}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Keywords & Actions */}
        <div>
          <label style={{ 
            display: 'block', 
            fontSize: '0.875rem', 
            fontWeight: '500', 
            color: '#374151',
            marginBottom: '8px'
          }}>
            Search Keywords:
          </label>
          <textarea
            value={keywords}
            onChange={(e) => onKeywordsChange(e.target.value)}
            placeholder="amazon sale, amazon deals, prime day"
            disabled={processing}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '1rem',
              resize: 'none',
              rows: 3,
              backgroundColor: processing ? '#f3f4f6' : '#ffffff',
              color: '#374151'
            }}
            rows={3}
          />
          
          {/* Action Buttons */}
          {selectedEvent && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
              {/* Step 1: Scrape Comments */}
              <button
                onClick={onScrapeComments}
                disabled={processing}
                style={{
                  backgroundColor: processing ? '#9ca3af' : '#3b82f6',
                  color: '#ffffff',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  fontWeight: '500',
                  cursor: processing ? 'not-allowed' : 'pointer',
                  fontSize: '1rem'
                }}
              >
                {processing && processingStep === 'scraping' ? 'Scraping Comments...' : '1. Scrape Comments'}
              </button>

              {/* Step 2: Analyze Sentiment */}
              <button
                onClick={onAnalyzeSentiment}
                disabled={processing || !eventData?.comments?.length}
                style={{
                  backgroundColor: processing || !eventData?.comments?.length ? '#9ca3af' : '#f59e0b',
                  color: '#ffffff',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  fontWeight: '500',
                  cursor: processing || !eventData?.comments?.length ? 'not-allowed' : 'pointer',
                  fontSize: '1rem'
                }}
              >
                {processing && processingStep === 'sentiment' ? 'Analyzing Sentiment...' : '2. Analyze Sentiment'}
              </button>

              {/* Step 3: Generate Insights */}
              <button
                onClick={onGenerateInsights}
                disabled={processing || !hasSentimentAnalysis}
                style={{
                  backgroundColor: processing || !hasSentimentAnalysis ? '#9ca3af' : '#10b981',
                  color: '#ffffff',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  fontWeight: '500',
                  cursor: processing || !hasSentimentAnalysis ? 'not-allowed' : 'pointer',
                  fontSize: '1rem'
                }}
              >
                {processing && processingStep === 'insights' ? 'Generating Insights...' : '3. Generate AI Insights'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Comments Section Component
function CommentsSection({ comments, eventName, isProcessed }) {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedSentiment, setSelectedSentiment] = useState('all');
  const commentsPerPage = 10;

  // Filter comments by sentiment
  const filteredComments = comments.filter(comment => {
    if (selectedSentiment === 'all') return true;
    return comment.sentiment === selectedSentiment;
  });

  // Pagination
  const totalPages = Math.ceil(filteredComments.length / commentsPerPage);
  const startIndex = (currentPage - 1) * commentsPerPage;
  const displayedComments = filteredComments.slice(startIndex, startIndex + commentsPerPage);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return { backgroundColor: '#dcfce7', color: '#166534' };
      case 'negative': return { backgroundColor: '#fee2e2', color: '#dc2626' };
      case 'neutral': return { backgroundColor: '#f3f4f6', color: '#374151' };
      default: return { backgroundColor: '#f3f4f6', color: '#374151' };
    }
  };

  const getSentimentEmoji = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      case 'neutral': return '😐';
      default: return '🤔';
    }
  };

  return (
    <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
      {/* Header */}
      <div style={{ padding: '24px', borderBottom: '1px solid #e5e7eb' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937', margin: '0 0 4px 0' }}>
              Reddit Comments
            </h2>
            <p style={{ color: '#6b7280', margin: '0' }}>
              {eventName && `Comments for ${eventName}`}
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6' }}>
              {comments.length}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Total Comments</div>
          </div>
        </div>

        {/* Sentiment Filter */}
        {isProcessed && comments.length > 0 && (
          <div style={{ marginTop: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={() => {
                setSelectedSentiment('all');
                setCurrentPage(1);
              }}
              style={{
                padding: '6px 12px',
                borderRadius: '16px',
                fontSize: '0.875rem',
                fontWeight: '500',
                border: 'none',
                cursor: 'pointer',
                backgroundColor: selectedSentiment === 'all' ? '#dbeafe' : '#f3f4f6',
                color: selectedSentiment === 'all' ? '#1e40af' : '#374151'
              }}
            >
              All ({comments.length})
            </button>
            {['positive', 'negative', 'neutral'].map(sentiment => {
              const count = comments.filter(c => c.sentiment === sentiment).length;
              if (count === 0) return null;
              
              const colors = getSentimentColor(sentiment);
              return (
                <button
                  key={sentiment}
                  onClick={() => {
                    setSelectedSentiment(sentiment);
                    setCurrentPage(1);
                  }}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '16px',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    border: 'none',
                    cursor: 'pointer',
                    backgroundColor: selectedSentiment === sentiment ? colors.backgroundColor : '#f3f4f6',
                    color: selectedSentiment === sentiment ? colors.color : '#374151',
                    textTransform: 'capitalize'
                  }}
                >
                  {getSentimentEmoji(sentiment)} {sentiment} ({count})
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Comments List */}
      <div style={{ padding: '24px' }}>
        {comments.length === 0 && !isProcessed ? (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>💬</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', margin: '0 0 8px 0' }}>No Comments Yet</h3>
            <p style={{ color: '#6b7280', margin: '0' }}>
              Process an event to scrape and analyze Reddit comments
            </p>
          </div>
        ) : comments.length === 0 && isProcessed ? (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📭</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', margin: '0 0 8px 0' }}>No Comments Found</h3>
            <p style={{ color: '#6b7280', margin: '0' }}>
              No relevant comments were found for this event. Try different keywords.
            </p>
          </div>
        ) : comments.length > 0 && filteredComments.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 0' }}>
            <p style={{ color: '#6b7280', margin: '0' }}>No comments match the selected sentiment filter.</p>
          </div>
        ) : comments.length > 0 ? (
          <>
            {/* Comments */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {displayedComments.map((comment, index) => {
                const sentimentColors = getSentimentColor(comment.sentiment);
                return (
                  <div key={index} style={{ 
                    backgroundColor: '#f9fafb', 
                    borderRadius: '8px', 
                    padding: '16px',
                    border: '1px solid #e5e7eb'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '0.875rem', fontWeight: '500', color: '#374151' }}>
                          r/{comment.subreddit}
                        </span>
                        <span style={{ color: '#d1d5db' }}>•</span>
                        <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                          u/{comment.author}
                        </span>
                        {comment.sentiment && (
                          <>
                            <span style={{ color: '#d1d5db' }}>•</span>
                            <span style={{
                              padding: '2px 8px',
                              borderRadius: '12px',
                              fontSize: '0.75rem',
                              fontWeight: '500',
                              ...sentimentColors
                            }}>
                              {getSentimentEmoji(comment.sentiment)} {comment.sentiment}
                            </span>
                          </>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', color: '#6b7280' }}>
                        <span>↑ {comment.score}</span>
                      </div>
                    </div>
                    
                    {comment.submission_title && (
                      <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#1f2937', marginBottom: '8px' }}>
                        Post: {comment.submission_title}
                      </div>
                    )}
                    
                    <div style={{ color: '#374151', lineHeight: '1.6' }}>
                      {comment.comment}
                    </div>
                    
                    {comment.url && (
                      <div style={{ marginTop: '8px' }}>
                        <a 
                          href={comment.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontSize: '0.875rem', color: '#3b82f6', textDecoration: 'none' }}
                        >
                          View on Reddit →
                        </a>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #e5e7eb' }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  Showing {startIndex + 1}-{Math.min(startIndex + commentsPerPage, filteredComments.length)} of {filteredComments.length} comments
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    style={{
                      padding: '6px 12px',
                      fontSize: '0.875rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      backgroundColor: currentPage === 1 ? '#f3f4f6' : '#ffffff',
                      color: currentPage === 1 ? '#9ca3af' : '#374151',
                      cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
                    }}
                  >
                    Previous
                  </button>
                  <span style={{ 
                    padding: '6px 12px', 
                    fontSize: '0.875rem', 
                    backgroundColor: '#dbeafe', 
                    color: '#1e40af', 
                    borderRadius: '6px' 
                  }}>
                    {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    style={{
                      padding: '6px 12px',
                      fontSize: '0.875rem',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      backgroundColor: currentPage === totalPages ? '#f3f4f6' : '#ffffff',
                      color: currentPage === totalPages ? '#9ca3af' : '#374151',
                      cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
                    }}
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}

// Sentiment Section Component
function SentimentSection({ distribution, isProcessed }) {
  const totalCount = distribution.reduce((sum, item) => sum + item.count, 0);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#10b981';
      case 'negative': return '#ef4444';
      case 'neutral': return '#6b7280';
      default: return '#9ca3af';
    }
  };

  const getSentimentEmoji = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      case 'neutral': return '😐';
      default: return '🤔';
    }
  };

  return (
    <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
      {/* Header */}
      <div style={{ padding: '24px', borderBottom: '1px solid #e5e7eb' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937', margin: '0 0 4px 0' }}>Sentiment Distribution</h2>
        <p style={{ color: '#6b7280', margin: '0' }}>AI-analyzed sentiment from Gemini</p>
      </div>

      {/* Content */}
      <div style={{ padding: '24px' }}>
        {distribution.length === 0 && !isProcessed ? (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📊</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', margin: '0 0 8px 0' }}>No Sentiment Data</h3>
            <p style={{ color: '#6b7280', margin: '0' }}>
              Process an event to analyze sentiment with AI
            </p>
          </div>
        ) : distribution.length === 0 && isProcessed ? (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📈</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', margin: '0 0 8px 0' }}>No Sentiment Analysis</h3>
            <p style={{ color: '#6b7280', margin: '0' }}>
              Sentiment analysis will appear here after processing comments
            </p>
          </div>
        ) : distribution.length > 0 ? (
          <>
            {/* Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              {distribution.map((item) => (
                <div key={item.sentiment} style={{ backgroundColor: '#f9fafb', borderRadius: '8px', padding: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '1.5rem' }}>{getSentimentEmoji(item.sentiment)}</span>
                      <span style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', textTransform: 'capitalize' }}>
                        {item.sentiment}
                      </span>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
                        {item.percentage}%
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                        {item.count} comments
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Visual Bar Chart */}
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', margin: '0 0 16px 0' }}>Visual Breakdown</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {distribution.map((item) => (
                  <div key={item.sentiment} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ width: '80px', fontSize: '0.875rem', fontWeight: '500', color: '#374151', textTransform: 'capitalize' }}>
                      {getSentimentEmoji(item.sentiment)} {item.sentiment}
                    </div>
                    <div style={{ flex: 1, backgroundColor: '#e5e7eb', borderRadius: '8px', height: '24px', position: 'relative' }}>
                      <div
                        style={{
                          height: '24px',
                          borderRadius: '8px',
                          backgroundColor: getSentimentColor(item.sentiment),
                          width: `${item.percentage}%`,
                          transition: 'width 0.5s ease-out'
                        }}
                      />
                      <div style={{
                        position: 'absolute',
                        top: '0',
                        left: '0',
                        right: '0',
                        bottom: '0',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#ffffff',
                        fontSize: '0.875rem',
                        fontWeight: '500'
                      }}>
                        {item.percentage}%
                      </div>
                    </div>
                    <div style={{ width: '60px', fontSize: '0.875rem', color: '#6b7280', textAlign: 'right' }}>
                      {item.count}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Summary Stats */}
            <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #e5e7eb' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  Total analyzed comments: <span style={{ fontWeight: '500' }}>{totalCount}</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '4px' }}>
                  Powered by Gemini AI sentiment analysis
                </div>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

// Insights Section Component
function InsightsSection({ insights, isProcessed }) {
  const formatInsights = (text) => {
    if (!text) return [];
    
    // Split by numbered sections and format
    const sections = text.split(/\*\*\d+\)\s+\*\*/).filter(section => section.trim());
    
    return sections.map((section, index) => {
      const lines = section.split('\n').filter(line => line.trim());
      if (lines.length === 0) return null;
      
      // First line is usually the title
      const title = lines[0].replace(/^\*\*|\*\*$/g, '');
      const content = lines.slice(1);
      
      return {
        id: index,
        title,
        content
      };
    }).filter(Boolean);
  };

  const formattedInsights = formatInsights(insights);

  return (
    <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
      {/* Header */}
      <div style={{ padding: '24px', borderBottom: '1px solid #e5e7eb' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937', margin: '0 0 4px 0' }}>AI Insights</h2>
        <p style={{ color: '#6b7280', margin: '0' }}>Comprehensive analysis powered by Gemini AI</p>
      </div>

      {/* Content */}
      <div style={{ padding: '24px' }}>
        {!insights && !isProcessed ? (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🧠</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', margin: '0 0 8px 0' }}>No AI Insights</h3>
            <p style={{ color: '#6b7280', margin: '0' }}>
              Process an event to generate comprehensive AI insights
            </p>
          </div>
        ) : !insights || insights.trim() === '' && isProcessed ? (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>⚠️</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1f2937', margin: '0 0 8px 0' }}>No Insights Available</h3>
            <p style={{ color: '#6b7280', margin: '0' }}>
              AI insights will appear here after analyzing comments
            </p>
          </div>
        ) : formattedInsights.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {formattedInsights.map((section) => (
              <div key={section.id} style={{
                background: 'linear-gradient(to right, #eff6ff, #e0e7ff)',
                borderRadius: '8px',
                padding: '24px',
                borderLeft: '4px solid #3b82f6'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#1f2937', margin: '0 0 12px 0' }}>
                  {section.title}
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {section.content.map((line, lineIndex) => {
                    const cleanLine = line.trim().replace(/^[-•]\s*/, '');
                    if (!cleanLine) return null;
                    
                    return (
                      <div key={lineIndex} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                        <div style={{ width: '6px', height: '6px', backgroundColor: '#3b82f6', borderRadius: '50%', marginTop: '8px', flexShrink: 0 }} />
                        <div style={{ color: '#374151', lineHeight: '1.6' }}>{cleanLine}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        ) : (
          // Fallback: display raw insights if formatting fails
          <div style={{
            background: 'linear-gradient(to right, #eff6ff, #e0e7ff)',
            borderRadius: '8px',
            padding: '24px',
            borderLeft: '4px solid #3b82f6'
          }}>
            <div style={{ whiteSpace: 'pre-wrap', color: '#374151', lineHeight: '1.6' }}>
              {insights}
            </div>
          </div>
        )}

        {/* AI Attribution */}
        {isProcessed && insights && (
          <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #e5e7eb' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontSize: '0.875rem', color: '#6b7280' }}>
              <span>⚡</span>
              <span>Generated by Gemini AI</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}