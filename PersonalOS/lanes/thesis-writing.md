---
id: thesis.writing
title: Thesis Writing
role: branch
priority: P1
status: active
version: 3
updated_at: 2026-07-16
keywords: 论文写作|摘要|绪论|章节|第三章|第四章|XeLaTeX|参考文献|GB/T 7714|西北工业大学
imports: research.kernel_aware_gemm#Decisions|research.kernel_aware_gemm#Verified Milestones
last_activity_at: 2026-07-16T03:29:04Z
---

# Goal

形成与真实实现和实验一致、符合西北工业大学 2025 版规范的硕士学位论文。

# Current Chapter

第三章已依据真实实验与实现重写完成，当前主线转入第四至第六章正文。第三章中心论点为：后端专属兼容性知识形成硬 Contract，来源标记的性能知识作为可由目标测量校准的软先验。

# Verified Milestones

- 已明确论文题目、研究问题、贡献边界和总体章节结构。
- 已多轮生成并修改中文摘要、绪论、研究背景及意义、贡献描述与实验定位。
- 已将西北工业大学研究生学位论文写作指南（2025版）设为默认格式约束。
- 已建立包含第三章、第四章图表和章节结构的论文草稿材料。
- 已形成 Kernel-aware GEMM 实验执行计划 v1.0。
- 已用 22 条 BLIS Fact、2 个真实 Contract、5 类 Rule、多来源冲突、f32/f64 路径验证和低预算校准结果重写第三章九节正文。
- 图 3-1 至图 3-4 已改为 R 可复现流程，提供 PDF/SVG/TIFF/PNG、源数据和机器 QA；29 项 Chapter 3 测试全部通过。
- 完整学位论文已由 XeLaTeX/Biber 成功生成 90 页 PDF；第三章 12 个物理页逐页抽样检查，无未解析引用、越界框或空白图。

# Doing

- 按最终证据目录重写第四至第六章，并统一摘要、绪论和结论边界。

# Next

1. 先重写第四章搜索空间、BaCO 与 Transform Dialect 链路；外部板端和跨主机结果返回后再补相应结论。

# Blockers

- K230 目前只有 ELF/反汇编证据，14900K/KF 只有可运行包；跨架构和跨主机性能结论等待外部实测。
- 第四至第六章旧稿尚未按最终证据目录重写，不能直接视为定稿。

# Decisions

- 论文具体内容默认给出 XeLaTeX 可编译片段。
- 采用正式简体中文和顺序编码制引用。
- 核心贡献表述围绕专家事实抽取、contract 兼容性和搜索空间生成，而不是“使用 Transform Dialect 优化 GEMM”。
- 实验结论强调相同预算下的搜索质量，不承诺全面超过成熟库。
- 硬兼容性 Contract 与软性能先验分离；软先验必须保留来源、范围和置信度，并允许在线反馈校准。
- 第三章只用后续实验验证表示与边界，不提前展开第六章完整调优器优劣结论。

# Knowledge State

| Topic | State | Evidence | Next evidence |
|---|---|---|---|
| 学位论文格式约束 | applied | NWPU 2025 模板完整编译为 90 页 PDF，第三章页面已检查 | 在后续章节重写后持续回归 |
| 摘要与绪论边界 | understood | 已多轮讨论目的、方法、结果和意义 | 结合最终实验结果重写定稿 |
| 方法与实验章节边界 | applied | 第三章已按 Fact/Contract/Rule、证据边界和贯穿案例落稿 | 用同一对象链重写第四至第六章 |

# Current Checkpoint

第三章已依据真实实验重写完成，R 图形流水线、29 项测试和整篇论文编译均通过。

# Recent Evidence

- 2026-07-16T03:29:04Z — /buddy-mlir/jlq/thesis/nwputhesis/content/thesis/graduate/chapter3.tex
- 2026-07-16T03:29:04Z — artifact: /buddy-mlir/jlq/thesis/nwputhesis/build/graduate.pdf
