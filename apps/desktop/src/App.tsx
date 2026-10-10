* {
  box-sizing: border-box;
}

:root {
  --bg: #0b1020;
  --bg-strong: #0f172a;
  --panel: #111827;
  --panel-strong: #1a2238;
  --panel-soft: #1f2937;
  --accent: #7dd3fc;
  --accent-strong: #38bdf8;
  --accent-warm: #fbbf24;
  --success: #34d399;
  --warning: #fbbf24;
  --danger: #f87171;
  --text: #e5eefc;
  --muted: #9aa8bd;
  --border: rgba(148, 163, 184, 0.18);
  --shadow: 0 18px 40px rgba(15, 23, 42, 0.45);
}

html, body, #root {
  margin: 0;
  min-height: 100%;
  background: linear-gradient(135deg, #0b1020 0%, #111827 100%);
  color: var(--text);
  font-family: Inter, 'Segoe UI', sans-serif;
}

body {
  min-height: 100vh;
}

button, input, select, textarea {
  font: inherit;
}

.app-shell {
  display: flex;
  min-height: 100vh;
  background: rgba(15, 23, 42, 0.9);
}

.sidebar {
  width: 260px;
  background: rgba(17, 24, 39, 0.9);
  border-right: 1px solid var(--border);
  padding: 20px 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  display: grid;
  place-items: center;
  color: #08111f;
  font-weight: 900;
}

.nav-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  color: var(--text);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: 0.2s ease;
}

.nav-item:hover,
.nav-item.active {
  background: rgba(125, 211, 252, 0.09);
  border-color: rgba(125, 211, 252, 0.2);
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 28px;
  border-bottom: 1px solid var(--border);
  background: rgba(11, 16, 32, 0.92);
}

.topbar h1 {
  margin: 0;
  font-size: 1.7rem;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.badge,
.pill {
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: var(--muted);
  background: rgba(17, 24, 39, 0.7);
}

.primary-btn,
.secondary-btn {
  border: 0;
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  transition: 0.2s ease;
}

.primary-btn {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #08111f;
  font-weight: 700;
}

.secondary-btn {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid var(--border);
  color: var(--text);
}

.main-panel {
  display: grid;
  grid-template-columns: 1.5fr 0.9fr;
  gap: 20px;
  padding: 22px 28px 28px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: rgba(17, 24, 39, 0.82);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow);
  padding: 18px;
}

.card h2, .card h3 {
  margin-top: 0;
  margin-bottom: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(140px, 1fr));
  gap: 14px;
}

.stat-box {
  background: rgba(148, 163, 184, 0.04);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
}

.stat-box small {
  color: var(--muted);
  display: block;
  margin-bottom: 8px;
}

.stat-box strong {
  font-size: 1.5rem;
}

.workspace {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.prompt-box,
.settings-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prompt-box textarea,
.prompt-box input,
.settings-panel input,
.settings-panel select {
  width: 100%;
  background: rgba(15, 23, 42, 0.9);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
}

.prompt-box textarea {
  min-height: 110px;
  resize: vertical;
}

.control-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.metric-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: var(--muted);
}

.metric-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.progress {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.12);
  overflow: hidden;
  margin-top: 12px;
}

.progress > div {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--success));
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.preview-tile {
  height: 120px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(125, 211, 252, 0.2), rgba(139, 92, 246, 0.18));
  border: 1px solid var(--border);
  display: flex;
  align-items: end;
  padding: 12px;
  color: #dfe9ff;
  font-weight: 600;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
}

.queue-item strong {
  display: block;
}

.queue-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  background: rgba(52, 211, 153, 0.1);
  color: var(--success);
  border: 1px solid rgba(52, 211, 153, 0.2);
}

@media (max-width: 1050px) {
  .main-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .app-shell {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }

  .stats-grid,
  .workspace,
  .gallery-grid,
  .control-row {
    grid-template-columns: 1fr;
  }
}
