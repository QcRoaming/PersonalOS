# PersonalOS Knowledge Index

> Generated cross-domain index. Knowledge facts remain owned by their lane files.

| Lane | Topic | State | Evidence | Next evidence |
|---|---|---|---|---|
| `research.kernel_aware_gemm` | Transform Dialect 调度链路 | applied | 已跑通基础 lowering 与执行链路 | 在 §4.5 artifact 上复现完整 tuning loop |
| `research.kernel_aware_gemm` | GEMM blocking 层次 | understood | 已讨论 MC/KC/NC 与 MR/NR 的职责 | 对照 BLIS 配置与源码符号记录证据 |
| `research.kernel_aware_gemm` | BLIS packing | applied | A/B micro-panel、K padding、M/N 临时 C 与 scatter 已通过动态 7-shape 测试 | 评估 packing/fringe 开销并扩展任意 stride |
| `research.kernel_aware_gemm` | microkernel contract | applied | f32 6x16 与 f64 6x8 contract 已驱动 36-shape direct/adapt 动态替换与运行时路径计数 | 扩展任意 stride、更多后端和跨主机验证 |
| `research.kernel_aware_gemm` | BaCO 参数接口 | applied | 固定 BaCO 3.0 已完成 B1-B4、消融和探索壳共 680 次五种子离线重放，17,000/17,000 回调有效 | 校准软先验并评估重复分类点与 GPy 数值稳定性 |
| `research.kernel_aware_gemm` | RVV 后端 | applied-build | K230 官方工具链已生成 scalar/RVV/OpenBLAS 三个静态 ELF 和部署包 | 物理板执行、正确性检查与 CSV 导入 |
| `thesis.writing` | 学位论文格式约束 | applied | 已绑定 NWPU 2025 + XeLaTeX 输出规则 | 在完整章节编译中验证 |
| `thesis.writing` | 摘要与绪论边界 | understood | 已多轮讨论目的、方法、结果和意义 | 结合最终实验结果重写定稿 |
| `thesis.writing` | 方法与实验章节边界 | understood | 已明确第三章方法、第四章实现实验 | 用真实模块和数据对齐章节 |
| `learning.inference` | Qwen attention/mask | understood | 已分析 causal、SW 与随机 mask 代码 | 在真实 forward 调用链断点验证 |
| `learning.inference` | Weight-only quantization | understood | 已区分 W4A16 与 W4A4、compute dtype 与 activation quantization | 调试一个量化 Linear kernel 调用 |
| `learning.inference` | Transformers 推理链路 | understood | 已形成 quickstart 级调用流程 | 固化可运行环境并逐层断点 |
| `learning.inference` | vLLM 调度与 KV cache | exposed | 已讨论 scheduler 和 continuous batching | 运行源码并打印真实状态 |
| `learning.inference` | SGLang/TensorRT-LLM | exposed | 已确定学习顺序 | 完成 vLLM 首个修改实验后开始 |
| `skills.mcp` | Skill 结构与触发 | understood | 已分析 nature-skills 与安装目录 | 创建并安装 personal-os Skill |
| `skills.mcp` | MCP 注册与运行 | understood | 已明确 config 注册和独立进程关系 | 运行一个 MCP server 并调用工具 |
| `skills.mcp` | 跨窗口状态协议 | applied | 已实现确定性 Handoff、单 Lane 启动和结构化检查点并通过测试 | 真实网页新窗口验收 |
| `skills.mcp` | 多机器同步 | applied | 已实现 Git commit-rebase-push 闭环并用本地远程仓库验证 | 第二台真实设备验收 |
| `skills.mcp` | 跨账号恢复 | applied | 已实现 GitHub 授权加 START_HERE 固定启动协议 | 第二个 ChatGPT 账号端到端验收 |
| `skills.mcp` | 会话与语音归档 | applied | 已实现 exact_export/provided_transcript/visible_context_only、语音转写/音频区分和 4 项归档测试 | 真实 ChatGPT 数据导出与语音窗口验收 |

Knowledge stages: unknown → exposed → understood → applied → verified. Use stale when older evidence must be revalidated.
