---
id: skills.mcp
title: Skills, MCP, and Agent Tooling
role: supporting
priority: P2
status: active
version: 14
updated_at: 2026-07-18
keywords: Skill|Skills|MCP|Codex|Agent|Plugin|nature-skills|CDP|slock|IDEA|VSCode|personal-os
imports: none
last_activity_at: 2026-07-18T16:41:09Z
---

# Goal

能够独立安装、配置、验证和开发 Codex/ChatGPT Skills 与 MCP server，并用 PersonalOS 协调跨窗口、CLI、IDE 和多机器状态。

# Current Checkpoint

完成 PersonalOS 仓库迁移对齐：GitHub 已将项目从 QcRoaming/PersonalOS-v1 重命名为 QcRoaming/PersonalOS，origin、ROUTES、README、START_HERE、AGENTS 与便携 Skill 均已更新到新权威地址。

# Verified Milestones

- 已理解 Skill 是包含 `SKILL.md`、references、scripts、assets 的完整目录，而不是单个提示词文件。
- 已理解 Codex 通过 name/description 发现 Skill，再按需读取正文和资源。
- 已理解 MCP server 是独立后端，必须注册到 Codex 配置；`SKILL.md` 不会自动注册或启动 MCP。
- 已尝试安装和配置 nature-skills，并在容器虚拟环境中安装部分 requirements。
- 已安装用于文档状态原型和私人仓库接入的连接能力。
- 已创建 6 条相互隔离的 PersonalOS Lane、全局画像、路由表、自动总览、并发 delta 协议和本地校验脚本。
- 已创建并安装 `personal-os` Skill，覆盖 ChatGPT 与 Codex 的支线路由、更新边界和冲突处理。
- 已将 PersonalOS v1 保存为跨窗口持久文件集。
- 已确定本地 Git 为首次发布方式，绕过第三方 GitHub App 缺少 Contents 写权限的问题。
- 已完成 PersonalOS v2：新增 START_HERE、HANDOFF、KNOWLEDGE，以及 start/checkpoint/views/sync/doctor/install 命令。
- 已在最新的 16 条实验注册表、CGO 扩展和跨平台待运行状态上完成兼容验证，没有回退研究主线。
- 已按 Codex 当前发现规则将全局协议安装到 ~/.codex/AGENTS.md，并将用户级 Skill 安装到 ~/.agents/skills/personal-os/。
- PR `#1` 已合并；本机 `main` 已同步，v2 install 与 doctor 均通过。
- 已新增独立会话归档注册表与 ARCHIVES.md，原始会话不会流入 Lane、个人画像、HANDOFF 或知识索引。
- 已实现 ChatGPT active branch 还原、在“导入”触发消息前截断、语音转写标记、显式音频复制和完整性哈希校验。
- v2.1 已在保留 16 条实验记录的前提下通过归档检查、结构检查和全部 14 项测试。
- PR `#2` 已干净合并；本机 v2.1 install 与 doctor 通过，全局协议和 Skill 已更新。

# Doing

- 在真实文本窗口和语音窗口验证导入触发、会话选择、触发点截断与覆盖级别。

# Next

1. 重启 Codex CLI 或 VS Code Codex 扩展，并在真实文本/语音窗口、第二账号和第二设备完成端到端验收。

# Current Blockers

- 跨账号恢复仍需在第二个真实 ChatGPT 账号完成 GitHub 私有仓库授权和固定启动消息验收。
- 多设备恢复仍需在第二台真实设备执行 clone、install、doctor 和一次 checkpoint/push/pull 往返。
- 网页端不能读取 VS Code 容器中未提交的原始实验文件；必须先同步 PersonalOS 元数据，原始证据还需单独授权其项目仓库或存储。
- nature-skills 的 Chrome CDP 代理未启动，涉及浏览器自动下载的端到端功能未验证；该问题与 PersonalOS v2 同步闭环独立。

# Decisions

- PersonalOS 动态个人数据不打包进 Skill；Skill 只保存定位、读取、路由、更新和同步协议。
- 本地、多机器和多账号统一使用私人 Git 仓库作为唯一权威源；聊天记忆、Library 和持久文件只可作为非权威缓存。
- 不保存所有对话；只保存语义状态增量。
- 新账号不依赖旧账号安装的 Skill：GitHub 授权加 START_HERE.md 是最小恢复路径。
- 自动 Git push 必须显式启用；默认实验刷新只更新本地元数据和生成视图。

# Knowledge State

| Topic | State | Evidence | Next evidence |
|---|---|---|---|
| Skill 结构与触发 | understood | 已分析 nature-skills 与安装目录 | 创建并安装 personal-os Skill |
| MCP 注册与运行 | understood | 已明确 config 注册和独立进程关系 | 运行一个 MCP server 并调用工具 |
| 跨窗口状态协议 | applied | 已实现确定性 Handoff、单 Lane 启动和结构化检查点并通过测试 | 真实网页新窗口验收 |
| 多机器同步 | applied | 已实现 Git commit-rebase-push 闭环并用本地远程仓库验证 | 第二台真实设备验收 |
| 跨账号恢复 | applied | 已实现 GitHub 授权加 START_HERE 固定启动协议 | 第二个 ChatGPT 账号端到端验收 |
| 会话与语音归档 | applied | 已实现 exact_export/provided_transcript/visible_context_only、语音转写/音频区分和 4 项归档测试 | 真实 ChatGPT 数据导出与语音窗口验收 |

# Recent Evidence

- 2026-07-18T16:41:09Z — 旧地址推送成功时 GitHub 返回仓库迁移提示；新地址 refs/heads/main 与本地已推送提交一致。
- 2026-07-18T16:41:09Z — artifact: QcRoaming/PersonalOS:README.md
- 2026-07-18T16:41:09Z — artifact: QcRoaming/PersonalOS:PersonalOS/ROUTES.md
- 2026-07-18T16:41:09Z — artifact: QcRoaming/PersonalOS:PersonalOS/START_HERE.md
- 2026-07-18T16:37:53Z — 结构检查、doctor、17 条实验注册表、0 条真实会话归档和 14 项单元测试均通过；独立 README 读者复测结论为可发布。
- 2026-07-18T16:37:53Z — artifact: QcRoaming/PersonalOS:README.md
- 2026-07-18T16:37:53Z — artifact: QcRoaming/PersonalOS:PersonalOS/README.md
- 2026-07-18T16:37:53Z — artifact: QcRoaming/PersonalOS:PersonalOS/START_HERE.md
- 2026-07-15T16:08:39Z — 远程最新第六章实验注册表得到保留；11 个实验条目结构检查通过。
- 2026-07-15T16:08:39Z — personal_os.py 的 start、checkpoint、install、views、doctor 与 Git sync 闭环已验证。
