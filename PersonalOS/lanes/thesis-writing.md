---
id: thesis.writing
title: Thesis Writing
role: branch
priority: P1
status: active
version: 4
updated_at: 2026-10-17
keywords: 论文写作|摘要|绪论|章节|第三章|第四章|XeLaTeX|参考文献|GB/T 7714|西北工业大学
imports: research.kernel_aware_gemm#Decisions|research.kernel_aware_gemm#Verified Milestones
last_activity_at: 2026-10-17T06:02:14Z
---

# Goal

形成与真实实现和实验一致、符合西北工业大学 2025 版规范的硕士学位论文。

# Current Chapter

当前完整稿为六章：第三章 Contract 建模，第四章空间生成与系统实现，第五章实验评估，第六章总结。已生成 96 页无空白隔页阅读版和保留奇数页起排的 108 页印刷版。2026-10-17 新增 AI 编译器面试用 16:9 整体架构图（PNG/PDF/SVG）、约三分钟讲解稿、动态边界例子与源码入口。

# Verified Milestones

- 2026-10-17 已对论文整体架构与当前源码、冻结证据核对，生成 4K 16:9 面试图、嵌入字体 PDF、轮廓 SVG 和讲解稿；文字尺寸、字形、页面边界、本地链接与目视检查通过。
- 论文分页调整已完成：原 108 页中的 12 个无内容隔页移除，阅读版 96 页，另保留 108 页印刷版；硕士可行性评估与具体送审待办已落盘。

- 已明确论文题目、研究问题、贡献边界和总体章节结构。
- 已多轮生成并修改中文摘要、绪论、研究背景及意义、贡献描述与实验定位。
- 已将西北工业大学研究生学位论文写作指南（2025版）设为默认格式约束。
- 已建立包含第三章、第四章图表和章节结构的论文草稿材料。
- 已形成 Kernel-aware GEMM 实验执行计划 v1.0。
- 已用 22 条 BLIS Fact、2 个真实 Contract、5 类 Rule、多来源冲突、f32/f64 路径验证和低预算校准结果重写第三章九节正文。
- 图 3-1 至图 3-4 已改为 R 可复现流程，提供 PDF/SVG/TIFF/PNG、源数据和机器 QA；29 项 Chapter 3 测试全部通过。
- 完整学位论文已由 XeLaTeX/Biber 成功生成 90 页 PDF；第三章 12 个物理页逐页抽样检查，无未解析引用、越界框或空白图。

# Doing

- 准备 AI 编译器面试的论文讲解，按架构图解释 Contract、空间生成、Transform/packing/ABI 与验证边界。

# Next

1. 沿架构图演练三分钟介绍和一个动态 fringe 案例；论文定稿时统一 checker 耗时来源并补齐提交信息。

# Blockers

- 送审信息仍未齐全：学号、作者、导师、实际提交日期，以及对应阶段的委员会、科研情况和签名需要真实资料。
- 第五章 checker 耗时 1.257/8.69 微秒与现存 E2 汇总 1.183/6.112 微秒不一致，需确定冻结来源并统一。
- 附录的 artifact 归档获取方式仍待落实。既有 i9 与物理 K230 结果已完成，不再列为待运行硬件实验。

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

2026-10-17 完成 AI 编译器面试用论文整体架构图（4K PNG、PDF、SVG）与三分钟讲解稿；同步六章成稿、96/108 页双版本及已确认送审待办。

# Recent Evidence

- 2026-10-17T06:02:14Z — /home/jlq/project/thesis/documents/interview/architecture_layout_qa.json
- 2026-10-17T06:02:14Z — /home/jlq/project/thesis/documents/reviews/masters_feasibility_2026-10-03.md
- 2026-10-17T06:02:14Z — artifact: /home/jlq/project/thesis/documents/interview/thesis_architecture.pdf
- 2026-10-17T06:02:14Z — artifact: /home/jlq/project/thesis/documents/interview/talk_track.md
- 2026-07-16T03:29:04Z — /buddy-mlir/jlq/thesis/nwputhesis/content/thesis/graduate/chapter3.tex
- 2026-07-16T03:29:04Z — artifact: /buddy-mlir/jlq/thesis/nwputhesis/build/graduate.pdf
