import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';

mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    fontFamily: 'Inter, system-ui, sans-serif',
    primaryColor: '#0f172a',
    primaryTextColor: '#f8fafc',
    primaryBorderColor: '#38bdf8',
    lineColor: '#94a3b8',
    secondaryColor: '#1e293b',
    tertiaryColor: '#22c55e'
  }
});

const barcodeRoot = document.querySelector('[data-barcode]');
const rerunButton = document.querySelector('[data-rerun]');
const summaryEl = document.querySelector('[data-summary]');
const metricEls = {
  delivered: document.querySelector('[data-metric="delivered"]'),
  recovered: document.querySelector('[data-metric="recovered"]'),
  retransmit: document.querySelector('[data-metric="retransmit"]'),
  dropped: document.querySelector('[data-metric="dropped"]'),
  loss: document.querySelector('[data-metric="loss"]'),
  duration: document.querySelector('[data-metric="duration"]')
};

const scenarioButtons = document.querySelectorAll('[data-scenario-option]');
const eyebrowEl = document.querySelector('[data-eyebrow]');
const taglineEl = document.querySelector('[data-tagline]');
const scenarioCopyEl = document.querySelector('[data-scenario-copy]');
const barcodeLeadEl = document.querySelector('[data-barcode-lead]');
const barcodeContextEl = document.querySelector('[data-barcode-context]');
const legendEls = document.querySelectorAll('[data-legend]');
const metricsContainer = document.querySelector('[data-metrics]');
const metricCards = metricsContainer ? metricsContainer.querySelectorAll('[data-metric-card]') : [];

const STATUS_LABELS = {
  delivered: 'Delivered cleanly',
  recovered: 'Recovered via Reed-Solomon FEC',
  retransmit: 'Retransmitted over QUIC',
  dropped: 'Dropped — manual follow-up'
};

const SCENARIOS = {
  motorsport: {
    eyebrow: 'TrackShift 2025 · Motorsport Mission Control',
    tagline: 'Quantum-safe, priority-aware data for race weekends where milliseconds decide podiums.',
    copy: 'Trackside engineers beam pit wall deltas back to HQ before the strategy window closes.',
    barcodeLead: 'Simulate a Bahrain GP qualifying transfer where PitLink PQC stripes every chunk with priority, delivery status, and transport path.',
    barcodeContext: 'Motorsport context: 32KB P0 slices ride private 5G with LEO backup while P2 footage trickles over best-effort links.',
    legend: {
      P0: 'P0 — Strategy Delta',
      P1: 'P1 — Engineering Feeds',
      P2: 'P2 — Media + Archives'
    },
    metrics: [
      { key: 'latency', label: 'P0 Latency', number: '180', unit: 'ms', footnote: '15× faster than FTP' },
      { key: 'resilience', label: 'Failover', number: '<100', unit: 'ms', footnote: 'QUIC multipath + FEC' },
      { key: 'savings', label: 'Cost savings', number: '₹42', unit: 'L', footnote: '58% vs. Aspera (₹1Cr)' }
    ],
    priorityConfig: {
      P0: { label: 'P0 — Strategy Delta', baseMs: 48, pathOptions: ['Trackside 5G', 'Low-Earth Orbit'], fec: 'RS(12,9)' },
      P1: { label: 'P1 — Engineering Feeds', baseMs: 110, pathOptions: ['Trackside 5G', 'Low-Earth Orbit'], fec: 'RS(20,16)' },
      P2: { label: 'P2 — Media + Archives', baseMs: 280, pathOptions: ['Low-Earth Orbit', 'Trackside 5G'], fec: 'RS(20,18)' }
    },
    buckets: [
      { priority: 'P0', count: 18 },
      { priority: 'P1', count: 22 },
      { priority: 'P2', count: 26 }
    ],
    summary(stats) {
      return stats.dropped === 0
        ? 'P0 SLA intact — all strategy deltas landed before the pit wall freeze.'
        : 'Manual follow-up required — archive footage needs a resend.';
    }
  },
  mobility: {
    eyebrow: 'TrackShift 2025 · Autonomous Mobility Command',
    tagline: 'Quantum-safe control loops for autonomous fleets and curbside pods.',
    copy: 'Citywide fleet orchestration pushes safety kernel patches to every pod.',
    barcodeLead: 'Simulate an autonomous mobility control room distributing updates across a dense downtown corridor.',
    barcodeContext: 'Mobility context: 32KB safety kernels sprint over C-V2X while map refreshes traverse edge mesh and satellite backhaul.',
    legend: {
      P0: 'P0 — Safety Kernel',
      P1: 'P1 — Fleet Telemetry',
      P2: 'P2 — HD Map + Media'
    },
    metrics: [
      { key: 'latency', label: 'Safety kernel latency', number: '150', unit: 'ms', footnote: 'C-V2X slices + PQC' },
      { key: 'resilience', label: 'Failover', number: '<80', unit: 'ms', footnote: 'Auto-switch to satellite' },
      { key: 'savings', label: 'Fleet uptime', number: '97', unit: '%', footnote: 'Fewer manual recalls' }
    ],
    priorityConfig: {
      P0: { label: 'P0 — Safety Kernel', baseMs: 42, pathOptions: ['C-V2X 5G', 'Satellite Backhaul'], fec: 'RS(12,9)' },
      P1: { label: 'P1 — Fleet Telemetry', baseMs: 95, pathOptions: ['C-V2X 5G', 'Edge Mesh'], fec: 'RS(18,14)' },
      P2: { label: 'P2 — HD Map + Media', baseMs: 230, pathOptions: ['Edge Mesh', 'Satellite Backhaul'], fec: 'RS(20,18)' }
    },
    buckets: [
      { priority: 'P0', count: 20 },
      { priority: 'P1', count: 28 },
      { priority: 'P2', count: 18 }
    ],
    summary(stats) {
      return stats.dropped === 0
        ? 'Every pod acknowledges the safety kernel inside 1.5 seconds.'
        : 'Flag a depot stop — a few pods missed their update window.';
    }
  },
  manufacturing: {
    eyebrow: 'TrackShift 2025 · Smart Manufacturing Ops Center',
    tagline: 'Quantum-safe interlocks and telemetry for gigafactory robotics lines.',
    copy: 'Digital twin orchestrators synchronise safety interlocks, machine telemetry, and sustainability ledgers across the plant.',
    barcodeLead: 'Simulate a gigafactory cycle close where PitLink PQC routes interlocks, telemetry, and ESG logs across OT networks.',
    barcodeContext: 'Manufacturing context: Fiber TSN carries P0 interlocks while ESG ledgers flow over LoRa supervisory links.',
    legend: {
      P0: 'P0 — Safety Interlocks',
      P1: 'P1 — Machine Telemetry',
      P2: 'P2 — Sustainability Ledger'
    },
    metrics: [
      { key: 'latency', label: 'Interlock delivery', number: '120', unit: 'ms', footnote: 'Fiber TSN primary path' },
      { key: 'resilience', label: 'Failover', number: '<60', unit: 'ms', footnote: 'Industrial 5G handoff' },
      { key: 'savings', label: 'Downtime avoided', number: '92', unit: '%', footnote: 'Predictive maintenance automation' }
    ],
    priorityConfig: {
      P0: { label: 'P0 — Safety Interlocks', baseMs: 55, pathOptions: ['Fiber Backbone', 'Industrial 5G'], fec: 'RS(18,13)' },
      P1: { label: 'P1 — Machine Telemetry', baseMs: 130, pathOptions: ['Industrial 5G', 'Fiber Backbone'], fec: 'RS(20,15)' },
      P2: { label: 'P2 — Sustainability Ledger', baseMs: 260, pathOptions: ['LoRa Supervisory', 'Fiber Backbone'], fec: 'RS(22,18)' }
    },
    buckets: [
      { priority: 'P0', count: 16 },
      { priority: 'P1', count: 24 },
      { priority: 'P2', count: 20 }
    ],
    summary(stats) {
      return stats.dropped === 0
        ? 'Digital twin stays green — robotics cycle closes with interlocks intact.'
        : 'Alert the OT engineer — resend the ESG ledger chunks over fiber.';
    }
  }
};

let currentScenario = SCENARIOS.motorsport;

function randomFrom(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function weightedStatus(priority) {
  const roll = Math.random();
  if (priority === 'P0') {
    if (roll < 0.08) return 'recovered';
    if (roll < 0.11) return 'retransmit';
    return 'delivered';
  }
  if (priority === 'P1') {
    if (roll < 0.1) return 'recovered';
    if (roll < 0.16) return 'retransmit';
    if (roll < 0.18) return 'dropped';
    return 'delivered';
  }
  // P2
  if (roll < 0.12) return 'recovered';
  if (roll < 0.22) return 'retransmit';
  if (roll < 0.28) return 'dropped';
  return 'delivered';
}

function generateRun(scenario) {
  const { priorityConfig, buckets } = scenario;
  const laneDurations = Object.keys(priorityConfig).reduce((acc, key) => {
    acc[key] = 0;
    return acc;
  }, {});

  const stats = {
    delivered: 0,
    recovered: 0,
    retransmit: 0,
    dropped: 0,
    total: 0
  };

  const chunks = [];
  let chunkIndex = 0;

  buckets.forEach(({ priority, count }) => {
    const config = priorityConfig[priority] || priorityConfig.P0;
    const baseMs = config && typeof config.baseMs === 'number' ? config.baseMs : 120;
    const pathOptions = Array.isArray(config?.pathOptions) && config.pathOptions.length > 0
      ? config.pathOptions
      : ['Primary link'];
    const fecCode = config?.fec || 'RS(12,9)';

    for (let i = 0; i < count; i += 1) {
      chunkIndex += 1;
      const status = weightedStatus(priority);
      const basePath = randomFrom(pathOptions);
      let path = basePath;
      let note = `${STATUS_LABELS[status]} via ${path}`;
      let effectiveMs = baseMs + Math.random() * baseMs * 0.9;

      if (status === 'recovered') {
        stats.recovered += 1;
        note = `${STATUS_LABELS[status]} (${fecCode} on ${path})`;
      } else if (status === 'retransmit') {
        stats.retransmit += 1;
        const alternate = pathOptions.find((option) => option !== basePath) || basePath;
        note = `${STATUS_LABELS[status]} — switched to ${alternate}`;
        path = `${basePath} → ${alternate}`;
        effectiveMs += baseMs * 0.6;
      } else if (status === 'dropped') {
        stats.dropped += 1;
        note = `${STATUS_LABELS[status]} (${fecCode} exhausted)`;
        effectiveMs += baseMs;
      } else {
        stats.delivered += 1;
      }

      laneDurations[priority] = (laneDurations[priority] || 0) + effectiveMs;

      chunks.push({
        id: chunkIndex,
        priority,
        status,
        height: 45 + Math.random() * 55,
        path,
        transferMs: effectiveMs,
        fec: fecCode,
        note,
        label: config?.label || priority
      });
    }
  });

  stats.total = chunks.length;
  const duration = Math.max(...Object.values(laneDurations)) / 1000;
  const lossRate = stats.total > 0
    ? (stats.recovered + stats.retransmit + stats.dropped) / stats.total
    : 0;

  return { chunks, stats, duration, lossRate };
}

function stripeLabel(chunk, scenario) {
  const label = scenario.priorityConfig[chunk.priority]?.label || chunk.priority;
  return `Chunk ${chunk.id}\n${label}\n${chunk.note}\n${chunk.transferMs.toFixed(0)}ms · ${chunk.fec}`;
}

function renderRun() {
  if (!barcodeRoot) return;
  const { chunks, stats, duration, lossRate } = generateRun(currentScenario);

  barcodeRoot.innerHTML = '';

  chunks.forEach((chunk) => {
    const stripe = document.createElement('div');
    stripe.className = `barcode__stripe barcode__stripe--${chunk.priority.toLowerCase()} barcode__stripe--${chunk.status}`;
    stripe.style.height = `${chunk.height}%`;
    stripe.dataset.label = stripeLabel(chunk, currentScenario);
    stripe.setAttribute('tabindex', '0');
    barcodeRoot.appendChild(stripe);
  });

  metricEls.delivered.textContent = `${stats.delivered}/${stats.total}`;
  metricEls.recovered.textContent = stats.recovered;
  metricEls.retransmit.textContent = stats.retransmit;
  metricEls.dropped.textContent = stats.dropped;
  metricEls.loss.textContent = `${(lossRate * 100).toFixed(1)}%`;
  metricEls.duration.textContent = `${duration.toFixed(2)}s`;

  const highlight = currentScenario.summary(stats);
  summaryEl.textContent = `Simulated run: ${stats.total - stats.dropped}/${stats.total} chunks secured, ${stats.recovered} repaired with FEC, ${stats.retransmit} retransmitted. ${highlight}`;
}

function applyScenario(key) {
  const scenario = SCENARIOS[key];
  if (!scenario) return;

  currentScenario = scenario;

  scenarioButtons.forEach((button) => {
    const active = button.dataset.scenarioOption === key;
    button.classList.toggle('is-active', active);
    button.setAttribute('aria-pressed', active ? 'true' : 'false');
  });

  if (eyebrowEl) eyebrowEl.textContent = scenario.eyebrow;
  if (taglineEl) taglineEl.textContent = scenario.tagline;
  if (scenarioCopyEl) scenarioCopyEl.textContent = scenario.copy;
  if (barcodeLeadEl) barcodeLeadEl.textContent = scenario.barcodeLead;
  if (barcodeContextEl) barcodeContextEl.textContent = scenario.barcodeContext;

  legendEls.forEach((el) => {
    const keyName = el.dataset.legend;
    if (keyName && scenario.legend[keyName]) {
      el.textContent = scenario.legend[keyName];
    }
  });

  metricCards.forEach((card) => {
    const metricKey = card.dataset.metricCard;
    const metric = scenario.metrics.find((item) => item.key === metricKey);
    if (!metric) return;
    const labelEl = card.querySelector('[data-metric-label]');
    const numberEl = card.querySelector('[data-metric-number]');
    const unitEl = card.querySelector('[data-metric-unit]');
    const footnoteEl = card.querySelector('[data-metric-footnote]');

    if (labelEl) labelEl.textContent = metric.label;
    if (numberEl) numberEl.textContent = metric.number;
    if (unitEl) unitEl.textContent = metric.unit || '';
    if (footnoteEl) footnoteEl.textContent = metric.footnote || '';
  });

  renderRun();
}

if (scenarioButtons.length) {
  scenarioButtons.forEach((button) => {
    button.addEventListener('click', () => {
      applyScenario(button.dataset.scenarioOption);
    });
  });
}

if (rerunButton) {
  rerunButton.addEventListener('click', () => {
    renderRun();
  });
}

applyScenario('motorsport');
