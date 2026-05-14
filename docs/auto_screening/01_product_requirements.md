# 01 产品需求与范围

## 一句话目标

持续扫描 Polymarket 官方 leaderboard 中近期表现较好、活跃度较高的账号，最多形成 10 万个唯一候选账号池，并从中自动筛出适合跟单的高评分目标账号。

## 业务目标

1. 自动发现候选账号
   - 以近期表现优先，重点扫描月榜和周榜。
   - 以活跃度辅助，扫描 PnL 榜和成交量榜。
   - 覆盖多个 Polymarket 分类，避免只看到 `OVERALL` 的头部账号。

2. 自动排除明显不适合账号
   - 高频账号、极深分页账号、明显低信号账号在预筛阶段跳过。
   - 尽量减少完整拉取和完整评分成本。

3. 自动评分
   - 复用当前仓库已有评分体系。
   - 继续以仓库内标杆账号作为 60 分锚点。
   - 每个完整取数账号生成 `account_analysis.json` 和中英文报告。

4. 自动通知和沉淀
   - `final_score > 40` 时推送 ServerChan。
   - 所有评分结果、跳过结果、推送结果进入 SQLite。
   - 高分结果和全量结果进入 Excel。

5. 长期运行
   - 支持常驻运行。
   - 支持断点恢复。
   - 扫描完一轮后自动从头开始新一轮。

## 默认候选池策略

单一 leaderboard shard 无法可靠得到前 10 万名。因此采用多 shard 候选池：

- `MONTH + PNL`
- `MONTH + VOL`
- `WEEK + PNL`
- `WEEK + VOL`
- `ALL + PNL`
- `ALL + VOL`

分类：

- `OVERALL`
- `POLITICS`
- `SPORTS`
- `CRYPTO`
- `CULTURE`
- `MENTIONS`
- `WEATHER`
- `ECONOMICS`
- `TECH`
- `FINANCE`

`DAY` shard 默认关闭，因为单日榜容易被短期异常和高频策略污染。

## 候选优先级

候选账号按综合优先级处理：

```text
priority =
  0.40 * month_pnl_rank_score
+ 0.25 * month_vol_rank_score
+ 0.20 * week_pnl_rank_score
+ 0.10 * week_vol_rank_score
+ 0.05 * category_diversity_score
```

这个权重让“近期赚钱”和“近期活跃”同时靠前，同时保留跨分类表现更稳定的账号。

## 非目标

- 不做自动跟单。
- 不下单、不撤单、不签名。
- 不接入 CLOB 私有交易认证。
- 不把 Excel 作为状态源。
- 不为了凑满 10 万而使用非官方或不稳定数据源。

## 默认阈值

- 推送阈值：`final_score > 40`
- 预筛窗口：最近 7 天
- 高频预筛：活跃日均交易数 `> 600`
- 预筛样本最大记录：`5000`
- 预筛样本最大唯一交易哈希：`2000`
- 一轮完成后冷却：60 分钟；如果一轮超过 60 分钟，则立即开始下一轮

