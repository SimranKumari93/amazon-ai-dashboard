import { useEffect, useState } from "react";
import { fetchEvents, fetchSentiment, fetchComments, fetchInsights } from "./api";
import SentimentChart from "./components/SentimentChart";
import CommentsTable from "./components/CommentsTable";
import InsightsPanel from "./components/InsightsPanel";

export default function App() {
  const [events, setEvents] = useState([]);
  const [slug, setSlug] = useState("");
  const [sentiment, setSentiment] = useState(null);
  const [comments, setComments] = useState({ total: 0, rows: [] });
  const [insights, setInsights] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEvents().then(e => {
      setEvents(e);
      if (e.length) setSlug(e[0].slug || e[0].name.toLowerCase().replace(/\W+/g,"_"));
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (!slug) return;
    setInsights("");
    fetchSentiment(slug).then(setSentiment).catch(() => setSentiment({ distribution: {} }));
    fetchComments(slug, 200, 0).then(setComments).catch(() => setComments({ total: 0, rows: [] }));
  }, [slug]);

  const onGenerate = async () => {
    setLoading(true);
    try {
      const r = await fetchInsights(slug, 200);
      setInsights(r.summary);
    } catch (e) {
      setInsights(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "24px auto", padding: 16, fontFamily: "Inter, system-ui, Arial" }}>
      <h1>Amazon Sale AI Dashboard</h1>

      <label>
        Event:&nbsp;
        <select value={slug} onChange={e => setSlug(e.target.value)}>
          {events.map((ev, i) => {
            const s = ev.slug || ev.name.toLowerCase().replace(/\W+/g,"_");
            return <option key={i} value={s}>{ev.name}</option>;
          })}
        </select>
      </label>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 16, marginTop: 16 }}>
        <SentimentChart distribution={sentiment?.distribution} />
        <CommentsTable rows={comments.rows} />
        <InsightsPanel text={insights} onGenerate={onGenerate} loading={loading} />
      </div>
    </div>
  );
}

// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.jsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App
