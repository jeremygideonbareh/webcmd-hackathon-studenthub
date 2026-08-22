// Atlas dashboard — fetches /api/digest, renders cards, POSTs feedback.

const FEEDBACK = { "👍": "like", "👎": "dislike", "⭐": "save", "🚫": "block" };
const RISK_COLORS = {
  SAFE: "#2ecc71",
  CAUTION: "#f39c12",
  WARNING: "#e67e22",
  DANGER: "#e74c3c",
};

const state = { weights: {} };

async function getJSON(url, options) {
  const r = await fetch(url, options);
  if (!r.ok) throw new Error(`${url} → ${r.status}`);
  return r.json();
}

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  return node;
}

function riskStyle(level) {
  return { borderColor: RISK_COLORS[level] || "#888", color: RISK_COLORS[level] || "#333" };
}

function renderGpa(gpa) {
  const section = document.getElementById("gpa-section");
  if (!gpa || !gpa.current_cgpa) {
    section.classList.add("hidden");
    return;
  }
  section.classList.remove("hidden");
  section.innerHTML = "";
  const chip = el("div", "gpa-chip");
  chip.innerHTML = `
    <span class="gpa-value">${gpa.current_cgpa}</span>
    <span class="gpa-label">CGPA</span>
    <span class="gpa-sub">sem ${gpa.semester_gpa} · ${gpa.gpa_trend || "stable"}</span>`;
  section.appendChild(chip);
}

function renderAttendance(list) {
  const grid = document.getElementById("attendance-grid");
  grid.innerHTML = "";
  if (!list.length) {
    grid.appendChild(el("p", "empty", "No attendance data yet."));
    return;
  }
  list.forEach((s) => {
    const card = el("div", "card attendance-card");
    const level = s.risk_level || "INFO";
    card.style.borderLeft = `4px solid ${RISK_COLORS[level] || "#888"}`;

    const head = el("div", "card-head");
    head.appendChild(el("span", "card-code", s.code));
    head.appendChild(el("span", "card-subject", s.name));
    head.appendChild(el("span", "risk-badge", level));

    const pct = el("div", "attendance-pct", `${s.current_pct}%`);
    pct.style.color = riskStyle(level).color;

    const meta = el("div", "card-meta");
    meta.appendChild(el("span", "", `${s.classes_present}/${s.classes_total} classes`));
    meta.appendChild(el("span", "muted", `skip ${s.classes_can_skip} · attend ${s.classes_must_attend}`));

    card.append(head, pct, meta);
    if (s.projection) card.appendChild(el("p", "projection", s.projection));
    grid.appendChild(card);
  });
}

function renderJobs(list) {
  const listEl = document.getElementById("jobs-list");
  listEl.innerHTML = "";
  if (!list.length) {
    listEl.appendChild(el("p", "empty", "No matched internships yet."));
    return;
  }
  list.forEach((job) => {
    const card = el("div", "card job-card");
    const head = el("div", "job-head");
    head.appendChild(el("div", "job-title-wrap"));
    head.querySelector(".job-title-wrap").appendChild(el("span", "job-title", job.title));
    head.querySelector(".job-title-wrap").appendChild(el("span", "job-company", job.company));
    const score = el("span", "match-score", `${Math.round(job.match_score * 100)}%`);
    head.appendChild(score);

    const meta = el("div", "card-meta");
    meta.appendChild(el("span", "", job.location || "—"));
    meta.appendChild(el("span", "", job.stipend || "—"));

    const reason = el("p", "match-reason", job.match_reason || "");
    const buttons = el("div", "feedback-row");
    buttons.dataset.itemType = "job";
    buttons.dataset.itemId = job.id;
    Object.keys(FEEDBACK).forEach((emoji) => {
      const b = el("button", "fb-btn", emoji);
      b.title = FEEDBACK[emoji];
      b.addEventListener("click", () => sendFeedback(buttons, emoji));
      buttons.appendChild(b);
    });

    card.append(head, meta, reason, buttons);
    listEl.appendChild(card);
  });
}

function renderHousing(list) {
  const grid = document.getElementById("housing-grid");
  grid.innerHTML = "";
  if (!list.length) {
    grid.appendChild(el("p", "empty", "No housing listings yet."));
    return;
  }
  list.forEach((h) => {
    const card = el("div", "card housing-card");
    card.appendChild(el("span", "housing-title", h.title));
    const price = el("div", "housing-price", h.price);
    card.appendChild(price);
    const meta = el("div", "card-meta");
    meta.appendChild(el("span", "", h.location || "—"));
    meta.appendChild(el("span", "muted", `${h.bedrooms || "?"} BHK · ${h.furnished || "—"}`));
    card.appendChild(meta);
    if (h.url) {
      const a = el("a", "housing-link", "view listing ↗");
      a.href = h.url;
      a.target = "_blank";
      card.appendChild(a);
    }
    grid.appendChild(card);
  });
}

async function sendFeedback(container, emoji) {
  try {
    const res = await getJSON("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        item_type: container.dataset.itemType,
        item_id: container.dataset.itemId,
        reaction: emoji,
      }),
    });
    state.weights = res.weights;
    flashLearned(container, emoji);
  } catch (e) {
    console.error("feedback failed", e);
  }
}

function flashLearned(container, emoji) {
  const note = el("span", "learned", `learned ${FEEDBACK[emoji]} ✓`);
  container.appendChild(note);
  setTimeout(() => note.remove(), 1600);
}

async function loadDigest() {
  try {
    const d = await getJSON("/api/digest");
    state.weights = d.weights || {};
    renderGpa(d.gpa);
    renderAttendance(d.attendance);
    renderJobs(d.jobs);
    renderHousing(d.housing);
    document.getElementById("last-updated").textContent =
      `updated ${new Date().toLocaleTimeString()}`;
  } catch (e) {
    console.error("digest failed", e);
  }
}

document.getElementById("refresh-btn").addEventListener("click", loadDigest);
loadDigest();