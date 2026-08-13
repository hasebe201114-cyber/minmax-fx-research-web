# minmax-fx-research-web

`minmax-fx-day-trading-lab` (FX マルチタイムフレーム検証ラボ) の研究成果を一般公開するための閲覧専用 Web サイト。

- **ラボ本PJ**: [`hasebe201114-cyber/minmax-fx-day-trading-lab`](https://github.com/hasebe201114-cyber/minmax-fx-day-trading-lab)
- **本サイト**: GitHub Pages で公開予定 (準備中)

## クイックスタート

```powershell
# 1. 依存インストール
cd 'C:\Users\Atsushi Hasebe\.minimax-agent\projects\minmax-fx-research-web'
python -m pip install -r requirements.txt

# 2. ローカルプレビュー
python -m mkdocs serve
# → http://localhost:8000

# 3. ビルド
python -m mkdocs build
# → site/ ディレクトリに静的 HTML 出力
```

## 技術スタック

- **MkDocs Material** (Python ネイティブ, 静的サイト)
- Markdown ベース, ノード / ビルドサーバ不要
- GitHub Pages 互換の静的ファイル出力

## ディレクトリ構成

```
minmax-fx-research-web/
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── research/
│   ├── backtest-results/
│   └── papers/
└── site/  (ビルド出力, git 管理外)
```

## AI エージェント向け

[`AGENTS.md`](./AGENTS.md) を参照してください。
