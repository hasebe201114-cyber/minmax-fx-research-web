# AGENTS.md (minmax-fx-research-web)

> このファイルは AI エージェント (Mavis 等) 向けのプロジェクト規約です。
> 人間向けは `README.md` を参照してください。

## 0. プロジェクト位置付け

**minmax-fx-research-web** は `minmax-fx-day-trading-lab` (本PJの兄弟プロジェクト、検証ラボ) の研究成果を**一般公開する閲覧専用 Web サイト**です。

- **研究の実体**: `minmax-fx-day-trading-lab` (別リポ・別プロセス)
- **本PJの役**: ラボの成果物 (Markdown / JSON) を静的サイトとして整形し、GitHub Pages 等で公開する

## 1. 命名・配置

- 識別子プレフィクス: `minmax-*` (minmax チーム共通)
- リポジトリ: `hasebe201114-cyber/minmax-fx-research-web`
- 配置: `C:\Users\Atsushi Hasebe\.minimax-agent\projects\minmax-fx-research-web\`

## 2. 技術スタック

- **MkDocs Material** (Python ネイティブ, 静的書き出し)
- ランタイム依存: `requirements.txt` (mkdocs, mkdocs-material, pymdown-extensions)
- ビルド時依存: `requirements-build.txt` (matplotlib: チャート生成スクリプト用)
- ビルド: `mkdocs build --strict` → `site/` ディレクトリに静的 HTML
- プレビュー: `mkdocs serve` (localhost:8000, 開発時のみ)
- デプロイ: GitHub Pages 想定 (`.github/workflows/deploy.yml` で main push → deploy-pages@v4)

## 3. ファイル構成

```
minmax-fx-research-web/
├── mkdocs.yml              # MkDocs 設定 (Material テーマ, 日本語, ナビゲーション)
├── requirements.txt        # ランタイム依存 (mkdocs, mkdocs-material, pymdown-extensions)
├── requirements-build.txt  # ビルド時依存 (matplotlib, chart 生成時のみ)
├── AGENTS.md               # 本ファイル (AI 向け)
├── README.md               # 人間向け
├── .github/workflows/deploy.yml  # GitHub Pages デプロイ
├── docs/                   # Markdown コンテンツ
│   ├── index.md            # ホーム
│   ├── about.md            # プロジェクト概要
│   ├── research/           # 研究成果 (戦略仕様, 通貨ピボット, アブレーション)
│   ├── backtest-results/
│   │   ├── index.md
│   │   ├── usd-jpy-2024.md
│   │   └── ablation/       # ラボ PJ から sync で取り込んだ JSON
│   ├── assets/charts/      # バランス曲線 / ドローダウン PNG (generate_charts.py で生成)
│   └── papers/
│       ├── index.md
│       └── adversarial/    # ラボ PJ から sync で取り込んだ adversarial レビュー
├── obs/minmax_fx_research_web/   # OBS ドキュメント (ラボPJ 規約に揃える)
│   └── 引き継ぎ/01進行中/
├── scripts/
│   ├── sync_from_lab.py    # ラボ PJ から JSON / MD を取り込み (機密検出 + frontmatter 付与)
│   └── generate_charts.py  # バランス曲線 / ドローダウン PNG を生成
└── site/                   # ビルド出力 (GitHub Pages 用, .gitignore 対象)
```

## 3.5. 補助スクリプト

### `scripts/sync_from_lab.py`

ラボ PJ の研究成果を本PJに**読み取り → コピー** で取り込む。**書き込みは本PJ側のみ**。

```powershell
# 全件取り込み (ablation JSON + adversarial MD)
python scripts/sync_from_lab.py

# ドライラン (コピーせず対象一覧)
python scripts/sync_from_lab.py --dry-run

# 片方だけ
python scripts/sync_from_lab.py --only ablation
python scripts/sync_from_lab.py --only papers

# 既存ファイル上書き
python scripts/sync_from_lab.py --force
```

**機密情報検出**: `API_KEY`, `SECRET`, `.env`, JWT-like, GitHub PAT, 口座残高 等を
含むファイルは警告して skip。

### `scripts/generate_charts.py`

ラボ PJ の `trades-*.json` から matplotlib で PNG 生成。
日本語フォント: Yu Gothic → MS Gothic → Noto Sans JP → Meiryo → BIZ UDPGothic の順でフォールバック。

```powershell
# 全通貨分生成
python scripts/generate_charts.py

# USD/JPY のみ
python scripts/generate_charts.py --pair USD_JPY
```

依存: `pip install -r requirements-build.txt` (matplotlib)。

## 4. 並走ルール (ラボ PJ との非干渉)

**最重要**: 本PJは `minmax-fx-day-trading-lab` の研究プロセス (バックテスト実行中等) に**一切干渉しない**こと。

- **触って良いもの**:
  - 本PJディレクトリ配下 (`minmax-fx-research-web/`)
  - ラボ PJ の **読み取り専用参照** (Markdown, JSON の中身を読むだけ)
  - 公開前のデータ抽出・整形 (ラボ PJ の出力 JSON を **コピー** して本PJに取り込む)
- **触ってはいけないもの**:
  - ラボ PJ の `data/raw/` `data/curated/` への書き込み
  - ラボ PJ の `research/EXP-FX000001/10-result/` の変更
  - ラボ PJ で実行中の Python プロセス
  - ラボ PJ の `scripts/run_train_val_test.py` などの編集

### 並走時のリソース注意
- ラボ PJ で Python プロセス稼働中 (例: AUD_JPY バックテスト smoke test) は
  CPU/メモリを消費する。本PJ側の重い処理 (大規模ビルド等) は直列で 1 つずつ。
- ラボ PJ の `data/raw/ds-1.json` (444 MB) には**絶対に触らない** (読み取りもしない)。

## 5. 同期ポリシー

ラボ PJ の研究成果が更新されたら、本PJで**再取り込み**が必要です:

```powershell
# 1. ラボ PJ から研究成果 JSON をコピー (書き込み禁止, 読み取り → 本PJへコピー)
Copy-Item 'C:\Users\Atsushi Hasebe\.minimax-agent\projects\minmax-fx-day-trading-lab\research\EXP-FX000001\10-result\ablation\*.json' `
          -Destination 'C:\Users\Atsushi Hasebe\.minimax-agent\projects\minmax-fx-research-web\docs\backtest-results\ablation\'

# 2. ラボ PJ の obs/ 議事録を取り込み
Copy-Item 'C:\Users\Atsushi Hasebe\.minimax-agent\projects\minmax-fx-day-trading-lab\obs\minmax_fx_day_trading_lab\85外部レビュー\*.md' `
          -Destination 'C:\Users\Atsushi Hasebe\.minimax-agent\projects\minmax-fx-research-web\docs\papers\adversarial\'

# 3. ローカルプレビュー
cd 'C:\Users\Atsushi Hasebe\.minimax-agent\projects\minmax-fx-research-web'
python -m mkdocs serve
# → http://localhost:8000 で確認

# 4. ビルド
python -m mkdocs build
# → site/ ディレクトリに静的 HTML 出力
```

## 6. 公開 / 秘匿の境界

**公開して良いもの** (ラボ PJ で 80採用 フォルダに移動済み / 採用 GO 済み):
- 戦略仕様 (K1m〜K7m 評価基準)
- バックテスト結果 (通貨別サマリ + 統計値)
- 採用 / 不採用の判断履歴 (adversarial レビュー結果)

**公開しないもの**:
- API キー / `.env.local` 等
- 機密ブローカー設定
- 未検証の戦略コード
- 個人を特定する情報 (損益, 口座残高等)

## 7. 開発方針

- 日本語メイン, 専門用語は英語混在 (ラボ PJ 規約に揃える)
- Markdown の表 / コードブロック / 折りたたみを積極利用
- 1 ページ = 1 通貨 or 1 戦略が目安 (細分化)
- 画像は `docs/assets/` に集約, ファイル名は `kebab-case-english.png`
- 数字は **3 桁カンマ区切り**, パーセントは **小数 2 桁**
- トレードオフ (リスク / コスト / 制約) は必ず併記
- 不採用 (REJECT) 案件も **教育的観点から残す** (判断プロセスの透明性)

## 8. マルチエージェント体制 (ラボ PJ と整合)

ラボ PJ の 6 体 (S/A/B/C/D/E) とは別に、本PJは軽量運用:

- **S/A/B/C/D**: ラボ PJ 側、内容はラボ PJ 側で確定
- **E 進行 (archivist-pm) 兼務**: 本PJの引き継ぎノート更新, ラボ PJ からの取り込み記録

採用判断の権限は人間 (司令塔 = ユーザー) に属し、本PJは**表示のみ**。判断の変更はラボ PJ 側で行う。

## 9. 必読資料

| 資料 | パス |
|---|---|
| ラボ PJ 規約 | `../minmax-fx-day-trading-lab/CLAUDE.md` (必読) |
| ラボ PJ 戦略仕様 | `../minmax-fx-day-trading-lab/research/EXP-FX000001/00-spec.md` |
| ラボ PJ 引き継ぎ | `../minmax-fx-day-trading-lab/obs/.../引き継ぎ/01進行中/` |
| 本PJ 引き継ぎ | `obs/.../引き継ぎ/01進行中/` |

## 10. 変更履歴

- 2026-08-14: 初版作成 (minmax-fx-day-trading-lab の研究成果公開のため)
