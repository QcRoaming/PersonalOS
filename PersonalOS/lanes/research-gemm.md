---
id: research.kernel_aware_gemm
title: Kernel-aware GEMM Expert Schedule Space
role: main
priority: P0
status: active
version: 33
updated_at: 2026-07-24
keywords: GEMM|BLIS|OpenBLAS|libxsmm|MLIR|Transform Dialect|BaCO|microkernel|packing|tiling|vectorization|search space|compatibility checker
imports: infra.tooling#Current Blockers|thesis.writing#Current Chapter
last_activity_at: 2026-07-24T06:04:50Z
---

# Goal

从 BLIS 为主、OpenBLAS 和 libxsmm 为补充的高性能 GEMM 库中抽取 microkernel shape、cache blocking、packing、vectorization、alignment 和 tail policy 等专家事实，将其抽象为带条件、硬约束、软先验和证据来源的规则；通过 microkernel contract 与 compatibility checker 自动生成 kernel-aware 的 MLIR Transform Dialect 调优空间，并交给 BaCO 等 tuner 搜索。

# Research Positioning

- Transform Dialect 解决“如何表达调度”。
- BaCO 解决“如何搜索参数”。
- 本课题解决“搜索什么、候选为什么合理、候选为何与目标 kernel 兼容”。
- 实验目标是在相同 autotuning budget 下证明专家空间比通用空间具有更高的有效候选率、高性能候选密度和收敛速度。
- 不把全面超过 BLIS/OpenBLAS/libxsmm 设为必要结论。

# Current Checkpoint

完成规范化 C 候选池离线 BaCO replay并冻结最终 E2 性能口径

# Verified Milestones

- 已跑通过 `linalg IR → Transform Dialect → lowering → CPU 可执行文件/ELF → 执行与性能测试` 的基础链路。
- 已形成课题定位、贡献边界、章节框架和实验核心假设。
- 已确定以 BLIS 为主要专家事实源。
- 已形成 `expert facts → microkernel contract → rules → candidate generation → compatibility check → BaCO` 总体链路。
- 已形成实验执行计划 v1.0（2026-07-10），包含 R0–R3、M0–M7、测量协议和指标。
- 已确定 baseline、手工缩小空间和专家自动生成空间共享 compile/run/measure/result 基础设施。
- 已完成六个 Task Context、两类 Haswell Contract、十一维 Compatibility Checker、四类搜索空间、条件参数域、provenance 和三个正式算法的 Chapter 4 原型。
- 已完成 direct/adapt/fallback 各一条真实 `Transform -> LLVM IR -> clang AOT -> correctness` 策略样例；3/3 通过，实际均为 fallback。
- 已本机部署固定 commit 的 BaCO 3.0.0，并完成 6 次真实调优回调；完整 Expert+Shell 为 249 点，smoke run 使用声明的 6 点低 IR 膨胀子域。
- 已生成图4-1至图4-5、表4-1至表4-3、复杂度/内存数据、完整日志和 53 项通过测试；一键复现入口验证通过。
- 已建立 PersonalOS 实验注册表，统一登记 Chapter 3、Chapter 4、Chapter 5、Transform Dialect §4.5 核心材料及五类历史实验；八个生成入口成功后自动刷新路径状态、体积、指纹、证据哈希和最近成功运行时间。
- 已新增 `transform.buddy.call_microkernel`、BLIS packing pass 与 C++ ABI adapter；`192x256x256 f32` 锚点的二进制确认链接并调用 `bli_sgemm_haswell_asm_6x16`，全矩阵正确性通过。
- 已形成独立 Chapter 5 实验包和自动注册入口；最终复现的静态锚点 fallback 与 direct 数据分别为 1.856 和 34.578 GFLOP/s，本机本次 direct 加速 18.63 倍，仅作为单主机锚点观测。
- 已实现 K 尾块零填充与实际 K 调用、M/N 尾块 6x16 临时 C 保序累加和有效区域 scatter；非零初始 C 的动态数值校验全部通过。
- 已实现一个动态 fallback 二进制和一个动态 BLIS 二进制跨 7 个运行时 shape 复用；3 个 direct 与 4 个 adapt shape 共 42 条独立 trial 全部通过，运行时 fringe 计数与解析期望逐条一致。
- 相对 scalar-loop 动态 fallback 的 shape 级几何平均加速为 15.905 倍，shape bootstrap 95% 区间为 [10.250, 22.036]；direct/adapt 分组几何平均分别为 21.941 和 12.495 倍。该区间重采样 shape，不代表跨主机置信区间。
- 已新增独立 `chapter4_5_integrated` 包，在不覆盖第四章冻结数据的前提下复用 Candidate、Contract、Checker 和 Expert+Shell 空间，并调用第五章 packing pass、Transform op 与 BLIS adapter。direct/adapt/fallback 路径矩阵 3/3 正确且预测与观测一致；adapt 的 752 次 runtime fringe 调用与解析期望一致。
- 已完成 6 次 unmodified BaCO 集成回调，6/6 有效，5 次观测为真实 BLIS direct、1 次为 exploration-shell fallback；完整源空间仍为 249 点，集成运行仅作为六点 smoke evidence。
- 已建立机器可读论文证据筛选清单及生成目录：11 个注册实验中，5 个为正文主证据、1 个为正文辅助、4 个仅用于附录、1 个仅作为外部论文参考。PersonalOS 刷新时自动同步该分类。
- 已完成第六章冻结矩阵：36 个 row-major f32 shape、8 个调优 shape、B1-B4 各 8 shape x 5 seed x 25 BaCO 回调，并完成 8 组消融和 5 个探索壳比例，共 680 次调优、17,000 条轨迹；所有回调有效。
- 已实测 1,256 个候选/shape case，Compatibility Checker 的 direct/adapt/fallback 预测与观测 100% 一致；36 个 shape 上 scalar、vectorized dynamic MLIR 和完整 `bli_sgemm` 均通过正确性。
- Vectorized dynamic MLIR 相对 scalar-loop 的几何平均加速为 7.710 倍，性能为完整 BLIS 的 0.184；B1/B2/B3/B4 的 best-at-25 相对 B5 几何平均分别为 0.781/0.948/0.791/0.800。
- 正式结果表明硬 Contract-only B2 的候选密度和固定预算结果最好；packing 规则移除后降至 0.046，相比之下当前 MR/NR、cache 与软排序先验并未带来整体收益。该结果作为方法边界保留，不把 B4 预设为必然优于 B2。
- 12 个 holdout shape 的 48 个方法/shape 零样本结果全部正确；2 个 tail case 的 B3/B4 本地空间为空，按预声明 B4->B3->B2->B1 链降级并显式记录。探索壳 30% 在本次五比例中最高，为 0.893 x B5。
- BaCO 3.0 离线重放记录到 370 次重复回调；GPy 原生 Cholesky 抖动耗尽后的确定性兼容兜底触发 1,292 次。候选域、种子和目标值保持不变，兼容介入单独披露，不作为算法贡献。
- 第六章已生成 4 张 LaTeX/CSV 表和 11 幅 SVG/PDF/600-dpi TIFF/PNG 图，机器 QA、人工预览和 13 项 artifact/space 测试全部通过；PersonalOS 注册表现为 11/11 全部可用。
- Chapter 3 的 16/16 条源码核验记录已由论文作者明确签核，机器检查和人工状态分别保持为 `pass` 与 `verified`；重跑提取器后验证器报告 0 条待签，图 6-1 和 RQ1 汇总同步为 100%。
- 已固定 OpenBLAS `b338322e9afc063d95e2c117e85bedf28213295a`，抽取 BLIS Haswell、OpenBLAS Haswell、BLIS RVV VLEN128 和 OpenBLAS ZVL128B 的事实/Contract，并显式记录 4 组跨源冲突；OpenBLAS Haswell 的 4 shape、28 条 CBLAS 实测全部正确。
- 已完成 36 shape x 28 candidate 的 1008-case 真实测量语料及 13,125 条在线轨迹。静态 BLIS 排序的 design/validation/holdout Spearman 为 0.080/0.034/0.167，校准后为 0.635/0.633/0.685；budget 5 下离线校准为 0.568 x pool-best、在线校准为 0.563，说明同主机已有充分离线训练时在线更新未额外获益，误导先验则可随反馈恢复。
- 已固定 K230 SDK `7e302f733311d284be255f0d81d3463b6ae6ee6d` 和官方 RT-Smart GCC 12.0.1 工具链，完成 OpenBLAS `RISCV64_ZVL128B` 8x8 microkernel/packing 的静态交叉构建。修正 RT-Smart ELF 入口为 `0x200000000` 后，scalar、显式 RVV、完整 OpenBLAS 三个 ELF 在物理 K230 上完成 560 条正确测量；按 shape 选择最佳 RVV 候选相对进程内 scalar 的几何平均为 2.288 倍，完整 OpenBLAS 为 13.470 倍。固定 BLIS 来源候选仅为 scalar 的 0.847 倍，说明兼容知识可迁移，但性能排序必须由目标反馈校准。
- Buddy packing pass 已从硬编码 f32 泛化到匹配的 f32/f64 memref；f64 Haswell `bli_dgemm_haswell_asm_6x8` 在 36 个冻结 shape 上完成 128 个唯一二进制、3132 条 trial，3024 条候选观测的 direct/adapt 预测与 runtime fringe 路径 100% 一致。每 shape 28 点池内最优相对完整 `bli_dgemm` 的几何比为 1.064。
- 已完成真实 `select -> fresh subprocess -> update` 闭环：12 个 holdout、4 种策略、5 个 seed、25 预算共 6000 次新进程目标测量，objective cache hit 为 0。预算 5 时离线/在线校准相对随机分别为 1.192 倍 [1.055, 1.343] 和 1.155 倍 [1.042, 1.277]。
- 已固定 Optuna 4.9.0 TPE，在同一有限候选池和 25 个唯一测量预算下完成 1500 次新进程目标测量；2035 个 callback 中 535 个重复建议被剪枝且不消耗有效预算。在线校准相对 TPE 在预算 5/25 的区间均跨 1，不宣称显著优于现有 tuner。
- 多来源消融保持 BLIS/OpenBLAS 不兼容硬 ABI 分离，仅比较同一 BLIS-hard-valid 池上的软排序。预算 5 时 BLIS-only 和校准先验相对 naive merge 分别为 1.063 倍 [1.029, 1.103] 和 1.067 倍 [1.018, 1.125]；校准与 BLIS-only 为 1.003 倍且区间跨 1，说明盲目增加来源会伤害排序，校准主要恢复而非必然超越可靠单源。
- 已生成面向 Ubuntu 20.04 x86_64 的 14900/14900K/14900KF 完全离线包，固定 Buddy `d7bb40c`、LLVM `09b849a`、BLIS `36df51a` 和 mimalloc `81a7711`。针对目标机 Buddy DIP 配置暴露的 JPEG 缺失，依赖闭包已补入 `libjpeg-dev`、`libpng-dev` 及头文件预检，并隔离 Conda Python 环境变量。修正版归档包含 211 个本地 APT 包、CMake 3.28.6、Python 3.10.14 源码、离线 wheels、完整目标机操作指南和全部实验源码；469 MiB 归档通过 SHA-256、277 文件清单和 4 项测试，当前状态仍为 `ready_pending_external_run`。
- 已执行 Hugging Face `Qwen2ForCausalLM` 真实控制流 shape trace：338 次原始 Linear、336 次核心 projection、192 次规范化融合 projection，映射为 8 个冻结 workload，覆盖 24 层核心 projection 调用与 FLOP 的 100%；`lm_head` 明确排除。
- 已完成 3 个预声明 K230 应用闭环案例：`linalg.generic -> transform.annotate -> convert-linalg-to-std -> LLVM IR -> RV64GCV ELF -> OpenBLAS packing/sgemm_kernel adapter`。Host ABI smoke 为 `PASS cases=3 adapter_calls=3`；静态 ELF 入口为 `0x200000000`、含 452 条 RVV 指令匹配，且未修改冻结的 Chapter 4 generator、未新增 compiler pass。
- 上述闭环已在物理 K230 RT-Smart 上完成 3 案例 x 3 variant x 5 repetition 共 45 条正确测量，direct/adapt 路径逐条匹配。C-adapter/MLIR-adapter 几何时间比为 0.9887，shape-cluster bootstrap 95% CI 为 [0.9765, 1.0009]，满足预注册 parity 门槛；MLIR adapter 相对完整 OpenBLAS 的几何性能比例为 0.7518，仅作为代表性闭环边界。
- i7 WSL 的 2088 进程确认性测量完成但状态为 `FAIL_UNSTABLE`：232 个 workload/variant 组仅 15.95% 通过 robust-CV 门槛。随后冻结并执行 120 进程的 6-CPU 测量资格测试，所有 CPU 均未使四组诊断全部通过，状态为 `FAIL_UNQUALIFIED`。旧 pilot 加权收益已撤出正式输出，本机 timing 仅作负向测量质量证据。
- 应用验证已登记为第 21 个论文证据条目和 PersonalOS 实验；13 项应用测试、17 项外部验证测试、53 项 Chapter 4 回归均通过。按实测 `/sdcard` 路径重建的 K230 包 SHA-256 为 `642272d2ebc564ce2689757f0fdf600734a39a1bb6990022e8f67410acc9d0d9`。
- K230 external-validation 完整池已冻结为 10 个 shape、160 个矩阵行、133 个可执行候选（104 direct、29 adapt）；串口协议要求 399 条 adapter 与 30 条完整 OpenBLAS 基线结果，并逐项核对 trial、shape、tile、path 和 correctness。18/18 项测试通过，新归档 SHA-256 为 `7a6fd7a754bbe07c7f513d998e8fe853e459166f1f4992ef32b41cc320301848`。
- K230 external-validation 在物理板上完成 429/429 条正确测量，覆盖 10 个 workload、133 个可执行候选和 10 个完整 OpenBLAS 基线；pool oracle 选出 8 direct、2 adapt。生成 adapter 相对完整 OpenBLAS 的 workload 几何性能为 0.6730，bootstrap 95% CI [0.6193,0.7253]，10 个 workload 无一获胜；8 个精确 Qwen shape 为 0.6653。
- 143 个板端测量组的中位 trial CV 为 0.158%，仅一个非最优候选超过 5%；最佳 adapter 最大 CV 为 0.300%，OpenBLAS 最大 CV 为 0.280%，最大投影误差 5.99e-6。Qwen trace-weighted 分析覆盖 decode/prefill 两场景；library guard 恢复到完整库基线，但因为 adapter 不产生运行收益，调优成本没有正的 break-even。
- Contract 独立负例实验覆盖 BLIS f32、BLIS f64 和 OpenBLAS RVV 三个 package 的 30 个案例；24 个危险变异全部被拒绝或安全降级，false accept/false reject 均为 0，路径、拒绝阶段和诊断字段准确率均为 100%。
- 对 36 个 workload 的 2600 点空间完成 93,600 次静态分类，并将 direct/adapt 微内核路径不活跃的 `vectorize` 规范为 false。G0/G1/C 平均唯一候选为 2600.0/951.9/104.4，C 的规范化 IR 重复率由 0.500 降至 0。随后按冻结协议在 8 个 28 点规范化 C 池上完成 40 条离线 BaCO replay：最终 D90=0.1875、time-to-90%-pool-best=8.0、达到率=0.925；旧 0.1964/11.5 仅保留为规范化前消融，且 replay 未重新编译或进行硬件测量。
- Package 复用审计确认三个 Contract 的 schema 交集/并集为 31/34、IoU 为 0.912，共享核心中 package-ID 特判为 0；BLIS f64 复用核心生成器，而 OpenBLAS RVV 仍使用 package-local 生成路径，因此只支持“共享 Contract 语义与 checker”，不支持“通用生成器已完全复用”。
- 搜索经济性实验将 i7 成本拆为 `C_c=58.239 ms` 与聚合 `sum C_s,j=531895.625 ms`。事后 winning-shape 上点估计/LCB95 break-even 为 165865/741587 个等频合成 deployment cycles，只是描述性上界；i9 和 K230 exact traces 相对完整库均无有限 break-even。

# Doing

- 按最终规范化 D90/time-to-90、部分复用和 LCB95 break-even 口径整理第四至六章

# Next

1. 在论文正文中并列报告最终 D90=0.1875、time-to-90=8.0 与规范化前消融 0.1964/11.5

# Current Blockers

- 当前覆盖单线程、行主序 f32 6x16 与 f64 6x8 两个 Haswell Contract，并完成 i7-10750H/i9-14900 两主机验证；任意 stride、更多后端 Contract、线程扩展和普遍跨主机泛化仍未验证。
- 当前软专家先验没有优于硬 Contract-only B2；论文必须把它表述为本次实现的经验限制和后续规则校准方向，而不是宣称完整专家空间全面获胜。
- BaCO 3.0 分类参数存在重复回调与 GPy 数值稳定性问题；固定预算以回调计，唯一候选数和兼容兜底触发数必须同时披露。
- K230 已完成单块 C908 RT-Smart 板端测量，但该结果不能外推为所有 RISC-V 后端的性能或排名泛化。
- i9-14900 外部归档已通过 importer；两主机结果只支持硬兼容迁移和低预算趋势，不能外推为所有 x86 主机的稳定排名或性能泛化。
- i7-10750H WSL 对 decode 亚毫秒完整 BLIS 基线的跨进程波动未通过预注册门槛；该环境不得用于新的应用级性能或搜索收益主张。

# Decisions

- 优先做单个静态 shape GEMM、单后端、单 dtype 的最小闭环，再扩展 batch GEMM、多 dtype 和多架构。
- 保留论文原始调优链路，采用插拔式搜索空间生成模块，而不是从头重建实验系统。
- 三条对比链路：A 原始 generic baseline；B 手工缩小空间；C 专家规则自动生成空间。
- microkernel 作为 contract/descriptor 建模，不默认把 `transform.to_library` 等同于任意 kernel 替换。
- 区分语义层融合与实现层支持；调度、codegen、microkernel/library epilogue 必须在正确层级匹配。
- 关键实验预算优先使用 25/50/100/200 等固定候选数，并报告 GFLOP/s、相对 BLIS 性能、有效率、剪枝率和收敛曲线。
- 完整专家空间与受控 smoke-run 子域分开记录；后者只控制实验成本，不改变合法性或 Contract 判定。
- BaCO 保持原样，专家知识通过参数域、lookup、默认点和 provenance 接入，不宣称修改其概率模型。
- PersonalOS 作为实验元数据控制面，不复制工作区中的原始数据、IR、二进制和构建输出；研究结论仍以各实验 artifact index 和冻结证据文件为准。
- Chapter 4 冻结证据保持原样；真实替换结果存入独立集成包，避免把历史 observed fallback 静默改写为 direct/adapt。
- 论文实验按 `primary_main_text`、`supporting_main_text`、`appendix_only` 和 `reference_only` 分级；只有前两类进入正文，且必须遵守各自 claim boundary。
- 第六章以真实结果为准：B2 是当前固定预算最佳方法，B3/B4 的价值主要体现在更快达到各自池内高质量点和 packing/路径约束，而不宣称其最终性能必然优于 B2。
- BaCO 保持固定版本和原候选域/目标值；`warnings`、scikit-learn 参数映射及 GPy 抖动兜底属于公开记录的运行时兼容层，不归入方法贡献。
- 将 ISA、microkernel shape、packing、layout 与 ABI 作为可条件迁移的硬兼容知识；把 MC/KC/NC、候选排序和库内经验参数作为必须由目标反馈校准的软性能先验。
- 同预算 tuner 对照以唯一实测候选数计预算；重复建议保留 callback 证据但不执行、不复用目标值，也不消耗唯一测量预算。
- 多来源知识不合并 backend-specific 的 microkernel/packing ABI；只有 source-labelled 性能特征可进入 naive 或 calibrated 软排序消融。
- K230 官方 GCC 的旧 RVV intrinsic API 通过生成式兼容头接入，不修改 OpenBLAS 上游 worktree、不替换 `RISCV64_ZVL128B` microkernel/packing；兼容映射和哈希属于构建 provenance，不作为算法贡献。

# Knowledge State

| Topic | State | Evidence | Next evidence |
|---|---|---|---|
| Transform Dialect 调度链路 | applied | 已跑通基础 lowering 与执行链路 | 在 §4.5 artifact 上复现完整 tuning loop |
| GEMM blocking 层次 | understood | 已讨论 MC/KC/NC 与 MR/NR 的职责 | 对照 BLIS 配置与源码符号记录证据 |
| BLIS packing | applied | A/B micro-panel、K padding、M/N 临时 C 与 scatter 已通过动态 7-shape 测试 | 评估 packing/fringe 开销并扩展任意 stride |
| microkernel contract | verified | f32 6x16 and f64 6x8 direct/adapt predictions match runtime across i7-10750H and i9-14900; K230 compatibility evidence is physically measured | extend to arbitrary stride and additional backends |
| Contract mutation robustness | verified | 3 packages, 30 independent cases, 24/24 dangerous mutations rejected or safely downgraded; no false accepts or rejects | add runtime memory-safety instrumentation for descriptor-consistent buffer corruption |
| search economics | verified | i7 posthoc point/LCB95 break-even is 165865/741587 synthetic equal-frequency cycles with explicit Cc/sum-Cs decomposition; i9 and K230 exact-shape generated paths have no finite positive-cost break-even | validate only when a future generated path first beats the complete-library baseline |
| BaCO 参数接口 | applied | 固定 BaCO 3.0 已完成 B1-B4、消融和探索壳共 680 次五种子离线重放，17,000/17,000 回调有效 | 校准软先验并评估重复分类点与 GPy 数值稳定性 |
| RVV 后端 | applied | K230 物理板完成既有560条后端测量、45条MLIR闭环和429条完整候选池测量；10-shape adapter/OpenBLAS为0.6730 [0.6193,0.7253] | 增加第二个 RVV 目标或硬件计数器分析以扩大外部有效性 |
| performance prior calibration | verified | i7 的低预算校准收益未在 i9 显著复制；当前专家软性能特征相对 Data-only 无显著增量 | 正文报告环境依赖与停止条件，扩展前先证明校准可摊销 |
| Transformer fan-out shared packing | verified | Optimized QKV and Gate-Up formal probe shows packing-count reduction but no stable latency gain against repeated packing and a significant loss against complete-BLIS portfolio. | Test fused epilogue or phase-specific portfolio mechanisms that cannot be reduced to weight concatenation. |

# Completion Criteria

- 能从真实库源码生成带证据的专家事实。
- 能将事实编译为规则和 microkernel contract。
- 能自动生成并校验 BaCO 可消费的搜索空间。
- 在相同预算下完成 A/B/C 公平对比并报告搜索空间质量与性能结果。

# Recent Evidence

- 2026-07-24T06:04:50Z — 冻结 replay：8 workload x 5 seed x budget 25，共 40 run/1000 callback；最终 D90=0.1875、time-to-90=8.0、reached=0.925；旧 0.1964/11.5 保留为规范化前消融；无编译、无硬件重测
- 2026-07-24T06:04:50Z — artifact: /buddy-mlir/jlq/thesis/experiments/chapter6_contract_space_validation/reports/contract_space_validation_results.md
- 2026-07-24T03:03:24Z — E2 C mean 208.7 to 104.4 and IR duplicates 0.500 to 0; E3 schema 31 intersection/34 union; E4 Cc=58.239 ms, sum Cs=531895.625 ms, LCB95 break-even=741587 cycles
- 2026-07-24T03:03:24Z — artifact: /buddy-mlir/jlq@0a373a0c8:thesis/experiments/chapter6_contract_space_validation/reports/contract_space_validation_results.md
- 2026-07-24T01:48:46Z — E1: 24/24 dangerous mutations handled with zero false accepts/rejects; E2: 93600 static classifications; E3: partial package reuse boundary; E4: no finite break-even on i9/K230 exact shapes
- 2026-07-24T01:48:46Z — artifact: /buddy-mlir/jlq@0a373a0c8:thesis/experiments/chapter6_contract_space_validation/reports/contract_space_validation_results.md
- 2026-07-24T01:46:35Z — E1 independent oracle PASS：3 packages、30 cases、24/24 dangerous mutations handled，false accept/false reject 为 0
- 2026-07-24T01:46:35Z — E2 修复前口径完成 93,600 次静态分类；G0/G1/C 平均候选 2600.0/1056.2/208.7，后由 version 32 checkpoint 的 vectorize 规范化结果取代
- 2026-07-24T01:46:35Z — E3 复用审计：共享 31 个 schema 叶字段、核心 package-ID 特判 0；BLIS f64 复用核心生成器，OpenBLAS RVV 仍为 package-local 生成路径
- 2026-07-24T01:46:35Z — E4 搜索经济性：i7 仅有后验描述性正 break-even；i9/K230 exact shapes 相对完整库无有限正成本 break-even
