# AI Pet 联调协作看板

> 用途：多个 AI 开发会话（Kimi CLI 等）跨仓库协作的唯一状态同步点。
> **使用规则（所有 AI 会话必读）：**
> 1. 开工前先读本文件，了解自己任务的上下游状态。
> 2. 完成一个任务后，立即更新对应状态和文末"进度日志"（一行：日期 + 仓库 + 事项）。
> 3. 本文件只记**状态与事实**，接口定义以契约文档为准：
>    - `ai-pet-backend/docs/06-HTTP-API规范.md`
>    - `xiaozhi-server/docs/05-与业务后端集成接口.md`
> 4. 改接口先改契约文档，再改代码，并在进度日志中注明"契约已变更"。
> 5. 密钥、密码不进本文件，只记位置（如"见服务器 .env"）。

## 仓库地图

| 仓库 | 路径 | 职责 | 当前开发会话 |
|------|------|------|-------------|
| **AI_pet（工作区总仓）** | `D:\Home_Work` | 多设备入口；子仓以 submodule 挂载。日常提交仍进各子仓 origin | 另一台电脑：`git clone --recurse-submodules https://github.com/ckmx-zkp/AI_pet.git` |
| ai-pet-backend | `D:\Home_Work\ai-pet-backend` | 业务后端：用户/设备/KB/persona/记忆/MCP/worker | `main=1d1a4f3`；130 测试全绿；ECS 最后明确部署 `ae1ddd8`，最新 27 类关系/宠物口吻提交待部署验证 |
| xiaozhi-server | `D:\Home_Work\xiaozhi-server` | 实时语音后台（xinnan-tech 上游二开） | `main=99aa353`，b13 已部署：无语音会话窗口 300 秒；等待 X1 剩余真机验收 |
| ai-pet-admin | `D:\Home_Work\ai-pet-admin` | Web 管理台 | `main=c6d4ae4`；本地生产构建通过；B5/B7/B8/D7 已部署，最新 KB 运营体验提交待补在线证据 |
| ai-pet-app | `D:\Home_Work\ai-pet-app` | 用户端（手机 PWA + 桌面） | `main=7c3d4ed`；本地生产构建通过；“我的”页聚合已实现，最后明确在线 hash 为 `index-BOxyZSUr.js`，最新提交待补部署证据 |
| ESP32_XIAOZHI | `D:\Home_Work\ESP32_XIAOZHI` | 母文档 + 固件 | `main=faaae15`；P4/BOX-3B/LCD EV Board 多板型基础；LCD EV V1.5 已烧录跑语音状态，待屏幕/唤醒目视验收 |
| ai-pet-ops | `D:\Home_Work\ai-pet-ops` | 服务器只读监测与告警 | V0 骨架，未部署 |
| prototype | `D:\Home_Work\prototype` | 产品/交互原型 | `main=f3b55a7`；新增本地排版决策中心；旧总览事实基线待更新 |

## 部署环境

| 项 | 值 |
|----|-----|
| 服务器 | 阿里云北京 ECS `39.107.143.71`（8C16G/148G，Ubuntu 22.04） |
| SSH | `ssh -i ~/.ssh/id_ed25519_aipet root@39.107.143.71`（密钥文件已存在，仅密钥登录；本机 ssh config 无 `aliyun-aipet` 别名，勿再用旧写法） |
| 部署目录 | backend：`/opt/ai-pet/ai-pet-backend`；admin：`/opt/ai-pet/ai-pet-admin`；xiaozhi-server：`/opt/xiaozhi-server` |
| 密钥位置 | 服务器 `/opt/ai-pet/ai-pet-backend/.env`（POSTGRES_PASSWORD / JWT_SECRET_KEY / INTERNAL_SERVICE_TOKEN） |
| 对外端口 | 22/443 + 8883(MQTTS，预留) + 8000/8002/8003=xiaozhi-server + 8080=admin Web + **80=协作看板展示页（Basic Auth）**；8010=backend web-api 仅供本机反代（UFW 未放行） |
| 内部端口 | PG 5432 / Redis 6379 仅 Docker 内网，不公网；xiaozhi 的 MySQL 3306/Redis 6379 也在其 compose 内网 |

### xiaozhi-server 部署详情（会话 B）

| 项 | 值 |
|----|-----|
| 版本 | 上游 v0.9.6 全模块（server + manager-web + MySQL + Redis，官方镜像） |
| 端口 | 8000=设备 WebSocket；8002=智控台(manager-web/api，OTA 也在这：`/xiaozhi/ota/`)；8003=视觉/HTTP |
| 代码 | 源码快照在 GitHub `ckmx-zkp/aipet-xiaozhi-server-`（钉 v0.9.6，无 fork 关联） |
| 状态 | ✅ 4 容器与公网端口正常；语音镜像 `xiaozhi-aipet-server:v0.9.6-b13`；LLM=MiniMax-M2.5、ASR=豆包流式 2.0、TTS=火山双向流式，密钥仅在服务器私有配置 |

## 集成点状态（双方共同维护）

| 集成点 | 契约 | backend 侧 | xiaozhi-server 侧 | 联调 |
|--------|------|-----------|-------------------|------|
| persona_pack 拉取 | `GET /api/internal/devices/{uid}/persona_pack` | ✅ 已部署（E2/E10）：固定 7 字段；未配置人设返回 404；当日内容由 backend 注入 | 🟡 b6 起支持首次拉取/300 秒刷新/缓存/onboarding；S7 身份与 C5 已真机通过 | 待真机验证人设修改后的刷新生效 |
| 转写旁路写入 | `POST /api/internal/chat/events` | ✅ 已部署：5 字段，`session_id`=字符串 UUID | 🟡 b12 已部署严格 FIFO 与有界重试 | 待真机 user/assistant 两类落库证据 |
| 外设状态快照 | `POST /api/internal/peripheral/events` | ✅ 已部署：单行全量覆盖写 | 🟡 b12 已部署单项/批量眼睛工具快照上报 | 待真机五工具与 backend 落库证据 |
| 会话结束通知 | `POST /api/internal/chat/sessions/{id}/end` | ✅ 已部署并触发异步任务 | 🟡 b12 已纳入严格 FIFO，使用原生字符串 UUID | 待真实断开与任务入队证据 |
| Memory MCP 挂载 | streamable HTTP MCP `/mcp`，三工具白名单 | ✅ HTTP 服务、401、初始化和工具清单已验收 | 🟡 b10 挂载、b12 合并 persona 检索提示；容器级已验收 | 待真机一次 `memory.search` |
| device_id 对齐 | 小写冒号 MAC `device_uid` | ✅ `devices/seen` 建资产并生成 `binding_id` | ✅ b11 启动扫描 + 30 秒复查智控台已绑定设备；旁路走 `web-api:8000`，现有 3 台已导入 | 容器级已通；待真机事件链证据 |
| 鉴权 | `/api/internal/*` 走 `X-Internal-Token` | ✅ 已实现 | ✅ 已配置并随旁路请求发送；真实请求到达 backend | 已联通 |

状态值约定：`未开始 / 骨架 / 已实现 / 已联调`

## 双方当前进度摘要

### ai-pet-backend（会话 A 维护）


- ✅ Epic A1 脚手架：FastAPI monorepo（web-api / memory-mcp / agent-worker / persona-compiler），CI 全绿
- ✅ Alembic 初始迁移：14 业务表 + agent_tasks 队列表
- ✅ **2026-08-01 首次部署完成**：5 容器全部 Up（web-api @8010、memory-mcp、agent-worker、pg16、redis），迁移已执行（15 表），healthz/401 验证通过，详见 `docs/09-部署进度与运维.md`
- ✅ E6.1 记忆画像、E2.1 问卷/preview、E7.1 反馈只建 draft、E8 同步 export/保留清理/运营指标、趣味测试与简略星盘均已部署；真实持续数据仍依赖 X1 会话链路。
- ✅ KB v3 第一人称内容与“反馈候选→draft”闭环已上线；最新代码新增 27 类结构化相处关系目录与用户直选接口，待 ECS 部署验证。
- ✅ **E1.1 已部署**：新增 `binding_id` 迁移；小智 `devices/seen` 首见生成绑定 ID；app `/devices/bind` 改按绑定 ID 认领；admin 调用用户 bind 返回 403。
- ✅ **E2 已部署**：KB 种子（四元素、12 星座、16 型 MBTI）；用户 persona GET/PUT；内部 persona_pack 固定 7 字段。问卷、KB 管理与发布仍不属于本项。
- ✅ **E4 已部署**：`GET /devices/{id}/messages` 按设备/时间窗分页读取脱敏内容；`DELETE` 必须带时间窗并写审计日志。
- ✅ **E10 已部署（2026-08-18）**：提交 `ff3b2d4` + 文档 `2a13d2a`；迁移 `0008_daily_fortune` 已执行，八字与每日运势用户接口、两类 Worker 任务及 persona_pack 当日内容注入均已上线。`FORTUNE_SEARCH_ENABLED=false`，当前明确为非实时检索；待真实账号验收生成链路。
- ✅ **E10.3 已部署（ECS 运行 `3b0b674`）**：每日 05:00 后预生成、东八区切日、greeting 昨日回退、admin 运势只读接口已上线；联网检索改为 M3 摘要 + `LLM_MODEL` 分发 JSON。对照实测 M2.7/M2.5 不能替代 M3。当日 L1 12 星座已联网生成；待真实账号验收。

### ai-pet-admin（Codex / 会话 C 维护）


- ✅ **M1+B1 完成**：Vue 3 + Vite + Element Plus + Pinia + axios 工程；注册/登录、JWT 本地保持、401 跳登录、侧边栏主布局，以及设备绑定、列表、详情、改名、解绑闭环均已实现，生产构建通过。
- ✅ auth 联调依赖验证：线上 `healthz` 与测试账号登录均返回 200。
- ✅ ECS HTTP 部署完成：Nginx 容器监听 `8080`，`/api/*` 同源反代到本机 backend `8010`；首页/SPA 路由 200，`/api/auth/me` 未登录返回 401，链路正常。
- ✅ 阿里云安全组与 UFW 均已放行 TCP 8080；公网 `http://39.107.143.71:8080/` 可达，真实账号登录、进入设备页、刷新保持登录均验证通过，浏览器控制台无错误。
- ℹ️ 已停止使用 Codex Sites；同源反代模式不需要 backend 增加 CORS 白名单。
- ✅ B1.1 已部署：已撤除管理台用户 `/devices/bind` 入口，页面明确设备认领由用户端以 `binding_id` 完成；当前仅保留当前账号设备查看，管理端资产接口现已由 backend 提供，待前端改接。
- ✅ 管理端设备资产/诊断接口已部署：`/api/admin/devices` 资产分页/详情、绑定码轮换、管理端人设、脱敏历史、外设快照和分析结果只读均可用；`GET /api/admin/devices/lookup?device_uid={MAC/SN}` 可精确读取当前 `binding_id`，不暴露或写入用户归属。
- 🟡 **M2 人设设置**：用户侧与管理端人设页面、`GET/PUT` 接口均已部署；12 星座、16 型 MBTI 均可保存。未认领设备管理端写入返回 409；xiaozhi 侧仍待接入同一领域的内部 `persona_pack`。
- 🟡 **M3 对话与记忆**：用户及管理端脱敏消息查询、用户/管理端 memories 列表与 candidate 审核、Memory MCP 实库均已部署；Admin 记忆审核页已接入。真实候选仍待 worker 持续产出与真机旁路验收。
- 🟡 **M4 分析、外设与 KB 运营**：管理端与用户侧 analyses/peripheral 只读接口均已部署；`/admin/kb/*` 草稿、发布、反馈审核已部署，v2 人设 KB 已发布。Admin 分析已改为卡片，不再展示原始 JSON；外设持续上报与 worker 分析产出仍待真机验收。
- ✅ **2026-08-18 体验改造已部署**：D1 分析卡片、D2 资产列表 20 条 offset 分页、D3 统一空态/错误/重试、D4 仓内文档回写、D5 dossier 保存提示「下次会话生效」。线上 `http://39.107.143.71:8080/` 新构建 200。
- ✅ **2026-08-18 跟进 backend 主人/宠物拆分与 bond**：B5 分析卡片扩展 memory_profile（长期记忆画像）/relationship_update（相处关系变化）；新增 B7 运势核对只读 tab（`GET /admin/devices/{id}/fortune/daily`，owner 星座）；新增 B8 人设页展示只读相处关系 bond；新增 D7 运营指标页（`GET /admin/ops/metrics`，任务计数不含对话内容）。apply-persona-growth 因仍为用户端点，admin 侧继续标记阻塞待产品/backend 拍板是否开放。线上已重新构建部署，`/` 200。

### ai-pet-app（用户端）依赖快照（2026-08-18）

**原则**：app 运行时只调用 backend 的公开用户 API，**不依赖 admin 才能运行**。admin 是运营/资产管理端；它的唯一直接前置是不得再占用用户设备归属，必须先完成 E1.1 的资产接口改造。

| App 欠缺项 | backend 前置 | admin 前置 | 当前结论 |
|------|-------------|------------|----------|
| B2.1/B2.2 设备认领、列表、详情、多设备切换 | E1.1 `binding_id` 生成/认领及用户设备列表已部署 | admin 不占用 `devices.user_id` | ✅ 已接入并部署：认领后自动设为当前设备，首页可列表、切换并持久化当前设备 |
| B3 配网引导 | 不依赖 backend/admin 用户 API | 不依赖 admin | 依赖固件/小智的实际配网能力与图文流程 |
| C1 人设设置、C4 首页人设摘要 | E2 人设读写、已发布的星座/MBTI 种子、`persona_pack` 实际可用并完成联调 | admin 的 KB 发布是后续运营能力，不是 app 保存人设的运行时依赖 | ✅ app C1、C4 已接入并部署；C4 按当前设备读取 persona，404 为可恢复空态 |
| C2 记忆管理 | memories CRUD/approve/reject、Memory MCP 实库 | admin 的审核/运营页面是协作配套，不是 app 运行时依赖 | ✅ App 已接入并部署记忆列表/搜索、新建、归档及候选审核；真实候选仍依赖持续对话数据 |
| C3 历史浏览 | E4 messages 查询/删除已部署 | 无运行时依赖 | ✅ app 已接入并部署；待真实用户消息数据验收 |
| D1 外设状态、D2 日运/小记、D3 数据导出 | peripheral/analyses/export 均已部署；持续内容依赖 chat events、会话结束和 worker | admin 的分析/KB 运营页面不阻塞 app | ✅ D1/D2/D3 均已接入；D3 与记忆画像、日运、八字已有真实账号通过记录；外设/持续小记仍依赖 X1 |
| A7 设备改名/解绑、D5 成长建议、D6 运势卡、D7 主人八字、D9 我的页聚合 | 对应 backend 用户接口均已部署 | 无运行时依赖 | ✅ 代码均已实现；D6/D7 已有真实账号通过记录；`7c3d4ed` 最新聚合页待补在线版本证据 |
| F1/F2 发布与安装 | 无业务 API 新前置；需完成端到端验收 | 无 | 还需域名与 HTTPS；当前 8081 HTTP 仅适合内测 |

### 原型核对（2026-08-02）

| 原型/用户端任务 | 后端接口状态 | 处理结论 |
|---|---|---|
| P4 记忆列表、搜索、新建、归档、候选审核 | ✅ memories CRUD + approve/reject + Memory MCP 实库已部署 | App 本轮直接开发 C2 |
| P6 日运/小记 | ✅ `GET /devices/{id}/analyses` 与 `daily_summary` worker 已部署，并已有首条真实产出 | App 本轮直接开发 D2；无结果时保持等待生成空态 |
| P1 人设摘要 | ✅ persona GET 已部署 | ✅ C4 已接入：当前设备星座、MBTI、知识库版本和跟随策略 |
| P2 配网图文引导 | 不依赖用户 API，取决于固件配网说明 | B3 待产品/固件提供最终步骤与素材 |
| P8 数据导出 | ✅ `POST /devices/{id}/export` 已返回同步 JSON 包 | ✅ App A8 已上线；导出包不含 `device_uid` 与生辰原始值 |
| 人设问卷 | ✅ E2.1 问卷、后端 MBTI 算型与 `persona/preview` 已部署 | ✅ App A10 已上线；客户端不计算 MBTI |

### xiaozhi-server（会话 B 维护）


- ✅ 上游 v0.9.6 源码钉版并首推 GitHub（ckmx-zkp/aipet-xiaozhi-server-）
- ✅ 全模块部署到 39.107.143.71 `/opt/xiaozhi-server`（4 容器正常；安全组+ufw 已放 8000/8002/8003；MySQL 弱密码已换）
- ✅ 修复三处部署坑：OTA 下发占位域名（`server.fronted_url`/`server.ota`/`server.websocket` 已指向公网地址）、`server.auth_key` 与 `server.secret` 不一致（真机连不上的隐患）
- ✅ 模型链路：LLM=MiniMax-M2.5（智能体“测试1”主用；千帆 `qianfan-code-latest`/GLM-4.5-Flash/Kimi K2.7 保留备用）；ASR=豆包流式 2.0（试用 20h）；TTS=火山双向流式·湾湾小何（`zh_female_wanwanxiaohe_moon_bigtts`）
- ✅ 真机 `8c:fd:49:0c:a8:78` 激活绑定+首轮对话联通（唤醒→ASR→GLM 人设→TTS→眼睛 emotion 联动）；固件联调看板：`AI-Pet固件联调看板.md`（本目录）
- 🟡 V0.2 业务集成：内网与内部鉴权已联通；`v0.9.6-b4` 已实现 persona_pack 定时刷新/缓存/onboarding、眼睛 MCP 外设状态旁路，`v0.9.6-b2` 已改为 MAC + 原生字符串 UUID 的 devices/seen、chat events、session end。四项均待真机 E2E 落库证据。
- ✅ **C5 + MiniMax 思考隔离已上线（2026-08-16）**：构建并切换 `xiaozhi-aipet-server:v0.9.6-b8`（线上由 b6 直跳 b8，b7 废弃）。内容：跨 chunk `<think>` 状态机过滤（`ThinkTagFilter`，本地提交 `e93bb14`）、MiniMax `thinking:{type:disabled}` 双保险、direct_answer 兜底剥离；并补齐服务器源码树 `connection.py` 此前缺失的 dynamic_context 合入块（否则 b7 即使上线 C5 也不会进 Prompt）。容器级验收通过：容器启动正常、容器内过滤器行为测试通过、容器内直连 C5 `GET /api/internal/context/device` 200/7ms/真机 3 条上下文；主机级复核：已认领真机 data 非空、未知设备空、无 token 401。仅剩真机验收。
- ✅ **“宠物否认自己有星座”已修复（2026-08-16，backend 侧）**：真机问“你是什么星座”总答“我是AI宠物”。根因：KB v2 片段全是第三人称教练视角 + `pet_default`“不编造人设”约束，模型拿不到身份事实。修复：backend `compile_profile` 在 KB 片段前固定注入身份行（“你的星座是天蝎座，MBTI 是 ENFP……”），提交 `8243e0d` 已上线（web-api 已重建），已验证 persona_pack 首条即身份行；小智侧 300 秒刷新自动生效，无需改仓。KB v2 片段的宠物视角重写已列入排期（见待决事项）。
- ✅ **失败可观测性已上线（2026-08-16）**：构建并切换 `xiaozhi-aipet-server:v0.9.6-b9`（b8 基础上叠加）。新增 `core/utils/integration_log.py` 统一旁路日志（tag=BIZ）：persona_pack、chat events、session end、peripheral events、C5 context provider 均记录 `device_uid`、`session_id`、耗时、outcome（ok/retry/dropped/degraded）与降级原因；重试中间过程仅 debug 不刷屏；不记录对话正文、token、完整 Prompt；接口通用，后续 Memory MCP 直接复用。本地提交 `2ef6d07`（含另一会话并入的契约定稿 docs 提交 `e5d5de9`）。容器级验证通过：b9 启动无错误、容器内 `log_op` 自测输出正确单行。真机日志证据随 E2E 验收一起取。
- ✅ **Memory MCP 已挂载（2026-08-16，`v0.9.6-b10`，提交 `ae620da`）**：小智 server 同时加入 `xiaozhi-server_default` 与 `ai-pet-backend_default`；私有配置仅在服务器。容器级 `tools/list`、`memory.search` 和错误 token 401 已验收；真机调用仍待 X1。
- ✅ **b12 集成可靠性修复已部署（2026-08-18）**：`f6ba94f` 已与 `origin/main` 对齐；业务旁路严格 FIFO、多工具眼睛快照/休息后处理、`memory.search` 合并 persona 检索提示均通过容器级定向验收。S7 三项真机已通过，X1 仅剩旁路五类、S1-S5、BIZ 日志与一次真实 `memory.search`。
- ✅ **b11 智控台设备自动导入已部署**：启动扫描并每 30 秒复查，旁路/C5 基址统一为 `http://web-api:8000`；现有 3 台已导入。旧 `host.docker.internal:8010` 路径被 UFW 丢弃期间的事件已丢失且不可回放。
- 📋 **BLE 偶遇双 AI 交流需求已校正（E9）**：户外低速 BLE 匿名发现，机器人主动询问主人；双方同意后交换短期 token 并各自上报，由 backend 生成本次双方受控交流内容。不是 App/智控台配对，不做实时会话桥；当前零实现。

## 任务拆分（2026-08-16 · 原型第五次校准）

> 来源：`prototype/需求分析与下一步原型方案-2026-08.md` 第五次校准（经五仓代码核实）。配套原型：`index.html`（总览）、`e2e-checklist.html`（真机验收墙）、`next-step.html`（人设三态）、`my-pet.html`（我的星仔）。
> 总体顺序：真机 E2E 验收 > App 新功能真实账号验收 > E11 架构拍板 > 固件 OTA 腾挪与第二只眼 > 正式发布链。A1/A8/A9/A10 与趣味测试/星盘均已部署。
> 2026-08-16 二次补齐：在既有 app/admin/backend/xiaozhi 表上补固件、运维、原型仓、app 阻塞项与明确不进本轮项。

### 取任务顺序（各会话）

| 优先级 | 做什么 | 负责仓 |
|---|---|---|
| P0 | 真机 E2E 验收（b8/b9、旁路五类、S1–S5） | xiaozhi-server + 固件联调 |
| P0 | Memory MCP 真机调用一次 `memory.search` | xiaozhi-server（容器级已完成） |
| P0 | App `ffd04ae` 新功能真实账号验收：档案、问卷、导出、画像、E10、趣味测试/星盘 | ai-pet-app |
| P3 | ~~App 遗留小项：overrides 覆盖 / 重复 onMounted~~ 已在 A1/A8/A9/A10 一并修掉 | ai-pet-app |
| P1 | ~~B9 联网检索触发~~ ✅ `3b0b674` 已部署并重跑当日 L1；E10 真实账号验收并入下方 | ai-pet-backend |
| P1 | E10 真实账号验收：运势 `generating`→结果、八字保存与 persona 当日内容 | ai-pet-backend + ai-pet-app |
| P1 | E11 主动播报先统一传输架构：已连接语音 WS 轮询 vs 空闲设备 MQTTS 控制通道 | backend + xiaozhi + 固件 + 运维 |
| P1 | 日运页真实数据验收 | ai-pet-app |
| P1 | 固件 OTA 分区腾挪（先于第二只眼） | ESP32 固件 |
| P2 | ~~E6.1→E8 / KB v3 / App A8-A10~~ ✅ backend 与 App 均已部署，剩真实账号验收 | ai-pet-backend + ai-pet-app |
| P2 | ~~App 趣味测试/简略星盘与分享卡~~ ✅ 已部署；Ops 采集器本地完善、Prototype R3 | ai-pet-ops + prototype |
| P3 | 域名 + ICP + HTTPS/WSS/MQTTS | 运维 / 产品 |
| 阻塞 | 配网引导、社交、E11 主动播报实现 | 见各表，不得提前画成可用 |

### prototype（产品评审，不写生产代码）

| # | 任务 | 说明 | 状态 |
|---|---|---|---|
| R0 | 总览页「代码现状」校准到 08-16 | `index.html` | ✅ 已交付 |
| R1 | 真机 E2E 验收墙 | `e2e-checklist.html` | ✅ 已交付 |
| R2 | 我的星仔 + 成长建议 + 人设第四态原型 | `my-pet.html`、`next-step.html` | ✅ 已交付 |
| R3 | 管理台分析卡片视觉方向稿 | 仅供 admin 仓参考，不在本仓实现管理台 | 待排期 |
| R4 | 真机验收后回写验收墙演示状态 | 不接真实接口；状态真源仍是本看板与固件联调看板 | 等 X1 |

### ai-pet-app（用户端前端）

| # | 任务 | 依赖 / 说明 | 状态 |
|---|------|-------------|------|
| A1 | 「我的星仔」角色档案页：dossier 六字段**全部可见可编辑**（身份/背景/角色/目标/进化规则/关系）；保存提示「下次和宠物说话时生效」 | 用户 2026-08-18 拍板不再等字段边界；独立页 `/star`，PUT 回传现有星座/MBTI/overrides | ✅ 已部署，待真实账号验收 |
| A2 | 成长建议卡：`kind=persona_growth` 建议/证据/置信度卡片 + `apply-persona-growth` 二次确认 | 接口已上线；实际端点为 `POST /devices/{id}/analyses/{aid}/apply-persona-growth`（带 analysis id）；`d1dd70d` 已提交推送 | ✅ 已部署，待真实 API 验收 |
| A3 | 人设生效第四态「已验证生效」（P3 三态扩展） | 2026-08-18 核实 backend 无此能力。用户要求 backend 补 `PersonaProfile` 状态字段与枚举后再做前端徽章；见下方跨会话消息 | ⏸ 搁置：已向 backend 提出补字段 |
| A4 | B3 配网引导页 | 等固件 F3 最终配网步骤与素材 | 阻塞 |
| A5 | 日运页真实数据验收：worker 修复后已重跑产出 8 条 `daily_summary`，App 刷新即可验证 | 链路已验证（8081 首页 200、analyses/fortune 未登录 401）；真实数据验收需用户登录账号 + 已绑定设备 | 待用户手测验收 |
| A6 | 文档债顺手回写：docs/06 勾选 D4（实质在 B2.2 落地）与 B2 父项、F2 加注 manifest/SW 已配置待 HTTPS；docs/03 修正 P3 人设页与 P2 绑定页口径 | 已随 `d1dd70d` 提交推送 | ✅ 已完成 |
| A7 | 设备改名 / 解绑 UI | backend `PATCH`/`DELETE /devices/{id}` 已上线（name 1–128 字；DELETE 204 仅解除归属、历史保留可重绑）；首页行内改名 + 二次确认解绑；`d1dd70d` 已提交推送 | ✅ 已部署，待真实 API 验收 |
| A8 | D3 数据导出页 | 我的页 `POST /export` 同步 JSON 摘要 + 本地下载；不含 MAC/生辰 | ✅ 已部署，待真实账号验收 |
| A9 | 记忆画像页 | 记忆页顶卡读 `GET /analyses?kind=memory_profile` | ✅ 已部署，待真实数据验收 |
| A10 | 人设问卷入口 | 已改接 `GET/POST /owner/questionnaire`，结果只写主人档案；独立页 `/owner` 标题「用户性格测试」，不再回填宠物性格 | ✅ 已部署 `94f8b6f` / `index-BOxyZSUr.js` |
| A11 | PWA 安装引导 / HTTPS 正式发布 | 等 O1 域名与证书 | 阻塞 |
| A12 | 桌面增强 Epic E（宽屏分栏、窗口记忆） | 不阻塞 V0.2 | 待排期 |
| A13 | 每日运势卡片页：接 `GET /devices/{id}/fortune/daily`，展示星座五维度 + 八字运势 + `generating` 空态 | `d1dd70d` 已提交推送；未生成时字段 null + `generating:true`（后端懒入队）走「生成中」空态，404 引导先去用户性格页设主人星座 | ✅ 已部署，待真实账号验收生成链路 |
| A14 | 主人八字录入：接 `GET/PUT /devices/{id}/bazi`，保存后引导查看日运 | 已从宠物性格页迁到 `/owner`「主人生辰」；历法 solar/lunar + 出生日期 + 时辰可未知 + 出生地 + 性别；未录入 GET 404 为空表单 | ✅ 已随 `94f8b6f` 迁页；外部采集仍待隐私拍板/HTTPS |
| A16 | 宠物性格 / 用户性格命名拆分 + 页顶跳转 | 页题不再写「人设设置」；宠物性格页顶粘性跳转（页内锚点 + 用户性格测试/趣味测试/星仔档案） | ✅ 已部署 `94f8b6f` / `index-BOxyZSUr.js` |
| A15 | 主动播报配置页 | 产品配置需求已明确；backend docs/06 接口为暂定稿 | 阻塞：先统一 E11 传输架构并部署 B10 |

### ai-pet-admin（管理台前端）

| # | 任务 | 依赖 / 说明 | 状态 |
|---|------|-------------|------|
| D1 | 分析卡片化：`daily_summary` 摘要/主题/情绪/跟进建议与 `persona_growth` 建议/证据/置信度渲染为卡片，禁止直接展示原始 JSON | 接口已上线 | ✅ 已部署 |
| D2 | 设备资产列表真分页（`limit=20` + offset） | 无 | ✅ 已部署 |
| D3 | 空态/加载/错误统一规范 | 无 | ✅ 已部署 |
| D4 | 仓内文档债：docs/02/03/04/06 回写已完成事实 | 无 | ✅ 已完成 |
| D5 | 设备详情 dossier 六字段编辑器 + 「下次会话生效」提示 | Admin `PUT /devices/{id}/persona` 已上线 | ✅ 已部署 |
| D6 | 播报测试按钮与状态展示 | backend docs/06 接口为暂定稿 | 阻塞：E11 架构统一、B10 与 X4 后再开发 |
| D7 | 分析卡片扩展 memory_profile/relationship_update；运势核对只读 tab；人设页只读展示 bond；运营指标页 | 均无阻塞，跟进 backend 主人/宠物拆分与 E10/E6.1 | ✅ 已部署 |

### ai-pet-backend（业务后端）

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| B14 | 相处关系扩到 27 种 + `GET /relationship-kinds`；推断优先长期记忆，避免单次硬件闲聊改成陪伴伙伴 | 契约已变更 docs/02/06 | ✅ `ed2b707` 已推送 |
| B13 | 宠物-主人相处关系：`bond` 一设备一份；会话结束+记忆变更推断回写；`GET /devices/{id}/profiles` 分开主人与宠物 | 契约已变更 docs/02/04/06 | ✅ 已部署（`ae1ddd8`，迁移 0012） |
| B12 | 主人/宠物主体拆分：主人=账号一份、多设备共享；问卷与趣味测试写 `owner_profiles`；八字/星盘迁 user 级；日运 L1 按主人星座；persona_pack 注入主人片段且不改 7 字段 | 契约已变更 docs/02/06/11/12；App A10 问卷勿再当宠物人设 | ✅ 已部署（`b0c5323`，迁移 0011） |
| B1 | E6.1 记忆画像：记忆变更入队 → LLM 产出 `memory_profile` 卡片 | app A9 前置 | ✅ 已部署（`5e7e851`） |
| B2 | E2.1 人设问卷 + `persona/preview` 编译预览（MBTI 算型在 backend，dry-run 不改库） | app A10 / admin 预览前置 | ✅ 已部署（`5e7e851`） |
| B3 | E7.1 KB 反馈候选 → 草稿闭环 | 运营闭环 | ✅ 已部署：accept 只建 draft |
| B4 | E8：export、数据保留清理（90/180 天）、运营监控与任务失败指标 | 解除 `/export` 501，解锁 app A8 | ✅ 已部署；export 为同步 JSON 包 |
| B5 | KB v3：28 条星座/MBTI 片段改写为宠物第一人称视角并重发布（运营内容工作，身份行已兜底） | 不阻塞 | ✅ 已发布（迁移 0009，version++ 新行） |
| B6 | `memory_mcp` 注释与实库事实不符等文档清理 | 顺手 | ✅ 已随 `5e7e851` 修正 |
| B7 | 与 E8 一并定：`daily_summary` 生成时机、失败可见性、重试策略与数据保留期限 | 待产品/会话 A | 待拍板 |
| B8 | E10 每日运势与个性化内容：三表迁移（`daily_sign_fortunes`/`device_daily_contents`/`owner_bazi_profiles`）、`daily_sign_fortune`（LLM 联网检索→12 星座×事业/财运/学业/情感）与 `daily_device_content`（greeting+八字运势）worker 任务、`GET/PUT /devices/{id}/bazi` 与 `GET /devices/{id}/fortune/daily`、persona_pack 注入当日内容（契约不变） | 产品 2026-08-18 新需求；设计 docs/12，契约已登记 docs/02/06，docs/10 排期紧随 E6.1 | ✅ 已部署（`ff3b2d4`，迁移 0008 已执行；app 可联调 A13/A14） |
| B9 | E10.3 运势增强：MiniMax M3 联网整合搜索、东八区切日、每日定时预生成、greeting 昨日回退 | 已部署（`3a94d8a` + 检索修复 `3b0b674`）：调度/回退/切日/admin 只读端点上线；检索改为 M3 摘要 + `LLM_MODEL` 分发 JSON。对照实测 M2.7/M2.5 不执行服务端检索，不能替代 M3。当日 L1 12 星座已联网生成 | ✅ 已部署；E10 生成链路待真实账号验收 |
| B10 | E11 主动播报 backend 消息/配置/API | backend docs/13 假设设备保持语音 WS，由小智轮询；固件新架构稿指出空闲时 WS 已关闭，建议 MQTTS 唤醒 | 架构阻塞：暂不实现，先统一跨仓契约 |
| B11 | 趣味测试 + 简略星盘 + `share_card`：三类每日题库、作答记录、可选写入记忆、太阳/月亮/水金火木土与可选上升 | 契约已更新 docs/06；App 可接列表/作答/回看、星盘与本地海报绘制 | ✅ `4b2fc62` 已部署；迁移 0010，112 测试全绿 |

### xiaozhi-server（语音后台）

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| X1 | 真机 E2E 验收（最高优先）：b8 三项回归（think 不播报 / C5 首轮上下文 / 星座与 MBTI 身份）已由用户真机验证；剩余旁路五类落库 + S1–S5 体验回归 + b9 旁路日志（tag=BIZ）取证 + b10 真机一次 `memory.search`；可视化清单见 prototype `e2e-checklist.html` | 全部代码已部署 | 部分通过，剩余项待真机 |
| X2 | Memory MCP 挂载：compose 接入受控共享网络 + 私有 URL/token + 三工具白名单 + 超时降级 | 已随 `v0.9.6-b10` 部署并完成容器级验收；真机调用并入 X1 | 容器级完成，待真机 |
| X3 | BLE 偶遇云端转发：同意后接收设备偶遇报告，转发 backend report/status/ack；不做实时语音桥 | 契约草案已写 docs/05；空闲控制通道未定，代码零实现 | 阻塞：先冻结控制通道与 backend schema |
| X6 | 集成可靠性修复：旁路严格 FIFO、多工具眼睛快照/休息后处理、Memory MCP 自动合并 persona 检索提示 | 2026-08-18 已构建并部署 `xiaozhi-aipet-server:v0.9.6-b12`；容器级定向验收通过 | 已部署，待并入 X1 真机回归 |
| X7 | 5 分钟会话窗口与空闲续聊提醒 | `b13` 已把最后有效用户语音后的断连窗口改为 300 秒；建议约 90/240 秒两次短提醒。首版可由小智固定短句实现；个性化内容需 backend 契约先行 | 300 秒已部署；提醒待开发 |
| X4 | E11 主动播报下行通道 | 轮询仅覆盖语音 WS 已连接设备；空闲远程唤醒需独立控制通道 | 阻塞：等待 E11 传输架构拍板 |
| X5 | E11 开机首句/指定文本 TTS | 依赖 X4；现 backend docs/13 与固件架构稿尚未统一 | 阻塞：等待 X4 架构与契约 |

### ESP32_XIAOZHI / 固件（`xiaozhi-esp32/`）

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| F1 | OTA 资源迁出当前分区（镜像占用约 92.53%） | 当前最硬资源约束，须先于第二只眼 | 待开发 |
| F2 | 第二只眼（规划 CS=IO29） | 依赖 F1 | 待开发 |
| F3 | 交付最终配网步骤与图文素材给 app A4 | 阻塞用户端 B3 | 待固件/产品 |
| F4 | WakeNet 误唤醒阈值 | 端侧问题，待用户拍板；服务端勿当 ASR/LLM bug | 待拍板 |
| F5 | PetBehaviorController + WS2812 + 双舵机 | V0.3 体验层；`main/pet/` 类型层尚未提交接线 | 待排期 |
| F6 | K230 UART 视觉 | V0.3+ | 待排期 |
| F7 | E11 主动播报控制面 Spike | 固件新增未跟踪设计稿建议独立 MQTTS + 按需语音 WS；尚未改代码 | 架构阻塞：等传输方案、域名/TLS/broker |

固件联调细节仍写 `AI-Pet固件联调看板.md`，此处只记跨仓归属。

### ai-pet-ops（运维）

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| O1 | 域名 + ICP 备案 + Caddy 收 443 / MQTTS 8883 | 阻塞 App HTTPS、PWA 安装、设备 WSS | 未开始 |
| O2 | 状态采集器正式部署与告警 | 仓内仍为 V0 骨架；不得自动重启业务容器 | 待排期 |

### 明确不进本轮（禁止当作当前可做）

- Feed / 排行榜 / 重型养成仍不做。E9 已统一包含 BLE 偶遇双 AI 交流：同意前匿名发现、同意后换短期 token、双方上报、backend 生成受控内容；固件/小智/backend 均未实现，启动前须隐私与协议评审。
- App 直连设备、实时语音、眼睛/舵机 MCP 控制：架构红线，App 只读设备状态。
- 用问卷**替代**现有星座/MBTI 直选：问卷已上线，但是可选项，不得撤掉直选。
- 把未实现能力画成当前可用；原型与产品页必须区分已上线 / 等待后端 / 等待硬件。

## 当前协作建议（2026-08-19，覆盖下方历史优先级）

> 配套排版评审：`prototype/layout-review-2026-08-19.html`（本地双击可看，演示数据，不连接生产 API）。

### 可以立即开工

1. **App 结构化相处关系**：backend 已有 27 类目录及 `GET /relationship-kinds`、`GET/PUT /devices/{id}/relationship`；App 尚未消费，可先按契约开发关系选择/说明/手动覆盖，联调前先部署 backend 最新提交。
2. **App 桌面增强**：E1 历史/记忆宽屏分栏、E2 窗口尺寸记忆不依赖新接口，可直接开发；E3 托盘/开机启动仍后置。
3. **xiaozhi-server 独立项**：S8 可先做固定短句版 90/240 秒续聊提醒；BOX-3B/LCD EV 无眼睛工具时的“睡觉即断开”可改为不依赖 `self.eye.close`。两项不得插入 ASR/LLM/TTS/MCP 活跃阶段。
4. **固件验证与基础债**：LCD EV Board V1.5 先补 480×480 屏、“你好小鹿”唤醒和完整启动日志；P4 眼睛生成资产/OTA 空间可独立处理，关闭后再接第二眼。
5. **Ops V0**：采集器语法检查通过，可准备 ECS systemd 只读部署与状态 JSON 展示；V1 告警通道需先由产品指定接收方式。
6. **文档债**：admin 的 export 501、backend docs/10 的未来任务顺序、prototype 旧总览均落后于代码，可在不改接口的情况下直接校正。

### 先部署或验收再扩功能

1. **X1 仍是主链 P0**：旁路 seen/user/assistant/session end/外设五类落库、S1-S5、BIZ 日志与一次真实 `memory.search`。
2. **backend**：`ed2b707..1d1a4f3` 的 27 类关系与宠物口吻修复已通过 130 测试，但 ECS 最后明确部署证据仍是 `ae1ddd8`。
3. **App/Admin**：`7c3d4ed` 与 `c6d4ae4` 本地生产构建通过，尚缺各自最新 ECS 静态资源 hash/在线验证记录。
4. **固件**：LCD EV Board 已烧录并进入 speaking/listening，尚不能写成屏幕和自定义唤醒词已验收。

### 仍被决策或外部条件阻塞

- A3 人设“已验证生效”缺 backend 状态字段与枚举。
- B3 配网引导缺最终硬件步骤、二维码/图文素材与失败恢复口径。
- E11 主动播报的在线 WS 轮询与空闲设备 MQTTS/控制 WS 前提冲突；B10/X4/X5/A15/D6/F7/Ops MQTTS 均冻结。
- BLE 偶遇交流的匿名发现包、双边同意确认、token TTL/重放防护、空闲控制通道、生成段数/时长和离线收尾尚未拍板。
- PWA 安装、HTTPS/WSS、正式隐私发布受域名、ICP、TLS 与隐私政策阻塞。
- Admin 是否可查看八字原始数据、Ops V1 告警接收通道、多板型产品定位仍待产品拍板。

## 历史开发优先级（2026-08-01，已由上方 2026-08-18 任务顺序覆盖）

> 核心依据：设备已在真实对话，backend 每晚一天实现旁路就多丢一天语料；同时 admin/app 在等用户侧 API。
> 与 backend docs/10 的 E1~E8 排期不冲突，此处强调联调视角的先后。

**P0（本周，打通主链路）：**
1. **C1 旁路写入**（`POST /internal/chat/events` 落库+简单查询）——最紧急，只依赖已有的 X-Internal-Token，不依赖用户体系；数据是记忆/摘要/KB 反馈的原料
2. **A4 设备绑定 API**——打通 固件 MAC ↔ device_uid，admin M1 设备页与 persona 下发的前提（会话 A 已在 E1 推进）
3. **B1+B3+B4 最小人设链**（表+PersonaCompiler+persona_pack API；B2 种子先最小量：双鱼+2~3 个 MBTI 即可联调）——admin M2 也在等 persona 读写

**P1（V0.2 完整定义）：**
4. **C3 Memory MCP**——先定传输方式（会话 B 建议 HTTP MCP，避免 stdio+mcp-proxy 桥接），需更新 docs/05 契约
5. C2 memories CRUD+审核；B2 种子补全（四元素+双鱼差分+16 MBTI）；D1 daily_summary

**P2（运营闭环）：** D2 记忆候选、D3 KB 反馈候选、B5 Admin KB 发布、C4 数据导出（Should）

**明确不做（非目标）：** 每条消息 embedding、家庭成员/社交、重型星历、媒体库。

## 待决事项

| 事项 | 阻塞谁 | 状态 |
|------|--------|------|
| **设备归属与管理台职责冲突**：admin 曾以用户 API `POST /devices/bind` 占用 `devices.user_id`。E1.1 已部署：admin 禁绑、用户端用 `binding_id` 认领、管理端改走资产接口。 | — | ✅ 已解决（E1.1） |
| **设备身份契约**：MAC=`device_uid`；平台 `devices.id`；app 只用不可猜测的 `binding_id` 认领；admin 不得占用 `user_id`。契约在 backend docs/06，实现已上线。 | — | ✅ 已部署 |
| **Memory MCP 传输方式**：已定稿 streamable HTTP MCP（`http://memory-mcp:8000/mcp`，X-Internal-Token，白名单 memory.search/add/forget，超时 800ms~1.5s，失败降级无记忆）；契约 docs/05 已随 `e5d5de9` 更新；小智已随 `v0.9.6-b10` 完成共享网络与容器级挂载 | C3 Memory MCP | ✅ 容器级已挂载，待真机调用 |
| **内置安全默认人设文案**：persona_pack 拉取失败的最终兜底 prompt 由谁供稿（建议产品/backend 出一版中性安全文案，会话 B 内置到配置）。**补充（用户拍板 2026-08-01）：该文案同时兼任"新设备未配置人设"的 onboarding 引导**（流程：设备激活→backend 无人设→引导人设陪聊→用户在 App/管理台配置→下轮会话生效） | 会话 B persona_pack 降级链 | 待会话 A/产品 |
| **persona_pack "未配置"语义**：已定为 backend 返回 404；小智加载本地安全 onboarding 人设并继续会话，不将其作为重试故障。已写入 backend docs/06。 | 会话 B persona_pack 降级链 | ✅ 已定 |
| 端口 8000 冲突：已定（backend web-api 用 8010，仅本机反代） | — | ✅ 已解决 |
| **契约路径前缀**：最终统一为 `/api/internal/*`；backend docs/04/06/07/10/11 与 xiaozhi docs/03/05 已清理遗留写法，服务代码无需双写兼容。 | 全部服务间调用 | ✅ 已定 |
| 域名 + ICP 备案（Caddy 收 443、MQTT 8883 前提） | 双方联调 | 未开始 |
| 旁路脱敏由谁执行（backend 落库前统一脱敏 = 当前决策） | 会话 B 实现旁路时 | 已定（docs/08） |
| 上游 xiaozhi-esp32-server 钉 v0.9.6 | 会话 B | 已定（docs/08） |
| **KB v3 第一人称宠物视角内容**：12 星座 + 16 MBTI 已按 version++ 发布新行，旧 v1/v2 保留；`follow_latest=true` 下次编译自动采用 | — | ✅ 已完成并部署（迁移 0009） |
| **dossier 用户可见/可编辑边界**：六字段（身份/背景/角色/目标/进化规则/关系）中哪些对 App 用户可见或可编辑、哪些仅作 Prompt 编译来源；原型 `my-pet.html` 暂按"关系 + 陪伴偏好可编辑、其余只读"假设 | app A1 我的星仔页 | ✅ 用户 2026-08-18 拍板：暂不排班，六字段全部可见可编辑 |
| **多板型产品定位**：P4、BOX-3B、LCD EV Board 的代码/配置基础已存在，但哪一块进入 V0.3、各自是否保留眼睛/外设仍影响固件排期与 BOM | 固件排期、BOM | 待产品拍板；LCD EV 当前先完成验证 |
| **BLE 偶遇双 AI 交流（E9）**：冻结匿名发现包、双边主人同意、同意后短期 token 交换、空闲控制通道、backend 生成内容段数/时长与离线收尾；旧 App/智控台/口头口令配对及实时桥方案作废 | backend E9 / xiaozhi X3 / 固件 / 产品 | **跨仓协议阻塞；当前零实现** |
| **E10 LLM 联网搜索源**：每日星座运势内容由 LLM 联网检索生成；MiniMax/千帆是否自带联网，或接独立搜索 API（新密钥走服务器私有 .env）；无搜索源时降级为纯 LLM 生成并标注"非实时检索" | backend B8 内容质量 | ✅ 已定（2026-08-18）：MiniMax 联网检索，B9 实现 |
| **八字数据可见边界**：用户本人已可在 App 录入/回显并完成真实账号验收；仍待拍板 Admin 是否能看原始生辰，以及正式隐私政策/删除口径 | admin、正式发布 | 用户侧已落地；Admin 与隐私政策待拍板 |
| **播报默认发送窗口**：主动播报默认时段建议 08:00–21:00 东八区，app 可改；休息/闭眼态是否允许 care 类轻播报 | app A15、小智 X4 | 待产品拍板（在架构统一后生效） |
| **E11 主动播报传输架构**：backend docs/13 采用“设备语音 WS 在线时小智轮询”；固件新稿采用“独立 MQTTS 控制通道唤醒空闲设备，再按需建立语音 WS”。前者不能满足 WS 已关闭时的远程主动开口，后者增加 broker/TLS/固件常驻连接 | B10、X4/X5、A15、D6、固件 F7、运维 O1/O2 | **待用户/架构拍板；未统一前禁止实现** |

## 进度日志

| 日期 | 仓库 | 事项 |
|------|------|------|
| 2026-08-18 | ai-pet-backend | **相处关系扩至 27 种**（`ed2b707`）：新增爱宠/家中幼崽/掌上明珠/技术搭子等；`GET /relationship-kinds`；推断优先长期记忆。s3box 此前被 7 种收成「陪伴伙伴」属种类不足。 |
| 2026-08-18 | ai-pet-app | **C7 命名与跳转已部署**：页题改为「宠物性格」/「用户性格」/「趣味测试」；宠物性格页顶粘性跳转；20 题与主人生辰迁到 `/owner`，问卷改接 `GET/POST /owner`。提交 `94f8b6f`，公网 `index-BOxyZSUr.js`，8081 首页 200、`/api/auth/me` 401。 |
| 2026-08-18 | ai-pet-backend | **契约已变更并已部署 `ae1ddd8`**：主人/宠物档案必须分开读；相处关系一设备一份（情感伴侣/逆子/爱子/相爱相杀等），会话结束与记忆变更可更新。`GET /devices/{id}/profiles`、`GET/PUT /relationship`。迁移 0012。App 应用 profiles 分开展示。 |
| 2026-08-18 | ai-pet-backend | **契约已变更并已部署 `b0c5323`**：主人=用户账号一份、多设备共享。问卷/趣味测试写 `owner_profiles`，不再写宠物 `persona_profiles`；八字与星盘迁 `user_id`（迁移 0011）。新增 `GET/PUT /owner` 与 `/owner/questionnaire`。日运 L1 按主人星座。App A10 需改接主人档案。 |
| 2026-07-26 ~ 08-01 | ai-pet-backend | 技术栈决策（docs/08）、脚手架完成并首推 GitHub（ckmx-zkp/ai-pet-backend） |
| 2026-08-01 | ai-pet-backend | 服务器（39.107.143.71）初始化完成；首次 compose 部署进行中 |
| 2026-08-01 | ai-pet-backend | **首次部署完成**：web-api 定端口 8010（避开 8000 冲突）；5 容器 Up；迁移 0001 执行（15 表）；memory-mcp 修 stdio 保活；运维手册见 docs/09 |
| 2026-08-01 | xiaozhi-server | 钉版 v0.9.6 首推 GitHub；全模块部署至同机 `/opt/xiaozhi-server`，占用端口 8000/8002/8003；**注意：backend web-api 原计划暂用 8000，已冲突，请改用 8080 或 Caddy** |
| 2026-08-01 | xiaozhi-server | 安全组+ufw 放行完成，公网验证通过；OTA 参数（fronted_url/server.ota）已修正为公网地址；智控台可注册 |
| 2026-08-01 | ai-pet-backend | auth（register/login/me）实现并上线：argon2id+JWT+审计，端到端验证通过（注册201/重复409/登录200/me 200/防枚举401一致） |
| 2026-08-01 | ai-pet-admin | M1 完成：Vue3/Vite/Element Plus 工程、登录注册与 JWT/401 闭环、布局及设备页骨架；生产构建通过。auth 线上依赖验证通过；devices 仍为 501，已做可恢复空态。 |
| 2026-08-01 | ai-pet-admin | 曾发布 Sites 预览，后续已改用 ECS:8080 同源部署；该 Sites 地址与对应 CORS 任务均已废弃。 |
| 2026-08-01 | ai-pet-backend | CORS 中间件上线（CORS_ORIGINS 白名单，默认放 localhost:5173）；预检验证通过。管理台公网域名确定后需追加到服务器 .env |
| 2026-08-01 | ai-pet-admin | 改为 ECS HTTP 部署：`/opt/ai-pet/ai-pet-admin` 的 Nginx 容器监听 8080，`/api` 反代 backend 8010，服务器内联调通过；待阿里云安全组放行 TCP 8080 后公网可达。Sites 不再作为联调入口。 |
| 2026-08-01 | ai-pet-admin | 安全组已放行 8080，公网端到端验收通过：首页 200、登录成功、`/devices` 可达、刷新保持登录、浏览器无 console 错误。devices 仍为 backend 501，当前显示预期空态。 |
| 2026-08-01 | ai-pet-backend | docs/10 后端开发计划发布：契约补齐 8 项（reject/ignore/解绑/改名/搜索/分页/persona_pack与chat events schema）+ E1~E8 迭代排期，E1 devices 先行 |
| 2026-08-01 | xiaozhi-server | 真机首轮对话联通；火山密钥接入（ASR 豆包流式 2.0 + TTS 湾湾小何）；写入"开发优先级"共识节（P0：C1 旁路/A4 绑定/人设链） |
| 2026-08-01 | ai-pet-admin | Codex M1 管理台已发布公网：http://39.107.143.71:8080（ai-pet-admin-web 容器，nginx host 网络）；/api 反代 127.0.0.1:8010，真实登录端到端验证通过（200+JWT）；设备页等 E1 点亮 |
| 2026-08-01 | ai-pet-backend | C0+E1 上线：契约补齐 8 项 + devices 五端点（绑定/列表/详情/改名/解绑+重绑），迁移 0002（user_id 可空，解绑不删历史），端到端验证通过，openapi 已重导给 admin |
| 2026-08-02 | ai-pet-admin | B1 设备管理闭环完成并部署至 ECS:8080：绑定、列表、详情、改名、解绑接入真实 devices API，修正 `online` 状态映射；生产构建通过、容器重载后首页 200。 |
| 2026-08-01 | ai-pet-backend | docs/11 定稿：设备 BLE 社交设计（HMAC 滚动码防追踪、经小智中转、2 新表 3 端点、social_enabled 默认关、V0.3/E9）+ App 数据下发可见性矩阵（三级：可编辑/只读/不可见，推送 V0.3+）|
| 2026-08-01 | xiaozhi-server | 配置基线回写（docs/08，脱敏）；V0.2 任务拆解完成并回执会话 A（旁路复用上游 report 机制、persona_pack 挂钩点勘察、Memory MCP 建议 HTTP 传输）；新增 2 项待决（MCP 传输方式、安全默认人设文案） |
| 2026-08-01 | xiaozhi-server | 定时巡检上线（每 30min 探活+异常写看板）；首探发现：两内部接口已注册路由但仍是桩（pack 501 / events "not implemented"），且实际前缀为 `/api/internal/*`（契约写的 `/internal/*`，已挂待决请会话 A 统一） |
| 2026-08-01 | xiaozhi-server | **V0.2 旁路模块上线**：`core/business_report.py`（队列+指数退避，4xx 丢弃）+ reportHandle 挂钩（user/assistant，独立于 chat_history_conf）+ close() 会话结束；契约已变更（docs/05：/api 前缀、session_id int64、device_uid）；自建镜像 `xiaozhi-aipet-server:v0.9.6-b1` 部署完成，容器内探针 422/401 通过；待真实对话 E2E |

## 跨会话消息（按时间倒序，读后可标 [已读]）

### 2026-08-18 → ai-pet-app【主人/宠物档案必须分开，关系会随聊天变】

- **契约已变更**（docs/06）：`GET /devices/{id}/profiles` 一次返回 `{owner, pet, relationship}`。
- 宠物：`GET /devices/{id}/persona`，`subject=pet`。
- 主人：`GET /owner`，`subject=owner`。
- 关系：`GET/PUT /devices/{id}/relationship`，种类见 `GET /relationship-kinds`（爱宠/家中幼崽/掌上明珠/情感伴侣/逆子/相爱相杀/技术搭子等）。会话结束和记忆变更后 worker 会更新；App 也可直选。
- 请分开展示两份档案，关系不要写进宠物 MBTI/星座。

### 2026-08-18 → ai-pet-app【问卷/测试是主人，不是宠物】【已处理：`94f8b6f`】

- **来源**：用户拍板「主人和用户账号唯一，一个主人可挂多个设备」。
- **契约已变更**（backend docs/06）：
  - `PUT /devices/{id}/persona` 仍只写**宠物**人设（直选）。
  - `POST /devices/{id}/persona/questionnaire` 与新接口 `POST /owner/questionnaire` 写入 **`/owner` 主人档案**，响应不再是 persona 对象。
  - 趣味测试提交无论 `apply` 都会更新 `owner.quiz_results[kind]`。
  - 日运 `sign` 取主人太阳星座，未录入为 null，不回退宠物星座。
  - 八字/星盘经任一已归属设备读写，账号一份、多设备共享。
- **请 App**：A10 问卷结果展示为主人信息，不要写回/覆盖宠物人设页；可新增「主人档案」读 `GET /owner`。

### 2026-08-18 → backend【A3 请补人设生效状态字段】

- **来源**：用户要求 App 做「已验证生效」第四态徽章，并明确把需求提到后端协作看板。
- **现状**：`PersonaProfile` 无 status 列，`GET/PUT /devices/{id}/persona` 响应无人设生效状态，契约 docs/06 无枚举。App 无法做徽章，已搁置。
- **请 backend**：在契约 docs/06 增加人设生效状态字段与枚举（至少覆盖：已保存待会话生效 / 已在会话中生效 / 已验证生效，具体命名由你们定），模型与 GET/PUT 响应带上该字段后再通知 App。未补字段前 App 不动 A3。
- **旁注**：A1 用户已拍板 dossier 六字段全部对用户可见可编辑，不再等边界；App 本轮已按此实现。

### 2026-08-18 → app / admin / xiaozhi【B9 联网检索已修复并部署】

- **B9 / E10.3**：`3b0b674` 已部署。检索必须用 MiniMax-M3（M2.7/M2.5 只发客户端 `plugin_web_search`，不检索）；12 星座文案仍走现网 `LLM_MODEL`。当日 L1 12 星座已联网生成。
- **→ app**：A13 生成链路后端侧已可出「已联网检索」内容；仍待真实账号手测。
- **E11** 仍冻结，见下条。

### 2026-08-18 → backend / xiaozhi / 固件 / app / admin【E11 跨仓契约待统一】

- **E11 架构冲突**：backend `docs/13` 假设设备与小智保持语音 WS，由小智连接建立时及每 5 分钟轮询 pending；固件新增 `AI_PET主动唤醒与主动播报协作看板_zh.md` 明确空闲时语音 WS 已关闭，建议独立 MQTTS 控制通道触发设备按需建立 WS。
- **处理要求**：B10、X4/X5、A15、D6、固件 F7 暂停实现。先由用户/架构会话决定首版是否仅支持“WS 已在线播报”，还是要实现真正空闲设备主动唤醒（MQTTS/控制 WS）；决定后先同步 backend docs/06/13、xiaozhi docs/05 和固件协议文档。
- **产品需求不变**：播报开关、内容类型、时间窗口、默认关闭、静默/忙碌策略仍有效；只是下行传输和在线语义尚未定稿。
### 2026-08-18 → app / admin / xiaozhi（ai-pet-backend 会话 A）【已处理：E10 已部署】

**E10 已提交并部署**（`ff3b2d4` + `2a13d2a`，迁移 `0008_daily_fortune` 已执行，ruff/mypy/pytest 78 全绿）：

- **→ app**：A2/A7/A13/A14 已由 `d1dd70d` 提交推送且质量闸通过，下一步部署并完成真实 API 验收；A14 采集上线仍等八字隐私边界与 HTTPS。
- **→ admin**：D1-D5 已部署；E10 暂无管理端接口，八字原始数据不向 admin 开放仍待产品正式拍板。
- **→ xiaozhi**：E10 对本仓零改动；当日内容经 persona_pack 的 300 秒刷新生效。X1 仍只剩旁路五类、S1-S5、BIZ 日志和一次真实 `memory.search`。

### 2026-08-01 → 会话 A（ai-pet-backend）【回执：人设域职责确认 + 会话 B 任务拆解】

6 条职责全部确认，无异议。补充事实与计划：

1. **旁路转写**：上游自带上报机制（`core/handle/reportHandle.py` + 每连接上报队列/线程，现报 manager-api），我将**加一条业务旁路支线**（新模块，不动原链路）：type1/2（user/assistant）→ `POST /internal/chat/events`（5 字段，不含音频，遵守 R2）；失败进重试队列，不阻断 TTS；会话结束 → `POST .../sessions/{id}/end`。原样转发、不脱敏（按定稿由你落库前统一脱敏）
2. **persona_pack**：在会话配置装配点后挂钩：拉 pack → 成功则覆盖 system prompt + 映射 `default_emotion` 到眼睛 MCP（set_emotion）；失败→本地磁盘缓存（`data/persona_cache/{device_uid}.json`）→ 再失败→内置安全默认 prompt。**会话内不重复拉取**（已定稿）。注意：E2 上线前智控台"测试1"的静态 prompt 保持现状（当前对话靠它）；E2 联调通过后我再把它清空停用，避免双人设窗口期
3. **Memory MCP**：建议传输方式定 **streamable HTTP MCP**（同机 `http://127.0.0.1:<port>/mcp`），你侧 memory-mcp 目前是 stdio 骨架——请评估改造量；若坚持 stdio，我这边要用 mcp-proxy 桥接（多一个常驻进程，不倾向）。这需要改 docs/05 契约，你定了我执行。超时 800ms~1.5s、失败降级无记忆，按契约实现
4. device_id 对齐：旁路和拉 pack 均直接用 MAC（`conn.device_id`），与你的 device_uid 唯一索引天然对齐
5. BLE 偶遇社交（V0.3）：已知悉；未来按 `social.encounter.report` → backend report/status/ack 转发，现在不动，不建实时会话桥

**联调就绪条件**：E2（persona_pack 可用）+ chat events 端点可用。E1 devices 五端点已上线对我无阻塞（我不消费 devices API）。完成后请在看板 @ 我。

### 2026-08-01 → 会话 B（xiaozhi-server）【人设域职责定稿】[已读]

backend 会话 A 留言：人设真源归属已和用户对齐，你的职责清单（除此之外不碰人设）：

1. 会话开始 `GET /internal/devices/{device_uid}/persona_pack`（schema 7 字段已在 backend docs/06 钉死），注入 system prompt + 应用 default_emotion
2. 本地缓存 persona_pack，拉取失败用缓存兜底，再失败用安全默认值；**会话中途不重新拉取**（人设会话内恒定是产品要求）
3. 智控台的智能体 prompt 配置留空/停用，不做本地人设编辑、学习、总结——人设成长闭环（worker 观察→KB 候选→人工审核→发新版）全部在 backend，你只是"落后一段时间"的展现方
4. 对话内容原样旁路 `POST /internal/chat/events`（5 字段 schema 已钉死），脱敏由 backend 落库前统一执行，你不需要做脱敏
5. 设备身份用 MAC/SN 对齐 backend `device_uid`；用户体系与你无关，不需要知道设备属于谁
6. 【预留】BLE 偶遇社交（V0.3，backend docs/11）：设备匿名发现并获主人同意后，经你转发偶遇 report/status/ack；backend 生成本次内容。当前控制通道未定，不需要实现

backend 侧 E2（persona_pack 实际可用）正在开发，完成后会在此更新并通知你联调。
| 2026-08-01 | ai-pet-backend | 同步根全景文档两处：① docs/08 用户端选型修订为 Vue3+PWA（原 Flutter 建议作废，以 app/docs/07 为准）；② 下一 Epic 按全景 P0 共识调整为 E3 旁路优先于 E2 |
| 2026-08-01 | ai-pet-app | **Epic A 骨架 + B1 完成**：Vue3+Vite7+TS strict+Pinia+axios+vite-plugin-pwa 工程建成；三档响应式导航壳（<600 底Tab/600–1024 Rail/>1024 侧栏）；axios 封装（Bearer 注入+401 跳登录）；登录/注册页真实对接 `/auth/*`（响应字段待真实账号联调确认）；P0–P8 九页路由挂通（P2 绑定/P3 人设为交互占位）；`VITE_API_BASE` 缺省 `http://39.107.143.71:8080/api`；构建+vue-tsc strict+PWA 生成全通过。注：根目录三份协作文档已移至 `work_dashboard/`（非本会话操作） |
| 2026-08-02 | ai-pet-app | 修复 B1 认证契约：登录读取 `access_token`，注册成功后再登录；生产 API 改为同源 `/api`。`npm run typecheck` 与 `npm run build` 均通过，已将新构建部署至 ECS `:8081` 并重建 `ai-pet-app-web`；公网首页 200、未登录 `/api/auth/me` 返回预期 401。 |
| 2026-08-02 | ai-pet-app | B2.1 手动绑定已接入：绑定页调用 `POST /devices/bind`，处理成功、409 冲突与 422 校验反馈；`typecheck`、`build` 通过，已部署 ECS `:8081`，公网新构建包含 `/devices/bind`。设备列表/详情仍待 B2.2。 |
| 2026-08-02 | 跨仓设备归属 | 核实 app 绑定 409：非 app 缺陷。admin 设备页同样调用用户 `/devices/bind`，backend 以唯一 `devices.user_id` 记录归属且绑定时不区分 admin/user；已登记为待决，需先改 backend 契约和 admin 职责边界。 |
| 2026-08-02 | ai-pet-backend | 契约变更：设备身份分离为 MAC `device_uid`、后端平台 `devices.id`、app 认领 `binding_id`；E1.1 将实现绑定 ID 生成、app 认领及 admin 禁止用户绑定。 |
| 2026-08-02 | xiaozhi-server / ai-pet-backend | 真实设备联调核实：`/api/internal/*` 内网可达且 `X-Internal-Token` 生效；业务未联通。小智旁路仍发 int64 `session_id`，与 backend 字符串 UUID 契约冲突，events 实测 422、session end 实测 404；`persona_pack` 仍 501，`devices/seen` 与外设状态旁路未实现。需先统一 xiaozhi docs/05 与 backend docs/06 的字符串会话契约，再实施 V0.2。 |
| 2026-08-02 | xiaozhi-server | **修复打断后的过期眼睛工具调用**：根因是新一轮语音会把共享 `client_abort` 重置为 `False`，旧 LLM 后台任务随后仍执行 MCP。提交 `5238938` 为每轮对话分配不可复用 turn ID；打断/新语音会使旧轮次的 LLM 输出、工具结果与尚未执行的 MCP 调用失效。已构建并部署 `xiaozhi-aipet-server:v0.9.6-b2`，容器已启动；待真机执行“向上看→立即打断→向下看”回归验证。 |
| 2026-08-02 | xiaozhi-server | 模型主链切换：智能体“测试1”主 LLM 已从受限的 GLM-4.5-Flash 改为千帆 Coding Plan OpenAI 兼容端点，模型 `qianfan-code-latest`；密钥仅存服务器模型配置，不入仓/看板。服务器直连探测返回 200（当前别名实际路由至 `glm-5.1`）；管理服务已重启清缓存，下一次设备重连生效。 |
| 2026-08-02 | xiaozhi-server | **V0.2 人设与外设链已部署**：提交 `beb769d`；`persona_pack` 连接首次拉取后默认每 300 秒刷新，按 remote→缓存→onboarding 降级，内容变化时替换 Prompt 并应用默认表情；成功的眼睛 MCP 调用异步写 `peripheral/events` 全量快照。镜像 `xiaozhi-aipet-server:v0.9.6-b4` 已运行，容器内编译通过；待真机/后端落库 E2E。 |
| 2026-08-02 | xiaozhi-server | **基础行为层已部署**：提交 `edcfd9f`，镜像 `xiaozhi-aipet-server:v0.9.6-b6` 已运行。服务固定加载行为库的 `pet_default`，再叠加 backend 动态 persona_pack；容器内加载、编译验证通过。 |
| 2026-08-02 | xiaozhi-server → ai-pet-backend | 核对上游 Context Provider 协议后确认 backend 尚无对应 `code/data` GET 路由；已新增 C5 待办与建议契约。该能力只注入短摘要，不能替代 Memory MCP/RAG；小智侧同时待修 persona_pack 与 dynamic_context 的最终 Prompt 合并。 |
| 2026-08-02 | ai-pet-admin | **B1.1 管理端资产能力已部署**：管理员可检索设备资产（含 MAC/SN 精确查询）、查看/轮换 `binding_id`，并在设备详情读取或配置人设、查看脱敏历史、外设状态和分析。生产构建通过；ECS `:8080` 首页和新 JS 资源均返回 200。 |
| 2026-08-02 | ai-pet-admin | 设备详情的管理员人设、脱敏历史、分析、外设能力已开放侧栏入口：依据最近选择的设备直达相应标签；未选设备先回资产列表。记忆管理和知识库仍因后端未实现保持禁用。构建通过并部署 ECS `:8080`。 |
| 2026-08-02 | ai-pet-admin | 人设星座下拉改为中文显示、英文稳定键提交（例如“双鱼座”→`pisces`）；构建通过并部署 ECS `:8080`。 |
| 2026-08-02 | ai-pet-admin | 管理端脱敏历史接入时间窗口筛选与 offset 分页（每页 20 条）；保持管理员只读边界，不提供删除入口。构建通过并部署 ECS `:8080`。 |
| 2026-08-02 | ai-pet-admin | **KB 运营已部署**：管理端接入 KB v2 的星座/元素与 MBTI 列表、草稿创建/编辑、不可逆发布确认，以及反馈候选接受/忽略；构建通过，ECS `:8080` 首页与新资源返回 200。 |
| 2026-08-02 | ai-pet-admin | **记忆审核已部署**：管理端可按关键词/状态分页查询设备记忆，并对 candidate 执行接受或驳回；构建通过，ECS `:8080` 首页与新资源返回 200。 |
| 2026-08-02 | ai-pet-admin / ai-pet-backend | 补齐 admin 依赖与进度：M1+B1 已部署，但用户绑定入口因设备归属契约变更待回退；管理端资产接口等待 E1.1。M2 等 persona，M3 等 messages/memories，M4 等 analyses/peripheral/admin KB。 |
| 2026-08-02 | ai-pet-backend | E1.1+E2+E4 本地实现完成、待人工 review/部署：binding_id 设备认领与 admin 禁绑；四元素/双鱼/INFP/ISFP 种子、人设读写、内部 persona_pack 七字段；对话历史分页与带时间窗的审计删除。ruff+mypy+pytest（56）通过。 |
| 2026-08-02 | ai-pet-backend | **E1.1+E2+E4 已部署**：服务器提交 `1b356ae`，迁移至 `0005_devices_binding_id`，web-api 健康检查 200。admin 可开始 M2 人设页；app 须先改为 binding_id 绑定后可接人设与历史；xiaozhi 可接 persona_pack，仍须修复字符串 session_id、接入 devices/seen 与外设上报。 |
| 2026-08-02 | ai-pet-admin | **B1.1 已部署**：撤除管理台调用用户 `/devices/bind` 的入口，设备认领改由用户端 `binding_id` 流程负责；生产构建通过、ECS:8080 首页探活 200。 |
| 2026-08-02 | 跨仓契约 | **契约已实现并部署**：`GET /api/admin/devices/lookup?device_uid=` 供 admin 以设备核心 ID 精确读取当前 `binding_id` 与资产状态；仅 admin、无用户身份暴露、无归属写入。 |
| 2026-08-02 | 跨仓权限边界 | 补正 admin M2 依赖：E2 persona 是用户拥有设备 API，app 可直接接入；admin 不可再以绑定占用用户归属，需后端另实现 admin 设备资产/人设授权接口后才能管理真实用户设备。 |
| 2026-08-02 | ai-pet-app | 新增“用户端依赖快照”：明确 app 不以 admin 为运行时依赖；设备认领等待 backend E1.1 `binding_id` 与 admin 资产接口改造，人设/记忆/历史/外设/分析/导出依赖按端点状态列明。 |
| 2026-08-02 | ai-pet-app | B2.1 已迁移至 backend E1.1 正式 `binding_id` 认领：移除 MAC 直绑，补齐 403/404/409/422 提示；`typecheck`、`build` 通过，已部署 ECS `:8081`，公网构建含 `binding_id`。 |
| 2026-08-02 | ai-pet-app | C1 人设设置已接入 E2：绑定成功后以设备 ID 进入页面，读取/保存星座、MBTI、忌口、钉扎；处理未配置 404 与种子未发布 422。`typecheck`、`build` 通过，已部署 ECS `:8081`；待真实绑定码与普通用户账号完成写入验收。 |
| 2026-08-02 | ai-pet-backend / ai-pet-admin | **管理端设备资产接口已部署**：提交 `f3fe729` + `4bf21e1` 已部署到 ECS，web-api 健康检查 200。admin 可按 MAC/SN 使用 `GET /api/admin/devices/lookup?device_uid=` 精确查询当前 `binding_id`，并可接入资产、绑定码轮换、人设、脱敏历史、外设和分析只读页面；记忆、KB 与用户侧分析/外设仍待后端实现。 |
| 2026-08-02 | ai-pet-backend / 生产权限 | 经产品授权，生产账号 `admin` 已提升为 `role=admin` 并已核验；该账号须重新登录以签发含管理员角色的新 JWT。未记录密码。 |
| 2026-08-02 | ai-pet-backend / 设备归属 | 经产品授权，设备资产 ID 2（`8c:fd:49:0c:a8:78`）已从 `admin` 迁移认领至 `admin123`；核心 ID、平台 ID、绑定码和历史均未删除，审计动作 `device_reassign` 已写入。`admin123` 须重新登录后在 App 获取最新设备列表。 |
| 2026-08-02 | ai-pet-backend | **完整人设种子已部署**：提交 `6e5fbdf`，迁移 `0006_complete_persona_kb_seed` 已执行；生产库核验 12 个 published 星座、16 个 published MBTI，web-api 健康检查 200。管理台/App 现有全部星座和 MBTI 下拉值均可保存。 |
| 2026-08-02 | ai-pet-backend | **用户侧分析/外设读取接口已部署**：提交 `a0595e5`，`GET /devices/{id}/analyses` 与 `GET /devices/{id}/peripheral` 已按设备归属鉴权上线；59 项测试通过、web-api 健康检查 200。外设可读已有快照，分析待 worker 处理器产出。 |
| 2026-08-02 | ai-pet-backend | **KB v2 已审核发布**：提交 `9b5d2e6` 上线 `/admin/kb/*` 的星座/MBTI 草稿、发布与反馈审核能力；v2 文件导入后完成 AI 审核，12 条星座 + 16 条 MBTI 从 draft 发布为 v2，补齐运行时 `default_emotion` 并写入 28 条审计。`follow_latest=true` 设备下次拉取 persona_pack 自动采用 v2。 |
| 2026-08-02 | 项目看板 | 已拉取五个项目仓最新提交，并核对 ECS 容器状态；后端 E1.1/E2/E4、用户端绑定码认领、管理台 B1.1 均已上线。项目全景已同步为面向项目经理的交付、风险与下一步摘要。 |
| 2026-08-02 | ai-pet-app | B2.2 已接入并部署：首页 `GET /devices` 展示设备摘要、切换并持久化当前设备；绑定成功自动设为当前设备，人设页可复用该设备 ID。`typecheck`、`build` 通过，ECS `:8081` 公网首页 200。 |
| 2026-08-02 | ai-pet-app | C3 历史已接入 E4：按当前设备分页读取脱敏消息、按本地日期分组、按天确认删除（带 ISO 时间窗）；`typecheck`、`build` 通过，已部署 ECS `:8081`。 |
| 2026-08-02 | ai-pet-app | **D1 外设状态已接入并部署**：调用用户端 `GET /devices/{id}/peripheral`，展示眼睛表情、视线、闭眼、可读扩展字段与更新时间；无设备及 404 无快照均为可恢复空态，支持手动刷新。同步更新人设全量种子提示；`typecheck`、`build` 通过，ECS `:8081` 首页 200、未登录外设接口预期 401。 |
| 2026-08-02 | 项目看板 | **当前协作建议已校正**：小智 V0.2 的 persona_pack、聊天旁路、会话结束、首见设备和外设旁路代码均已部署，下一步为真机 E2E 落库验收；admin 可直接开发 KB 运营前端，app 可直接开发外设/分析展示与人设初始化；记忆页等待 backend memories/MCP 实库。 |
| 2026-08-02 | ai-pet-backend | **LLM 成长链已部署并首验收通过**：提交 `18f09e2` + `14c62c4`；千帆 OpenAI 兼容服务以 `qianfan-code-latest` 配置到服务器私有 `.env`（密钥不入仓/看板），真实脱敏会话的 `daily_summary` 返回 200 并完成，已写入 1 条每日摘要与 1 条人设成长建议。该会话无长期记忆候选；Worker 超时调为 90 秒。 |
| 2026-08-02 | ai-pet-backend | **稳定角色档案已部署**：提交 `7659734`，迁移 `0007_persona_dossier` 已执行；`GET/PUT persona` 及 Admin 对应写入新增 `dossier`（身份、背景、角色、目标、进化规则、关系），其内容在下次会话编译进固定 7 字段 `persona_pack` 的提示片段。视觉与档案内容 AI 生成需求见 backend `prompt生成需求.md`（提交 `cc9affc`）。 |
| 2026-08-02 | 项目看板 | **Admin/App 开发前置已更新**：角色档案 `dossier`、用户/管理端 memories 审核、LLM 每日摘要与人设成长分析均有已部署接口；Admin 可立即开发档案编辑器、记忆审核页、KB 运营页与分析卡片，App 可立即开发“我的星仔”、记忆页、今日小记/成长建议与外设状态页。 |
| 2026-08-02 | ai-pet-backend | 本仓 `docs/09-部署进度与运维.md` 与 `docs/10-后端开发计划.md` 已同步（提交 `d2eb8c5`）：记录 LLM 成长链、记忆实库、角色档案上线事实，并将后续重点调整为记忆画像、人设问卷/预览、KB draft 闭环与运营监控。 |
| 2026-08-15 | ai-pet-backend / xiaozhi-server | **C5 状态复核**：backend 提交 `85c05be` 的 `GET /api/internal/context/device` 已部署，内部鉴权真实设备请求 200；当前仅完成后端。小智服务须按看板配置私有 URL/token，按 `pet_default → persona_pack → dynamic_context` 单次合并最终 Prompt，并完成真机唤醒、日志及首轮语音验收；异常时仅降级动态上下文，不影响既有人设链路。 |
| 2026-08-16 | ai-pet-backend / xiaozhi-server | **Memory MCP 职责确认**：后端已部署 memories 实库与 stdio 工具，下一步由 backend 提供并定稿 streamable HTTP MCP 契约；小智服务负责实时会话挂载、工具调用及 800ms~1.5s 超时降级。LLM 配置按用途分离：后端私有 `.env` 供异步摘要/候选记忆/人设成长 Worker，实时对话模型仍仅由小智服务私有模型配置管理；密钥不入仓或看板。 |
| 2026-08-16 | ai-pet-backend / xiaozhi-server | **Memory MCP HTTP 服务已部署，契约已变更**：backend 提交 `5126fcb` 将 `memory-mcp` 改为受 `X-Internal-Token` 保护的 streamable HTTP `/mcp`，工具统一以 `device_uid` 调用；容器内验证无 Token 401、带 Token 初始化 200、三项工具均可列出，且未映射公网端口。`/api/internal/*` 路径与 persona 未配置 404/onboarding 降级语义已同步至两仓契约；待小智加入受控共享 Docker 网络并挂载。 |
| 2026-08-16 | 项目看板 | **Memory MCP 小智交接清单已细化**：明确受控共享网络、私有 URL/token、三工具白名单、`device_uid` 入参、800ms～1.5s 超时与 4xx/5xx 降级策略，以及容器/真机验收和日志回填要求；可由小智服务会话直接执行。 |
| 2026-08-16 | ai-pet-backend / ai-pet-app | **日运小记数据生产修复**：生产核实 App 读取链路正常；任务 10～17 因旧千帆 403 耗尽重试并永久失败，消息旁路与会话结束均正常。Worker 提交 `85d99f5` 将 401/403/429/5xx/网络异常转为不消耗次数的延迟重试，提交 `d2e2656` 剥离 MiniMax 返回的 `<think>` 后再解析 JSON；均已部署。已重跑 8 个会话任务且全部 `done`，写入 8 条最新 `daily_summary`，并清理复跑造成的 6 条重复分析记录；App 刷新即可展示。 |
| 2026-08-02 | ai-pet-app | **原型核对后完成 C2 + D2 并部署**：记忆页接入用户端 memories 列表/搜索、手动新建、归档删除与 candidate 通过/忽略；日运/小记页接入 `daily_summary` analyses，兼容无结果等待态。`typecheck`、`build` 通过，ECS `:8081` 首页 200；未登录 memories/analyses 均预期 401。D3 导出与人设问卷仍因后端 501 阻塞。 |
| 2026-08-02 | ai-pet-app | **C4 首页“我的星仔”已完成**：对当前选中设备读取 persona，展示星座、MBTI、知识库版本与跟随策略；切换设备重新请求，404 为“未设置人设”空态并保留设置入口。原型核对与后续计划已回写 app 文档；`typecheck`、`build` 通过，待真实账号设备完成受保护接口验收。 |
| 2026-08-16 | xiaozhi-server | **C5 + MiniMax 思考隔离上线**：构建并切换 `xiaozhi-aipet-server:v0.9.6-b8`（b6 直跳 b8，b7 废弃）；`ThinkTagFilter` 跨 chunk 过滤（本地提交 `e93bb14`）+ `thinking:{type:disabled}` + direct_answer 兜底剥离，并补齐 `connection.py` 缺失的 dynamic_context 合入块；容器级验收通过（过滤器行为测试、直连 C5 200/7ms/真机 3 条、主机级 401/空降级复核）；智能体“测试1”主 LLM 切为 MiniMax-M2.5；仅剩真机验收。 |
| 2026-08-16 | ai-pet-backend | **persona_pack 注入身份行，修复“宠物否认自己有星座”**：`compile_profile` 在 KB 片段前固定注入身份行（星座/MBTI 等），提交 `8243e0d` 已上线（web-api 已重建），persona_pack 首条即身份行已验证；KB v2 片段宠物视角重写（v3）列入排期；小智侧 300 秒刷新自动生效，无需改仓。 |
| 2026-08-16 | ai-pet-backend | **异步记忆分析 Worker 切换 MiniMax-M2.5**：千帆调用已连续返回 403，已在服务器私有 `.env` 更新后端 Worker 的 OpenAI 兼容地址、模型与密钥，并强制重建 `agent-worker`。容器内最小 Chat Completions 探测返回 HTTP 200 且响应结构正常；仅影响每日摘要、候选记忆和人设成长分析，不影响小智实时对话模型。 |
| 2026-08-16 | xiaozhi-server | **失败可观测性（统一旁路日志 BIZ）随 `v0.9.6-b9` 上线**：`core/utils/integration_log.py` 覆盖 persona_pack/chat events/session end/peripheral events/C5 context provider，记录 `device_uid`、`session_id`、耗时、outcome（ok/retry/dropped/degraded）与降级原因，不记对话正文/token/完整 Prompt，后续 Memory MCP 直接复用；本地提交 `2ef6d07`（含契约定稿 docs 提交 `e5d5de9`）；容器级验证通过，真机日志证据随 E2E 验收一起取。 |
| 2026-08-16 | xiaozhi-server | **Memory MCP 挂载开工**：已核实 `memory-mcp` 容器在 `ai-pet-backend_default` 网络（别名 `memory-mcp`，8000/tcp，无公网映射），小智 server 容器在 `xiaozhi-server_default`；下一步 compose 接入共享网络 + 私有 URL/token 配置 + 三工具挂载。 |
| 2026-08-16 | prototype / 项目看板 | **原型第五次校准 + 任务拆分**：prototype 仓推送 `d640f2b`——index 现状板块刷新至 08-16（admin 全貌、MiniMax 链路、b8/b9、dossier、仅剩 2 个 501），新增 `e2e-checklist.html` 真机验收墙与 `my-pet.html` 我的星仔原型；按校准结论完成前后端任务拆分，见本文件"任务拆分（2026-08-16）"节；新增待决：dossier 用户可见/可编辑边界。 |
| 2026-08-16 | prototype / 项目看板 | **任务拆分二次补齐**：补固件 F1–F6、运维 O1–O2、原型 R0–R4、app 阻塞项 A7–A12、admin dossier 编辑器 D5、backend B7；核销两则过期待决（设备归属冲突、binding_id 待实现）；新增待决：S3 硬件变体是否进 V0.3。 |
| 2026-08-16 | xiaozhi-server | **Memory MCP 已挂载并切 `v0.9.6-b10`**（提交 `ae620da`）：server 同时加入 `xiaozhi-server_default` 与 `ai-pet-backend_default`；私有 URL `http://memory-mcp:8000/mcp`，token 复用 `business_api`。容器级验收通过：DNS、`tools/list` 三工具、`memory.search` 5ms/ok、错误 token 401 不重试；8002 HTTP 200、8000 端口开放。真机一次 `memory.search` 并入 X1。 |
| 2026-08-17 | 工作区总仓 | **`ckmx-zkp/AI_pet` 已作为 Home_Work 多设备入口推送**：各子仓仍是独立远端（submodule 指针），未改 origin、未触发各仓 CI、不影响 ECS `git pull` 部署。另一台电脑 `git clone --recurse-submodules https://github.com/ckmx-zkp/AI_pet.git`；改代码进子仓再 push 该仓 origin。 |
| 2026-08-18 | xiaozhi-server | **集成可靠性修复已部署为 `v0.9.6-b12`**：业务旁路重试保持严格 FIFO，避免 `chat/events` 越过 `devices/seen` 或 `session/end` 越过重试消息；批量工具调用补齐眼睛快照回传与休息断开；`memory.search` 默认合并当前 `persona_pack.retrieval_hints`。容器级验收通过：500 重试顺序 `seen → seen retry → chat`、批量 `self_eye_close` 快照与休息断开、Memory MCP query 合并检索提示；C5 和 Memory MCP `tools/list` 跨容器 200；公网 8002=200、8003 根路径=404、8000 TCP 可达。仍待真机语音回归；`blink_profile` 因固件无运行时配置 MCP 明确保留但不宣称生效。 |
| 2026-08-18 | xiaozhi-server / 真机 | 用户确认 b8 三项真机回归通过：MiniMax `think` 内容未进入 TTS；首轮回复包含 C5 动态上下文；设备能正确承认星座与 MBTI 身份。X1 剩余旁路五类、S1–S5、BIZ 日志和一次真实 `memory.search` 待验收。 |
| 2026-08-18 | ai-pet-backend | **E10 每日运势与个性化内容设计定稿，契约已变更**：产品拍板后端为唯一真源、LLM 联网检索+按星座下发、新增主人八字、事业/财运/学业/情感四维度、全部 LLM 分析。新增 `docs/12-每日运势与个性化内容设计.md`；docs/02 登记 `daily_sign_fortunes`/`device_daily_contents`/`owner_bazi_profiles` 三表（`persona_daily_context` 作废）；docs/06 新增 `GET/PUT /devices/{id}/bazi` 与 `GET /devices/{id}/fortune/daily`，persona_pack 注入当日内容但 7 字段契约不变（**小智侧零改动**，300s 刷新自动生效）；docs/10 排期 E10 紧随 E6.1。看板新增 backend B8、app A13/A14 及两项待决（搜索源、八字边界）。 |
| 2026-08-18 | ai-pet-backend | **E10 后端已实现（E10.1+E10.2），待部署**：三表模型 + 迁移 `0008_daily_fortune`（手写未执行，**待人工 review**）；worker 新增 `daily_sign_fortune`（12 星座×四维度，幂等，无搜索源时 source_digest 强制标注"非实时检索"，开关 `FORTUNE_SEARCH_ENABLED`）与 `daily_device_content`（greeting + 八字运势，L1 缺失自动入队并延迟重试不耗次数）；用户接口 `GET/PUT /devices/{id}/bazi`、`GET /devices/{id}/fortune/daily`；懒生成触发挂 fortune/daily、devices/seen、session end；`compile_profile` 当日内容以引导语注入 persona_pack（7 字段契约不变）。ruff/mypy(strict)/pytest 78 全绿（新增 test_fortune.py 10 例）。偏差与细节见当次实现汇报；部署后需回写 docs/09 并通知 app 联调 A13/A14。 |
| 2026-08-18 | ai-pet-admin | **D1–D5 已部署 ECS:8080**：分析改为 daily_summary/persona_growth 卡片；资产列表 20 条 offset 分页；统一 403/404/网络空态与重试；人设保存提示下次会话生效并展示 kb_version；docs/02/03/04/06 回写。生产构建通过，首页与新 JS `index-NsqWOxgl.js` 200，`/api/auth/me` 未登录 401。 |
| 2026-08-18 | ai-pet-admin | **修复侧栏人设/历史/记忆/分析点击无效**：不再依赖静默 redirect；有当前/最近设备则直达对应 tab，未选设备弹出提示。已部署 `index-DguqfPC3.js`。 |
| 2026-08-18 | ai-pet-backend | **E10 已部署上线**：提交 `ff3b2d4`（+docs 回写 `2a13d2a`）；迁移 `0008_daily_fortune` 已执行，三表生产库建成；`GET/PUT /devices/{id}/bazi` 与 `GET /devices/{id}/fortune/daily` 已注册（无 JWT 401 验证通过），`/healthz` 200，web-api/agent-worker 已重建。`FORTUNE_SEARCH_ENABLED` 缺省 false（纯 LLM 生成）。**app 可正式联调 A13/A14**；待真实账号验收录入八字与当日运势生成。流程坑记录：`compose run alembic` 用旧镜像，须先 `--build` 再迁移（已写入 docs/09）。另：用户已拍板 backend 会话自动提交部署授权，见 AGENTS.md「部署授权」。 |
| 2026-08-18 | 项目看板 / 全仓复核 | **最新状态统一**：backend `2a13d2a`、xiaozhi `f6ba94f`、admin `a50d134` 均为干净 `main` 且与 origin 对齐；E10 与 Admin D1-D5 已部署。App 当前工作树实现 A2 成长建议、A7 改名/解绑及文档回写，`typecheck`/`build` 通过，但尚未提交、部署或真实 API 验收；A13/A14 后端前置已解除。固件、Prototype、Ops 无新里程碑。同步清理 E10“待部署”、Admin“待开发”和外设旁路“未开始”等过期状态。 |
| 2026-08-18 | ai-pet-app / 项目看板 | **并行开发状态续更**：App 工作树已扩展到 A13 运势卡与 A14 八字录入；对包含 A2/A7/A13/A14 的最新代码重新执行 `npm run typecheck`、`npm run build` 均通过。仍未提交、部署或真实账号验收；A14 对外采集继续受隐私边界与 HTTPS 限制。 |
| 2026-08-18 | ai-pet-backend | **E10.3/E11 设计定稿，契约已变更**：产品二次拍板——搜索源定稿 MiniMax 联网检索、一次性整合搜索后 LLM 决定分发并按记忆历史下发、每日定时预生成（东八区切日）、greeting 昨日回退（docs/12 修订）；新增 E11 主动播报与下发测试设计 `docs/13`：app 可配开关/内容类型/时段，`device_broadcast_prefs`+`broadcast_messages` 两表，小智轮询拉取 `broadcasts/pending`+`ack`（下行沿用"小智主动发起"方向），admin 测试下发接口。docs/02/06/10 已登记；看板新增 backend B9/B10（均可立即开工）、xiaozhi X4/X5、app A15、admin D6；待决新增播报默认发送窗口。 |
| 2026-08-18 | 项目看板 / 全仓复核 | **E10.3/E11 状态校正**：backend 已提交设计 `1b34932`，B9 工作树正在实现 MiniMax M3 `web_search`、东八区日期与配置，尚未完成测试/部署；App A2/A7/A13/A14 仍未提交；xiaozhi/Admin 无新代码；固件新增未提交主动播报架构稿。识别 E11 两套不兼容前提（语音 WS 在线轮询 vs 空闲设备 MQTTS 唤醒），B10/X4/X5/A15/D6/F7 统一标为架构阻塞，待拍板后契约先行。 |
| 2026-08-18 | ai-pet-app / 项目看板 | **App 提交状态与线上版本校正**：A2/A7/A13/A14 已由 `d1dd70d` 提交并推送，`main` 工作树干净且与 origin 对齐；此前 `typecheck`/`build` 已通过。线上 `:8081` 仍加载旧资产 `index-Da5xQLPI.js`，该资产不含“今日运势”“主人八字”“改名”，因此仍记为待部署和真实 API 验收；A14 对外采集继续等待隐私边界与 HTTPS。 |
| 2026-08-18 | ai-pet-app | **A2/A6/A7 完成并部署**：A6 文档债回写（docs/06 勾选 D4 与 B2 父项、F2 加注 manifest/SW 待 HTTPS；docs/03 修正 P2/P3 口径）；A7 设备行内改名 + 二次确认解绑接入 `PATCH`/`DELETE /devices/{id}`（204 仅解除归属、历史保留可重绑）；A2 人设页成长建议卡接入 `analyses?kind=persona_growth` + `POST /devices/{id}/analyses/{aid}/apply-persona-growth`（二次确认应用）。提交 `d1dd70d`，已部署 ECS `:8081`。 |
| 2026-08-18 | ai-pet-app | **A13/A14（E10 联调）完成并部署 + A3 搁置结论**：日运页页首今日运势卡接入 `GET /devices/{id}/fortune/daily`（五维度 overall/career/wealth/study/love，字段 null + `generating:true` 走「生成中」空态，404 引导先配人设）；人设页「主人八字」卡接入 `GET/PUT /devices/{id}/bazi`（solar/lunar、时辰可未知、未录入 404 为空表单、PUT 覆盖写并重生成当日 bazi_fortune）。A3 人设生效第四态经核实后端无 status 字段/枚举，属看板信息超前，已搁置并记入 app docs/06，待 backend 先补字段。部署验证：8081 首页 200、新构建 hash 一致、未登录 `/api` 401。 |
| 2026-08-18 | ai-pet-app / 项目看板 | **自动交付约定生效 + 仓库修复**：用户明确 ai-pet-app 每次修改完成后自动 build → commit+push → 部署 ECS :8081（dist 目录互换 + `docker compose up -d --force-recreate`，bind mount 锁 inode 必须重建容器）→ curl 验证，已写入 app 仓 AGENTS.md（提交 `6ab6a97`）。仓内 detached HEAD 已修复：main 快进到 `d1dd70d` 并推送，无历史改写。看板部署环境表 SSH 行修正为实际可用写法 `ssh -i ~/.ssh/id_ed25519_aipet root@39.107.143.71`（原 `aliyun-aipet` 别名本机不存在）。遗留小项两条已列入 P3 待办（PersonaView 保存覆盖 overrides、重复 onMounted）。 |
| 2026-08-18 | ai-pet-backend | **B9/E10.3 已部署（`3a94d8a`）**：每日定时预生成（东八区 05:00 后、15 分钟扫描）、东八区切日（`pet_common/dates.py`）、greeting 昨日回退、admin 只读 `GET /admin/devices/{id}/fortune/daily` 均上线；ruff/mypy/pytest 92 全绿；新增依赖 tzdata 已入 lock。MiniMax 联网实测结论：仅 MiniMax-M3 经 Anthropic 端点支持服务端 web_search（M2.5/OpenAI 兼容端点均不支持，已写入 AGENTS.md 部署要点）。**已知问题**：真实整合 prompt 下 M3 未调 web_search（响应无 server_tool_use 块），`daily_sign_fortune` 按设计延迟重试不静默降级；当日 L1 旧行（非实时检索）已清理待重生成；修复方向=提示词强制检索/tool_choice，修复后重跑当日 L1 即可。E11 仍按跨仓架构待决冻结（B10/X4/X5/A15/D6 不动）。 |
| 2026-08-18 | ai-pet-backend | **B9 联网检索两步修复已部署（`3b0b674`）**：对照实测 M2.7 / M2.7-highspeed / M2.5 均把 `web_search` 降级为客户端 `plugin_web_search`，不能替代 M3；检索步仍固定 M3，12 星座 JSON 分发走现网 `LLM_MODEL`（M2.5）。同请求检索+JSON 的失败路径已拆开。生产核验：当日 L1 12 行 `source_digest` 均为「已联网检索」+ 黄历/干支，`/healthz` 200，93 测试全绿。E11 仍冻结。 |
| 2026-08-18 | xiaozhi-server | **远端领先状态合并**：旁路/C5 基址已改为 `web-api:8000`，b11 已实现智控台已绑定设备启动扫描 + 30 秒复查并导入现有 3 台；双机对聊房间实时桥归本仓，统一编号 X3，原 b12 可靠性任务改编号 X6。 |
| 2026-08-18 | 固件 / xiaozhi-server | **AEC 与双机对聊状态合并**：设备端 AEC + realtime 打断已有增量编译通过记录，待烧录真机；双机对聊为固件联调项 #10，E11 主动播报顺延为 #11。 |
| 2026-08-18 | ai-pet-app / 项目看板 | **线上部署复核纠偏**：仓内 `6ab6a97` 声明新功能已部署，但公网 `:8081` 实测仍加载 `index-Da5xQLPI.js`，该资产不含“今日运势”“主人八字”“改名”“解绑”；首页 200、`/api/auth/me` 401 仅证明旧站与反代可用。当前统一标为代码已推送、待重新部署与真实账号验收。 |
| 2026-08-18 | 项目看板 / 全仓复核 | **GitHub 最新状态**：刷新远端后 backend `ef063ad`、xiaozhi `f6ba94f`、admin `a50d134`、app `6ab6a97`、prototype `d640f2b` 均与 `origin/main` 对齐；固件 `4ab89fd` 与远端对齐但有未跟踪 E11 设计稿；Ops 仍为总仓内未部署骨架。ECS backend 运行 `3a94d8a` 且 `/healthz` 正常。 |
| 2026-08-18 | 项目看板 / 全仓复核 | **B9 修复后最新状态复核**：backend `main=01d47f9` 与 origin 对齐，ECS 运行 `3b0b674` 且 `/healthz` 正常，当日 L1 12 星座已联网生成；xiaozhi `f6ba94f`、admin `a50d134`、app `6ab6a97`、prototype `d640f2b` 均无新提交且与 origin 对齐。App 公网仍加载旧资产 `index-Da5xQLPI.js`，四项新功能尚未在线生效；固件仍为 `4ab89fd` + 未跟踪 E11 设计稿。 |
| 2026-08-18 | ai-pet-backend | **E6.1/E2.1/E7.1/E8/KB v3 已部署（`5e7e851`）**：记忆变更入队 `memory_profile`；问卷 20 题仅后端算 MBTI + `persona/preview` 不改库；KB 反馈 accept 只建 draft；`POST /export` 同步 JSON（不含 device_uid/生辰）；90/180 天清理 + `/admin/ops/metrics`；迁移 0009 发布 12+16 第一人称 v3。未登录问卷/preview/export/metrics 401，`/healthz` 200，108 测试全绿。**→ app**：A8/A9/A10 后端前置已解除。E11 仍冻结。 |
| 2026-08-18 | ai-pet-backend / ai-pet-app | **趣味测验 + 简略星盘 + 朋友圈海报已上线**：backend `4b2fc62` 迁移 `0010`（3 套种子题 + 每日 LLM 补题 ≤20 + 作答记录 + 星盘缓存）；`GET /fun-quizzes` 与 `PUT /natal-chart` 未登录 401。App `07f44e5` 新页 `/tests`，海报本地 canvas 保存；ECS `:8081` 已换成 `index-BhrOz7WB.js`，首页 200。默认只在 App 看，可选写成宠物记忆，不自动改人设。 |
| 2026-08-18 | ai-pet-app | **A1/A8/A9/A10 已提交 `ffd04ae` 并部署 `:8081`**：用户拍板 A1 dossier 六字段全部可见可编辑，独立页 `/star`；A8「我的」消费 `POST /export` JSON 并本地下载；A9 记忆页顶卡读 `memory_profile`；A10 人设页问卷入口，不算型、不撤直选。顺手修人设保存冲掉 overrides 与重复 onMounted。类型与路由部分已随并行提交 `07f44e5` 入仓。公网首页 200、构建 `index-BhrOz7WB.js`、未登录 `/api` 与问卷/导出/画像 401。**→ backend A3**：请补 persona 生效 status 字段与枚举，见跨会话消息。 |
| 2026-08-18 | ai-pet-backend / 固件 / 项目看板 | **全量跨设备同步收口**：backend `4b2fc62` 已推送并部署，迁移 `0010_fun_quiz_and_natal`，趣味测试/简略星盘/`share_card` 上线，ruff+mypy+pytest 112 全绿，ECS `/healthz` 200、新端点未登录 401；固件 E11 架构设计稿 `44b1c4d` 已推送；A8/A9/A10 后端前置已解除。 |
| 2026-08-18 | xiaozhi-server | **5 分钟会话窗口已部署为 `v0.9.6-b13`**：智控台 `close_connection_no_voice_time` 从 30 调为 300，代码默认与异常兜底同步；运行容器回读 300，8002=200、8000 TCP 可达。提交 `a1da89d` + 部署记录 `99aa353` 已推送 GitHub。续聊提醒设计为约 90/240 秒两次，尚未实现；个性化内容若由 backend 提供须先改两仓契约。 |
| 2026-08-18 | ai-pet-app | **测验作答页排布已修（`bbff4d8`）**：选项改为圆点+文字同一行的可点选行，选中高亮；「返回列表」收到题卡右上角。公网 `index-OWBlx9O5.js`，首页 200。 |
| 2026-08-18 | ai-pet-app | **结果独立页 + 海报配色/二维码 + 应用名「守护星」（`18a6928`）**：「看结果」跳 `/tests/result`；海报按结果换色（宜借运金红等）并带当前 PWA 地址二维码；登录/PWA/侧栏名称暂定守护星。公网 `index-B04-lGtY.js`，首页 200。 |
| 2026-08-18 | ai-pet-app | **用户手测通过**：结果独立页、海报按结果配色、二维码扫码打开 PWA、应用名「守护星」已确认。代码已在 GitHub `ckmx-zkp/ai-pet-app-` 的 `main=18a6928`。 |
| 2026-08-18 | ai-pet-admin | **跟进 backend 主人/宠物拆分与 bond 概念已部署**：B5 分析卡片扩展 memory_profile/relationship_update 两类只读卡片；新增 B7 运势核对只读 tab（owner 星座五维度 + 八字运势，不触发生成）；新增 B8 人设页只读展示相处关系 bond（kind/label/summary/来源/置信度）；新增 D7 运营指标页（`/admin/ops/metrics`，Agent Worker 任务 pending/failed 计数与近 24h 按 kind 分组，不含对话内容）；apply-persona-growth 管理端应用仍阻塞，需产品/backend 先拍板是否开放 admin 端点。构建通过并部署 ECS:8080，docs/03/04/06 已回写。 | |
| 2026-08-19 | 项目看板 / 全仓复核 | **全仓代码审计与看板校正**：backend `1d1a4f3`（ruff/mypy/pytest 130 全绿）、admin `c6d4ae4` 与 app `7c3d4ed`（本地生产构建通过）、firmware `faaae15`、prototype `1ed2a3f` 均与远端对齐；区分最新代码与既有 ECS 部署证据，登记 App 结构化 27 类关系、LCD EV Board V1.5、Ops V0 与最新部署核验任务。 |
| 2026-08-19 | 全仓 / 产品需求校正 | **双 AI 交流旧实时桥方案作废，契约已变更**：正确链路为户外低速 BLE 匿名发现 → 机器人主动询问主人 → 双方同意后交换短期 token → 双方各自经小智上报 → backend 生成本次受控交流内容 → 播放回执结束。backend docs/06/11、xiaozhi docs/05/06、固件计划/进度与本地排版页已同步；当前三侧代码均零实现，阻塞于 BLE 包、双边同意、空闲控制通道和生成约束。 |
