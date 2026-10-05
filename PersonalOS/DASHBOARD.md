# PersonalOS Dashboard

> Generated view. Do not edit facts here; edit the owning lane and regenerate.

## Global

- Main lane: `research.kernel_aware_gemm`
- State watermark: 2026-10-05T07:41:55Z
- Canonical store: `private_git`
- Remote repository: `QcRoaming/PersonalOS`

## Lane Overview

| Lane | Role | Priority | Status | Last activity | Current checkpoint |
|---|---|---:|---|---|---|
| `research.kernel_aware_gemm` | main | P0 | active | 2026-07-27T07:49:46Z | 补齐论文第1至4章五幅流程图并完成96页全文排版QA |
| `infra.tooling` | supporting | P1 | active | 2026-10-05T07:41:55Z | 2026-10-05 按用户选择继续细化 BuddyGraph README：新增 2.5 广播 Add 逐函数数据追踪与可运行示例、2.6 换条件练习及六个核心文件精读动作；为 22 个核心问答补充例子、机制、取舍或第二层追问。 |
| `thesis.writing` | branch | P1 | active | 2026-07-16T03:29:04Z | 第三章已依据真实实验重写完成，R 图形流水线、29 项测试和整篇论文编译均通过。 |
| `learning.inference` | independent | P2 | active | 2026-07-10 | 从 Transformers baseline 进入 vLLM 源码调试；框架学习尚未形成已验证的端到端修改实验。 |
| `skills.mcp` | supporting | P2 | active | 2026-07-18T16:41:09Z | 完成 PersonalOS 仓库迁移对齐：GitHub 已将项目从 QcRoaming/PersonalOS-v1 重命名为 QcRoaming/PersonalOS，origin、ROUTES、README、START_HERE、AGENTS 与便携 Skill 均已更新到新权威地址。 |
| `markets.ai_infrastructure` | independent | P3 | paused | 2026-07-10 | 已完成 AI → 存储 → 半导体 → 光模块/CPO → 电力与基础设施的初步讨论；当前没有明确持续任务，支线暂停。 |

## Experiment Registry

- Human-readable index: `EXPERIMENTS.md`
- Registered experiments: 22
- Fully available paths: 22/22
- Runner-maintained entries: 21/22
- Main-text eligible entries: 16/22
- Last refreshed: `2026-07-24T06:03:58Z`

## Conversation Archive

- Archived conversations: 0
- Latest archive: never
- Human-readable index: ARCHIVES.md

## Main-line Next Actions

1. 执行最终送审版全篇一致性检查并冻结交付PDF

## Active Blockers

- learning.inference: 最近一次 Qwen3.5 import 链路出现 `torchvision::nms` 与 torch/torchvision 兼容问题；当前环境状态需要重新验证。
- infra.tooling: 历史 Docker 容器曾出现只读、DNS/代理和 content-store 不一致问题；当前是否完全解决需要重新验证。
- research.kernel_aware_gemm: 当前覆盖单线程、行主序 f32 6x16 与 f64 6x8 两个 Haswell Contract，并完成 i7-10750H/i9-14900 两主机验证；任意 stride、更多后端 Contract、线程扩展和普遍跨主机泛化仍未验证。
- skills.mcp: 跨账号恢复仍需在第二个真实 ChatGPT 账号完成 GitHub 私有仓库授权和固定启动消息验收。
