# PitLink PQC Prototype Showcase

This directory now ships a lightweight, cross-industry prototype that demonstrates the key ideas behind the **PitLink PQC** priority-aware, quantum-safe data shuttle.  Use it to pitch PitLink in motorsport, autonomous mobility, smart manufacturing, or any future scenario you imagine for TrackShift 2025 showcases and onboarding sessions.

## 🎯 Prototype Goals

- Visualise how files are chunked and prioritised (P0 / P1 / P2) across multiple industries
- Show weighted fair queuing (WFQ) combined with earliest-deadline-first (EDF) ordering
- Emulate multi-path delivery across lossy links with forward error correction (FEC)
- Provide concise metrics for delivery time, losses, and recoveries
- Swap scenarios instantly (motorsport, urban mobility, gigafactory) to suit different TrackShift judging rubrics

## 🧪 Running the Demo

```bash
cd MonkOS/prototypes/pitlink_pqc
python prototype.py --scenario motorsport
```

Swap the scenario to explore other TrackShift narratives:

```bash
python prototype.py --scenario mobility --seed 42
python prototype.py --scenario manufacturing --priority P1 --size-mb 4
```

Each preset tunes chunk sizes, FEC ratios, and network paths to match a different innovation story. You can further tweak the dictionaries at the top of `prototype.py` to experiment with fresh industries, link conditions, or storytelling angles.

## 📈 Example Output

```
=== PitLink PQC Prototype · Motorsport — Trackside to Factory ===
Simulate a Formula 1 team pushing pit wall strategy files, high-rate telemetry, and bulk video from the circuit to HQ under fickle 5G and satellite conditions.
Available paths:
  • Trackside 5G — Private mmWave 5G slicing inside the paddock.
  • Low-Earth Orbit — Starlink backhaul for redundancy when cellular drops off.

Priority lane: P0 — Critical race strategy PDFs and control-plane commands.
Chunk size: 32768 bytes — data chunks: 64, parity chunks: 30

[Scheduler] Batch 01 → 11 chunks after WFQ+EDF

[Scheduler] Batch 02 → 9 chunks after WFQ+EDF
...
Summary: delivered 58/64 data chunks
Parity delivered: 24, lost: 6
Recovered via FEC: 6, unrecovered losses: 0
Total simulated time: 5.73s
Effective success ratio: 100.0%
Result: SLA met — all critical data reconstructed
Race control receives every delta before the pit wall freeze — mission accomplished.
```

Use the `--verbose` flag for more detailed logs:

```bash
python prototype.py --verbose
```

## 🧭 Scenario Presets

| Scenario (`--scenario`) | Narrative | P0 Focus | Representative Links |
|-------------------------|-----------|----------|-----------------------|
| `motorsport` | Trackside ➜ factory race strategy hand-offs | Strategy delta PDFs & control-plane commands | Trackside 5G · LEO backhaul |
| `mobility` | Autonomous robo-taxi fleet orchestration | Safety kernel hotfixes and emergency stops | C-V2X 5G · Edge mesh · Satellite |
| `manufacturing` | Battery gigafactory & robotics operations | Safety interlocks and compliance patches | Fiber TSN · Industrial 5G · LoRa OT |

All scenarios share the same PitLink pipeline — chunking, PQC, WFQ+EDF, FEC — but their chunk sizes, FEC ratios, weights, and storytelling notes are tuned to the domain. Extend the `SCENARIOS` dictionary in `prototype.py` to create additional industry lenses (telehealth, disaster response, climate monitoring, etc.).

## 🗺️ Flow Chart

```mermaid
flowchart TD
    S0([Select `--scenario`]):::scenario --> S1{Load scenario config}
    S1 -->|Priorities| P0[Priority templates<br/>Chunk size · FEC · weights]
    S1 -->|Paths| N0[Network paths<br/>Latency · loss · brownouts]
    S1 -->|Narrative| R0[Story cues<br/>Success/fail messaging]

    P0 --> C0[Adaptive chunking + BLAKE3 hashing]
    C0 --> K0[ML-KEM handshake → AES-GCM keys]
    K0 --> Q0[Queue chunks by priority lane]
    Q0 --> S2[WFQ batch selection]
    S2 --> E2[EDF ordering by deadline]
    E2 --> F2[Apply scenario FEC profile]
    F2 --> PATH{Select network path per chunk}
    PATH -->|Path A (e.g. Fiber / 5G)| TX1[QUIC transmit]
    PATH -->|Path B (e.g. Mesh / Satellite)| TX2[QUIC transmit]
    PATH -->|Path C (optional)| TX3[QUIC transmit]
    TX1 --> RX[Reassemble + verify Merkle tree]
    TX2 --> RX
    TX3 --> RX
    RX --> D0[Decrypt + commit to storage]
    D0 --> T0[Telemetry + SLA dashboard]
    T0 --> S0

    classDef scenario fill:#312e81,stroke:#a5b4fc,stroke-width:2px,color:#f8fafc;
```

The chart highlights where the scenario preset hooks into the pipeline (priority tuning, path definitions, narrative cues) before the shared PitLink delivery flow takes over.

## 🌐 Showcase Website

Need a quick way to impress TrackShift judges without running the Python simulator live?  Open the static showcase site shipped in
`web/`:

```bash
cd MonkOS/prototypes/pitlink_pqc/web
python -m http.server 8000  # optional; or just open index.html in a browser
```

The page includes:

- A **scenario switcher** that retells PitLink for motorsport, autonomous mobility, and gigafactory manufacturing.
- A **priority barcode** visualiser that adapts chunk counts, latency profiles, and recovery messaging per scenario.
- All eight **mermaid diagrams** from the TrackShift brief, ready to export as PNGs.
- A TrackShift-themed hero layout with dynamic metrics that refresh when you pivot industries.

The visualiser runs entirely client-side (vanilla JS + mermaid) so it works offline after a single load.

### 📤 Push Your Changes to GitHub

Ready to publish the latest simulator updates, flow chart, and showcase assets?  Commit locally and push them to your fork:

```bash
git checkout work        # or your feature branch
git status               # review changes
git add MonkOS/prototypes/pitlink_pqc
git commit -m "Refine PitLink showcase and docs"
git remote add origin https://github.com/<your-username>/<repo>.git  # first time only
git push -u origin work  # push your branch
```

Open a pull request on GitHub if you want collaborators to review the updates before merging into `main`.

### 🚀 Deploying to GitHub Pages for Free

Want to share the showcase without provisioning servers? GitHub Pages can host the static site straight from this repository:

1. **Prepare the `gh-pages` branch.** From the repository root run:
   ```bash
   git subtree split --prefix MonkOS/prototypes/pitlink_pqc/web -b gh-pages
   git push origin gh-pages
   ```
   This extracts the `web/` folder and makes it the root of a dedicated `gh-pages` branch.
2. **Enable GitHub Pages.** In the GitHub UI open **Settings → Pages**, select the **gh-pages** branch with the **/(root)** folder, and click **Save**.
3. **Wait for the deploy (≈1 minute).** Your site will appear at `https://<your-username>.github.io/<repository-name>/`.

Optional polish:

- Update the "View Prototype README" and "Prototype Script" buttons in `index.html` to point at the public GitHub URLs (e.g., `https://github.com/<user>/<repo>/blob/main/...`) so they work from the published site.
- Configure a custom domain from the same **Settings → Pages** screen if you own one.

To redeploy after local changes:

```bash
git checkout main
git pull
git subtree split --prefix MonkOS/prototypes/pitlink_pqc/web -b gh-pages
git push origin gh-pages --force
```

GitHub Pages rebuilds automatically after each push, keeping the TrackShift showcase free to host and easy to share with judges.

## 🧩 File Overview

| File | Purpose |
|------|---------|
| `prototype.py` | Self-contained Python simulator for PitLink PQC concepts |
| `sample_payload.txt` | Human-readable payload used when no file path is provided |
| `web/index.html` | Interactive TrackShift-ready landing page with barcode simulation and diagrams |
| `web/styles.css` | Styling for the showcase site |
| `web/app.js` | Mermaid init + barcode simulation logic |

## 📚 Next Steps

- Wrap the simulator in a small Flask/FastAPI service for live dashboards
- Integrate a Rust microservice once the QUIC engine is ready
- Hook into Grafana or another telemetry stack for real-time visualisations

