---
id: infra.tooling
title: Development and Experiment Infrastructure
role: supporting
priority: P1
status: active
version: 9
updated_at: 2026-10-18
keywords: Docker|WSL|Conda|CUDA|torch|torchvision|container|容器|artifact|依赖|环境|QEMU|网络|代理|只读
imports: none
last_activity_at: 2026-10-17T16:15:07Z
---

# Goal

维护可复现、可调试且不会因环境漂移阻塞研究与学习的开发基础设施。

# Current Checkpoint

2026-10-18 按用户纠正恢复最初打印范围：BGraphOps.cpp、import_onnx.py、BGraphToLinalg.cpp 仅关键节选，其余六个文件全文；覆盖原 45 页包，现为 30 页。

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

- 2026-10-17T16:15:07Z — 打印脚本为三个长文件配置显式原始行号范围及起始内容校验；分别收录 82/527、219/458、202/461 行。总计打印源码 1341 行；省略位置用灰色提示条标明，保留原始行号、等宽字体和续排。importer 明确仅保留公共 dispatch 与 Add/Relu 等分支。九份分项 PDF 与原合集路径均已更新，目录、README、打印说明和来源清单同步修正。按各范围提取 PDF 正文并忽略排版空白后与原代码一致；A4、字体嵌入、越界检查、30 页与 11 书签、链接和 git diff --check 通过，并目检目录和节选样张。编译器源码未改，未重跑功能回归。
- 2026-10-17T16:15:07Z — artifact: /home/jlq/project/buddygraph/打印文件夹/00_直接打印_九份源码与框架图.pdf
- 2026-10-17T16:15:07Z — artifact: /home/jlq/project/buddygraph/打印文件夹/打印说明.md
- 2026-10-17T16:15:07Z — artifact: /home/jlq/project/buddygraph/scripts/prepare_interview_print_pack.py
- 2026-10-17T16:04:57Z — 新增 scripts/prepare_interview_print_pack.py；九个文件共 2284 行全文，9.5 pt 等宽字体、原始行号、长行续排、A4 纵向源码与横向框架图、PDF 书签和目录页码。提取九份 PDF 正文并忽略排版空白后与源代码逐字一致；A4 尺寸、嵌入字体、越界文本、来源哈希、框架图原样复制、文档链接和 git diff --check 通过。已目检目录、代码样张与全部 45 页缩略图。未添加 IR 或备用测试，未修改编译器源码、未重跑功能回归、未评定用户掌握程度。
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/打印文件夹/00_直接打印_九份源码与框架图.pdf
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/打印文件夹/打印说明.md
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/打印文件夹/来源清单.json
- 2026-10-17T16:04:57Z — artifact: /home/jlq/project/buddygraph/scripts/prepare_interview_print_pack.py
- 2026-10-17T15:40:06Z — 对照 importer、Pass 定义、BN folding、elementwise fusion、FullConversion、driver 和 E2E 源码核实五阶段流程，区分项目规则与框架复用，标明可选 shape refinement 和独立 runner。PDF 单页 A4 横向、字体嵌入、中文可检索、无越页文本；PNG 3508 像素宽；SVG XML、本地文档链接和 git diff --check 通过，并完成渲染目检。仅增加面试材料与绘图脚本、补充 README 链接，未修改编译器功能、未重跑回归、未评定个人掌握程度。
