---
id: infra.tooling
title: Development and Experiment Infrastructure
role: supporting
priority: P1
status: active
version: 8
updated_at: 2026-10-18
keywords: Docker|WSL|Conda|CUDA|torch|torchvision|container|容器|artifact|依赖|环境|QEMU|网络|代理|只读
imports: none
last_activity_at: 2026-10-17T16:04:57Z
---

# Goal

维护可复现、可调试且不会因环境漂移阻塞研究与学习的开发基础设施。

# Current Checkpoint

2026-10-18 按用户限定九个文件（优先八个加 InferShapes.cpp）整理 BuddyGraph 可直接打印包，九份源码全文加框架图与目录组成 45 页 PDF，并提供十份分项 PDF、打印说明和来源清单。

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

- 2026-10-17T16:04:57Z — 新增 scripts/prepare_interview_print_pack.py；九个文件共 2284 行全文，9.5 pt 等宽字体、原始行号、长行续排、A4 纵向源码与横向框架图、PDF 书签和目录页码。提取九份 PDF 正文并忽略排版空白后与源代码逐字一致；A4 尺寸、嵌入字体、越界文本、来源哈希、框架图原样复制、文档链接和 git diff --check 通过。已目检目录、代码样张与全部 45 页缩略图。未添加 IR 或备用测试，未修改编译器源码、未重跑功能回归、未评定用户掌握程度。
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/打印文件夹/00_直接打印_九份源码与框架图.pdf
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/打印文件夹/打印说明.md
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/打印文件夹/来源清单.json
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/scripts/prepare_interview_print_pack.py
- 2026-10-17T15:40:06Z — 对照 importer、Pass 定义、BN folding、elementwise fusion、FullConversion、driver 和 E2E 源码核实五阶段流程，区分项目规则与框架复用，标明可选 shape refinement 和独立 runner。PDF 单页 A4 横向、字体嵌入、中文可检索、无越页文本；PNG 3508 像素宽；SVG XML、本地文档链接和 git diff --check 通过，并完成渲染目检。仅增加面试材料与绘图脚本、补充 README 链接，未修改编译器功能、未重跑回归、未评定个人掌握程度。
- 2026-10-17T15:40:06Z — artifact: /home/jlq/project/buddygraph/docs/interview/buddygraph-architecture.pdf
- 2026-10-17T15:40:06Z — artifact: /home/jlq/project/buddygraph/docs/interview/architecture.md
- 2026-10-17T15:40:06Z — artifact: /home/jlq/project/buddygraph/scripts/render_project_architecture.py
- 2026-10-05T07:41:55Z — 仅编辑根 README，功能源码及用户 docs/副本.md 未改。新广播示例 CPU 输出 23；换值输出 33、rank-1 广播输出 23、错误结果 shape 被 verifier 拒绝、动态结果直接 conversion 失败但 infer-shapes 后输出 23，均已执行。修正两张表是组织方式而非硬性要求、shape Pass 无通用单调细化/函数签名更新、use 与 user 区别、runner 参数及 benchmark 仅 off/all 有结构计数等细节。文档共 44 题、T1–T4、54 个有效本地链接；19 段 Bash 中原 18 段逐字保留；git diff --check 通过。本轮未重跑完整 14 项回归，也未评定用户个人学习进度。
