---
id: infra.tooling
title: Development and Experiment Infrastructure
role: supporting
priority: P1
status: active
version: 4
updated_at: 2026-10-05
keywords: Docker|WSL|Conda|CUDA|torch|torchvision|container|容器|artifact|依赖|环境|QEMU|网络|代理|只读
imports: none
last_activity_at: 2026-10-04T17:31:22Z
---

# Goal

维护可复现、可调试且不会因环境漂移阻塞研究与学习的开发基础设施。

# Current Checkpoint

2026-10-05 BuddyGraph README 已按 AI 辅助背景调整：补充个人能力自测、项目与 MLIR 复用边界、分层简历模板、源码规模审计及精简方案；保留演示并扩展至 44 个问题。本轮只修改文档，未实施功能重构。

# Verified Milestones

- 已成功加载并运行过 Transform Dialect/Buddy-MLIR 相关 Docker 镜像和容器。
- 已确认论文核心 CPU 实验不刚需 GPU；不复现 Case Study 1 时无需下载对应模型。
- 已处理过失败 `docker load` 造成的 containerd blob/metadata 不一致，并认识到破坏性清理前必须先 `docker export`/`docker cp` 备份。
- 已在 nature-skills 目录创建虚拟环境并安装部分 MCP server requirements。
- 已掌握容器文件复制、tar.xz 解压和环境清理等基础操作。

# Doing

- 重新确认当前 Docker 容器、镜像和实验 artifact 的有效状态。
- 为论文实验记录准确的 MLIR/LLVM、Transform Dialect、BaCO、编译器和硬件版本。
- 重新构建干净的 Qwen/vLLM 环境，避免 base Python 与多个 pip/conda 环境混用。

# Next

1. 为 Transform Dialect 实验建立一条可重复执行的环境检查命令和版本清单。
2. 备份 Buddy-MLIR 容器中不可再生的修改与数据。
3. 固化 Docker 网络/DNS/代理配置。
4. 为 Qwen/vLLM 创建独立环境并锁定 Python、CUDA、torch、torchvision 和 transformers 版本。
5. 将环境状态写入对应项目仓库，而不是继续依赖聊天记录。

# Current Blockers

- 历史 Docker 容器曾出现只读、DNS/代理和 content-store 不一致问题；当前是否完全解决需要重新验证。
- Qwen 环境曾出现 `torchvision::nms` 不存在和依赖导入链错误，不能假定已经恢复。
- nature-skills 的 Chrome CDP 代理端口 3456 尚未完成端到端验证，自动下载能力可能不可用。

# Decisions

- 研究环境、推理环境和 Skill/MCP 环境必须分开，不在同一个 Python 环境中混装。
- 重要容器先备份再清理；不执行无法恢复的 Docker 重置操作。
- 环境状态使用“最后验证时间”表述，避免把历史运行状态误当成当前事实。

# Last-known Environment

| Area | Last-known state | Confidence |
|---|---|---|
| Host | Windows + WSL Ubuntu + Docker Desktop | confirmed |
| Transform artifact | 包含 MLIR/LLVM、Python、TensorFlow、BaCO；CPU-only 可进行核心复现 | confirmed from artifact discussion |
| Buddy-MLIR container | 曾存在约 35.8 GB 可写层和重要文件 | stale; recheck required |
| Qwen environment | torch/torchvision/transformers 曾不匹配 | confirmed historical blocker |
| nature-skills | venv requirements 已部分安装；CDP 未验证 | confirmed historical state |

# Recent Evidence

- 2026-10-04T17:31:22Z — 源码基线 2dee429；核心 16 文件 2324 物理行，代码/测试/配置/示例合计 49 文件 4034 行；git diff --check 通过，18 段 Bash 与基线一致，44 题连续，49 个本地链接/锚点有效。建议共享 Conv shape 与 Relu/Clamp scalar helper，广播 verifier 与 refinement 不能机械合并。本轮未重跑运行时测试，既有 14/14 与 GDB 结果属于此前助手验证；用户实际模块分工与独立掌握程度尚未核实。
- 2026-10-04T17:31:22Z — artifact: /home/jlq/project/buddygraph/README.md
- 2026-10-04T16:38:40Z — 项目源码基线 a2de7ff9a533b658b45c78846ab1c2a8ced27459，仅 README 为本次跟踪文件修改；40 个问答、48 个链接核验通过。复用 MLIR 21 与 Python 3.10.19；/home/jlq/.cache/buddygraph/build-debug 为 RelWithDebInfo、-O1 -g；gdb 停在 FoldBatchNormPattern::matchAndRewrite。主模型=7，Clamp=0.5 且 NaN 保留，signed-zero 为正零，LLVM IR 导出成功；generic/alloc 7→4、静态 alloc bytes 88→40。结果只证明环境与命令有效，不代表用户知识掌握程度。命令日志 /home/jlq/project/buddygraph/tmp/interview/readme-commands.log。
- 2026-10-04T16:38:40Z — artifact: /home/jlq/project/buddygraph/README.md
- 2026-10-02T16:20:47Z — 源码 /home/jlq/project/buddygraph @ a2de7ff9a533b658b45c78846ab1c2a8ced27459；构建 /home/jlq/.cache/buddygraph/build；MLIR/LLVM CMake 使用既有 llvm-cmake-relocated；Python 3.10.19 独立 venv，numpy 1.26.4、onnx 1.17.0；在 BuddyGraph .deps 中建立 MLIR Python 链接映射，解决旧 /buddy-mlir 路径及 Python 3.12 ABI 不匹配，未修改共享 LLVM；source tmp/env.sh 后可运行；git status 干净。
- 2026-10-02T16:20:47Z — artifact: /home/jlq/project/buddygraph/tmp/env.sh
