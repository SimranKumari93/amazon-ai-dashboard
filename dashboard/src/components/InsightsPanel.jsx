export default function InsightsPanel({ text, onGenerate, loading }) {
  const hasContent = text && text.trim().length > 0;
  
  return (
    <div>
      <div style={{ 
        display: "flex", 
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "16px"
      }}>
        <button 
          onClick={onGenerate} 
          disabled={loading}
          style={{
            padding: "12px 24px",
            fontSize: "1rem",
            fontWeight: "600",
            color: "white",
            backgroundColor: loading ? "#9ca3af" : "#3b82f6",
            border: "none",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            transition: "background-color 0.2s"
          }}
        >
          {loading ? "Generating Insights..." : "Generate AI Insights"}
        </button>
      </div>
      
      <div style={{
        minHeight: "200px",
        padding: "20px",
        backgroundColor: "#f9fafb",
        borderRadius: "8px",
        border: "1px solid #e5e7eb"
      }}>
        {loading && (
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "200px",
            color: "#6b7280"
          }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ marginBottom: "8px" }}>🤖</div>
              <div>Generating insights with AI...</div>
            </div>
          </div>
        )}
        
        {!loading && !hasContent && (
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "200px",
            color: "#6b7280",
            textAlign: "center"
          }}>
            <div>
              <div style={{ fontSize: "2rem", marginBottom: "12px" }}>🧠</div>
              <div style={{ fontSize: "1.1rem", marginBottom: "4px" }}>
                No insights generated yet
              </div>
              <div style={{ fontSize: "0.9rem" }}>
                Click "Generate AI Insights" to analyze the comments
              </div>
            </div>
          </div>
        )}
        
        {!loading && hasContent && (
          <div style={{
            lineHeight: "1.6",
            color: "#374151"
          }}>
            <div 
              dangerouslySetInnerHTML={{
                __html: text
                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/### (.*)/g, '<h3 style="color: #1f2937; margin: 20px 0 10px 0; font-size: 1.2rem;">$1</h3>')
                  .replace(/## (.*)/g, '<h2 style="color: #1f2937; margin: 24px 0 12px 0; font-size: 1.4rem;">$1</h2>')
                  .replace(/- (.*)/g, '<div style="margin: 8px 0; padding-left: 20px;">• $1</div>')
                  .replace(/\n/g, '<br>')
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}