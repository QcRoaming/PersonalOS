---
id: skills.mcp
title: Skills, MCP, and Agent Tooling
role: supporting
priority: P2
status: active
version: 5
updated_at: 2026-07-10
keywords: Skill|Skills|MCP|Codex|Agent|Plugin|nature-skills|CDP|slock|IDEA|VSCode|personal-os
imports: none
---

# Goal

能够独立安装、配置、验证和开发 Codex/ChatGPT Skills 与 MCP server，并用 PersonalOS 协调跨窗口、CLI、IDE 和多机器状态。

# Current Checkpoint

PersonalOS v1 文件系统和 `personal-os` Skill 已完成并通过校验；已选择本地 Git 路线，下一步是首次推送并切换多机器权威源。

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

# Doing

- 准备在两个新窗口中分别验证主线和推理支线隔离。
- 将下载包从 WSL 首次推送到 `QcRoaming/personal-os`，验证后切换多机器权威源。

# Next

1. 在新窗口使用 `继续主线` 验证 Skill 是否只加载 GEMM 支线。
2. 在另一窗口使用 `切换到推理框架支线` 验证上下文隔离。
3. 创建或授权私人 PersonalOS 仓库，并完成首次多机器同步。
4. 在本地 Codex CLI 和 IDE 中设置 `PERSONAL_OS_ROOT`。
5. 为 nature-skills 完成一个不依赖 CDP 的最小 Skill 验证，再处理自动下载链路。

# Current Blockers

- 已确定私人仓库为 `QcRoaming/personal-os`。GitHub App 已选择该仓库，但授权页只包含 metadata 读取和 issues/pull requests 读写，不包含 repository Contents 写入；因此首次创建 `README.md` 返回 `Resource not accessible by integration`，仓库仍为空。
- nature-skills 的 Chrome CDP 代理未启动，涉及浏览器自动下载的端到端功能未验证。
- 不同 Codex 表面对全局 Skill 和持久文件的可见性需要通过真实新窗口测试。

# Decisions

- PersonalOS 动态个人数据不打包进 Skill；Skill 只保存读取、路由和更新协议。
- 本地和多机器最终使用私人 Git 仓库作为唯一权威源，持久文件区作为 ChatGPT 跨窗口镜像。
- 不保存所有对话；只保存语义状态增量。
- 首次发布采用用户本地 Git 凭据；第三方 GitHub App 继续只用于其已授权的 issues/PRs 能力。

# Knowledge State

| Topic | State | Evidence | Next evidence |
|---|---|---|---|
| Skill 结构与触发 | understood | 已分析 nature-skills 与安装目录 | 创建并安装 personal-os Skill |
| MCP 注册与运行 | understood | 已明确 config 注册和独立进程关系 | 运行一个 MCP server 并调用工具 |
| 跨窗口状态协议 | applied | 已建立文件、路由、Skill 与更新协议 | 新窗口读写验证 |
| 多机器同步 | exposed | 已确定私人 Git 单一真源方案 | 绑定仓库并在第二台环境验证 |
