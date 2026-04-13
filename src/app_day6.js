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

  const exportPDF = async () => {
    const pdf = new jsPDF();

    // Title
    pdf.setFontSize(18);
    pdf.text("Smart Business Decision Assistant Report", 10, 20);

    // Executive Summary
    pdf.setFontSize(14);
    pdf.text("Executive Summary:", 10, 40);

    pdf.setFontSize(12);
    pdf.text(
      "Tesla dominates the EV market with strong innovation leadership and global brand recognition.",
      10,
      50
    );

    // SWOT
    pdf.setFontSize(14);
    pdf.text("SWOT Analysis:", 10, 70);

    pdf.setFontSize(12);
    pdf.text("Strength: Strong brand & innovation", 10, 80);
    pdf.text("Weakness: High pricing", 10, 90);
    pdf.text("Opportunity: Emerging markets", 10, 100);
    pdf.text("Threat: Intense EV competition", 10, 110);

    // Capture Pie Chart
    const pie = document.getElementById("pie-chart");
    const pieCanvas = await html2canvas(pie);
    const pieImg = pieCanvas.toDataURL("image/png");

    pdf.addImage(pieImg, "PNG", 15, 130, 180, 80);

    // Capture Bar Chart
    const bar = document.getElementById("bar-chart");
    const barCanvas = await html2canvas(bar);
    const barImg = barCanvas.toDataURL("image/png");

    pdf.addPage();
    pdf.text("Competitor Market Share Comparison", 10, 20);
    pdf.addImage(barImg, "PNG", 15, 30, 180, 90);

    pdf.save("SBDA_Report.pdf");
  };

  const pieData = [
    { name: "Tesla", value: 45 },
    { name: "BYD", value: 30 },
    { name: "NIO", value: 10 },
    { name: "Others", value: 15 }
  ];

  const barData = [
    { company: "Tesla", marketShare: 45 },
    { company: "BYD", marketShare: 30 },
    { company: "NIO", marketShare: 10 },
    { company: "Others", marketShare: 15 }
  ];

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  const cardStyle = {
    background: "white",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 14px rgba(0,0,0,0.12)"
  };

  const metricCard = {
    ...cardStyle,
    flex: 1,
    textAlign: "center"
  };

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial",
        background: "linear-gradient(135deg,#dbeafe,#f0f9ff)",
        minHeight: "100vh"
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
            width: "55%",
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

        <button
          onClick={exportPDF}
          style={{
            marginLeft: "10px",
            padding: "12px 22px",
            borderRadius: "6px",
            border: "none",
            background: "#1976d2",
            color: "white",
            fontWeight: "bold",
            cursor: "pointer"
          }}
        >
          Export PDF
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
          <div id="pie-chart" style={{ ...cardStyle, marginBottom: "20px" }}>
            <h2>📊 Market Share Distribution</h2>

            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={pieData} outerRadius={100} dataKey="value" label>
                  {pieData.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>

                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Bar Chart */}
          <div id="bar-chart" style={{ ...cardStyle, marginBottom: "20px" }}>
            <h2>📊 Competitor Market Share Comparison</h2>

            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="company" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="marketShare" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Executive Summary */}
          <div style={{ ...cardStyle, marginBottom: "20px" }}>
            <h2>🧾 Executive Summary</h2>
            <p>
              Tesla dominates the EV market with strong innovation leadership
              and global brand recognition.
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