---
id: personal.routes
version: 7
updated_at: 2026-07-16
main_lane: research.kernel_aware_gemm
canonical_store: private_git
git_repository: QcRoaming/PersonalOS-v1
repository_subdir: PersonalOS
sync_method: git_checkpoint
web_access: github_connector
bootstrap_entry: START_HERE.md
conversation_archive: opt_in_private_git
---

# Context Routes

## Lane Map

| Lane | Role | Priority | Status | File | Parent |
|---|---|---:|---|---|---|
| `research.kernel_aware_gemm` | main | P0 | active | `lanes/research-gemm.md` | — |
| `thesis.writing` | branch | P1 | active | `lanes/thesis-writing.md` | `research.kernel_aware_gemm` |
| `infra.tooling` | supporting | P1 | active | `lanes/infra.md` | — |
| `learning.inference` | independent | P2 | active | `lanes/inference.md` | — |
| `skills.mcp` | supporting | P2 | active | `lanes/skills-mcp.md` | — |
| `markets.ai_infrastructure` | independent | P3 | paused | `lanes/markets.md` | — |

## Context Firewall

- 每次对话默认只选择一个活动 Lane。
- `PERSONAL.md` 的稳定偏好可作用于所有 Lane。
- 独立 Lane 之间默认不共享任务、知识状态或推荐结果。
- 跨 Lane 只传递明确声明的依赖小节，不传递整份文件。
- 没有匹配到 Lane 的一次性问题归为 `adhoc`，不持久化。
- 原始会话归档位于 `archives/conversations/`，不属于任何 Lane；只有用户明确要求检查或恢复时才读取。

## Explicit Dependencies

| Consumer | Provider | Imported scope | Reason |
|---|---|---|---|
| `research.kernel_aware_gemm` | `infra.tooling` | Current Blockers | 实验依赖 Docker、MLIR、BaCO 与硬件环境 |
| `research.kernel_aware_gemm` | `thesis.writing` | Current Chapter | 实现进度需要与第三、四章表述一致 |
| `thesis.writing` | `research.kernel_aware_gemm` | Decisions, Verified Milestones | 论文内容必须受真实实现和实验约束 |
| `skills.mcp` | all lanes | File locations only | Skill 负责路由，不导入业务内容 |

## Routing Hints

- GEMM、BLIS、OpenBLAS、libxsmm、Transform Dialect、BaCO、microkernel、packing、tiling、search space、compatibility checker → `research.kernel_aware_gemm`
- 摘要、绪论、章节、论文格式、XeLaTeX、参考文献、写作 → `thesis.writing`
- Docker、WSL、Conda、CUDA、依赖、容器、artifact、环境错误 → `infra.tooling`
- Qwen、vLLM、SGLang、TensorRT-LLM、量化、GPTQ、AWQ、W4A4、KV cache、attention mask → `learning.inference`
- Skill、MCP、Codex 配置、Agent、nature-skills、CDP → `skills.mcp`
- 股票、AI 产业链、存储、半导体、光模块、CPO、电力 → `markets.ai_infrastructure`

## Store Resolution

1. 本地 CLI/IDE：优先读取环境变量 `PERSONAL_OS_ROOT`，其次读取 `~/.personal-os-root` 指向的私人仓库工作副本。
2. 当前目录或父目录包含本文件时：使用该目录，但工作前先与权威远程仓库快进同步。
3. ChatGPT 网页或新账号：通过已授权的 GitHub 连接器读取默认分支中的 `START_HERE.md` 与 `HANDOFF.md`，再读取画像、路由和单一 Lane。
4. 旧账号持久文件区只可作为只读缓存；它不能覆盖私人 Git 权威源。
5. 新账号未授权私人仓库或本地状态尚未推送时，必须明确报告状态不可见，不得用聊天记忆推断。
6. 不同副本不得按文件时间静默覆盖；使用 Lane version、Git rebase 和 pending delta 解决冲突。

## Active Sync Configuration

- 权威仓库：`QcRoaming/PersonalOS-v1`。
- PersonalOS 根目录：仓库内 `PersonalOS/`。
- 本地同步方式：语义检查点 → 校验生成视图 → Git commit → rebase → push。
- 网页读取方式：GitHub 连接器读取权威仓库；不依赖旧账号聊天记录。
- 恢复入口：`START_HERE.md`；最近进度：`HANDOFF.md`；知识总览：`KNOWLEDGE.md`。
- 会话归档：仅由精确独立命令“导入”触发，存入私人 Git 的隔离目录；语义状态仍由 Lane 文件拥有。
