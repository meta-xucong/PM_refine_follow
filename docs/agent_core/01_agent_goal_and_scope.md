# 01 Agent 目标与边界

## 总目标

把当前程序从固定规则流水线升级为一个可持续学习用户偏好的 Polymarket 跟单研究 Agent。

现有能力：

```text
leaderboard scan -> prefilter -> collect -> Auto V3 score -> Excel/ServerChan
```

Agent 化后的目标：

```text
observe -> score -> reason -> plan -> act -> remember -> evaluate
```

## 核心用户目标

用户最终需要的是：

- 扫描 Polymarket 近期表现较好、活跃度较高的账号。
- 从中找出适合跟单的目标账户。
- 过滤高频、难复制、多腿结构复杂、数据不足、近期表现虚高的账号。
- 推送值得人工复核的账号，并持续追踪结果。

## Agent MVP 范围

第一版只做研究辅助，不做自主策略修改。

必须实现：

- 单候选 AI 复核。
- 复核结果结构化入库。
- Excel 增加 Agent 字段。
- ServerChan 推送加入 Agent 摘要。
- 人工反馈记录。
- 基础 memory 查询。

暂不实现：

- 自动改 Auto V3 权重。
- 自动生成交易指令。
- 自动把账号加入跟单系统。
- 多模型投票。
- 复杂强化学习。

## Agent 成熟版范围

后续阶段逐步实现：

- 每日扫描计划。
- 待复查账号调度。
- 推送后 7d/30d outcome tracking。
- 反馈驱动的偏好画像。
- 权重调整建议，但需要人工确认后生效。

## 硬边界

- 只读公开 Data API。
- 不接触私钥。
- 不调用 CLOB 下单接口。
- 不把 `final_score <= 40` 的账号推送为正候选。
- 不允许 LLM 覆盖高频 skip、data quality cap、severe risk gate。
- 配置写入、阈值长期修改必须有显式命令或人工确认。

