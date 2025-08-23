export default function CommentsTable({ rows = [] }) {
  return (
    <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 12 }}>
      <h3>Sample Comments</h3>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th align="left">Post</th>
            <th align="left">Comment</th>
            <th align="left">Subreddit</th>
            <th align="left">Sentiment</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} style={{ borderTop: "1px solid #f2f2f2" }}>
              <td>{r.submission_title || "-"}</td>
              <td>{r.comment || "-"}</td>
              <td>{r.subreddit || "-"}</td>
              <td>{r.sentiment || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
