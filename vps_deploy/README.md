# PM Refine Follow VPS 部署版

这个目录是一套独立的 VPS 部署包，目标是在 Ubuntu/Debian VPS 上一键完成：

- 拉取或更新主程序代码。
- 创建 Python venv 并安装运行依赖。
- 生成 VPS 专用配置。
- 把运行数据、配置、密钥和日志分离到 Linux 标准目录。
- 创建独立的 systemd dashboard 服务和常驻扫描服务，避免扫描 OOM 拖死前端。
- 配置 Nginx 反向代理和登录保护。
- 内置自动磁盘清理策略，避免历史归档和缓存长期堆积导致磁盘打满。
- scanner/复核任务启动前会尝试截断 SQLite WAL，避免写前日志长期膨胀占用磁盘。
- 默认准备 2GB swapfile，降低小内存 VPS 被瞬时内存峰值打死的概率。

## VPS 与本地版的关键差异

| 项目 | 本地版 | VPS 版 |
| --- | --- | --- |
| 程序代码 | 项目目录 | `/opt/pm-refine-follow/current` |
| 配置文件 | 项目目录下 `*.ui.json` | `/etc/pm-refine-follow/*.json` |
| ServerChan SendKey | `~/.codex/secrets/serverchan_sendkey.txt` | `/etc/pm-refine-follow/secrets/serverchan_sendkey.txt` |
| 扫描数据 | `auto_screen_data` | `/var/lib/pm-refine-follow` |
| 运行日志 | 项目数据目录 | `/var/log/pm-refine-follow` |
| Dashboard 访问 | `127.0.0.1:8787` | Nginx 反代到公网域名/IP |
| 登录保护 | 无 | Nginx Basic Auth |

## 一键安装

在 VPS 上执行：

```bash
git clone https://github.com/meta-xucong/PM_refine_follow.git
cd PM_refine_follow
cp vps_deploy/env.example vps_deploy/.env
nano vps_deploy/.env
sudo bash vps_deploy/scripts/install_vps.sh vps_deploy/.env
```

最少需要改：

- `DOMAIN`：域名或 VPS 公网 IP。没有域名可以填 `_`。
- `BASIC_AUTH_USER` / `BASIC_AUTH_PASSWORD`：看板登录账号密码。
- `SCT_SENDKEY`：可选。也可以部署后在看板配置页填写。

安装完成后访问：

```text
http://你的域名或IP/
```

如果启用 `ENABLE_LETSENCRYPT=1`，并且域名已经正确解析到 VPS，脚本会自动申请 HTTPS 证书。

## 常用命令

```bash
# 看 dashboard 服务
sudo systemctl status pm-refine-follow-dashboard

# 看常驻扫描服务
sudo systemctl status pm-refine-follow-auto-screen

# 重启 dashboard。只影响前端，不会连带重启常驻扫描。
sudo systemctl restart pm-refine-follow-dashboard

# 重启常驻扫描
sudo systemctl restart pm-refine-follow-auto-screen

# 看 dashboard 日志
sudo journalctl -u pm-refine-follow-dashboard -f

# 看常驻扫描服务日志
sudo journalctl -u pm-refine-follow-auto-screen -f

# 看扫描日志
sudo tail -f /var/log/pm-refine-follow/auto_screen.log

# 看高分复核小队列定时器
sudo systemctl list-timers pm-refine-follow-watchlist-refresh.timer

# 手动触发一次 60 分以上账号复核
# 复核运行时会暂停常驻扫描，结束后再拉起，避免两个重任务叠加。
sudo systemctl start pm-refine-follow-watchlist-refresh.service

# 看当前 API 状态
bash /opt/pm-refine-follow/current/vps_deploy/scripts/status.sh

# 手动跑一次清理（含数据库瘦身）
sudo -u pmfollow /opt/pm-refine-follow/current/.venv/bin/python -m auto_screen.cli --config /etc/pm-refine-follow/auto_screen_config.json cleanup
```

## 自动清理说明

VPS 默认启用 `storage_cleanup`，会在每轮启动前自动清理：

- 旧的 `archive_*` 历史目录（按保留数量 + 天数）。
- 非关键账号缓存目录（保留最近 N 个，并保护已推送/待推送地址）。
- 过大的日志文件（自动截断为最新尾部）。
- `state.sqlite3` 的历史运行记录（保留近期限额并执行 WAL checkpoint/VACUUM）。

当剩余磁盘低于阈值时，会触发一轮更激进的紧急清理。

## SendKey 修改方式

推荐在看板配置页修改。VPS 版会写入：

```text
/etc/pm-refine-follow/secrets/serverchan_sendkey.txt
```

也可以 SSH 手动改：

```bash
sudo -u pmfollow tee /etc/pm-refine-follow/secrets/serverchan_sendkey.txt >/dev/null
sudo systemctl restart pm-refine-follow-dashboard
```

## Nginx 登录保护

脚本会创建：

```text
/etc/nginx/sites-available/pm-refine-follow.conf
/etc/nginx/sites-enabled/pm-refine-follow.conf
/etc/nginx/.pm-refine-follow.htpasswd
```

它使用 Nginx Basic Auth。浏览器打开看板时会弹出登录框，输入 `.env` 里配置的用户名和密码即可。

## 目录清单

```text
vps_deploy/
  env.example
  requirements.vps.txt
  README.md
  scripts/
    install_vps.sh
    status.sh
  templates/
    auto_screen_config.vps.json
    agent_core_config.vps.json
    nginx.pm-refine-follow.conf
    pm-refine-follow-auto-screen.service
    pm-refine-follow-dashboard.service
    pm-refine-follow-watchlist-refresh.service
    pm-refine-follow-watchlist-refresh.timer
```
