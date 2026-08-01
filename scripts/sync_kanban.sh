#!/usr/bin/env bash
# 重新生成看板 HTML 并同步到阿里云 ECS（http://39.107.143.71/，Basic Auth）
# 用法：bash scripts/sync_kanban.sh
set -euo pipefail
cd "$(dirname "$0")/.."

.venv/Scripts/python scripts/build_kanban.py
scp 看板.html aliyun-aipet:/opt/ai-pet/kanban/index.html
echo "已同步到 http://39.107.143.71/ （Basic Auth，账号密码问仓库管理员）"
