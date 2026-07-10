# PersonalOS Dashboard

> Generated view. Do not edit facts here; edit the owning lane and regenerate.

## Global

- Main lane: `research.kernel_aware_gemm`
- Last generated: 2026-07-10
- Canonical store: `persistent_files`
- Remote repository: `QcRoaming/personal-os`

## Lane Overview

| Lane | Role | Priority | Status | Current checkpoint |
|---|---|---:|---|---|
| `research.kernel_aware_gemm` | main | P0 | active | 建立第三章最小实现闭环，并复现 Transform Dialect 论文 §4.5 / Fig.10 型 baseline；保留原始调优闭环，只替换搜索空间生成层。 |
| `infra.tooling` | supporting | P1 | active | 需要把 Transform Dialect artifact、Qwen/vLLM 环境和 Skill/MCP 环境分别固化，避免继续在不明确的 base/conda/pip 状态上叠加依赖。 |
| `thesis.writing` | branch | P1 | active | 第三章：高性能 GEMM 专家知识抽取、microkernel contract 建模与兼容性规则。当前应先完成可运行 schema/checker，再固化章节细节。 |
| `learning.inference` | independent | P2 | active | 从 Transformers baseline 进入 vLLM 源码调试；框架学习尚未形成已验证的端到端修改实验。 |
| `skills.mcp` | supporting | P2 | active | PersonalOS v1 文件系统和 `personal-os` Skill 已完成并通过校验；已选择本地 Git 路线，下一步是首次推送并切换多机器权威源。 |
| `markets.ai_infrastructure` | independent | P3 | paused | 已完成 AI → 存储 → 半导体 → 光模块/CPO → 电力与基础设施的初步讨论；当前没有明确持续任务，支线暂停。 |

## Main-line Next Actions

1. 完成 R0：固定工具链并对 3 个 GEMM shape 执行生成、编译、运行、正确性校验和计时。
2. 完成 R1：复用或重建 §4.5 / Fig.10 型 generic baseline，保存原始 `search_space.json`。
3. 固定实验公共接口：`compile/run/measure/baco_adapter/result_logger`。
4. 创建第一版 `expert_facts.yaml`，要求包含 source library、source path/symbol/commit、condition、constraint level、evidence 和 confidence。
5. 创建第一版 microkernel contract，至少覆盖 dtype、ISA、MR/NR、KC multiple、packing、alignment、tail policy 和 calling convention。

## Active Blockers

- learning.inference: 最近一次 Qwen3.5 import 链路出现 `torchvision::nms` 与 torch/torchvision 兼容问题；当前环境状态需要重新验证。
- infra.tooling: 历史 Docker 容器曾出现只读、DNS/代理和 content-store 不一致问题；当前是否完全解决需要重新验证。
- research.kernel_aware_gemm: Transform Dialect artifact 中 §4.5 baseline 的准确入口、命令和参数对象尚未完成端到端确认。
- skills.mcp: 已确定私人仓库为 `QcRoaming/personal-os`。GitHub App 已选择该仓库，但授权页只包含 metadata 读取和 issues/pull requests 读写，不包含 repository Contents 写入；因此首次创建 `README.md` 返回 `Resource not accessible by integration`，仓库仍为空。
