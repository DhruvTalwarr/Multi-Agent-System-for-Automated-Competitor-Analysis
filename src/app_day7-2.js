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

    pdf.setFontSize(18);
    pdf.text("Smart Business Decision Assistant Report", 10, 20);

    pdf.setFontSize(14);
    pdf.text("Executive Summary:", 10, 40);

    pdf.setFontSize(12);
    pdf.text(
      "Tesla dominates the EV market with strong innovation leadership and global brand recognition.",
      10,
      50
    );

    pdf.setFontSize(14);
    pdf.text("SWOT Analysis:", 10, 70);

    pdf.setFontSize(12);
    pdf.text("Strength: Strong brand & innovation", 10, 80);
    pdf.text("Weakness: High pricing", 10, 90);
    pdf.text("Opportunity: Emerging markets", 10, 100);
    pdf.text("Threat: Intense EV competition", 10, 110);

    const pie = document.getElementById("pie-chart");
    const pieCanvas = await html2canvas(pie);
    const pieImg = pieCanvas.toDataURL("image/png");

    pdf.addImage(pieImg, "PNG", 15, 130, 180, 80);

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

  const COLORS = ["#00eaff", "#ff2bd6", "#3b82f6", "#ec4899"];

  const neonCard = {
    background: "#0f172a",
    padding: "22px",
    borderRadius: "16px",
    boxShadow: "0 0 20px #00eaff, 0 0 20px #ff2bd6",
    marginBottom: "25px",
    color: "white"
  };

  return (

    <div style={{ display: "flex", fontFamily: "Arial", minHeight: "100vh" }}>

      {/* Sidebar */}

      <div
        style={{
          width: "230px",
          background: "linear-gradient(180deg,#020617,#0f172a)",
          color: "#ff2bd6",
          padding: "25px",
          boxShadow: "0 0 20px #ff2bd6"
        }}
      >
        <h2>SBDA</h2>
        <p>📊 Dashboard</p>
        <p>📑 Reports</p>
        <p>⚙ Settings</p>
      </div>

      {/* Main Content */}

      <div
        style={{
          flex: 1,
          padding: "35px",
          background:
            "linear-gradient(135deg,#020617,#1e3a8a,#ff2bd6,#00eaff)",
          color: "white"
        }}
      >

        <h1 style={{color:"#00eaff"}}>Smart Business Decision Assistant</h1>

        {/* Query Box */}

        <div style={{
          ...neonCard,
          background:"linear-gradient(135deg,#00eaff,#ff2bd6)"
        }}>

          <input
            type="text"
            placeholder="Enter competitor analysis query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              padding: "12px",
              width: "60%",
              marginRight: "10px",
              borderRadius: "8px",
              border: "none"
            }}
          />

          <button
            onClick={handleAnalyze}
            style={{
              padding: "12px 20px",
              marginRight: "10px",
              borderRadius: "8px",
              border: "none",
              background: "#020617",
              color: "#00eaff",
              fontWeight: "bold"
            }}
          >
            Analyze
          </button>

          <button
            onClick={exportPDF}
            style={{
              padding: "12px 20px",
              borderRadius: "8px",
              border: "none",
              background: "#020617",
              color: "#ff2bd6",
              fontWeight: "bold"
            }}
          >
            Export PDF
          </button>

        </div>

        {loading && <h3>⏳ Running Multi-Agent Analysis...</h3>}

        {showReport && (

          <div>

            {/* Metrics */}

            <div style={{ display: "flex", gap: "25px", marginBottom: "30px" }}>

              <div style={{
                flex:1,
                padding:"30px",
                borderRadius:"18px",
                background:"linear-gradient(135deg,#00eaff,#3b82f6)",
                textAlign:"center",
                boxShadow:"0 0 20px #00eaff"
              }}>
                <h3>📄 Completeness</h3>
                <h1>85%</h1>
              </div>

              <div style={{
                flex:1,
                padding:"30px",
                borderRadius:"18px",
                background:"linear-gradient(135deg,#3b82f6,#ff2bd6)",
                textAlign:"center",
                boxShadow:"0 0 20px #ff2bd6"
              }}>
                <h3>🔍 Evidence Score</h3>
                <h1>92%</h1>
              </div>

              <div style={{
                flex:1,
                padding:"30px",
                borderRadius:"18px",
                background:"linear-gradient(135deg,#ff2bd6,#00eaff)",
                textAlign:"center",
                boxShadow:"0 0 20px #ff2bd6"
              }}>
                <h3>🧠 Analysis Depth</h3>
                <h1>88%</h1>
              </div>

            </div>

            {/* Pie Chart */}

            <div id="pie-chart" style={neonCard}>

              <h3>Market Share Distribution</h3>

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

            <div id="bar-chart" style={neonCard}>

              <h3>Competitor Market Share Comparison</h3>

              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#00eaff"/>
                  <XAxis dataKey="company" stroke="#ffffff"/>
                  <YAxis stroke="#ffffff"/>
                  <Tooltip />
                  <Bar dataKey="marketShare" fill="#ff2bd6"/>
                </BarChart>
              </ResponsiveContainer>

            </div>

            {/* Executive Summary */}

            <div style={{
              ...neonCard,
              background:"linear-gradient(135deg,#00eaff,#ff2bd6)"
            }}>
              <h3>Executive Summary</h3>
              <p>
                Tesla dominates the EV market with strong innovation leadership
                and global brand recognition.
              </p>
            </div>

            {/* SWOT */}

            <div style={{
              ...neonCard,
              background:"linear-gradient(135deg,#ff2bd6,#00eaff)"
            }}>
              <h3>SWOT Analysis</h3>
              <p><b>Strength:</b> Strong brand & innovation</p>
              <p><b>Weakness:</b> High pricing</p>
              <p><b>Opportunity:</b> Emerging markets</p>
              <p><b>Threat:</b> Intense EV competition</p>
            </div>

          </div>

        )}

      </div>

    </div>

  );
}

export default App;