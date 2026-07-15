# PersonalOS Dashboard

> Generated view. Do not edit facts here; edit the owning lane and regenerate.

## Global

- Main lane: `research.kernel_aware_gemm`
- State watermark: 2026-07-15T17:39:31Z
- Canonical store: `private_git`
- Remote repository: `QcRoaming/PersonalOS-v1`

## Lane Overview

| Lane | Role | Priority | Status | Last activity | Current checkpoint |
|---|---|---:|---|---|---|
| `research.kernel_aware_gemm` | main | P0 | active | 2026-07-15 | 第三章事实与规则、BLIS/OpenBLAS 多源冲突、第四章空间生成、第五章真实 BLIS direct/fringe/dynamic、Chapter 4-5 集成及第六章正式 B1-B4 均已有独立证据包。新增 CGO 扩展已完成 f64 6x8 Contract、真实在线反馈、Optuna TPE 同预算对照和多来源软先验消融；14900K/KF 固定 revision 离线包已生成。K230 与第二 x86 主机都等待外部硬件执行，在结果导入前不形成跨主机或跨架构性能结论。 |
| `infra.tooling` | supporting | P1 | active | 2026-07-10 | 需要把 Transform Dialect artifact、Qwen/vLLM 环境和 Skill/MCP 环境分别固化，避免继续在不明确的 base/conda/pip 状态上叠加依赖。 |
| `thesis.writing` | branch | P1 | active | 2026-07-10 | 第三章：高性能 GEMM 专家知识抽取、microkernel contract 建模与兼容性规则。当前应先完成可运行 schema/checker，再固化章节细节。 |
| `learning.inference` | independent | P2 | active | 2026-07-10 | 从 Transformers baseline 进入 vLLM 源码调试；框架学习尚未形成已验证的端到端修改实验。 |
| `skills.mcp` | supporting | P2 | active | 2026-07-15T17:39:31Z | PersonalOS v2 已通过 PR `QcRoaming/PersonalOS-v1#1` 合并到 `main`，本机已快进到合并提交 `a0bcea7` 并成功执行 install 和 doctor。根指针、全局 Codex 指导与用户级 `personal-os` Skill 均指向权威目录；下一阶段是重启 Codex 表面，并完成真实第二账号和第二设备端到端验收。 |
| `markets.ai_infrastructure` | independent | P3 | paused | 2026-07-10 | 已完成 AI → 存储 → 半导体 → 光模块/CPO → 电力与基础设施的初步讨论；当前没有明确持续任务，支线暂停。 |

## Experiment Registry

- Human-readable index: `EXPERIMENTS.md`
- Registered experiments: 16
- Fully available paths: 16/16
- Runner-maintained entries: 15/16
- Main-text eligible entries: 9/16
- Last refreshed: `2026-07-15T17:22:25Z`

## Main-line Next Actions

1. 在 14900K/KF 上运行 `x86_cross_host` 包并导入归档，检验低预算排序、f64 Contract 和相对 BLIS 性能的跨主机稳定性。
2. 在 K230 C908 大核上运行 `board/run_k230_suite.sh` 并导入 CSV，形成跨架构正确性与性能结果。
3. 用 Chapter 6 与 CGO 扩展报告撰写第六章，明确低预算校准优于随机、与 Optuna 无显著差异、naive 多源合并有害，以及 B2 仍是原正式评估最佳空间。

## Active Blockers

- learning.inference: 最近一次 Qwen3.5 import 链路出现 `torchvision::nms` 与 torch/torchvision 兼容问题；当前环境状态需要重新验证。
- infra.tooling: 历史 Docker 容器曾出现只读、DNS/代理和 content-store 不一致问题；当前是否完全解决需要重新验证。
- research.kernel_aware_gemm: 当前本机覆盖单线程、行主序 f32 6x16 与 f64 6x8 两个 Haswell Contract；任意 stride、更多后端 Contract 和跨主机泛化尚未验证。
- skills.mcp: 跨账号恢复仍需在第二个真实 ChatGPT 账号完成 GitHub 私有仓库授权和固定启动消息验收。
