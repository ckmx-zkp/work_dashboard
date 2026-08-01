# AI Pet 项目全景与进度（根协作文档）

> **本文档是所有子项目 AI 会话的第一信息源。** 各仓会话开工前先读本文档拉取全局上下文，再读 `AI-Pet协作看板.md`（日常状态流水）和本仓 `AGENTS.md`。
> 本文档记录**经代码核实的真实进度快照**（最近核实：2026-08-02，逐仓核对源码、提交记录与线上容器状态）。
> 日常状态变更仍记 `AI-Pet协作看板.md` / `AI-Pet固件联调看板.md`；当某仓完成阶段性里程碑后，回写本文档对应小节并更新"核实日期"。
> 密钥、密码不进本文档，只记位置。

## 一、体系架构一句话

固件（ESP32）⇄ xiaozhi-server（实时语音/OTA/MCP 路由）⇄ ai-pet-backend（业务真源：用户/设备/persona/记忆/KB）⇄ ai-pet-admin（运营管理台）+ ai-pet-app（用户端 PWA/桌面）。全部署在阿里云 ECS `39.107.143.71`（端口分配见协作看板，唯一真源）。

## 项目经理摘要（2026-08-02）

| 工作流 | 已交付 | 当前状态 | 下一步 / 主要风险 |
|---|---|---|---|
| 用户端 | 注册登录、绑定码认领、设备列表/切换、人设设置已上线 | 🟡 可做内测 | 对话历史待接入；正式发布还需域名与 HTTPS |
| 业务后端 | 账号、设备身份、人设、历史、管理端资产、分析/外设读取已上线 | 🟡 主链路基础已具备 | 记忆、知识库运营和 worker 分析产出尚未完成 |
| 管理台 | 资产查询、绑定码管理、人设、历史、外设与分析入口已上线 | 🟡 运营闭环建设中 | 记忆管理、知识库与分析数据产出仍待后端能力 |
| 设备与语音 | 真机激活、首轮语音、单眼情绪联动；人设刷新/外设回传已部署 | 🟡 待真机验收 | 需取得人设变更、消息回传、断开会话与眼睛动作的端到端证据 |

**本周优先级**：优先完成真实设备端到端验收（人设变更、转写回传、会话结束、眼睛状态）；再推进用户端历史体验和后端记忆/分析产出。当前全套线上容器正在运行；展示页、管理台、用户端均已部署，但用户端仍仅适合 HTTP 内测。

## 二、接口契约真源（改接口先改这里）

- 用户/内部 HTTP API：`ai-pet-backend/docs/06-HTTP-API规范.md`
- backend ↔ xiaozhi-server 集成：`xiaozhi-server/docs/05-与业务后端集成接口.md`
- 设备协议（WS/MCP/OTA）：`ESP32_XIAOZHI/xiaozhi-esp32/docs/`（上游文档，中英双语）

---

## 三、ai-pet-backend（业务后端）

**定位**：FastAPI monorepo（web-api / memory-mcp / agent-worker / persona-compiler + pet_common 共享层）。Python 3.11+ / SQLAlchemy 2.0 async / PG16+pgvector / 队列=PG SKIP LOCKED。GitHub `ckmx-zkp/ai-pet-backend`，分支 main，工作区干净。

**真实代码进度**（核实 2026-08-01）：

- ✅ **2026-08-02 新近上线**：设备绑定码认领（E1.1）、人设读写与默认人设素材（E2）、对话历史查询/删除（E4）；数据库迁移已到 `0005_devices_binding_id`，线上健康检查通过。

- ✅ **已实现并上线**：账号、用户设备、人设、脱敏历史、内部 persona_pack/chat events/peripheral/session end、管理端资产/绑定码/人设/历史/外设/分析读取，以及用户侧 analyses/peripheral 读取；worker 消费循环已就绪但**任务注册表仍为空**。
- ⬜ **待实现**：memories 及 Memory MCP 实库、管理端 KB、反馈审核、worker 分析产出与用户数据导出。
- ⬜ **memory-mcp 三工具（search/add/forget）是桩**，未接库——容器在跑但功能不可用。
- ⬜ E9 社交端点仅文档定稿（docs/11），代码零实现（计划内，V0.3）。
- 迁移 2 个：0001 建 14 表 + agent_tasks；0002 devices.user_id 可空。
- 测试 4 文件 26 用例，只覆盖已实现部分（auth 8 / devices 13 / compiler 2 / smoke 3）。

**文档清单**（docs/，全中文）：00 三仓边界 / 01 概述 / 02 数据模型 / 03 人设与星座KB / 04 记忆与脱敏 / 05 MCP与Worker / 06 HTTP API 契约 / 07 backlog / 08 技术栈决策 / 09 部署运维（端口表+上线记录）/ 10 开发计划（C0+E1~E9）/ 11 设备社交 V0.3。

**下一步**：以真机完成 persona_pack、设备首见登记、转写、会话结束和外设回传验收；再完成 memories/MCP、KB 运营与 worker 分析产出。

**出入提示**：docs/09 的"上线"仅指进程存活——memory-mcp 是桩、worker 无处理器，分析链路实际不可用。

## 四、xiaozhi-server（实时语音后台）

**定位**：上游 `xinnan-tech/xiaozhi-esp32-server` v0.9.6 快照二开。Python 语音服务 + Java manager-api + Vue2 manager-web，全模块 Docker Compose。GitHub `ckmx-zkp/aipet-xiaozhi-server-`。

**真实代码进度**（核实 2026-08-02）：

- 本地 git 仅 2 个提交（导入快照 + gitignore），**仓内代码/compose/脚本相对上游零二开**；`config.yaml` 仅填入 1 个 GLM key，`server.websocket` 在仓内仍是占位符。
- ⚠️ **仓内状态 ≠ 线上状态**：部署和配置修改（OTA 公网地址、auth_key、模型链路 GLM+豆包ASR+火山TTS）发生在服务器 `/opt/xiaozhi-server`，未回同步到本地仓。以 `AI-Pet协作看板.md` 和 `AI-Pet固件联调看板.md` 为线上状态真源。**后续会话在服务器上改配置后应回写本地仓或文档，避免漂移。**
- 线上（以看板为准）：4 容器 Up，端口 8000/8002/8003 公网验证通过，真机 `8c:fd:49:0c:a8:78` 激活+首轮对话已通。

**文档清单**：00 三仓边界与硬边界 / 01 概述（Must 清单）/ 02 部署OTA与设备接入 / 03 人设注入（首选会话开始 HTTP 拉 persona_pack）/ 04 设备MCP路由 / 05 与backend集成接口（契约）/ 06 任务清单 Epic A–D / 07 模型与采购清单（未提交）。

**下一步**：V0.2 集成——按当前字符串会话标识完成 persona_pack 拉取、chat/events 旁路写入、设备首见登记与会话结束回传；Memory MCP 待传输方式定稿。

## 五、ai-pet-admin（Web 管理台）

**定位**：运营/调试向管理台前端，纯前端。Vue3 + Vite + TS + Element Plus + Pinia + axios。GitHub `ckmx-zkp/ai-pet-admin`。已上线 `http://39.107.143.71:8080`（Nginx 同源反代 backend 8010）。

**真实代码进度**（核实 2026-08-02）：

- ✅ **B1.1+M2/M3/M4 部分能力已上线**：管理端资产查询与绑定码轮换、人设、脱敏历史、外设和分析读取均已部署；用户设备归属不再被管理台占用。

- ✅ **完整实现**：http 层（Bearer+401 拦截）、auth api/store（token 持久化）、路由守卫、登录/注册页、MainLayout（侧栏未实现项 disabled+标"后续"、admin 才显 KB、智控台外链）。
- 🟡 **骨架**：设备列表页（调真实接口，501 显可恢复空态，**无绑定功能**）；`api/devices.ts` 仅 list/get。
- ⬜ **空态/不存在**：设备详情页（纯 el-empty）；persona/messages/memories/analyses/peripheral/kb 全部无路由无页面。
- 即 docs/04 的 A1/A2/A3 **实际已完成**（仓内看板 docs/06 滞后，仍列待办）；B1 仅只读列表。

**文档清单**：00 协作边界 / 01 概述与IA / 02 页面交互规格（登录方式描述已过时，实际=login_name+密码）/ 03 API 清单 / 04 任务清单 A–D / 05 Codex 交接任务书 / 06 仓内看板 / 07 五仓定位 / `api-openapi.json` 契约快照（有 1 行未提交改动）。

**下一步**：完成记忆管理、知识库运营与分析结果消费；这些能力仍依赖后端 Memory MCP/worker/KB 实现。

## 六、ai-pet-app（用户端）

**定位**：手机 PWA + 桌面，用户自服务（登录/绑设备/人设/记忆/日运）。Vue3 应用骨架、账号流程与设备绑定码认领已完成并部署到 ECS `:8081`，GitHub `ckmx-zkp/ai-pet-app-`。

**已完成**：Vue3 + Vite + TS strict 工程、响应式导航、注册/登录与会话保持、`binding_id` 设备认领、设备列表/切换与人设设置；类型检查与生产构建通过，已部署内测。

**文档清单**：00 协作边界（可做/禁做清单）/ 01 用户场景（7 个 JTBD，成功标准=5 分钟注册→绑设备→定人设）/ 02 功能拆解 MoSCoW（V0.2 Must=登录+绑定+人设+历史+记忆审核）/ 03 IA 与 P0–P8 页面规格 / 04 跨端断点（<600 底Tab / 600–1024 Rail / >1024 侧栏）/ 05 API 映射与配网流程 / 06 任务清单 Epic A–F（全未勾选）/ 07 选型决策。

**AI 会话约定**（README 原文要点）：TS strict；写完自测通过再进下一功能；小步提交（一页面/端点一会话）；最简单实现优先；**先改 docs 再实现并回写**。

**下一步**：对话历史与首页摘要；记忆、分析、外设和数据导出仍需完整的后端业务产出；正式发布需域名与 HTTPS。

## 七、ESP32_XIAOZHI（固件 + 母文档）

**定位**：真仓库在 `xiaozhi-esp32/`（上游 v2.2.6 fork，GitHub `ckmx-zkp/Tboy_P4_xiaozhi`）；根目录为母文档库（PRD/赛道/市场/服务器需求，只读勿删）。目标硬件 Waveshare ESP32-P4-WIFI6-Touch-LCD-7B。

**真实代码进度**（核实 2026-08-02）：

- ✅ 已提交可跑：AI Pet 板型（I2C 音频、SPI GC9A01 眼屏、CSI 摄像头复用上游、BOOT 键）；`pet_eye_display` C1 整帧状态图（SetEmotion/SetGaze/BlinkOnce/SetClosed/SetAutoIdle 全实现）；**5 个眼睛 MCP 工具已注册**（look/blink/close/open/set_emotion）并真机语音验证；17 个 RGB565 资产（9 帧已嵌入）。
- 🟡 `main/pet/`（未提交）：视觉/行为**类型层设计稿**（pet_types、平台能力矩阵、K230 JSON 数据结构）——无解析器、无 UART 驱动、无 .cc、未被构建引用。
- ⬜ 未开始：第二只眼（CS=IO29 已规划）、WS2812 灯带、双舵机（引脚均未配）、K230 实物链路、MIPI/触摸/背光。
- 里程碑（AI_PET_PROGRESS_zh.md，07-18）：M0 基线✅ / M1 板型✅ / M2 双眼🟡 / M3 灯带舵机⬜ / M4 视觉⬜ / M5 体验层🟡。
- 已知问题：误唤醒偏高（端侧 WakeNet 阈值）、「休息」只闭眼不挂断（待用户拍板方案）——详见固件联调看板。
- 未提交改动：`AI_PET_PROGRESS_zh.md`、`sdkconfig.defaults`、`main/pet/`、美术交接文档、后续规划文档。

**文档清单**：`AI_PET_DEV_PLAN_zh.md`（设计总纲）/ `AI_PET_PROGRESS_zh.md`（**进度真源，改代码必更新**）/ `AI_PET_VISION_REALTIME_PLAN_zh.md` / `AI_PET_EYE_*`（资产规格与绘图管线）/ `2026-07-18_后续开发规划_需二次审阅.md` / `xiaozhi-esp32/docs/`（上游协议：mqtt-udp/websocket/mcp/blufi/custom-board/code_style）。

**下一步**：接第二只眼 → 状态机驱动眼睛 → WS2812+舵机 → K230 UART 视觉。

---

## 八、跨仓集成状态速查

详细表见 `AI-Pet协作看板.md`"集成点状态"。当前阻塞链：**backend 501 → xiaozhi V0.2 集成 / admin M2 / app V0.2 全在等**。P0 共识（2026-08-01）：C1 旁路写入 > A4 设备绑定（已完成）> B1+B3+B4 最小人设链。

## 九、看板分工（不要写错地方）

| 内容 | 写到哪里 |
|------|----------|
| 业务侧日常状态、部署环境、集成点、待决事项 | `AI-Pet协作看板.md` |
| 固件↔服务端联调状态、服务端待执行 S1–S5 | `AI-Pet固件联调看板.md` |
| 代码级真实进度快照、文档地图（本文档） | 里程碑达成后回写本文件 |
| 仓内任务流转 | 各仓 docs 内看板（admin docs/06、backend docs/10、固件 PROGRESS） |
