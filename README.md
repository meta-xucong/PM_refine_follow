# PM Refine Follow

这是一个 Polymarket 账号自动筛选与看板程序，用于持续扫描近期排行榜账号，拉取交易与 PnL 数据，按跟单适配规则评分，并通过 ServerChan 推送符合条件的账号。

## 目录结构

```text
PM_refine_follow/
  auto_screen/        核心扫描、预筛、评分、推送逻辑
  agent_core/         Agent 复核与记忆模块
  dashboard/          本地 Web 看板
  skill/              账号分析与评分 skill
  docs/               设计文档、评分文档、验收文档
  windows_deploy/     Windows 本地部署版
  vps_deploy/         VPS / Linux 服务器部署版
```

核心代码保持一套，Windows 和 VPS 只拆分部署脚本、配置模板和运维说明，避免两份程序逻辑分叉。

## Windows 本地部署

适合本机长期运行、浏览器访问 `127.0.0.1:8787`。

```powershell
cd F:\AI\PM_refine_follow
powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\prepare_windows.ps1
powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\start_dashboard.ps1 -AutoStartScan
```

详细说明见：

[windows_deploy/README.md](windows_deploy/README.md)

## VPS 服务器部署

适合本地网络不稳定时，把程序放到 Ubuntu/Debian VPS 上常驻运行，并通过 Nginx 反向代理加登录保护访问看板。

```bash
git clone https://github.com/meta-xucong/PM_refine_follow.git
cd PM_refine_follow
cp vps_deploy/env.example vps_deploy/.env
nano vps_deploy/.env
sudo bash vps_deploy/scripts/install_vps.sh vps_deploy/.env
```

详细说明见：

[vps_deploy/README.md](vps_deploy/README.md)

## ServerChan SendKey

两种部署方式都支持在看板「配置」页直接修改 SendKey。

默认保存位置：

| 部署方式 | SendKey 文件 |
| --- | --- |
| Windows | `~/.codex/secrets/serverchan_sendkey.txt` |
| VPS | `/etc/pm-refine-follow/secrets/serverchan_sendkey.txt` |

页面只展示掩码，不展示完整密钥。

## 常用功能

- 按月榜 / 周榜扫描 Polymarket 排行榜账号。
- 预筛高频或明显不合格账号。
- 拉取候选账号交易、持仓、PnL 等数据。
- 按 Auto V3 评分规则判断是否适合跟单。
- 超过推送阈值的账号凑满批次后推送 ServerChan。
- 输出 Excel 与 JSON sidecar 数据。
- Web 看板查看运行状态、当前账号、推送历史、候选列表、配置和日志。

## 测试

```bash
python -m pytest -q -p no:cacheprovider
```

当前项目不依赖数据库服务，运行数据默认保存在 SQLite、JSON 和 xlsx 文件中。
