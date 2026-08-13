"""
generate_charts.py
==================

ラボ PJ (minmax-fx-day-trading-lab) の `research/EXP-FX000001/10-result/trades-*.json`
を読み取り、各トレードの pnl 累積でバランス曲線、rolling max との差でドローダウン
を matplotlib で PNG 出力する。

出力:
    docs/assets/charts/{pair}-balance.png
    docs/assets/charts/{pair}-dd.png

制約:
    - ラボ PJ には書き込まない (読み取りのみ)
    - 800x400 px, 1 MB 以下を目安
    - 日本語フォント設定 (Yu Gothic / MS Gothic / Noto Sans JP フォールバック)

Usage:
    python scripts/generate_charts.py                   # ラボ PJ の全 trades-*.json
    python scripts/generate_charts.py --pair USD_JPY    # USD/JPY のみ
    python scripts/generate_charts.py --dry-run         # 出力せず対象一覧
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 非インタラクティブ
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# --- Paths ---

THIS_PJ = Path(__file__).resolve().parent.parent
LAB_PJ = THIS_PJ.parent / "minmax-fx-day-trading-lab"

LAB_TRADES_DIR = LAB_PJ / "research" / "EXP-FX000001" / "10-result"
DST_CHARTS_DIR = THIS_PJ / "docs" / "assets" / "charts"


# --- Font setup (Japanese) ---

JP_FONT_CANDIDATES = [
    "Yu Gothic",
    "MS Gothic",
    "MS PGothic",
    "Noto Sans JP",
    "Meiryo",
    "BIZ UDPGothic",
]


def setup_japanese_font() -> str | None:
    """日本語フォントを設定し、実際に使われたフォント名を返す (見つからなければ None)。"""
    available = {f.name for f in fm.fontManager.ttflist}
    for name in JP_FONT_CANDIDATES:
        if name in available:
            plt.rcParams["font.family"] = name
            # 豆腐回避 (Noto 系など一部フォントで必要)
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return name
    print("WARN: 日本語フォントが見つかりません。タイトルが文字化けする可能性あり。", file=sys.stderr)
    return None


# --- Chart rendering ---


def _draw_balance(ax, rows: list[dict], pair: str) -> None:
    """バランス曲線 (累積 pnl) を描画。rows は [{exit_time, pnl, cum_pnl, dd_jpy}, ...]"""
    xs = [r["exit_time"] for r in rows]
    ys = [r["cum_pnl"] for r in rows]
    ax.plot(xs, ys, color="#1976d2", linewidth=1.4, label="Cumulative PnL")
    ax.fill_between(xs, ys, 0, color="#1976d2", alpha=0.12)
    ax.axhline(0, color="#888888", linewidth=0.6, linestyle="--")
    ax.set_title(f"{pair} バランス曲線 (2024, 累積損益 JPY)", fontsize=12, pad=8)
    ax.set_xlabel("トレード終了時刻")
    ax.set_ylabel("累積損益 (JPY)")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax.legend(loc="upper left", fontsize=9)
    if rows:
        final = ys[-1]
        ax.annotate(
            f"final: {int(final):+,} JPY",
            xy=(xs[-1], final),
            xytext=(10, -10),
            textcoords="offset points",
            fontsize=9,
            color="#1976d2",
        )


def _draw_dd(ax, rows: list[dict], pair: str) -> None:
    """ドローダウン曲線 (rolling max - cum_pnl) を描画。"""
    xs = [r["exit_time"] for r in rows]
    ys = [r["dd_jpy"] for r in rows]
    ax.fill_between(xs, ys, 0, color="#d32f2f", alpha=0.30, label="Drawdown")
    ax.plot(xs, ys, color="#d32f2f", linewidth=1.2)
    ax.set_title(f"{pair} ドローダウン (JPY, 2024)", fontsize=12, pad=8)
    ax.set_xlabel("トレード終了時刻")
    ax.set_ylabel("ドローダウン (JPY, 0=最高値)")
    ax.invert_yaxis()  # 下に伸びる方が自然 (DD)
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax.legend(loc="lower left", fontsize=9)
    if rows:
        # 最悪 DD の位置
        worst = max(ys)
        worst_x = xs[ys.index(worst)]
        ax.annotate(
            f"max DD: {int(worst):,} JPY",
            xy=(worst_x, worst),
            xytext=(10, 10),
            textcoords="offset points",
            fontsize=9,
            color="#d32f2f",
        )


def render_pair_chart(trades_path: Path, dst_dir: Path) -> tuple[Path, Path, dict]:
    """1 通貨分のバランス曲線 + ドローダウン PNG を出力 (各 800x400 px)。"""
    data = json.loads(trades_path.read_text(encoding="utf-8"))
    pair = data["pair"]
    trades = data["trades"]
    if not trades:
        raise ValueError(f"{trades_path.name}: trades が空です")

    # dict リストで処理 (pandas 依存を回避)
    rows: list[dict] = []
    for t in trades:
        rows.append(
            {
                "exit_time": datetime.fromisoformat(t["exit_time"]),
                "pnl": float(t["pnl"]),
            }
        )
    rows.sort(key=lambda r: r["exit_time"])
    cum = 0.0
    for r in rows:
        cum += r["pnl"]
        r["cum_pnl"] = cum
    # rolling max → DD
    running_max = 0.0
    for r in rows:
        if r["cum_pnl"] > running_max:
            running_max = r["cum_pnl"]
        r["dd_jpy"] = running_max - r["cum_pnl"]

    summary = {
        "pair": pair,
        "n_trades": len(rows),
        "total_pnl_jpy": round(cum, 1),
        "max_dd_jpy": round(max(r["dd_jpy"] for r in rows), 1),
    }

    dst_dir.mkdir(parents=True, exist_ok=True)
    balance_path = dst_dir / f"{pair}-balance.png"
    dd_path = dst_dir / f"{pair}-dd.png"

    # バランス曲線 (800x400 px)
    fig1, ax1 = plt.subplots(figsize=(8, 4), dpi=100)
    _draw_balance(ax1, rows, pair)
    fig1.tight_layout()
    fig1.savefig(balance_path, dpi=100, bbox_inches="tight")
    plt.close(fig1)

    # ドローダウン (800x400 px)
    fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=100)
    _draw_dd(ax2, rows, pair)
    fig2.tight_layout()
    fig2.savefig(dd_path, dpi=100, bbox_inches="tight")
    plt.close(fig2)

    return balance_path, dd_path, summary


def main() -> int:
    p = argparse.ArgumentParser(description="バランス曲線 / ドローダウン PNG を生成")
    p.add_argument("--pair", help="通貨ペア (例: USD_JPY)。未指定なら全 trades-*.json")
    p.add_argument("--dry-run", action="store_true", help="対象一覧だけ表示")
    args = p.parse_args()

    if not LAB_TRADES_DIR.exists():
        print(f"ERROR: ラボ PJ の trades dir が見つかりません: {LAB_TRADES_DIR}", file=sys.stderr)
        return 2

    setup_japanese_font()

    targets = sorted(LAB_TRADES_DIR.glob("trades-*.json"))
    if args.pair:
        targets = [t for t in targets if args.pair in t.name]
    if not targets:
        print(f"ERROR: 対象 trades-*.json が見つかりません (pair={args.pair})", file=sys.stderr)
        return 3

    print(f"this_pj: {THIS_PJ}")
    print(f"lab_pj:  {LAB_PJ} (read-only)")
    print(f"output:  {DST_CHARTS_DIR.relative_to(THIS_PJ)}")
    print(f"targets: {len(targets)} files")

    summaries: list[dict] = []
    for src in targets:
        if args.dry_run:
            print(f"  [DRY] {src.name} -> {DST_CHARTS_DIR.relative_to(THIS_PJ)}/{src.stem.replace('trades-', '')}-{{balance,dd}}.png")
            continue
        try:
            bp, dp, summary = render_pair_chart(src, DST_CHARTS_DIR)
            bp_size = bp.stat().st_size
            dp_size = dp.stat().st_size
            print(f"  [OK] {src.name}")
            print(f"       -> {bp.relative_to(THIS_PJ)} ({bp_size:,} bytes)")
            print(f"       -> {dp.relative_to(THIS_PJ)} ({dp_size:,} bytes)")
            print(
                f"       trades={summary['n_trades']}  total_pnl={summary['total_pnl_jpy']:+,} JPY  "
                f"max_dd={summary['max_dd_jpy']:,} JPY"
            )
            summaries.append(summary)
        except Exception as e:
            print(f"  [FAIL] {src.name}: {e}", file=sys.stderr)
            return 1

    if summaries:
        print("\n=== サマリ ===")
        print(f"{'pair':<12} {'trades':>8} {'total_pnl':>14} {'max_dd':>12}")
        for s in summaries:
            print(
                f"{s['pair']:<12} {s['n_trades']:>8} "
                f"{s['total_pnl_jpy']:>+14,.1f} {s['max_dd_jpy']:>12,.1f}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
