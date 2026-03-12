import { useState, useRef } from "react";

const MONTHS = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December"
];

const BASE_URL = "http://localhost:8000";

export default function App() {
  const [activeTab, setActiveTab] = useState("upload");
  const [form, setForm] = useState({ name: "", month: "January", date: "", generation: "", type: "" });
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [videoMonth, setVideoMonth] = useState("January");
  const [videoStatus, setVideoStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileRef = useRef();

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    if (!image) return setUploadStatus({ error: "Please select an image." });
    setLoading(true); setUploadStatus(null);
    try {
      const fd = new FormData();
      fd.append("name", form.name);
      fd.append("month", form.month);
      fd.append("date", form.date);
      fd.append("generation", form.generation);
      fd.append("type", form.type);
      fd.append("image", image);
      const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setUploadStatus({ success: true, data });
    } catch (e) {
      setUploadStatus({ error: e.message });
    } finally { setLoading(false); }
  };

  const handleGenerateVideo = async () => {
    setLoading(true); setVideoStatus(null);
    try {
      const res = await fetch(`${BASE_URL}/generate-video/${videoMonth}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Video generation failed");
      setVideoStatus({ success: true, data });
    } catch (e) {
      setVideoStatus({ error: e.message });
    } finally { setLoading(false); }
  };

  return (
    <div style={styles.root}>
      <style>{css}</style>
      <div style={styles.grain} />

      <header style={styles.header}>
        <div style={styles.logoRow}>
          <span style={styles.logoIcon}>◈</span>
          <span style={styles.logoText}>AutoVid</span>
        </div>
        <p style={styles.tagline}>Let's make it memorable</p>
      </header>

      <nav style={styles.nav}>
        {["upload", "generate"].map(t => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            style={{ ...styles.navBtn, ...(activeTab === t ? styles.navBtnActive : {}) }}
          >
            {t === "upload" ? "↑ Upload Image" : "▶ Generate Video"}
          </button>
        ))}
      </nav>

      <main style={styles.main}>
        {activeTab === "upload" && (
          <div style={styles.panel} className="panel-enter">
            <h2 style={styles.panelTitle}>Upload</h2>

            <div style={styles.grid} className="panel-grid">
              <Field label="Full Name">
                <input style={styles.input} placeholder="e.g. John Doe"
                  value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
              </Field>

              <Field label="Month">
                <select style={styles.input} value={form.month}
                  onChange={e => setForm({...form, month: e.target.value})}>
                  {MONTHS.map(m => <option key={m}>{m}</option>)}
                </select>
              </Field>

              <Field label="Date">
                <input style={styles.input} type="number" placeholder="1–31"
                  min={1} max={31} value={form.date}
                  onChange={e => setForm({...form, date: e.target.value})} />
              </Field>

              <Field label="Generation">
                <input style={styles.input} type="number" placeholder="e.g. 1"
                  value={form.generation}
                  onChange={e => setForm({...form, generation: e.target.value})} />
              </Field>

              <Field label="Type" span>
                <input style={styles.input} placeholder="e.g. Birthday"
                  value={form.type} onChange={e => setForm({...form, type: e.target.value})} />
              </Field>
            </div>

            <div style={styles.dropZone} onClick={() => fileRef.current.click()} className="drop-zone">
              {imagePreview
                ? <img src={imagePreview} alt="preview" style={styles.preview} />
                : (
                  <div style={styles.dropInner}>
                    <span style={styles.dropIcon}>⊕</span>
                    <span style={styles.dropText}>Click to select image</span>
                    <span style={styles.dropSub}>JPG, PNG</span>
                  </div>
                )
              }
              <input ref={fileRef} type="file" accept="image/*"
                style={{ display: "none" }} onChange={handleImageChange} />
            </div>

            <button style={styles.btn} onClick={handleUpload}
              disabled={loading} className="btn-hover">
              {loading ? <span className="spinner">◌</span> : "↑ Upload"}
            </button>

            <StatusBox status={uploadStatus} />
          </div>
        )}

        {activeTab === "generate" && (
          <div style={styles.panel} className="panel-enter">
            <h2 style={styles.panelTitle}>Generate Video</h2>
            <p style={styles.desc}>Compile all uploaded images for the selected month into a video.</p>

            <Field label="Select Month">
              <select style={{ ...styles.input, fontSize: "1.1rem", padding: "14px 18px" }}
                value={videoMonth} onChange={e => setVideoMonth(e.target.value)}>
                {MONTHS.map(m => <option key={m}>{m}</option>)}
              </select>
            </Field>

            <div style={styles.monthCard}>
              <span style={styles.monthIcon}>◈</span>
              <span style={styles.monthLabel}>{videoMonth}</span>
            </div>

            <button style={styles.btn} onClick={handleGenerateVideo}
              disabled={loading} className="btn-hover">
              {loading ? <span className="spinner">◌</span> : "▶ Generate Video"}
            </button>

            <StatusBox status={videoStatus} />
          </div>
        )}
      </main>

      <footer style={styles.footer}>AutoVid © {new Date().getFullYear()}</footer>
    </div>
  );
}

function Field({ label, children, span }) {
  return (
    <div style={{ ...(span ? { gridColumn: "1 / -1" } : {}) }}>
      <label style={styles.label}>{label}</label>
      {children}
    </div>
  );
}

function StatusBox({ status }) {
  if (!status) return null;
  const ok = status.success;
  return (
    <div style={{ ...styles.statusBox, ...(ok ? styles.statusOk : styles.statusErr) }} className="status-pop">
      {ok ? "✓ " : "✕ "}
      {ok ? (status.data?.message || "Success!") : status.error}
      {ok && status.data?.response && (
        <pre style={styles.pre}>{JSON.stringify(status.data.response, null, 2)}</pre>
      )}
    </div>
  );
}

const SAND = "#f5ede0";
const INK = "#1a1410";
const AMBER = "#c8860a";
const LIGHT = "#faf7f2";

const styles = {
  root: { minWidth:" 1580px", minHeight: "100vh", background: LIGHT, color: INK, fontFamily: "'Cormorant Garamond', Georgia, serif", position: "relative", overflow: "hidden" },
  grain: { position: "fixed", inset: 0, backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\")", pointerEvents: "none", zIndex: 0 },
  // CHANGED: clamp for fluid vertical padding on mobile
  header: { textAlign: "center", padding: "clamp(28px, 6vw, 52px) 24px 24px", position: "relative", zIndex: 1 },
  logoRow: { display: "flex", alignItems: "center", justifyContent: "center", gap: 12, marginBottom: 6 },
  logoIcon: { fontSize: "2.2rem", color: AMBER },
  // CHANGED: clamp so logo shrinks on narrow screens
  logoText: { fontSize: "clamp(1.6rem, 5vw, 2.4rem)", fontWeight: 700, letterSpacing: "0.22em", color: INK },
  tagline: { fontSize: "0.9rem", letterSpacing: "0.3em", color: "#8a7560", textTransform: "uppercase", margin: 0 },
  // CHANGED: flexWrap so buttons stack on very small screens
  nav: { display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 0, margin: "0 auto 40px", maxWidth: 480, border: `1.5px solid ${AMBER}`, borderRadius: 2, overflow: "hidden", position: "relative", zIndex: 1 },
  navBtn: { flex: 1, padding: "13px 20px", background: "transparent", border: "none", cursor: "pointer", fontFamily: "inherit", fontSize: "0.85rem", letterSpacing: "0.15em", textTransform: "uppercase", color: "#8a7560", transition: "all 0.25s" },
  navBtnActive: { background: AMBER, color: "#fff" },
  // CHANGED: clamp for fluid horizontal padding
  main: {  margin: "0 auto", padding: "0 clamp(12px, 4vw, 20px) 60px", position: "relative", zIndex: 1 },
  // CHANGED: clamp for panel padding so it breathes on desktop but stays tight on mobile
  panel: { background: "#fff", border: `1.5px solid #e8ddd0`, borderRadius: 3, padding: "clamp(20px, 5vw, 40px) clamp(16px, 5vw, 36px)", boxShadow: "0 4px 40px rgba(26,20,16,0.07)" },
  panelTitle: { fontSize: "1.7rem", fontWeight: 600, letterSpacing: "0.06em", marginBottom: 28, marginTop: 0, borderBottom: `1px solid #e8ddd0`, paddingBottom: 16, color: INK },
  // CHANGED: auto-fit/minmax so columns collapse naturally instead of forcing 2-col
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "18px 20px", marginBottom: 24 },
  label: { display: "block", fontSize: "0.7rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#8a7560", marginBottom: 6, fontFamily: "sans-serif" },
  input: { width: "100%", padding: "11px 14px", border: `1.5px solid #e0d4c4`, borderRadius: 2, fontSize: "0.95rem", fontFamily: "inherit", background: LIGHT, color: INK, outline: "none", boxSizing: "border-box", transition: "border-color 0.2s" },
  dropZone: { border: `2px dashed #d4c4ae`, borderRadius: 3, minHeight: 180, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", marginBottom: 24, overflow: "hidden", transition: "border-color 0.2s, background 0.2s", background: LIGHT },
  dropInner: { display: "flex", flexDirection: "column", alignItems: "center", gap: 8, padding: 24 },
  dropIcon: { fontSize: "2.5rem", color: AMBER },
  dropText: { fontSize: "0.95rem", color: "#8a7560", letterSpacing: "0.08em" },
  dropSub: { fontSize: "0.75rem", color: "#b8a898", letterSpacing: "0.12em", fontFamily: "sans-serif" },
  preview: { width: "100%", maxHeight: 260, objectFit: "cover" },
  btn: { width: "100%", padding: "15px", background: INK, color: SAND, border: "none", borderRadius: 2, fontSize: "0.85rem", letterSpacing: "0.25em", textTransform: "uppercase", fontFamily: "inherit", cursor: "pointer", transition: "background 0.2s", marginTop: 4 },
  statusBox: { marginTop: 20, padding: "14px 18px", borderRadius: 2, fontSize: "0.95rem", fontFamily: "sans-serif" },
  statusOk: { background: "#f0f7ef", border: "1.5px solid #a8d5a2", color: "#2d6a27" },
  statusErr: { background: "#fdf0ef", border: "1.5px solid #e8a8a2", color: "#8b2020" },
  pre: { marginTop: 10, fontSize: "0.75rem", whiteSpace: "pre-wrap", wordBreak: "break-all", color: "#4a6644" },
  desc: { color: "#8a7560", fontSize: "1rem", marginBottom: 28, marginTop: -10, lineHeight: 1.6 },
  monthCard: { display: "flex", alignItems: "center", gap: 14, padding: "22px 24px", background: SAND, borderRadius: 3, margin: "24px 0", border: `1px solid #e0d0bc` },
  monthIcon: { fontSize: "1.6rem", color: AMBER },
  monthLabel: { fontSize: "1.8rem", fontWeight: 600, letterSpacing: "0.1em" },
  footer: { textAlign: "center", padding: "20px", fontSize: "0.7rem", letterSpacing: "0.25em", color: "#b8a898", fontFamily: "sans-serif", position: "relative", zIndex: 1 },
};

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&display=swap');
  * { box-sizing: border-box; }
  .panel-enter { animation: fadeUp 0.4s ease both; }
  @keyframes fadeUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:none; } }
  .btn-hover:hover:not(:disabled) { background: #c8860a !important; }
  .btn-hover:disabled { opacity: 0.6; cursor: not-allowed; }
  .drop-zone:hover { border-color: #c8860a !important; background: #fdf8f2 !important; }
  input:focus, select:focus { border-color: #c8860a !important; }
  .status-pop { animation: pop 0.3s ease both; }
  @keyframes pop { from { opacity:0; transform:scale(0.97); } to { opacity:1; transform:none; } }
  .spinner { display:inline-block; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* CHANGED: single column grid below 400px */
  @media (max-width: 400px) {
    .panel-grid { grid-template-columns: 1fr !important; }
  }
  /* CHANGED: nav buttons go full-width and stack below 360px */
  @media (max-width: 360px) {
    nav button { flex: 1 1 100%; }
  }
`;
