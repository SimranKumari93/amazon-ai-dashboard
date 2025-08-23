export default function InsightsPanel({ text, onGenerate, loading }) {
  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 12 }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>AI Insights</h3>
        <button onClick={onGenerate} disabled={loading} style={{ padding: "8px 12px" }}>
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>
      <pre style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>{text || "Click Generate to produce insights."}</pre>
    </div>
  );
}
