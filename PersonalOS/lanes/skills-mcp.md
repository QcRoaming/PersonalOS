---
id: skills.mcp
title: Skills, MCP, and Agent Tooling
role: supporting
priority: P2
status: active
version: 10
updated_at: 2026-07-15
keywords: Skill|Skills|MCP|Codex|Agent|Plugin|nature-skills|CDP|slock|IDEA|VSCode|personal-os
imports: none
last_activity_at: 2026-07-15T17:39:31Z
---

# Goal

能够独立安装、配置、验证和开发 Codex/ChatGPT Skills 与 MCP server，并用 PersonalOS 协调跨窗口、CLI、IDE 和多机器状态。

# Current Checkpoint

PersonalOS v2 已通过 PR `QcRoaming/PersonalOS-v1#1` 合并到 `main`，本机已快进到合并提交 `a0bcea7` 并成功执行 install 和 doctor。根指针、全局 Codex 指导与用户级 `personal-os` Skill 均指向权威目录；下一阶段是重启 Codex 表面，并完成真实第二账号和第二设备端到端验收。

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
- 已通过认证的本地 Git 将 v2 分支推送到远端，并创建到 `main` 的 PR `#1`。
- PR `#1` 已合并；本机 `main` 已同步，install 与 doctor 均通过，全局 Skill 内容与仓库版本一致。

# Doing

- 重启 Codex CLI 或 VS Code Codex 扩展，并在真实新账号、新设备上验证恢复流程。

# Next

1. 重启 Codex CLI 或 VS Code Codex 扩展，使其重建指令链。
2. 用另一个 ChatGPT 账号授权同一私有仓库并发送 START_HERE.md 中的固定启动消息。
3. 在第二台设备执行 clone、install、doctor，并完成一次 checkpoint/push/pull 往返。
4. 完成一次 VS Code 实验 refresh --sync-push，再验证网页 HANDOFF.md 能看到相同检查点。

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

# Recent Evidence

- 2026-07-15T16:08:39Z — 远程最新第六章实验注册表得到保留；11 个实验条目结构检查通过。
- 2026-07-15T16:08:39Z — personal_os.py 的 start、checkpoint、install、views、doctor 与 Git sync 闭环已验证。
- 2026-07-15T16:08:39Z — 10 项单元测试全部通过，另以本地 bare remote 验证 commit、rebase、push。
- 2026-07-15T16:08:39Z — artifact: QcRoaming/PersonalOS-v1:PersonalOS/START_HERE.md
- 2026-07-15T16:08:39Z — artifact: QcRoaming/PersonalOS-v1:PersonalOS/HANDOFF.md
- 2026-07-15T16:08:39Z — artifact: QcRoaming/PersonalOS-v1:PersonalOS/KNOWLEDGE.md
- 2026-07-15T16:11:37Z — GitHub App 读取远程最新提交成功，但创建 agent/personal-os-cross-account-v2 分支返回 403；已确定改用本地认证 Git 发布。
- 2026-07-15T17:26:55Z — 本地认证 Git 已推送 v2 分支并创建 PR `QcRoaming/PersonalOS-v1#1`；16 条实验全部可用，10 项测试通过。
- 2026-07-15T17:39:31Z — PR `#1` 已合并到 `main`；本机 install 和 doctor 通过，根指针与全局 Skill 安装结果一致。
