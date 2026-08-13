# Adversarial レビュー

> ラボ PJ (minmax-fx-day-trading-lab) の採用判断に対する adversarial レビュー記録。
> `scripts/sync_from_lab.py` でラボ PJ の `obs/.../85外部レビュー/` から取り込み。

## 一覧

| OBS ID | タイトル | 対象戦略 / 通貨 | 判定 | 取込日 |
|---|---|---|---|---|
| OBS000004 | SYS-FX007 AUD/JPY 採用候補 adversarial レビュー | SYS-FX007 v2 / AUD_JPY | 保留 | 2026-08-14 |

## 個別ページ

- [OBS000004 - SYS-FX007 AUD/JPY「採用候補」に対する Adversarial レビュー](OBS000004-SYSFX007-AUDJPY採用候補-adversarialレビュー.md)

## ラボ PJ 取り込み方法

```powershell
# adversarial レビューだけ取り込み
python scripts/sync_from_lab.py --only papers

# 全件 (ablation + papers)
python scripts/sync_from_lab.py
```

機密情報 (API_KEY, .env, 口座残高, 個人損益) が含まれるファイルは自動 skip されます。
