import { useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

// ── API config ────────────────────────────────────────────────────────────────
const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function fetchAnalysis(query) {
  const res = await fetch(`${BASE_URL}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      region: "india",
      max_competitors: 5,
      include_swot: true,
      include_risk: true,
    }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

async function fetchReport(query) {
  const res = await fetch(`${BASE_URL}/api/v1/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, region: "india", format: "markdown" }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Report generation failed");
  }
  return res.json();
}

// ── Color palette (matches your original) ────────────────────────────────────
const COLORS = ["#00eaff", "#ff2bd6", "#3b82f6", "#ec4899", "#a78bfa"];

// ── Styles (unchanged from your original) ────────────────────────────────────
const neonCard = {
  background: "#0f172a",
  padding: "22px",
  borderRadius: "16px",
  boxShadow: "0 0 20px #00eaff, 0 0 20px #ff2bd6",
  marginBottom: "25px",
  color: "white",
};

function App() {
  const [query, setQuery]         = useState("");
  const [showReport, setShowReport] = useState(false);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);

  // Real data from API
  const [analysisData, setAnalysisData] = useState(null);
  const [reportData, setReportData]     = useState(null);

  // ── Derived chart data from real API response ─────────────────────────────
  const pieData = analysisData
    ? analysisData.competitors.map((c) => ({
        name: c.name,
        value: parseFloat(c.market_share) || 10,
      }))
    : [];

  const barData = analysisData
    ? analysisData.competitors.map((c) => ({
        company: c.name,
        marketShare: parseFloat(c.market_share) || 10,
      }))
    : [];

  // ── Analyze button ────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (query.trim().length < 10) {
      setError("Please enter a more detailed query (min 10 characters).");
      return;
    }

    setLoading(true);
    setShowReport(false);
    setError(null);
    setAnalysisData(null);
    setReportData(null);

    try {
      const [analysis, report] = await Promise.all([
        fetchAnalysis(query),
        fetchReport(query),
      ]);
      setAnalysisData(analysis);
      setReportData(report);
      setShowReport(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ── Export PDF (real data) ────────────────────────────────────────────────
  const exportPDF = async () => {
    const pdf = new jsPDF();

    pdf.setFontSize(18);
    pdf.text("Smart Business Decision Assistant Report", 10, 20);

    // Executive summary from real API
    pdf.setFontSize(14);
    pdf.text("Executive Summary:", 10, 40);
    pdf.setFontSize(11);
    const summary = reportData?.summary || "No summary available.";
    pdf.text(pdf.splitTextToSize(summary, 180), 10, 50);

    // SWOT from real API
    pdf.setFontSize(14);
    pdf.text("SWOT Analysis:", 10, 80);
    pdf.setFontSize(11);

    if (analysisData?.swot) {
      const { strengths, weaknesses, opportunities, threats } = analysisData.swot;
      pdf.text(`Strength: ${strengths[0] || "—"}`, 10, 90);
      pdf.text(`Weakness: ${weaknesses[0] || "—"}`, 10, 100);
      pdf.text(`Opportunity: ${opportunities[0] || "—"}`, 10, 110);
      pdf.text(`Threat: ${threats[0] || "—"}`, 10, 120);
    }

    // Strategic recommendation
    if (reportData?.strategic_recommendation) {
      pdf.setFontSize(14);
      pdf.text("Strategic Recommendation:", 10, 140);
      pdf.setFontSize(11);
      pdf.text(
        pdf.splitTextToSize(reportData.strategic_recommendation, 180),
        10, 150
      );
    }

    // Capture charts
    const pie = document.getElementById("pie-chart");
    if (pie) {
      const pieCanvas = await html2canvas(pie);
      pdf.addPage();
      pdf.text("Market Share Distribution", 10, 20);
      pdf.addImage(pieCanvas.toDataURL("image/png"), "PNG", 15, 30, 180, 80);
    }

    const bar = document.getElementById("bar-chart");
    if (bar) {
      const barCanvas = await html2canvas(bar);
      pdf.addPage();
      pdf.text("Competitor Market Share Comparison", 10, 20);
      pdf.addImage(barCanvas.toDataURL("image/png"), "PNG", 15, 30, 180, 90);
    }

    pdf.save("SBDA_Report.pdf");
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div style={{ display: "flex", fontFamily: "Arial", minHeight: "100vh" }}>

      {/* Sidebar — unchanged */}
      <div
        style={{
          width: "230px",
          background: "linear-gradient(180deg,#020617,#0f172a)",
          color: "#ff2bd6",
          padding: "25px",
          boxShadow: "0 0 20px #ff2bd6",
        }}
      >
        <h2>SBDA</h2>
        <p>📊 Dashboard</p>
        <p>📑 Reports</p>
        <p>⚙ Settings</p>
      </div>

      {/* Main Content — unchanged layout */}
      <div
        style={{
          flex: 1,
          padding: "35px",
          background: "linear-gradient(135deg,#020617,#1e3a8a,#ff2bd6,#00eaff)",
          color: "white",
        }}
      >
        <h1 style={{ color: "#00eaff" }}>Smart Business Decision Assistant</h1>

        {/* Query Box */}
        <div
          style={{
            ...neonCard,
            background: "linear-gradient(135deg,#00eaff,#ff2bd6)",
          }}
        >
          <input
            type="text"
            placeholder="Enter competitor analysis query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
            style={{
              padding: "12px",
              width: "60%",
              marginRight: "10px",
              borderRadius: "8px",
              border: "none",
            }}
          />

          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
              padding: "12px 20px",
              marginRight: "10px",
              borderRadius: "8px",
              border: "none",
              background: "#020617",
              color: "#00eaff",
              fontWeight: "bold",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
            Analyze
          </button>

          <button
            onClick={exportPDF}
            disabled={!showReport}
            style={{
              padding: "12px 20px",
              borderRadius: "8px",
              border: "none",
              background: "#020617",
              color: "#ff2bd6",
              fontWeight: "bold",
              cursor: !showReport ? "not-allowed" : "pointer",
              opacity: !showReport ? 0.4 : 1,
            }}
          >
            Export PDF
          </button>
        </div>

        {/* Error message */}
        {error && (
          <div
            style={{
              ...neonCard,
              background: "linear-gradient(135deg,#7f1d1d,#450a0a)",
              boxShadow: "0 0 20px #ef4444",
              color: "#fca5a5",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {loading && <h3>⏳ Running Multi-Agent Analysis...</h3>}

        {showReport && analysisData && (

          <div>

            {/* Metrics — now from real data */}
            <div style={{ display: "flex", gap: "25px", marginBottom: "30px" }}>

              <div style={{
                flex: 1, padding: "30px", borderRadius: "18px",
                background: "linear-gradient(135deg,#00eaff,#3b82f6)",
                textAlign: "center", boxShadow: "0 0 20px #00eaff",
              }}>
                <h3>🏢 Competitors Found</h3>
                <h1>{analysisData.competitors.length}</h1>
              </div>

              <div style={{
                flex: 1, padding: "30px", borderRadius: "18px",
                background: "linear-gradient(135deg,#3b82f6,#ff2bd6)",
                textAlign: "center", boxShadow: "0 0 20px #ff2bd6",
              }}>
                <h3>🔍 Risk Factors</h3>
                <h1>{analysisData.risks?.length ?? 0}</h1>
              </div>

              <div style={{
                flex: 1, padding: "30px", borderRadius: "18px",
                background: "linear-gradient(135deg,#ff2bd6,#00eaff)",
                textAlign: "center", boxShadow: "0 0 20px #ff2bd6",
              }}>
                <h3>🧠 SWOT Points</h3>
                <h1>
                  {analysisData.swot
                    ? analysisData.swot.strengths.length +
                      analysisData.swot.weaknesses.length +
                      analysisData.swot.opportunities.length +
                      analysisData.swot.threats.length
                    : 0}
                </h1>
              </div>

            </div>

            {/* Pie Chart */}
            <div id="pie-chart" style={neonCard}>
              <h3>Market Share Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={pieData} outerRadius={100} dataKey="value" label>
                    {pieData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Bar Chart */}
            <div id="bar-chart" style={neonCard}>
              <h3>Competitor Market Share Comparison</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#00eaff" />
                  <XAxis dataKey="company" stroke="#ffffff" />
                  <YAxis stroke="#ffffff" />
                  <Tooltip />
                  <Bar dataKey="marketShare" fill="#ff2bd6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Executive Summary — real data */}
            <div style={{
              ...neonCard,
              background: "linear-gradient(135deg,#00eaff,#ff2bd6)",
            }}>
              <h3>Executive Summary</h3>
              <p>{reportData?.summary}</p>
              {reportData?.strategic_recommendation && (
                <>
                  <h4>Strategic Recommendation</h4>
                  <p>{reportData.strategic_recommendation}</p>
                </>
              )}
            </div>

            {/* SWOT — real data */}
            {analysisData.swot && (
              <div style={{
                ...neonCard,
                background: "linear-gradient(135deg,#ff2bd6,#00eaff)",
              }}>
                <h3>SWOT Analysis</h3>
                <p><b>Strength:</b> {analysisData.swot.strengths[0]}</p>
                <p><b>Weakness:</b> {analysisData.swot.weaknesses[0]}</p>
                <p><b>Opportunity:</b> {analysisData.swot.opportunities[0]}</p>
                <p><b>Threat:</b> {analysisData.swot.threats[0]}</p>
              </div>
            )}

            {/* Risk Analysis — real data */}
            {analysisData.risks && analysisData.risks.length > 0 && (
              <div style={neonCard}>
                <h3>Risk Analysis</h3>
                {analysisData.risks.map((r, i) => (
                  <div
                    key={i}
                    style={{
                      marginBottom: "12px",
                      padding: "12px",
                      borderRadius: "8px",
                      background: r.severity === "high"
                        ? "rgba(239,68,68,0.2)"
                        : r.severity === "medium"
                        ? "rgba(234,179,8,0.2)"
                        : "rgba(34,197,94,0.2)",
                      borderLeft: `4px solid ${
                        r.severity === "high" ? "#ef4444"
                        : r.severity === "medium" ? "#eab308"
                        : "#22c55e"
                      }`,
                    }}
                  >
                    <b>[{r.severity.toUpperCase()}]</b> {r.risk}
                    <br />
                    <span style={{ color: "#94a3b8", fontSize: "13px" }}>
                      → {r.mitigation}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Competitor Cards — real data */}
            <div style={neonCard}>
              <h3>Competitor Profiles</h3>
              {analysisData.competitors.map((c, i) => (
                <div
                  key={i}
                  style={{
                    padding: "14px",
                    marginBottom: "12px",
                    borderRadius: "10px",
                    background: "#1e293b",
                    borderLeft: `4px solid ${COLORS[i % COLORS.length]}`,
                  }}
                >
                  <b style={{ color: COLORS[i % COLORS.length] }}>{c.name}</b>
                  {" "}— {c.market_share} market share | {c.hq}
                  <br />
                  <span style={{ color: "#94a3b8", fontSize: "13px" }}>
                    Products: {c.key_products.join(", ")}
                  </span>
                  <br />
                  <span style={{ color: "#86efac", fontSize: "13px" }}>
                    ✓ {c.strengths.join(" · ")}
                  </span>
                </div>
              ))}
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

export default App;
