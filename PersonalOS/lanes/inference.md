---
id: learning.inference
title: LLM Inference and Quantization
role: independent
priority: P2
status: active
version: 1
updated_at: 2026-07-10
keywords: Qwen|DeepSeek|vLLM|SGLang|TensorRT-LLM|quantization|量化|GPTQ|AWQ|bitsandbytes|W4A4|W4A16|KV cache|attention mask|FlashAttention|Marlin|CUTLASS|Triton
imports: infra.tooling#Current Blockers
---

# Goal

在已经熟悉 Qwen 等模型结构的基础上，掌握主流大模型推理框架的请求生命周期、调度、KV cache、attention backend、量化层与低精度 kernel，并能通过断点和源码修改完成实验。

# Current Checkpoint

从 Transformers baseline 进入 vLLM 源码调试；框架学习尚未形成已验证的端到端修改实验。

# Verified Milestones

- 已理解 causal mask、sliding-window causal mask、随机 attention mask 与 BERT token mask 的区别和实现位置。
- 已明确 Qwen 系列配置默认不使用 sliding window；DeepSeek 讨论范围限定为 R1。
- 已理解 bitsandbytes 主要是 weight-only 量化；`bnb_4bit_compute_dtype` 控制计算浮点 dtype，不等于 activation 量化。
- 已明确 bitsandbytes/AWQ/GPTQ 通常属于 W4A16 或 W4ABF16，而非通用 W4A4。
- 已理解反量化通常位于 CUDA kernel 内部，不一定显式生成完整高精度权重矩阵。
- 已讨论 vLLM scheduler、continuous batching、KV cache block 和 prefill/decode 总体链路。

# Doing

- 准备建立可断点进入 Qwen/Transformers 模型和量化层的最小推理脚本。
- 准备按请求生命周期阅读 vLLM 源码。

# Next

1. 固定一个可运行的 Transformers text-generation baseline，并验证 Qwen3.5 环境。
2. 源码方式安装 vLLM，跑通单请求 prefill/decode。
3. 在 scheduler、KV cache manager、model runner 和 attention backend 添加日志或断点。
4. 修改一个小行为并对比结果，形成首个源码实验闭环。
5. 再学习 SGLang、TensorRT-LLM 和 kernel 层 FlashAttention/Marlin/CUTLASS/Triton。

# Current Blockers

- 最近一次 Qwen3.5 import 链路出现 `torchvision::nms` 与 torch/torchvision 兼容问题；当前环境状态需要重新验证。
- GPU、CUDA、Python、torch、torchvision 与 transformers 的最终组合尚未固化。
- vLLM 源码调试仓库和可重复启动命令尚未记录为已完成。

# Decisions

- 学习顺序：Transformers baseline → vLLM → SGLang → TensorRT-LLM → kernel 层。
- 实操方式：跑通请求 → 打日志/断点 → 修改源码 → 做对比实验。
- Blackwell 可优先研究 NVFP4；A100/H100/4090 更现实的通用路线是 W4A16、AWQ、GPTQ 或 FP8，而不是假设所有硬件都支持 W4A4。
- 本支线默认不影响 GEMM 论文主线；只有明确研究低精度 GEMM contract 时才建立依赖。

# Knowledge State

| Topic | State | Evidence | Next evidence |
|---|---|---|---|
| Qwen attention/mask | understood | 已分析 causal、SW 与随机 mask 代码 | 在真实 forward 调用链断点验证 |
| Weight-only quantization | understood | 已区分 W4A16 与 W4A4、compute dtype 与 activation quantization | 调试一个量化 Linear kernel 调用 |
| Transformers 推理链路 | understood | 已形成 quickstart 级调用流程 | 固化可运行环境并逐层断点 |
| vLLM 调度与 KV cache | exposed | 已讨论 scheduler 和 continuous batching | 运行源码并打印真实状态 |
| SGLang/TensorRT-LLM | exposed | 已确定学习顺序 | 完成 vLLM 首个修改实验后开始 |

