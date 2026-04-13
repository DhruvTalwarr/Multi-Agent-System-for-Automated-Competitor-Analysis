import { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

function App() {
  const [query, setQuery] = useState("");
  const [showReport, setShowReport] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = () => {
    if (query.trim() !== "") {
      setLoading(true);
      setShowReport(false);

      setTimeout(() => {
        setLoading(false);
        setShowReport(true);
      }, 1500);
    }
  };

  const pieData = [
    { name: "Tesla", value: 45 },
    { name: "BYD", value: 30 },
    { name: "NIO", value: 10 },
    { name: "Others", value: 15 },
  ];

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  const cardStyle = {
    background: "white",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 14px rgba(0,0,0,0.12)",
  };

  const metricCard = {
    ...cardStyle,
    flex: 1,
    textAlign: "center",
  };

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial",
        background: "linear-gradient(135deg, #dbeafe, #f0f9ff)",
        minHeight: "100vh",
      }}
    >
      <h1>📊 Smart Business Decision Assistant (SBDA)</h1>
      <p style={{ color: "#444" }}>
        Domain-Specific Multi-Agent System for Competitor Intelligence
      </p>

      {/* Input */}
      <div style={{ ...cardStyle, marginTop: "30px", marginBottom: "25px" }}>
        <input
          type="text"
          placeholder="Enter competitor analysis query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            padding: "12px",
            width: "65%",
            borderRadius: "6px",
            border: "1px solid #ccc",
            marginRight: "10px",
          }}
        />
        <button
          onClick={handleAnalyze}
          style={{
            padding: "12px 22px",
            borderRadius: "6px",
            border: "none",
            background: "linear-gradient(90deg,#4CAF50,#2e7d32)",
            color: "white",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Analyze
        </button>
      </div>

      {loading && <h3>⏳ Running Multi-Agent Analysis...</h3>}

      {showReport && (
        <div>
          {/* Metrics */}
          <div style={{ display: "flex", gap: "20px", marginBottom: "25px" }}>
            <div style={metricCard}>
              <h3>📄 Completeness</h3>
              <h2 style={{ color: "#2e7d32" }}>85%</h2>
            </div>
            <div style={metricCard}>
              <h3>🔍 Evidence Score</h3>
              <h2 style={{ color: "#1565c0" }}>92%</h2>
            </div>
            <div style={metricCard}>
              <h3>🧠 Analysis Depth</h3>
              <h2 style={{ color: "#ef6c00" }}>88%</h2>
            </div>
          </div>

          {/* Pie Chart */}
          <div style={{ ...cardStyle, marginBottom: "20px" }}>
            <h2>📊 Market Share Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={100}
                  dataKey="value"
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Executive Summary */}
          <div style={{ ...cardStyle, marginBottom: "20px" }}>
            <h2>🧾 Executive Summary</h2>
            <p>
              Tesla dominates the EV market with strong innovation leadership and global brand recognition.
            </p>
          </div>

          {/* SWOT */}
          <div style={{ ...cardStyle, marginBottom: "20px" }}>
            <h2>🧠 SWOT Analysis</h2>
            <p><b>Strength:</b> Strong brand & innovation</p>
            <p><b>Weakness:</b> High pricing</p>
            <p><b>Opportunity:</b> Emerging markets</p>
            <p><b>Threat:</b> Intense EV competition</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;