# work_dashboard — AI Pet 协作看板仓

AI Pet 五仓体系的**跨仓协作文档仓库**。远程同事在 GitHub 上查看/在线编辑；本地 AI 编程会话（Kimi CLI / Codex 等）开工前从这里拉取全局上下文。

## 文件

| 文件 | 内容 | 更新时机 |
|------|------|----------|
| `AI-Pet项目全景与进度.md` | **第一信息源**：经代码核实的各仓真实进度快照、文档地图、出入提示 | 里程碑达成后回写，并更新核实日期 |
| `AI-Pet协作看板.md` | 业务侧日常状态流水：部署环境（唯一真源）、集成点状态、待决事项、进度日志 | 每次会话收工必更新 |
| `AI-Pet固件联调看板.md` | 固件↔xiaozhi-server 联调状态、服务端待执行项 | 联调动作后立即更新 |

## 同步纪律（人与 AI 会话共同遵守）

1. **改之前先 `git pull`**——多人 + 多 AI 会话在改同一份文件，不拉就改必然覆盖别人。
2. 改完立即 `git commit && push`，提交信息一行说清"哪个仓/侧 + 什么事"。
3. 看板只记**状态与事实**；接口定义以契约文档为准（`ai-pet-backend/docs/06`、`xiaozhi-server/docs/05`，在各自仓库）。
4. 密钥、密码不进本仓，只记位置。
5. 各仓内部的详细规则见各仓根目录 `AGENTS.md`；工作区总入口为 `D:/Home_Work/AGENTS.md`（不入本仓）。

## 远程同事用法

- **网页展示版（推荐）**：`http://39.107.143.71/` —— 三份看板渲染成的单页应用（顶部 tab 切换），Basic Auth 保护（账号密码找仓库管理员要）。只读。
- 查看源文件：GitHub 网页直接打开对应 .md（原生渲染表格）。
- 修改：GitHub 网页上点 Edit（铅笔图标）直接改，提交即同步；本地会话下次 `git pull` 拿到。
- 本仓为私有仓，需要仓库成员权限；找仓库管理员（ckmx-zkp）加 collaborator。

## 展示页维护（AI 会话 / 本地）

- 生成器：`scripts/build_kanban.py`（依赖 `markdown` 包，装在仓内 `.venv`）。
- **改完看板 md 后**：`bash scripts/sync_kanban.sh` 一键重新生成 + scp 到 ECS。
- 服务器部署：`/opt/ai-pet/kanban/`（index.html + default.conf + .htpasswd），`kanban-web` 容器（nginx:alpine，宿主机 80 → 容器 8081），Nginx 配置在 `deploy/nginx-kanban.conf`。
