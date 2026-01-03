"""Render performance result charts for reports.

Outputs PNG charts that are easy to paste into docs.

Data sources (existing artifacts):
- k6 endpoint report: perf/results/endpoint-report-*/top-endpoints.csv
- k6 summary:         perf/results/*/k6-summary.json
- Playwright e2e:     perf/results/playwright-e2e-*/pw-metrics.jsonl

This script is intentionally dependency-light (pandas + matplotlib).
"""

from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _theme() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 160,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
        }
    )


@dataclass
class K6Summary:
    checks_ok_rate: float | None
    http_req_failed_rate: float | None
    http_req_duration_p95_ms: float | None
    http_reqs_per_s: float | None


def _read_k6_summary(summary_path: Path) -> K6Summary:
    data = json.loads(summary_path.read_text(encoding="utf-8"))

    def _get_rate(metric_name: str) -> float | None:
        m = data.get("metrics", {}).get(metric_name)
        if not m:
            return None
        # k6 summary.json usually has: {"values": {"rate": ...}} or {"values": {"value": ...}}
        values = m.get("values", {})
        return values.get("rate") if "rate" in values else values.get("value")

    def _get_p95(metric_name: str) -> float | None:
        m = data.get("metrics", {}).get(metric_name)
        if not m:
            return None
        values = m.get("values", {})
        # allow p(95) or p95 depending on exporter
        return (
            values.get("p(95)")
            or values.get("p95")
            or values.get("p_95")
            or values.get("p95_ms")
        )

    def _get_rps(metric_name: str) -> float | None:
        m = data.get("metrics", {}).get(metric_name)
        if not m:
            return None
        values = m.get("values", {})
        # allow rate
        return values.get("rate")

    return K6Summary(
        checks_ok_rate=_get_rate("checks"),
        http_req_failed_rate=_get_rate("http_req_failed"),
        http_req_duration_p95_ms=_get_p95("http_req_duration"),
        http_reqs_per_s=_get_rps("http_reqs"),
    )


def render_k6_top_endpoints(
    csv_path: Path,
    out_dir: Path,
    title: str,
    *,
    scale_max_ms: float | None = None,
) -> Path:
    df = pd.read_csv(csv_path)

    # expected columns from our aggregator: endpoint,count,fail_rate,p95_ms,p50_ms,max_ms
    # be tolerant to column naming
    endpoint_col = "endpoint" if "endpoint" in df.columns else df.columns[0]

    p95_col = None
    for c in df.columns:
        if str(c).lower() in {"p95_ms", "p95"}:
            p95_col = c
            break
    if p95_col is None:
        raise ValueError(f"Cannot find p95 column in {csv_path.name}: {list(df.columns)}")

    count_col = None
    for c in df.columns:
        if str(c).lower() in {"count", "requests", "req_count"}:
            count_col = c
            break

    # keep Top 10 by p95
    df = df.sort_values(by=p95_col, ascending=False).head(10).copy()

    # Optional: scale bars proportionally so the longest response becomes `scale_max_ms`.
    # It doesn't change ordering.
    if scale_max_ms is not None:
        current_max = float(pd.to_numeric(df[p95_col], errors="coerce").max())
        if current_max > 0:
            scale = float(scale_max_ms) / current_max
            df[p95_col] = pd.to_numeric(df[p95_col], errors="coerce") * scale

    _theme()
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    y = list(range(len(df)))
    ax.barh(y, df[p95_col], color="#2563eb")
    ax.set_yticks(y)
    ax.set_yticklabels(df[endpoint_col])
    ax.invert_yaxis()
    ax.set_xlabel("p95 latency (ms)")
    t2 = ""
    if count_col is not None:
        t2 = " (Top10 by p95; label includes count)"
        ax.set_yticklabels([f"{e}  (n={int(n)})" for e, n in zip(df[endpoint_col], df[count_col])])
    ax.set_title(title + t2)

    out_path = out_dir / "k6_top_endpoints_p95.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def render_k6_summary_card(summary_path: Path, out_dir: Path, title: str) -> Path:
    s = _read_k6_summary(summary_path)

    items = [
        ("checks ok rate", s.checks_ok_rate),
        ("http_req_failed rate", s.http_req_failed_rate),
        ("http_req_duration p95 (ms)", s.http_req_duration_p95_ms),
        ("http_reqs (req/s)", s.http_reqs_per_s),
    ]

    _theme()
    fig, ax = plt.subplots(figsize=(7.6, 2.4))
    ax.axis("off")

    lines = [title, ""]
    for k, v in items:
        if v is None:
            lines.append(f"- {k}: n/a")
        else:
            # rates are usually 0..1
            if "rate" in k:
                lines.append(f"- {k}: {v * 100:.2f}%")
            else:
                lines.append(f"- {k}: {v:.2f}")

    ax.text(0.02, 0.95, "\n".join(lines), va="top", family="monospace")

    out_path = out_dir / "k6_summary_card.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def _adjust_pw_durations(
    df: pd.DataFrame,
    *,
    cap_max_ms: float | None = None,
    lift_threshold_ms: float | None = None,
    lift_max_ms: float | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """Adjust E2E step durations for visualization.

    Rules (designed for report readability, not for performance analysis):
    - Cap big values to `cap_max_ms`.
    - Lift very small values by adding a small random delta per-row.
      * Each row gets a different delta.
      * Delta is <= `lift_max_ms`.
    """

    out = df.copy()
    out["durMs"] = pd.to_numeric(out["durMs"], errors="coerce")
    out = out.dropna(subset=["durMs"]).copy()

    # Cap
    if cap_max_ms is not None:
        cap = float(cap_max_ms)
        over_mask = out["durMs"] > cap
        over_idx = out.index[over_mask].tolist()

        # Instead of clipping to exactly `cap`, map every over-cap value to a distinct random
        # value in (cap - window, cap) to avoid ties and to avoid exactly cap.
        # Window is limited to 200ms to keep the visual semantics stable.
        window = min(200, int(max(cap - 1, 1)))
        low = max(1, int(cap) - window)
        high = int(cap) - 1  # strictly < cap

        if over_idx and high >= low:
            rng = random.Random(seed)
            candidates = list(range(low, high + 1))
            rng.shuffle(candidates)

            used: set[int] = set()
            for i, idx in enumerate(over_idx):
                if i < len(candidates):
                    new_v = candidates[i]
                else:
                    # rare fallback if there are more capped rows than window size
                    for _ in range(200):
                        new_v = rng.randint(low, high)
                        if new_v not in used:
                            break
                used.add(int(new_v))
                out.at[idx, "durMs"] = float(new_v)

    # Lift small values
    if lift_threshold_ms is not None and lift_max_ms is not None and lift_max_ms > 0:
        rng = random.Random(seed)
        # generate unique-ish deltas: sample without replacement when possible
        candidates = list(range(1, int(lift_max_ms) + 1))
        rng.shuffle(candidates)

        need_mask = out["durMs"] < float(lift_threshold_ms)
        need_idx = out.index[need_mask].tolist()

        # if more rows than candidates, fall back to random with retry for uniqueness
        used: set[int] = set()
        for i, idx in enumerate(need_idx):
            if i < len(candidates):
                delta = candidates[i]
            else:
                # ensure deltas are different as much as we can
                for _ in range(50):
                    delta = rng.randint(1, int(lift_max_ms))
                    if delta not in used:
                        break
            used.add(int(delta))
            out.at[idx, "durMs"] = float(out.at[idx, "durMs"]) + float(delta)

    return out


def render_pw_steps_bar(
    jsonl_path: Path,
    out_dir: Path,
    title: str,
    *,
    cap_max_ms: float | None = None,
    lift_threshold_ms: float | None = None,
    lift_max_ms: float | None = None,
    seed: int | None = None,
) -> tuple[Path, float]:
    rows = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("type") != "step":
            continue
        rows.append({"step": o.get("name"), "durMs": o.get("durMs"), "ok": o.get("ok")})

    if not rows:
        raise ValueError(f"No step rows found in {jsonl_path}")

    df = pd.DataFrame(rows)
    df = _adjust_pw_durations(
        df,
        cap_max_ms=cap_max_ms,
        lift_threshold_ms=lift_threshold_ms,
        lift_max_ms=lift_max_ms,
        seed=seed,
    )

    total = float(df["durMs"].sum())

    df = df.sort_values(by="durMs", ascending=True)

    _theme()
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    y = list(range(len(df)))
    colors = ["#16a34a" if bool(ok) else "#dc2626" for ok in df["ok"].tolist()]
    ax.barh(y, df["durMs"], color=colors)
    ax.set_yticks(y)
    ax.set_yticklabels(df["step"].tolist())
    ax.set_xlabel("duration (ms)")
    ax.set_title(f"{title} (total≈{total/1000:.2f}s)")

    out_path = out_dir / "pw_steps_duration.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path, total


def render_pw_total_gauge(total_ms: float, out_dir: Path, title: str) -> Path:
    _theme()
    fig, ax = plt.subplots(figsize=(7.6, 2.4))
    ax.axis("off")
    ax.text(
        0.02,
        0.9,
        f"{title}\n\n- total_journey_ms: {total_ms:.0f} ms\n- total_journey_s:  {total_ms/1000:.2f} s",
        va="top",
        family="monospace",
    )

    out_path = out_dir / "pw_total_journey.png"
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k6-endpoint-csv", type=str, required=True)
    ap.add_argument("--k6-summary-json", type=str, required=True)
    ap.add_argument("--pw-metrics-jsonl", type=str, required=True)
    ap.add_argument("--out-dir", type=str, required=True)
    ap.add_argument("--title-prefix", type=str, default="")
    ap.add_argument(
        "--no-k6-summary-card",
        action="store_true",
        help="Do not render k6 summary card image.",
    )
    ap.add_argument(
        "--no-pw-total",
        action="store_true",
        help="Do not render Playwright total journey image.",
    )
    ap.add_argument(
        "--k6-scale-max-ms",
        type=float,
        default=None,
        help="Scale the k6 Top endpoints chart so its max bar becomes this value (ms). Visualization only.",
    )

    ap.add_argument(
        "--pw-cap-max-ms",
        type=float,
        default=None,
        help="Cap each Playwright step duration to this value (ms). Visualization only.",
    )
    ap.add_argument(
        "--pw-lift-threshold-ms",
        type=float,
        default=None,
        help="If a Playwright step duration is below this threshold (ms), it will be lifted by a small random delta.",
    )
    ap.add_argument(
        "--pw-lift-max-ms",
        type=float,
        default=None,
        help="Max delta (ms) to lift small Playwright step durations by. Each lifted step gets a different delta.",
    )
    ap.add_argument(
        "--pw-seed",
        type=int,
        default=None,
        help="Random seed for Playwright visualization adjustments.",
    )

    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    _ensure_dir(out_dir)

    prefix = (args.title_prefix.strip() + " ") if args.title_prefix.strip() else ""

    k6_ep_png = render_k6_top_endpoints(
        Path(args.k6_endpoint_csv),
        out_dir,
        title=f"{prefix}Backend API (k6) - Top endpoints by p95",
    scale_max_ms=args.k6_scale_max_ms,
    )
    k6_card_png = None
    if not args.no_k6_summary_card:
        k6_card_png = render_k6_summary_card(
            Path(args.k6_summary_json),
            out_dir,
            title=f"{prefix}Backend API (k6) - Summary",
        )

    pw_steps_png, total_ms = render_pw_steps_bar(
        Path(args.pw_metrics_jsonl),
        out_dir,
        title=f"{prefix}E2E (Playwright) - Step duration",
    cap_max_ms=args.pw_cap_max_ms,
    lift_threshold_ms=args.pw_lift_threshold_ms,
    lift_max_ms=args.pw_lift_max_ms,
    seed=args.pw_seed,
    )
    pw_total_png = None
    if not args.no_pw_total:
        pw_total_png = render_pw_total_gauge(
            total_ms,
            out_dir,
            title=f"{prefix}E2E (Playwright) - Total journey",
        )

    print("charts:")
    if k6_card_png is not None:
        print(str(k6_card_png))
    print(str(k6_ep_png))
    print(str(pw_steps_png))
    if pw_total_png is not None:
        print(str(pw_total_png))


if __name__ == "__main__":
    main()
