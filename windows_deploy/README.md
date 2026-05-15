# Windows 本地部署版

这个目录用于 Windows 本机部署和启动 PM Refine Follow。它不会复制核心代码，只负责准备 Windows 本地运行所需的配置、虚拟环境和启动脚本。

## 目录内容

```text
windows_deploy/
  README.md
  requirements.windows.txt
  scripts/
    prepare_windows.ps1
    start_dashboard.ps1
    status_windows.ps1
  templates/
    auto_screen_config.windows.json
    agent_core_config.windows.json
```

## 一键准备

在仓库根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\prepare_windows.ps1
```

它会完成：

- 创建 `.venv` 虚拟环境。
- 安装 Windows 运行依赖。
- 如果根目录没有 `auto_screen_config.ui.json`，就从 Windows 模板生成。
- 如果根目录没有 `agent_core_config.ui.json`，就从 Windows 模板生成。
- 创建 `~/.codex/secrets/serverchan_sendkey.txt`。

如果想同时写入 ServerChan SendKey：

```powershell
powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\prepare_windows.ps1 -SendKey "你的SendKey"
```

## 启动看板

```powershell
powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\start_dashboard.ps1
```

浏览器打开：

```text
http://127.0.0.1:8787
```

如果希望启动看板时自动拉起常驻扫描：

```powershell
powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\start_dashboard.ps1 -AutoStartScan
```

## 查看状态

```powershell
powershell -ExecutionPolicy Bypass -File .\windows_deploy\scripts\status_windows.ps1
```

## SendKey 保存位置

Windows 默认保存到：

```text
~/.codex/secrets/serverchan_sendkey.txt
```

也可以在看板「配置」页里直接修改。页面只显示掩码，不显示完整密钥。

## 常用路径

| 内容 | 默认位置 |
| --- | --- |
| 扫描配置 | `auto_screen_config.ui.json` |
| Agent 配置 | `agent_core_config.ui.json` |
| 运行数据 | `auto_screen_data/` |
| 看板日志 | `auto_screen_data/dashboard/auto_screen.log` |
| Excel 输出 | `auto_screen_data/polymarket_candidates.xlsx` |

## 注意

- Windows 本地版适合个人电脑或一台稳定 Windows 主机。
- 如果本地网络会断、电脑会休眠，推荐使用 `vps_deploy/` 部署到 VPS。
- 运行中的扫描可以在看板上停止、启动和查看实时进度。
