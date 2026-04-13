import { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [showReport, setShowReport] = useState(false);

  const handleAnalyze = () => {
    if (query.trim() !== "") {
      setShowReport(true);
    }
  };

  const cardStyle = {
    background: "white",
    padding: "20px",
    borderRadius: "10px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
    marginBottom: "20px"
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial", background: "#eef2f7", minHeight: "100vh" }}>
      
      <h1 style={{ marginBottom: "5px" }}>📊 Smart Business Decision Assistant (SBDA)</h1>
      <p style={{ color: "#555" }}>
        Domain-Specific Multi-Agent System for Competitor Intelligence
      </p>

      {/* Input Card */}
      <div style={{ ...cardStyle, marginTop: "30px" }}>
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
            marginRight: "10px"
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
            cursor: "pointer"
          }}
        >
          Analyze
        </button>
      </div>

      {/* Report */}
      {showReport && (
        <div>

          <div style={cardStyle}>
            <h2>🧾 Executive Summary</h2>
            <p>
              Tesla dominates the EV market with strong innovation leadership and global brand recognition.
            </p>
          </div>

          <div style={cardStyle}>
            <h2>📊 Competitor Comparison</h2>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ backgroundColor: "#f1f3f6" }}>
                  <th style={{ padding: "10px", border: "1px solid #ddd" }}>Company</th>
                  <th style={{ padding: "10px", border: "1px solid #ddd" }}>Market Share</th>
                  <th style={{ padding: "10px", border: "1px solid #ddd" }}>Strength</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>Tesla</td>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>45%</td>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>Innovation</td>
                </tr>
                <tr>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>BYD</td>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>30%</td>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>Cost Efficiency</td>
                </tr>
                <tr>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>NIO</td>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>10%</td>
                  <td style={{ padding: "10px", border: "1px solid #ddd" }}>Premium Branding</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style={cardStyle}>
            <h2>🧠 SWOT Analysis</h2>
            <p><b>Strength:</b> Strong brand & innovation</p>
            <p><b>Weakness:</b> High pricing</p>
            <p><b>Opportunity:</b> Emerging markets</p>
            <p><b>Threat:</b> Intense EV competition</p>
          </div>

          <div style={cardStyle}>
            <h2>⚠ Risk Assessment</h2>
            <p>Supply chain disruptions and regulatory uncertainties.</p>
          </div>

          <div style={cardStyle}>
            <h2>🚀 Strategic Recommendations</h2>
            <p>Expand global manufacturing and invest in battery R&D.</p>
          </div>

        </div>
      )}

    </div>
  );
}

export default App;