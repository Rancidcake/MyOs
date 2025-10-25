"""PitLink PQC prototype simulator.

This refactored version supports multiple cross-industry scenarios so teams can
showcase PitLink PQC beyond motorsport.  Each scenario tunes the priority
settings, network paths, and storytelling hooks while keeping the core pipeline
intact:

- Adaptive chunking based on priority class
- Weighted fair queuing (WFQ) blended with earliest deadline first (EDF)
- Multi-path transmission across lossy links with optional brownouts
- Simplified forward error correction (FEC) accounting similar to RS(n, k)

The simulator remains dependency-free and intentionally lightweight for live
demos.  Use ``--scenario`` to explore variations such as autonomous mobility or
smart manufacturing.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import random
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


SCENARIOS = {
    "motorsport": {
        "label": "Motorsport — Trackside to Factory",
        "description": (
            "Simulate a Formula 1 team pushing pit wall strategy files, high-rate telemetry, "
            "and bulk video from the circuit to HQ under fickle 5G and satellite conditions."
        ),
        "default_priority": "P0",
        "default_payload_mb": 2.0,
        "priority_settings": {
            "P0": {
                "label": "P0 — Strategy Delta",
                "chunk_size": 32 * 1024,
                "deadline": 2.0,
                "fec": (16, 11),
                "weight": 8,
                "description": "Critical race strategy PDFs and control-plane commands.",
            },
            "P1": {
                "label": "P1 — Engineering Feeds",
                "chunk_size": 128 * 1024,
                "deadline": 8.0,
                "fec": (20, 16),
                "weight": 3,
                "description": "High-rate telemetry and digital twin updates for factory analysts.",
            },
            "P2": {
                "label": "P2 — Media + Archives",
                "chunk_size": 512 * 1024,
                "deadline": 30.0,
                "fec": (20, 18),
                "weight": 1,
                "description": "Bulk onboard footage, lidar captures, and sensor backlogs.",
            },
        },
        "background_traffic": {
            "P0": {"P1": 2, "P2": 2},
            "P1": {"P0": 1, "P2": 2},
            "P2": {"P1": 3},
        },
        "paths": [
            {
                "name": "Trackside 5G",
                "base_latency_ms": 55,
                "loss_rate": 0.08,
                "brownout_chance": 0.04,
                "brownout_multiplier": 2.4,
                "description": "Private mmWave 5G slicing inside the paddock.",
            },
            {
                "name": "Low-Earth Orbit",
                "base_latency_ms": 540,
                "loss_rate": 0.02,
                "brownout_chance": 0.01,
                "brownout_multiplier": 1.6,
                "description": "Starlink backhaul for redundancy when cellular drops off.",
            },
        ],
        "success_narrative": {
            "pass": "Race control receives every delta before the pit wall freeze — mission accomplished.",
            "fail": "Escalate to the trackside strategist: not every strategy delta arrived in time.",
        },
    },
    "mobility": {
        "label": "Urban Mobility — Autonomous Fleet Ops",
        "description": (
            "Co-ordinate over-the-air calibration bundles, live vehicle telemetry, and HD map refreshes across "
            "an autonomous robo-taxi fleet in a dense smart-city corridor."
        ),
        "default_priority": "P0",
        "default_payload_mb": 1.5,
        "priority_settings": {
            "P0": {
                "label": "P0 — Safety Kernel Patch",
                "chunk_size": 32 * 1024,
                "deadline": 1.5,
                "fec": (16, 11),
                "weight": 9,
                "description": "Safety-critical control patches and stop commands for the fleet.",
            },
            "P1": {
                "label": "P1 — Live Fleet Telemetry",
                "chunk_size": 96 * 1024,
                "deadline": 5.0,
                "fec": (18, 14),
                "weight": 3,
                "description": "LiDAR + perception telemetry routed to the edge AI orchestrator.",
            },
            "P2": {
                "label": "P2 — HD Map + Media",
                "chunk_size": 384 * 1024,
                "deadline": 25.0,
                "fec": (20, 18),
                "weight": 1,
                "description": "City-scale HD map refreshes and passenger experience content.",
            },
        },
        "background_traffic": {
            "P0": {"P1": 3, "P2": 1},
            "P1": {"P2": 3},
            "P2": {"P1": 2},
        },
        "paths": [
            {
                "name": "C-V2X 5G",
                "base_latency_ms": 40,
                "loss_rate": 0.06,
                "brownout_chance": 0.05,
                "brownout_multiplier": 2.0,
                "description": "City-operated cellular V2X slicing along arterial roads.",
            },
            {
                "name": "Edge Mesh",
                "base_latency_ms": 120,
                "loss_rate": 0.04,
                "brownout_chance": 0.02,
                "brownout_multiplier": 1.8,
                "description": "Municipal WiFi/mesh relays on lamp posts and EV chargers.",
            },
            {
                "name": "Satellite Backhaul",
                "base_latency_ms": 620,
                "loss_rate": 0.015,
                "brownout_chance": 0.008,
                "brownout_multiplier": 1.5,
                "description": "Always-on fallback via LEO constellations across the metro.",
            },
        ],
        "path_preferences": {
            "P0": ["C-V2X 5G", "Satellite Backhaul"],
            "P1": ["C-V2X 5G", "Edge Mesh"],
            "P2": ["Edge Mesh", "Satellite Backhaul"],
        },
        "success_narrative": {
            "pass": "Fleet orchestration green-lit — every vehicle receives the safety kernel within SLA.",
            "fail": "Trigger depot fallback mode — at least one pod missed its control update window.",
        },
    },
    "manufacturing": {
        "label": "Smart Manufacturing — Gigafactory Ops",
        "description": (
            "Synchronise robotics safety patches, machine telemetry, and sustainability audits across a battery "
            "gigafactory that spans wired and wireless OT networks."
        ),
        "default_priority": "P0",
        "default_payload_mb": 2.5,
        "priority_settings": {
            "P0": {
                "label": "P0 — Safety Interlocks",
                "chunk_size": 48 * 1024,
                "deadline": 1.8,
                "fec": (18, 13),
                "weight": 8,
                "description": "Robot safety interlocks, shutdown commands, and OSHA compliance patches.",
            },
            "P1": {
                "label": "P1 — Machine Telemetry",
                "chunk_size": 160 * 1024,
                "deadline": 6.0,
                "fec": (20, 15),
                "weight": 3,
                "description": "Predictive maintenance data and energy optimisation feeds.",
            },
            "P2": {
                "label": "P2 — Sustainability Ledger",
                "chunk_size": 512 * 1024,
                "deadline": 45.0,
                "fec": (22, 18),
                "weight": 2,
                "description": "Immutable ESG ledgers, QA video, and supplier provenance records.",
            },
        },
        "background_traffic": {
            "P0": {"P1": 2, "P2": 1},
            "P1": {"P0": 1, "P2": 2},
            "P2": {"P1": 2},
        },
        "paths": [
            {
                "name": "Industrial 5G",
                "base_latency_ms": 35,
                "loss_rate": 0.05,
                "brownout_chance": 0.03,
                "brownout_multiplier": 1.9,
                "description": "Private 5G slicing across the production floor.",
            },
            {
                "name": "Fiber Backbone",
                "base_latency_ms": 18,
                "loss_rate": 0.01,
                "brownout_chance": 0.005,
                "brownout_multiplier": 1.2,
                "description": "Deterministic TSN fiber linking OT zones to the control room.",
            },
            {
                "name": "LoRa Supervisory",
                "base_latency_ms": 480,
                "loss_rate": 0.03,
                "brownout_chance": 0.015,
                "brownout_multiplier": 1.4,
                "description": "Low-bandwidth supervisory network for environmental telemetry.",
            },
        ],
        "path_preferences": {
            "P0": ["Fiber Backbone", "Industrial 5G"],
            "P1": ["Industrial 5G", "Fiber Backbone"],
            "P2": ["LoRa Supervisory", "Fiber Backbone"],
        },
        "success_narrative": {
            "pass": "Digital twin stays green — all safety interlocks landed before the robotics cycle reset.",
            "fail": "Alert OT engineer: resend interlocks or route through the deterministic fiber segment.",
        },
    },
}


@dataclass
class Chunk:
    """Represents a data or parity chunk queued for transmission."""

    id: str
    priority: str
    payload: bytes
    deadline: float
    group: int
    is_parity: bool = False
    hash_hex: str = field(init=False)

    def __post_init__(self) -> None:
        self.hash_hex = hashlib.blake2s(self.payload).hexdigest()


@dataclass
class NetworkPath:
    """A lossy transmission path used by the simulator."""

    name: str
    base_latency_ms: float
    loss_rate: float
    brownout_chance: float = 0.0
    brownout_multiplier: float = 1.0
    rng: random.Random = field(default_factory=random.Random)
    active_brownout: int = 0

    def transmit(self, chunk: Chunk) -> Tuple[bool, float, bool]:
        """Simulate transmitting a chunk.

        Returns a tuple of (delivered, latency_ms, brownout_active).
        """

        # Occasionally trigger a brownout where latency and loss spike.
        if self.active_brownout > 0:
            self.active_brownout -= 1
            loss_rate = min(0.95, self.loss_rate * self.brownout_multiplier)
            latency = self.base_latency_ms * self.brownout_multiplier
            brownout = True
        else:
            if self.rng.random() < self.brownout_chance:
                # Enter brownout for the next few transmissions
                self.active_brownout = self.rng.randint(3, 6)
                loss_rate = min(0.95, self.loss_rate * self.brownout_multiplier)
                latency = self.base_latency_ms * self.brownout_multiplier
                brownout = True
            else:
                loss_rate = self.loss_rate
                latency = self.base_latency_ms
                brownout = False

        # Latency jitter (±20%)
        jitter_factor = 1.0 + self.rng.uniform(-0.2, 0.2)
        latency *= jitter_factor

        delivered = self.rng.random() > loss_rate
        return delivered, latency, brownout


@dataclass
class FECGroup:
    """Tracks loss / recovery statistics for a group of chunks."""

    parity_total: int
    data_lost: int = 0
    parity_lost: int = 0

    def account_loss(self, is_parity: bool) -> None:
        if is_parity:
            self.parity_lost += 1
        else:
            self.data_lost += 1

    def recovery_report(self) -> Tuple[int, int]:
        available_parity = max(0, self.parity_total - self.parity_lost)
        recovered = min(self.data_lost, available_parity)
        unrecovered = max(0, self.data_lost - recovered)
        return recovered, unrecovered


def load_payload(path: Optional[Path], target_size_mb: float) -> bytes:
    if path is None:
        default_path = Path(__file__).with_name("sample_payload.txt")
        data = default_path.read_bytes()
    else:
        data = Path(path).read_bytes()

    target_bytes = int(target_size_mb * 1024 * 1024)
    if len(data) >= target_bytes:
        return data[:target_bytes]

    repeats = math.ceil(target_bytes / len(data))
    expanded = (data * repeats)[:target_bytes]
    return expanded


def build_chunks(
    payload: bytes, priority: str, priority_settings: Dict[str, Dict[str, object]]
) -> Tuple[List[Chunk], Dict[int, FECGroup]]:
    settings = priority_settings[priority]
    chunk_size = settings["chunk_size"]
    n, k = settings["fec"]
    parity_count = n - k

    chunks: List[Chunk] = []
    fec_groups: Dict[int, FECGroup] = {}

    total_chunks = math.ceil(len(payload) / chunk_size)
    for index in range(total_chunks):
        start = index * chunk_size
        end = start + chunk_size
        piece = payload[start:end]
        if len(piece) < chunk_size:
            piece = piece + bytes(chunk_size - len(piece))
        group = index // k
        chunk = Chunk(
            id=f"c{index}",
            priority=priority,
            payload=piece,
            deadline=priority_settings[priority]["deadline"],
            group=group,
        )
        chunks.append(chunk)
        fec_groups.setdefault(group, FECGroup(parity_total=parity_count))

    # Generate parity placeholders (no payload hashing required for parity)
    for group_index in range(math.ceil(total_chunks / k)):
        for parity_idx in range(parity_count):
            chunk = Chunk(
                id=f"p{group_index}_{parity_idx}",
                priority=priority,
                payload=bytes([parity_idx % 256]) * chunk_size,
                deadline=priority_settings[priority]["deadline"],
                group=group_index,
                is_parity=True,
            )
            chunks.append(chunk)

    return chunks, fec_groups


def seed_background_traffic(
    priority: str,
    rng: random.Random,
    priority_settings: Dict[str, Dict[str, object]],
    background_config: Dict[str, Dict[str, int]],
) -> List[Chunk]:
    """Generate placeholder background traffic to make WFQ visible."""

    background: List[Chunk] = []
    config = background_config.get(priority, {})
    for prio, count in config.items():
        settings = priority_settings.get(prio)
        if not settings:
            continue
        dummy_payload = bytes(settings["chunk_size"])
        for _ in range(count):
            chunk = Chunk(
                id=f"bg_{prio}_{rng.randint(0, 9999)}",
                priority=prio,
                payload=dummy_payload,
                deadline=settings["deadline"],
                group=0,
            )
            background.append(chunk)
    return background


def wfq_batch(
    queues: Dict[str, List[Chunk]],
    batch_size: int,
    priority_settings: Dict[str, Dict[str, object]],
) -> List[Chunk]:
    weights = {prio: priority_settings[prio]["weight"] for prio in queues.keys() if prio in priority_settings}
    total_weight = sum(weights.values())
    selection: List[Chunk] = []
    for priority, queue in queues.items():
        if not queue:
            continue
        share = max(1, int(round(batch_size * (weights[priority] / total_weight))))
        for _ in range(min(share, len(queue))):
            selection.append(queue.pop(0))
    return selection


def edf_sort(chunks: List[Chunk]) -> List[Chunk]:
    return sorted(chunks, key=lambda chunk: chunk.deadline)


def select_path(
    chunk: Chunk,
    paths: List[NetworkPath],
    scenario: Dict[str, object],
) -> NetworkPath:
    """Choose a path based on priority and expected latency."""

    preferences = scenario.get("path_preferences", {})
    pref_list: Optional[Iterable[str]] = preferences.get(chunk.priority) if preferences else None
    if pref_list:
        pref_names = list(pref_list)
        for name in pref_names:
            candidate = next((p for p in paths if p.name == name and p.active_brownout == 0), None)
            if candidate:
                return candidate
        for name in pref_names:
            candidate = next((p for p in paths if p.name == name), None)
            if candidate:
                return candidate

    if chunk.priority == "P0":
        return min(paths, key=lambda p: (p.base_latency_ms, p.loss_rate))
    if chunk.priority == "P1":
        return min(paths, key=lambda p: p.base_latency_ms * 1.5 + p.loss_rate * 500)
    return min(paths, key=lambda p: p.loss_rate * 1000 + p.base_latency_ms * 0.5)


def simulate_transfer(
    payload: bytes,
    priority: str,
    scenario: Dict[str, object],
    verbose: bool = False,
    seed: Optional[int] = None,
) -> None:
    rng = random.Random(seed)
    priority_settings: Dict[str, Dict[str, object]] = scenario["priority_settings"]
    background = seed_background_traffic(
        priority,
        rng,
        priority_settings,
        scenario.get("background_traffic", {}),
    )

    chunks, fec_groups = build_chunks(payload, priority, priority_settings)

    queues: Dict[str, List[Chunk]] = {prio: [] for prio in priority_settings}
    for chunk in chunks + background:
        queues.setdefault(chunk.priority, []).append(chunk)

    for queue in queues.values():
        queue.sort(key=lambda c: c.id)

    total_data_chunks = sum(1 for c in chunks if not c.is_parity)
    parity_chunks = sum(1 for c in chunks if c.is_parity)

    paths = [
        NetworkPath(
            name=path_def["name"],
            base_latency_ms=path_def["base_latency_ms"],
            loss_rate=path_def["loss_rate"],
            brownout_chance=path_def.get("brownout_chance", 0.0),
            brownout_multiplier=path_def.get("brownout_multiplier", 1.0),
            rng=rng,
        )
        for path_def in scenario.get("paths", [])
    ]
    if not paths:
        raise ValueError("Scenario must define at least one network path")

    print(f"=== PitLink PQC Prototype · {scenario['label']} ===")
    print(scenario["description"])
    print("Available paths:")
    for path_def in scenario.get("paths", []):
        desc = path_def.get("description", "")
        suffix = f" — {desc}" if desc else ""
        print(f"  • {path_def['name']}{suffix}")
    print()

    settings = priority_settings[priority]
    print(f"Priority lane: {priority} — {settings['description']}")
    print(
        f"Chunk size: {settings['chunk_size']} bytes — data chunks: {total_data_chunks}, parity chunks: {parity_chunks}"
    )
    print()

    current_time_s = 0.0
    delivered_data = 0
    delivered_parity = 0
    lost_data = 0
    lost_parity = 0

    batch_index = 0
    while any(queues.values()):
        batch_index += 1
        batch = wfq_batch(queues, batch_size=12, priority_settings=priority_settings)
        if not batch:
            break
        batch = edf_sort(batch)
        print(f"[Scheduler] Batch {batch_index:02d} → {len(batch)} chunks after WFQ+EDF")

        for chunk in batch:
            path = select_path(chunk, paths, scenario)
            delivered, latency_ms, brownout = path.transmit(chunk)
            current_time_s += latency_ms / 1000.0
            label = "Parity" if chunk.is_parity else "Chunk"
            is_primary_data = not chunk.is_parity and chunk.id.startswith("c")
            is_primary_parity = chunk.is_parity and chunk.id.startswith("p")
            if delivered:
                if is_primary_parity:
                    delivered_parity += 1
                elif is_primary_data:
                    delivered_data += 1
                if verbose:
                    status = "brownout" if brownout else "ok"
                    print(
                        f"  [Path {path.name}] {label} {chunk.id} delivered in {latency_ms:5.1f} ms (hash {chunk.hash_hex[:8]}..., {status})"
                    )
            else:
                group = fec_groups.get(chunk.group)
                if group:
                    group.account_loss(chunk.is_parity)
                if is_primary_parity:
                    lost_parity += 1
                elif is_primary_data:
                    lost_data += 1
                outcome = "lost"
                if verbose:
                    status = "brownout" if brownout else "loss"
                    print(
                        f"  [Path {path.name}] {label} {chunk.id} {outcome.upper()} (hash {chunk.hash_hex[:8]}..., {status})"
                    )
        print()

    recovered = 0
    unrecovered = 0
    for group in fec_groups.values():
        got, missed = group.recovery_report()
        recovered += got
        unrecovered += missed

    success_ratio = (delivered_data + recovered) / total_data_chunks if total_data_chunks else 1.0

    summary_lines = [
        f"Summary: delivered {delivered_data}/{total_data_chunks} data chunks",
        f"Parity delivered: {delivered_parity}, lost: {lost_parity}",
        f"Recovered via FEC: {recovered}, unrecovered losses: {unrecovered}",
        f"Total simulated time: {current_time_s:.2f}s",
        f"Effective success ratio: {success_ratio * 100:.1f}%",
    ]

    narrative_key: Optional[str]
    if unrecovered == 0:
        summary_lines.append("Result: SLA met — all critical data reconstructed")
        narrative_key = "pass"
    else:
        summary_lines.append("Result: SLA breached — consider boosting parity or rerouting")
        narrative_key = "fail"

    success_notes = scenario.get("success_narrative", {})
    if success_notes and narrative_key:
        note = success_notes.get(narrative_key)
        if note:
            summary_lines.append(note)

    print("\n".join(summary_lines))


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PitLink PQC prototype simulator")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS.keys()),
        default="motorsport",
        help="Scenario to simulate (default: motorsport).",
    )
    parser.add_argument(
        "--payload",
        type=Path,
        default=None,
        help="Optional path to a payload file. Defaults to sample_payload.txt.",
    )
    parser.add_argument(
        "--priority",
        choices=["P0", "P1", "P2"],
        default=None,
        help="Priority lane to simulate. Defaults to the scenario's critical lane.",
    )
    parser.add_argument(
        "--size-mb",
        type=float,
        default=None,
        help="Override payload size in megabytes. Defaults to the scenario baseline.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging of every transmission.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Deterministic RNG seed for reproducible demos.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    scenario = SCENARIOS[args.scenario]
    priority = args.priority or scenario["default_priority"]
    if priority not in scenario["priority_settings"]:
        available = ", ".join(scenario["priority_settings"].keys())
        parser.error(f"Priority {priority} is not defined for the {args.scenario} scenario (options: {available}).")
        return

    size_mb = args.size_mb if args.size_mb is not None else scenario.get("default_payload_mb", 2.0)

    try:
        payload = load_payload(args.payload, size_mb)
    except FileNotFoundError as exc:
        parser.error(str(exc))
        return

    header = textwrap.dedent(
        f"""
        PitLink PQC demo payload configured
        - Scenario: {scenario['label']}
        - Priority: {priority} ({scenario['priority_settings'][priority]['label']})
        - Payload size: {len(payload) / (1024 * 1024):.2f} MiB
        """
    ).strip()
    print(header)
    print()

    simulate_transfer(payload, priority, scenario, verbose=args.verbose, seed=args.seed)


if __name__ == "__main__":
    main()
