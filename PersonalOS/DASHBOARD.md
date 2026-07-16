# PersonalOS Dashboard

> Generated view. Do not edit facts here; edit the owning lane and regenerate.

## Global

- Main lane: `research.kernel_aware_gemm`
- State watermark: 2026-07-16T11:02:51Z
- Canonical store: `private_git`
- Remote repository: `QcRoaming/PersonalOS-v1`

## Lane Overview

| Lane | Role | Priority | Status | Last activity | Current checkpoint |
|---|---|---:|---|---|---|
| `research.kernel_aware_gemm` | main | P0 | active | 2026-07-16T11:02:51Z | 修复 14900 离线构建的 MLIRCAPIIR 依赖闭包：LLVM 预构建新增 MLIRCAPIIR 并校验 libMLIRCAPIIR.a，操作文档新增 new 解压目录说明和原地补编流程；重封装归档通过 277 文件校验与 4 项测试。 |
| `infra.tooling` | supporting | P1 | active | 2026-07-10 | 需要把 Transform Dialect artifact、Qwen/vLLM 环境和 Skill/MCP 环境分别固化，避免继续在不明确的 base/conda/pip 状态上叠加依赖。 |
| `thesis.writing` | branch | P1 | active | 2026-07-16T03:29:04Z | 第三章已依据真实实验重写完成，R 图形流水线、29 项测试和整篇论文编译均通过。 |
| `learning.inference` | independent | P2 | active | 2026-07-10 | 从 Transformers baseline 进入 vLLM 源码调试；框架学习尚未形成已验证的端到端修改实验。 |
| `skills.mcp` | supporting | P2 | active | 2026-07-15T17:58:29Z | PersonalOS v2.1 已通过 PR `QcRoaming/PersonalOS-v1#2` 合并到 `main`，本机已同步到合并提交 `d45146c`，install、doctor、归档检查、16 条实验注册表检查及 14 项测试全部通过。精确独立命令“导入”会启动隔离归档，并用覆盖级别与 SHA-256 防止把不完整上下文冒充完整备份；当前真实归档数为 0，尚待文本与语音窗口验收。 |
| `markets.ai_infrastructure` | independent | P3 | paused | 2026-07-10 | 已完成 AI → 存储 → 半导体 → 光模块/CPO → 电力与基础设施的初步讨论；当前没有明确持续任务，支线暂停。 |

## Experiment Registry

- Human-readable index: `EXPERIMENTS.md`
- Registered experiments: 16
- Fully available paths: 16/16
- Runner-maintained entries: 15/16
- Main-text eligible entries: 10/16
- Last refreshed: `2026-07-16T11:01:38Z`

## Conversation Archive

- Archived conversations: 0
- Latest archive: never
- Human-readable index: ARCHIVES.md

## Main-line Next Actions

1. 目标机执行 TARGET_MACHINE_OPERATION_GUIDE.md 第 8.6 节，确认 MLIRCAPIIR: OK 后重新运行 bootstrap_and_run.sh，并返回结果归档。

## Active Blockers

- learning.inference: 最近一次 Qwen3.5 import 链路出现 `torchvision::nms` 与 torch/torchvision 兼容问题；当前环境状态需要重新验证。
- infra.tooling: 历史 Docker 容器曾出现只读、DNS/代理和 content-store 不一致问题；当前是否完全解决需要重新验证。
- research.kernel_aware_gemm: 当前本机覆盖单线程、行主序 f32 6x16 与 f64 6x8 两个 Haswell Contract；任意 stride、更多后端 Contract 和跨主机泛化尚未验证。
- skills.mcp: 跨账号恢复仍需在第二个真实 ChatGPT 账号完成 GitHub 私有仓库授权和固定启动消息验收。
