import { PieChart, Pie, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function SentimentChart({ distribution }) {
  const data = Object.entries(distribution || {}).map(([name, value]) => ({ name, value }));
  return (
    <div style={{ width: "100%", height: 300, border: "1px solid #eee", borderRadius: 8, padding: 12 }}>
      <h3>Sentiment Distribution</h3>
      <ResponsiveContainer>
        <PieChart>
          <Pie dataKey="value" data={data} label />
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
