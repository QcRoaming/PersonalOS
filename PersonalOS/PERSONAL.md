---
id: personal.profile
version: 2
updated_at: 2026-07-16
---

# Personal Profile

## Communication and Collaboration

- 默认使用中文回答。
- 学习编译器、MLIR、推理框架和系统实现时，优先从具体代码、源码调用链、驱动链路和底层机制解释。
- 偏好小型代码示例、逐行说明、完整流程和结构化总结。
- 论文讨论采用同级合作者模式；不默认认可既有设想，应直接指出创新性、实验说服力、风险和修改方案。
- 日常说明应能较快读懂，避免只有概念或过度复杂的堆砌。

## Long-term Direction

- 当前唯一 P0 主线：面向 MLIR Transform Dialect 的 Kernel-aware GEMM 专家调度搜索空间生成。
- 长期学习领域：MLIR、LLVM、AI 编译器、高性能 GEMM、CPU/RVV 后端、推理框架与低精度 kernel。
- 当前研究目标不是重写或全面超过 BLIS/OpenBLAS/libxsmm，而是解决自动调优系统“搜什么以及为什么这样搜”。

## Thesis Output Contract

- 论文具体内容默认输出为 XeLaTeX 可直接编译的 LaTeX 片段。
- 默认遵循《西北工业大学研究生学位论文写作指南（2025版）》。
- 正文使用正式简体中文；章节使用 `\\chapter{}`、`\\section{}`、`\\subsection{}`。
- 引用采用顺序编码制和 GB/T 7714 兼容形式，优先使用 `\\cite{}`。
- 图、表、公式按章编号；表格默认三线表。

## Working Style

- 偏好从最小闭环开始，再扩展 dtype、架构、调优器和实验规模。
- 实操学习以“跑通请求或程序 → 打日志和断点 → 阅读调用链 → 修改源码 → 对比实验”为主。
- 对环境、Docker、依赖和源码问题需要可执行命令及原因说明。

## Environment Context

- 常用环境为 Windows + WSL Ubuntu + Docker Desktop。
- 同时使用 ChatGPT、Codex CLI 和 IDE；目标是多机器共享同一 PersonalOS 状态。

## Conversation Archive Contract

- 当用户消息的全部内容恰好为“导入”时，显式请求备份该窗口中触发消息之前的全部对话。
- 文本对话与语音对话都适用；语音默认保存聊天历史中的转写，只有用户另外提供音频文件时才保存原始音频。
- 原始会话只能进入 archives/conversations/，不得自动改变 Lane、知识阶段或个人画像。
- 没有完整数据导出或用户提供的逐字稿时，必须标记为 visible_context_only，不得声称完成了完整备份。

## Profile Update Policy

- 只有用户明确表达或跨多次对话稳定出现的事实才能写入本文件。
- 单次提问、临时兴趣、模型推断和短期环境状态不得写入本文件。
- 新旧事实冲突时，较新的用户明确表达优先；重大变化需确认。

