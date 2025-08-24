const getSentimentColor = (sentiment) => {
  switch(sentiment?.toLowerCase()) {
    case 'positive': return '#10b981';
    case 'negative': return '#ef4444';
    case 'neutral': return '#6b7280';
    default: return '#94a3b8';
  }
};

const formatDate = (timestamp) => {
  if (!timestamp) return '-';
  return new Date(timestamp * 1000).toLocaleDateString();
};

export default function CommentsTable({ rows = [] }) {
  if (rows.length === 0) {
    return (
      <div style={{ 
        padding: '40px',
        textAlign: 'center',
        color: '#6b7280',
        fontSize: '1rem'
      }}>
        No comments available for this event
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ 
        width: "100%", 
        borderCollapse: "collapse",
        fontSize: '0.9rem'
      }}>
        <thead>
          <tr style={{ 
            backgroundColor: '#f9fafb',
            borderBottom: '2px solid #e5e7eb'
          }}>
            <th style={{ 
              padding: '12px 8px', 
              textAlign: 'left', 
              fontWeight: '600',
              color: '#374151'
            }}>
              Post Title
            </th>
            <th style={{ 
              padding: '12px 8px', 
              textAlign: 'left', 
              fontWeight: '600',
              color: '#374151',
              minWidth: '300px'
            }}>
              Comment
            </th>
            <th style={{ 
              padding: '12px 8px', 
              textAlign: 'left', 
              fontWeight: '600',
              color: '#374151'
            }}>
              Subreddit
            </th>
            <th style={{ 
              padding: '12px 8px', 
              textAlign: 'left', 
              fontWeight: '600',
              color: '#374151'
            }}>
              Sentiment
            </th>
            <th style={{ 
              padding: '12px 8px', 
              textAlign: 'left', 
              fontWeight: '600',
              color: '#374151'
            }}>
              Date
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index} style={{ 
              borderBottom: "1px solid #f3f4f6",
              '&:hover': { backgroundColor: '#f9fafb' }
            }}>
              <td style={{ 
                padding: '12px 8px',
                maxWidth: '200px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                <div title={row.submission_title}>
                  {row.submission_title || "-"}
                </div>
              </td>
              <td style={{ 
                padding: '12px 8px',
                maxWidth: '400px',
                lineHeight: '1.4'
              }}>
                <div style={{
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }} title={row.comment}>
                  {row.comment || "-"}
                </div>
              </td>
              <td style={{ 
                padding: '12px 8px',
                color: '#6b7280'
              }}>
                {row.subreddit ? `r/${row.subreddit}` : "-"}
              </td>
              <td style={{ 
                padding: '12px 8px'
              }}>
                {row.sentiment && (
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '0.8rem',
                    fontWeight: '500',
                    color: 'white',
                    backgroundColor: getSentimentColor(row.sentiment)
                  }}>
                    {row.sentiment}
                  </span>
                )}
                {!row.sentiment && "-"}
              </td>
              <td style={{ 
                padding: '12px 8px',
                color: '#6b7280',
                fontSize: '0.8rem'
              }}>
                {formatDate(row.created_utc)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}