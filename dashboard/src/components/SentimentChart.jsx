import { PieChart, Pie, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";

const COLORS = {
  'Positive': '#10b981',
  'Negative': '#ef4444', 
  'Neutral': '#6b7280'
};

export default function SentimentChart({ distribution = {} }) {
  const data = Object.entries(distribution).map(([name, value]) => ({ 
    name, 
    value,
    color: COLORS[name] || '#94a3b8'
  }));

  if (data.length === 0) {
    return (
      <div style={{ 
        height: 300, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: '#6b7280',
        fontSize: '1rem'
      }}>
        No sentiment data available
      </div>
    );
  }

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div style={{ width: "100%", height: 400 }}>
      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie 
              dataKey="value" 
              data={data} 
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              outerRadius={80}
              fill="#8884d8"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [`${value} comments`, 'Count']} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
      
      {/* Summary Stats */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '16px',
        marginTop: '20px'
      }}>
        {data.map(({ name, value, color }) => (
          <div key={name} style={{
            padding: '12px',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            textAlign: 'center',
            borderLeft: `4px solid ${color}`
          }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color }}>
              {value}
            </div>
            <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>
              {name} ({((value / total) * 100).toFixed(1)}%)
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}