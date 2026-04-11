# 评分规则（中文摘要）

## 1. 评分组成

- `copyability_score`：0..35
- `deployability_score`：0..20
- `multi_market_structure_score`：0..20
- `pnl_curve_stability_score`：-28..+28
- `risk_penalty_adjustment`：-34..0
- `concentration_penalty`：额外扣分项

`raw_score` 先计算，再做低频封顶，最后做锚点校准得到 `final_score`。

## 2. 低频封顶（强化）

- 严重低频：封顶 48
- 中低频：封顶 56
- 中频不足：封顶 64

维度同时考虑 `deployable_event_equivalent`、`deployable_event_density`、`active_trading_days`、`trade_count`。

## 3. 锚点基线

- 锚点地址：`0x39d0f1dca6fb7e5514858c1a337724a426764fe8`
- 目标：锚点账号校准后固定 60 分
- 使用冻结文件：`baseline/baseline_anchor.json`

## 4. 结论映射（风险门槛制）

- `>=78` 且风险门槛干净：`relative_copyable`
- `40..77.99`：默认 `selective_copying_only`
- `<40`：`not_recommended`

风险门槛：
- `caution_risk_gate`：禁止宽跟，最多筛选着跟
- `severe_risk_gate`：叠加低分时强制不值得跟

## 5. 黑名单增强

关键词使用加权脏度判断：
- `dirty_like = (dirty + 0.60 * semiclean) / total`

并叠加 dirty 事件加权提升，强化 hard/soft blacklist 覆盖，用于“筛选着跟”落地。
