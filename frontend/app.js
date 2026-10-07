// ===== Config: change this to your FastAPI URL =====
// When the page is opened from the backend (port 8000) it uses the same address automatically.
const API_BASE_URL = (location.protocol === "file:" || location.port === "5500") ? "http://127.0.0.1:8000" : location.origin;
 
const FEATURES = [
  ["rst_count", "Number of TCP reset flags"],
  ["ICMP", "ICMP packet indicator (0 or 1)"],
  ["Min", "Minimum packet size"],
  ["AVG", "Average packet size"],
  ["IAT", "Inter-arrival time between packets"],
  ["Number", "Number of packets"],
  ["Variance", "Variance of packet size"],
  ["Weight", "Traffic weight"],
];
const SAMPLES = { // real rows from CICIoT2023
  normal: { rst_count: 0, ICMP: 1, Min: 42, AVG: 42, IAT: 83124075.84, Number: 9.5, Variance: 0, Weight: 141.55 },
  attack: { rst_count: 7391.2, ICMP: 0, Min: 66, AVG: 1144.67, IAT: 166522106.15, Number: 13.5, Variance: 1, Weight: 244.6 },
};
 
const $ = (id) => document.getElementById(id);
let records = [];
let page = 0;
const PER = 10;
const demo = () => $("demo").checked;
 
// ===== Toast =====
function toast(msg) {
  const t = $("toast");
  t.textContent = msg;
  t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), 4000);
}
 
let lastNetToast = 0;
function netToast(e) { // at most one error popup per 30 seconds, so auto-refresh does not spam
  if (Date.now() - lastNetToast < 30000) return;
  lastNetToast = Date.now();
  toast("Cannot reach the API (" + e.message + "). Is the backend running? Is Demo mode off? Check API_BASE_URL.");
}
 
// ===== API layer (all backend calls live here) =====
function mockRecords() {
  const out = [];
  for (let i = 1; i <= 40; i++) {
    const attack = Math.random() < 0.55;
    out.push({
      id: i,
      timestamp: new Date(Date.now() - (41 - i) * 600000).toISOString(),
      features: { ...(attack ? SAMPLES.attack : SAMPLES.normal) },
      prediction: attack ? "Attack" : "Normal",
      confidence: +(0.8 + Math.random() * 0.19).toFixed(2),
    });
  }
  return out;
}
const api = {
  async call(path, opts) {
    try {
      const r = await fetch(API_BASE_URL + path, opts);
      if (!r.ok) throw new Error("Server returned " + r.status);
      return await r.json();
    } catch (e) {
      netToast(e);
      throw e;
    }
  },
  async predict(f) {
    if (demo()) { // demo only: simple rule, NOT the real model
      const attack = f.rst_count > 500 || f.Variance > 0.5;
      const p = { prediction: attack ? "Attack" : "Normal", confidence: +(0.85 + Math.random() * 0.1).toFixed(2) };
      records.push({ id: records.length + 1, timestamp: new Date().toISOString(), features: f, ...p });
      return p;
    }
    return this.call("/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(f) });
  },
  async stats() {
    if (demo()) return statsFrom(records);
    return this.call("/stats");
  },
  async predictions() {
    return demo() ? records : this.call("/predictions");
  },
  async metrics() {
    if (demo()) return null;
    try { // a 404 just means evaluate.py has not been run yet, so no popup
      const r = await fetch(API_BASE_URL + "/metrics");
      return r.ok ? await r.json() : null;
    } catch (e) { netToast(e); return null; }
  },
};
 
// ===== Helpers =====
function statsFrom(rs) { // used by Demo mode only
  const a = rs.filter((r) => r.prediction === "Attack"), o = rs.filter((r) => r.prediction === "Normal");
  const m = (x) => (x.length ? x.reduce((t, r) => t + r.confidence, 0) / x.length : 0);
  return { total: rs.length, normal: o.length, attack: a.length, avg_confidence_normal: m(o), avg_confidence_attack: m(a) };
}
const fmt = (iso) => new Date(iso).toLocaleString();
const badge = (p) => `<span class="tag ${p === "Attack" ? "red" : "green"}">${p}</span>`;
const feat = (f) => Object.entries(f).map(([k, v]) => k + "=" + v).join(", ");
function table(el, rows) {
  el.innerHTML = "<tr><th>ID</th><th>Time</th><th>Features</th><th>Result</th><th>Confidence</th></tr>" +
    (rows.length ? rows.map((r) => `<tr><td>${r.id}</td><td>${fmt(r.timestamp)}</td><td>${feat(r.features)}</td><td>${badge(r.prediction)}</td><td>${Math.round(r.confidence * 100)}%</td></tr>`).join("")
      : '<tr><td colspan="5" class="muted">No predictions yet. Use Analyze traffic to create one.</td></tr>');
}
 
// ===== Dashboard =====
async function renderDash() {
  try { records = demo() && !records.length ? mockRecords() : await api.predictions(); } catch { records = []; }
  let st; // real totals from the database, so the numbers keep growing past 500
  try { st = await api.stats(); } catch { st = statsFrom([]); }
  const n = st.total, a = st.attack, ok = st.normal;
  $("stats").innerHTML = [["Total predictions", n], ["Normal", ok], ["Attacks", a], ["Attack rate", (n ? Math.round((a / n) * 100) : 0) + "%"]]
    .map(([l, v]) => `<div class="card"><b>${v}</b><span>${l}</span></div>`).join("");
  // donut
  const C = 2 * Math.PI * 40, da = n ? (a / n) * C : 0;
  $("donut").innerHTML = `<svg viewBox="0 0 100 100" width="170"><circle cx="50" cy="50" r="40" fill="none" stroke="#34d399" stroke-width="14"/>
    <circle cx="50" cy="50" r="40" fill="none" stroke="#f87171" stroke-width="14" stroke-dasharray="${da} ${C}" transform="rotate(-90 50 50)"/></svg>
    <div class="legend"><span>Normal ${ok}</span><span>Attack ${a}</span></div>`;
  // line: split records into up to 10 buckets
  const L = records.length, B = Math.max(1, Math.min(10, L)), bk = []; // only the rows we actually have
  for (let b = 0; b < B; b++) {
    const s = records.slice(Math.floor((b * L) / B), Math.floor(((b + 1) * L) / B));
    bk.push([s.filter((r) => r.prediction === "Normal").length, s.filter((r) => r.prediction === "Attack").length]);
  }
  const mx = Math.max(1, ...bk.flat()), W = 300, H = 120;
  const pts = (k) => bk.map((b, i) => `${bk.length > 1 ? (i / (bk.length - 1)) * W : W / 2},${H - (b[k] / mx) * H}`).join(" ");
  $("line").innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="140" preserveAspectRatio="none"><polyline points="${pts(0)}" fill="none" stroke="#34d399" stroke-width="2"/><polyline points="${pts(1)}" fill="none" stroke="#f87171" stroke-width="2"/></svg>
    <div class="legend"><span>Normal</span><span>Attack</span></div>`;
  // avg confidence
  const avg = (p) => (p === "Normal" ? st.avg_confidence_normal : st.avg_confidence_attack);
  $("bars").innerHTML = [["Normal", "#34d399"], ["Attack", "#f87171"]].map(([p, c]) =>
    `<div>${p} <span class="muted">${Math.round(avg(p) * 100)}%</span><div class="bar"><i style="width:${avg(p) * 100}%;background:${c}"></i></div></div>`).join("");
  table($("recent"), records.slice(-10).reverse());
}
 
// ===== Analyze =====
function buildForm() {
  $("fields").innerHTML = FEATURES.map(([k, tip]) =>
    `<label class="f" title="${tip}">${k} <span class="muted">(${tip})</span><input name="${k}" type="number" step="any" required><span class="err" id="e_${k}"></span></label>`).join("");
}
function fill(s) { FEATURES.forEach(([k]) => (document.querySelector(`[name=${k}]`).value = s[k])); }
$("sN").onclick = () => fill(SAMPLES.normal);
$("sA").onclick = () => fill(SAMPLES.attack);
$("form").onsubmit = async (e) => {
  e.preventDefault();
  const f = {}; let valid = true;
  FEATURES.forEach(([k]) => {
    const inp = document.querySelector(`[name=${k}]`), v = inp.value.trim();
    const bad = v === "" || isNaN(Number(v));
    inp.classList.toggle("bad", bad);
    $("e_" + k).textContent = bad ? "Enter a number" : "";
    if (bad) valid = false; else f[k] = Number(v);
  });
  if (!valid) return;
  $("result").innerHTML = '<p class="muted">Analyzing...</p>';
  try {
    const r = await api.predict(f), atk = r.prediction === "Attack", pc = Math.round(r.confidence * 100);
    $("result").innerHTML = `<div class="verdict ${atk ? "bad" : "ok"}">${atk ? "ATTACK DETECTED" : "NORMAL"}</div>
      <div>Confidence ${pc}%</div><div class="bar"><i style="width:${pc}%;background:${atk ? "#f87171" : "#34d399"}"></i></div>
      <p class="muted">${new Date().toLocaleString()}${demo() ? " - demo result, not the real model" : ""}</p>`;
  } catch {
    $("result").innerHTML = '<p class="err">The analysis failed.</p><button class="btn ghost" onclick="document.getElementById(\'form\').requestSubmit()">Retry</button>';
  }
};
 
// ===== History =====
async function renderHist() {
  try { records = demo() && !records.length ? mockRecords() : await api.predictions(); } catch { records = []; }
  const q = $("search").value.toLowerCase(), fl = $("filter").value;
  const rows = records.filter((r) => (fl === "all" || r.prediction === fl) && (r.id + " " + feat(r.features)).toLowerCase().includes(q)).reverse();
  const pages = Math.max(1, Math.ceil(rows.length / PER));
  page = Math.min(page, pages - 1);
  table($("hist"), rows.slice(page * PER, page * PER + PER));
  $("pg").textContent = `Page ${page + 1} of ${pages}`;
  $("hist").dataset.csv = JSON.stringify(rows);
}
$("filter").onchange = $("search").oninput = () => { page = 0; renderHist(); };
$("prev").onclick = () => { page = Math.max(0, page - 1); renderHist(); };
$("next").onclick = () => { page++; renderHist(); };
$("export").onclick = () => {
  const rows = JSON.parse($("hist").dataset.csv || "[]");
  const head = ["id", "timestamp", ...FEATURES.map((f) => f[0]), "prediction", "confidence"];
  const csv = [head.join(","), ...rows.map((r) => [r.id, r.timestamp, ...FEATURES.map(([k]) => r.features[k]), r.prediction, r.confidence].join(","))].join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  a.download = "predictions.csv"; a.click();
};
 
// ===== Model info =====
async function renderModel() {
  const m = await api.metrics();
  const keys = ["accuracy", "precision", "recall", "f1", "roc_auc"];
  $("models").innerHTML = [["XGBoost", "xgboost"], ["Random Forest", "random_forest"]].map(([name, id]) => {
    const d = m && m[id];
    return `<div class="panel"><h3>${name}</h3>${keys.map((k) => `<p>${k.replace("_", "-")}: <b>${d && d[k] != null ? d[k] : "Not available yet"}</b></p>`).join("")}
      <p>Confusion matrix: <b>${d && d.confusion_matrix ? JSON.stringify(d.confusion_matrix) : "Not available yet"}</b></p></div>`;
  }).join("");
}
 
// ===== Router =====
const routes = { "/": ["dash", renderDash], "/analyze": ["analyze", () => {}], "/history": ["history", renderHist], "/model": ["model", renderModel] };
function route() {
  const [id, fn] = routes[location.hash.slice(1) || "/"] || routes["/"];
  document.querySelectorAll(".page").forEach((p) => p.classList.toggle("on", p.id === id));
  document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("on", a.dataset.p === id));
  $("side").classList.remove("open");
  fn();
}
$("menu").onclick = () => $("side").classList.toggle("open");
$("demo").onchange = () => { $("demoTag").style.display = demo() ? "" : "none"; records = []; route(); };
window.onhashchange = route;
buildForm();
route();
 
// Live updates: re-fetch the dashboard / history every 5 seconds (real API only)
setInterval(() => {
  if (demo() || document.hidden) return;
  const h = location.hash.slice(1) || "/";
  if (h === "/") renderDash();
  else if (h === "/history") renderHist();
}, 5000);