"""
sync_from_lab.py
=================

ラボ PJ (minmax-fx-day-trading-lab) の研究成果を本PJ (minmax-fx-research-web) に
**読み取り → コピー** で取り込むユーティリティ。

並走ルール:
- ラボ PJ には **絶対に書き込まない** (読み取りのみ)
- 本PJの `docs/backtest-results/ablation/` および `docs/papers/adversarial/` にコピー
- 機密情報 (API_KEY, SECRET, .env, 口座残高, 個人損益) が含まれていたら警告して skip

Usage:
    python scripts/sync_from_lab.py                  # 全部コピー
    python scripts/sync_from_lab.py --dry-run         # コピーせず対象一覧だけ表示
    python scripts/sync_from_lab.py --only ablation  # ablation だけ
    python scripts/sync_from_lab.py --only papers     # papers だけ
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


# --- Paths ---

THIS_PJ = Path(__file__).resolve().parent.parent
LAB_PJ = THIS_PJ.parent / "minmax-fx-day-trading-lab"

LAB_ABLATION_DIR = LAB_PJ / "research" / "EXP-FX000001" / "10-result" / "ablation"
LAB_PAPERS_DIR = LAB_PJ / "obs" / "minmax_fx_day_trading_lab" / "85外部レビュー"

DST_ABLATION_DIR = THIS_PJ / "docs" / "backtest-results" / "ablation"
DST_PAPERS_DIR = THIS_PJ / "docs" / "papers" / "adversarial"


# --- Secret / sensitive pattern detection ---

# 機密情報パターン: 検出時は skip (warning)
SECRET_PATTERNS = [
    re.compile(r"API_KEY", re.IGNORECASE),
    re.compile(r"\bSECRET\b", re.IGNORECASE),
    re.compile(r"\.env(?:\.local)?\b", re.IGNORECASE),
    re.compile(r"PRIVATE_KEY", re.IGNORECASE),
    re.compile(r"BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PRIVATE)\s+KEY", re.IGNORECASE),
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"),  # JWT-like
    re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{16,}"),  # Stripe-like
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),  # GitHub PAT
    re.compile(r"password\s*[:=]\s*['\"][^'\"]{6,}", re.IGNORECASE),
    re.compile(r"口座残高"),
    re.compile(r"総損益.*[0-9]{6,}"),  # 6桁以上の個人損益 (JPY 個人確定値)
]

# Markdown / JSON frontmatter 末尾に追記する取り込み情報
SYNC_METADATA = (
    "\n\n<!-- minmax-fx-research-web 取り込み情報 -->\n"
    "<!-- synced_from: {src} -->\n"
    "<!-- synced_at: {ts} -->\n"
)


def detect_secrets(text: str) -> list[str]:
    """機密情報パターンを検出する。検出されたパターン名のリストを返す。"""
    hits: list[str] = []
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


def copy_file_with_metadata(src: Path, dst: Path, dry_run: bool = False) -> str:
    """ファイルを dst にコピーし、frontmatter (Markdown) または末尾 (JSON) に
    取り込み日時メタデータを付与する。

    Returns:
        "copied" | "skipped_secret" | "skipped_exists" | "dry_run"
    """
    if dst.exists():
        return "skipped_exists"

    text = src.read_text(encoding="utf-8")
    secrets = detect_secrets(text)
    if secrets:
        print(f"  [SKIP:secret] {src.name}")
        print(f"     patterns: {secrets[:3]}{'...' if len(secrets) > 3 else ''}")
        return "skipped_secret"

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = SYNC_METADATA.format(src=str(src.relative_to(LAB_PJ)), ts=ts)

    if dry_run:
        print(f"  [DRY] {src.name} -> {dst.relative_to(THIS_PJ)}")
        return "dry_run"

    dst.parent.mkdir(parents=True, exist_ok=True)
    # Markdown は末尾に HTML コメントで追記 (frontmatter として認識されない)
    # JSON はそのままコピー (コメントは JSON 仕様外なので末尾文字列付与しない)
    if src.suffix.lower() == ".md":
        dst.write_text(text + meta, encoding="utf-8")
    else:
        shutil.copy2(src, dst)
    print(f"  [OK] {src.name} -> {dst.relative_to(THIS_PJ)}")
    return "copied"


def sync_ablation(dry_run: bool = False) -> tuple[int, int, int]:
    """ラボ PJ の ablation/*.json を本PJの docs/backtest-results/ablation/ にコピー。"""
    print(f"\n=== ablation (src: {LAB_ABLATION_DIR.relative_to(THIS_PJ.parent)}) ===")
    if not LAB_ABLATION_DIR.exists():
        print(f"  [WARN] lab source not found: {LAB_ABLATION_DIR}")
        return (0, 0, 0)

    copied = skipped = skipped_secret = 0
    for src in sorted(LAB_ABLATION_DIR.glob("*.json")):
        result = copy_file_with_metadata(src, DST_ABLATION_DIR / src.name, dry_run)
        if result == "copied":
            copied += 1
        elif result == "skipped_secret":
            skipped_secret += 1
        elif result in ("skipped_exists", "dry_run"):
            skipped += 1
    print(f"  -> copied={copied}, skipped_exists={skipped}, skipped_secret={skipped_secret}")
    return (copied, skipped, skipped_secret)


def sync_papers(dry_run: bool = False) -> tuple[int, int, int]:
    """ラボ PJ の obs/.../85外部レビュー/*.md を本PJの docs/papers/adversarial/ にコピー。"""
    print(f"\n=== papers (src: {LAB_PAPERS_DIR.relative_to(THIS_PJ.parent)}) ===")
    if not LAB_PAPERS_DIR.exists():
        print(f"  [WARN] lab source not found: {LAB_PAPERS_DIR}")
        return (0, 0, 0)

    copied = skipped = skipped_secret = 0
    for src in sorted(LAB_PAPERS_DIR.glob("*.md")):
        result = copy_file_with_metadata(src, DST_PAPERS_DIR / src.name, dry_run)
        if result == "copied":
            copied += 1
        elif result == "skipped_secret":
            skipped_secret += 1
        elif result in ("skipped_exists", "dry_run"):
            skipped += 1
    print(f"  -> copied={copied}, skipped_exists={skipped}, skipped_secret={skipped_secret}")
    return (copied, skipped, skipped_secret)


def main() -> int:
    p = argparse.ArgumentParser(description="ラボ PJ から本PJへ研究成果を同期")
    p.add_argument("--dry-run", action="store_true", help="コピーせず対象一覧だけ表示")
    p.add_argument("--only", choices=["ablation", "papers", "all"], default="all")
    p.add_argument("--force", action="store_true", help="既存ファイルも上書き")
    args = p.parse_args()

    if not LAB_PJ.exists():
        print(f"ERROR: ラボ PJ が見つかりません: {LAB_PJ}", file=sys.stderr)
        return 2

    print(f"this_pj: {THIS_PJ}")
    print(f"lab_pj:  {LAB_PJ} (read-only)")
    print(f"mode:    {'DRY-RUN' if args.dry_run else 'COPY'}  force={args.force}")

    if args.force and not args.dry_run:
        # 上書きモード: 既存ファイル削除 (本PJ側のみ)
        for d in (DST_ABLATION_DIR, DST_PAPERS_DIR):
            if d.exists():
                for f in d.iterdir():
                    if f.is_file():
                        f.unlink()

    totals = {"copied": 0, "skipped": 0, "skipped_secret": 0}
    if args.only in ("all", "ablation"):
        c, s, ss = sync_ablation(args.dry_run)
        totals["copied"] += c
        totals["skipped"] += s
        totals["skipped_secret"] += ss
    if args.only in ("all", "papers"):
        c, s, ss = sync_papers(args.dry_run)
        totals["copied"] += c
        totals["skipped"] += s
        totals["skipped_secret"] += ss

    print(f"\n=== TOTAL ===")
    print(f"  copied={totals['copied']}  skipped_exists={totals['skipped']}  skipped_secret={totals['skipped_secret']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
