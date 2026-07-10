---
id: thesis.writing
title: Thesis Writing
role: branch
priority: P1
status: active
version: 1
updated_at: 2026-07-10
keywords: 论文写作|摘要|绪论|章节|第三章|第四章|XeLaTeX|参考文献|GB/T 7714|西北工业大学
imports: research.kernel_aware_gemm#Decisions|research.kernel_aware_gemm#Verified Milestones
---

# Goal

形成与真实实现和实验一致、符合西北工业大学 2025 版规范的硕士学位论文。

# Current Chapter

第三章：高性能 GEMM 专家知识抽取、microkernel contract 建模与兼容性规则。当前应先完成可运行 schema/checker，再固化章节细节。

# Verified Milestones

- 已明确论文题目、研究问题、贡献边界和总体章节结构。
- 已多轮生成并修改中文摘要、绪论、研究背景及意义、贡献描述与实验定位。
- 已将西北工业大学研究生学位论文写作指南（2025版）设为默认格式约束。
- 已建立包含第三章、第四章图表和章节结构的论文草稿材料。
- 已形成 Kernel-aware GEMM 实验执行计划 v1.0。

# Doing

- 将第三章的专家事实、contract、规则和 checker 描述与实际文件 schema 对齐。
- 继续区分第二章相关工作、第三章方法、第四章实现与实验，避免贡献重复。

# Next

1. 完成 `expert_facts.yaml` 与 `microkernel_contracts.yaml` 后回填第三章字段定义和示例。
2. 完成 compatibility checker 后补充判定流程、伪代码和复杂度说明。
3. 完成 baseline 与 ours 的公共实验接口后固定第四章实验设置。
4. 建立正式 BibTeX 库并统一 GB/T 7714 引用键。
5. 对摘要、绪论和贡献表述进行一次全局一致性检查。

# Blockers

- 第三、四章不能领先于真实实现过多；当前主要阻塞来自研究主线的 schema、checker 和 baseline 尚未完成。
- 部分已生成论文材料需要在实现收敛后重新核验，不能直接视为定稿。

# Decisions

- 论文具体内容默认给出 XeLaTeX 可编译片段。
- 采用正式简体中文和顺序编码制引用。
- 核心贡献表述围绕专家事实抽取、contract 兼容性和搜索空间生成，而不是“使用 Transform Dialect 优化 GEMM”。
- 实验结论强调相同预算下的搜索质量，不承诺全面超过成熟库。

# Knowledge State

| Topic | State | Evidence | Next evidence |
|---|---|---|---|
| 学位论文格式约束 | applied | 已绑定 NWPU 2025 + XeLaTeX 输出规则 | 在完整章节编译中验证 |
| 摘要与绪论边界 | understood | 已多轮讨论目的、方法、结果和意义 | 结合最终实验结果重写定稿 |
| 方法与实验章节边界 | understood | 已明确第三章方法、第四章实现实验 | 用真实模块和数据对齐章节 |

