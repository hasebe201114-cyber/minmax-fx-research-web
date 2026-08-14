# Adversarial レビュー (C 品質チーム)

> ラボ PJ の `minmax-fx-day-trading-lab` で実施された C 品質チーム (adversarial-reviewer) による懐疑的検証の記録。
> 透明性確保のため、レビュー本体も `sync_from_lab.py` 経由で本PJに取り込んで公開しています。

## レビュー一覧

| OBS | 対象 | 結論 | 取り込み元 |
|---|---|---|---|
| [OBS000004](OBS000004-SYSFX007-AUDJPY採用候補-adversarialレビュー.md) | AUD/JPY 採用候補 (PROVISIONAL ACCEPT → 保留) | 7 件の差し戻し指摘 (1-2 完了, 3-7 残) | `obs/.../85外部レビュー/` |

## C 品質チームの役割 (再掲)

ラボ PJ のマルチエージェント体制において、C 品質チーム (adversarial-reviewer) は:

- 良好結果への **懐疑的検証** (HARKing 防止の最終砦)
- 採用/不採用の **断定的判断** (ただし最終 GO は人間 = 司令塔)
- 不採用案件も**教育的観点から残す**判断プロセスの透明性確保

## 凡例

- ✅ **ACCEPT**: K1m〜K7m すべてクリア、本採用候補
- ⏸ **PROVISIONAL ACCEPT**: K1m〜K7m 概ねクリア、追加検証待ち
- ⏸ **保留**: 過学習検証 (train/val/test) 未完了
- ❌ **REJECT**: K1m〜K7m のいずれか未達
