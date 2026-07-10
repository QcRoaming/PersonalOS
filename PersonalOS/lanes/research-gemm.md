---
id: research.kernel_aware_gemm
title: Kernel-aware GEMM Expert Schedule Space
role: main
priority: P0
status: active
version: 1
updated_at: 2026-07-10
keywords: GEMM|BLIS|OpenBLAS|libxsmm|MLIR|Transform Dialect|BaCO|microkernel|packing|tiling|vectorization|search space|compatibility checker
imports: infra.tooling#Current Blockers|thesis.writing#Current Chapter
---

# Goal

从 BLIS 为主、OpenBLAS 和 libxsmm 为补充的高性能 GEMM 库中抽取 microkernel shape、cache blocking、packing、vectorization、alignment 和 tail policy 等专家事实，将其抽象为带条件、硬约束、软先验和证据来源的规则；通过 microkernel contract 与 compatibility checker 自动生成 kernel-aware 的 MLIR Transform Dialect 调优空间，并交给 BaCO 等 tuner 搜索。

# Research Positioning

- Transform Dialect 解决“如何表达调度”。
- BaCO 解决“如何搜索参数”。
- 本课题解决“搜索什么、候选为什么合理、候选为何与目标 kernel 兼容”。
- 实验目标是在相同 autotuning budget 下证明专家空间比通用空间具有更高的有效候选率、高性能候选密度和收敛速度。
- 不把全面超过 BLIS/OpenBLAS/libxsmm 设为必要结论。

# Current Checkpoint

建立第三章最小实现闭环，并复现 Transform Dialect 论文 §4.5 / Fig.10 型 baseline；保留原始调优闭环，只替换搜索空间生成层。

# Verified Milestones

- 已跑通过 `linalg IR → Transform Dialect → lowering → CPU 可执行文件/ELF → 执行与性能测试` 的基础链路。
- 已形成课题定位、贡献边界、章节框架和实验核心假设。
- 已确定以 BLIS 为主要专家事实源。
- 已形成 `expert facts → microkernel contract → rules → candidate generation → compatibility check → BaCO` 总体链路。
- 已形成实验执行计划 v1.0（2026-07-10），包含 R0–R3、M0–M7、测量协议和指标。
- 已确定 baseline、手工缩小空间和专家自动生成空间共享 compile/run/measure/result 基础设施。

# Doing

- 梳理 BLIS packing、microkernel、MR/NR、MC/KC/NC 与数据布局的源码位置和证据形式。
- 准备复现 Transform Dialect §4.5 实验链路。
- 设计 `expert_facts.yaml`、`microkernel_contracts.yaml`、`expert_rules.yaml` 与 candidates JSONL。
- 将第三章理论描述约束到可实现的 schema、checker 和生成器。

# Next

1. 完成 R0：固定工具链并对 3 个 GEMM shape 执行生成、编译、运行、正确性校验和计时。
2. 完成 R1：复用或重建 §4.5 / Fig.10 型 generic baseline，保存原始 `search_space.json`。
3. 固定实验公共接口：`compile/run/measure/baco_adapter/result_logger`。
4. 创建第一版 `expert_facts.yaml`，要求包含 source library、source path/symbol/commit、condition、constraint level、evidence 和 confidence。
5. 创建第一版 microkernel contract，至少覆盖 dtype、ISA、MR/NR、KC multiple、packing、alignment、tail policy 和 calling convention。
6. 实现 compatibility checker，先覆盖 dtype、ISA、MR/NR、packing 和 tail policy。
7. 生成 BaCO 兼容的专家搜索空间并记录 raw/valid/pruned 数量。

# Current Blockers

- Transform Dialect artifact 中 §4.5 baseline 的准确入口、命令和参数对象尚未完成端到端确认。
- 最小论文版的目标 CPU/ISA 尚未最终固化；当前建议范围为 x86-64 FP32、AVX2 或 AVX-512。
- BLIS 专家事实的自动提取与人工校验边界尚未通过真实样本验证。

# Decisions

- 优先做单个静态 shape GEMM、单后端、单 dtype 的最小闭环，再扩展 batch GEMM、多 dtype 和多架构。
- 保留论文原始调优链路，采用插拔式搜索空间生成模块，而不是从头重建实验系统。
- 三条对比链路：A 原始 generic baseline；B 手工缩小空间；C 专家规则自动生成空间。
- microkernel 作为 contract/descriptor 建模，不默认把 `transform.to_library` 等同于任意 kernel 替换。
- 区分语义层融合与实现层支持；调度、codegen、microkernel/library epilogue 必须在正确层级匹配。
- 关键实验预算优先使用 25/50/100/200 等固定候选数，并报告 GFLOP/s、相对 BLIS 性能、有效率、剪枝率和收敛曲线。

# Knowledge State

| Topic | State | Evidence | Next evidence |
|---|---|---|---|
| Transform Dialect 调度链路 | applied | 已跑通基础 lowering 与执行链路 | 在 §4.5 artifact 上复现完整 tuning loop |
| GEMM blocking 层次 | understood | 已讨论 MC/KC/NC 与 MR/NR 的职责 | 对照 BLIS 配置与源码符号记录证据 |
| BLIS packing | understood | 已能解释沿 K 展开、micro-panel 与 stride 问题 | 运行 packing 代码并检查实际 buffer |
| microkernel contract | understood | 已形成字段集合与兼容性目标 | 实现可校验 schema 和真实 descriptor |
| BaCO 参数接口 | exposed | 已了解 parameterized Transform IR → tuner → measure 总链路 | 定位实际 JSON/adapter 入口并运行 |
| RVV 后端 | exposed | 长期方向已确定 | 最小 x86 闭环完成后再建立 RVV 实验线 |

# Completion Criteria

- 能从真实库源码生成带证据的专家事实。
- 能将事实编译为规则和 microkernel contract。
- 能自动生成并校验 BaCO 可消费的搜索空间。
- 在相同预算下完成 A/B/C 公平对比并报告搜索空间质量与性能结果。

