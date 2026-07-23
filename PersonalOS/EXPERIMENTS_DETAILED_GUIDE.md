# 全部实验详细说明

> 更新时间：2026-07-23。本文覆盖 PersonalOS 注册表中的 21 项实验，作为实验链路、设备、协议、结果和证据路径的统一入口。

## 1. 阅读与路径约定

- 本地工作区根目录为 `/buddy-mlir`，下文路径均相对该目录，例如 `jlq/thesis/experiments/chapter6_evaluation`。
- `processed/` 保存机器可读汇总，`reports/` 保存论文可读报告，`provenance/` 保存哈希、版本和导入清单，`raw/` 或 `board_results/` 保存原始测量。
- 总结论入口是 `jlq/thesis/experiments/FINAL_EXPERIMENT_AUDIT.md`。
- 正文证据筛选入口是 `jlq/thesis/experiments/PAPER_EVIDENCE_CATALOG.md`。
- PersonalOS 机器可读注册表位于 `/root/personal-os/PersonalOS/registries/experiments.json`。
- 当前注册实验数为 21，i9-14900 与物理 K230 的冻结目标实验均已返回；冻结的学位论文实验边界内没有待执行硬件实验。

## 2. 总体实验链路

1. 从固定版本的 BLIS 和 OpenBLAS 源码提取微内核尺寸、打包格式、布局约束和缓存分块提示，并记录源码位置与冲突。
2. 将知识分为 Fact、Microkernel Contract 和 Expert Rule。硬 Contract 只描述合法性，软规则只提供排序或采样偏置。
3. 输入 GEMM 的 dtype、M/N/K、布局和目标设备，生成 Generic、Contract-only、Expert-core、Expert+Shell 等候选池。
4. Compatibility Checker 将候选判定为 direct、adapt、fallback 或 reject，并记录每条判定的来源。
5. 调优器在固定候选池和唯一测量预算下选择 tile_m、tile_n、tile_k、packing 等参数；Transform Dialect 将参数物化到 linalg 变换链。
6. 合法候选经 packing/call adapter 调用 BLIS 或 OpenBLAS 微内核；不整除 M/N/K 通过 fringe adapt 处理，不满足 Contract 的候选进入 fallback。
7. IR 继续 lowering 到 LLVM IR，链接运行时或目标库，生成 x86 可执行文件或 RV64GCV ELF。
8. 目标机运行 correctness、path、wall-time、GFLOP/s 和稳定性测量；返回包经过 SHA-256、清单、可执行文件和结果覆盖审计。
9. 固定预算比较、bootstrap 置信区间、消融、time-to-95%-oracle 和校准成本分析生成论文证据。

## 3. 设备与环境矩阵

| 标识 | 设备/环境 | 主要用途 | 关键边界 |
|---|---|---|---|
| `i7_10750h_wsl2` | Intel Core i7-10750H，6C/12T，WSL2，AVX2/FMA | 主要开发主机；Chapter 3-6、f32/f64、BaCO/Optuna、消融 | WSL 定时资格审计失败的 exact-shape 数据只作诊断；其他冻结实验按各自协议使用 |
| `i9_14900_linux` | Intel Core i9-14900，Ubuntu 20.04 原生 Linux，单核绑核 | 第二 x86 主机；跨主机 f64、Transformer exact-shape、同池先验复制 | 单线程、row-major；`perf stat` 因权限不可用，主结果使用 wall time |
| `k230_c908` | K230/C908，RV64GCV，RT-Smart；Linux 侧负责存储/部署 | 物理 RISC-V 正确性、RVV/OpenBLAS、MLIR wrapper closure、exact-shape 池 | 单块开发板和固定工具链，不外推到全部 RISC-V |
| `qemu_riscv64` | QEMU user-mode RV64 | 历史 correctness 与工具链检查 | 不用于真实性能结论 |
| `host_mlir_aot` | x86 主机 MLIR/LLVM AOT | 历史 Transform 到 LLVM 的闭环验证 | 不是 BLIS 替换或正式性能证据 |

## 4. 当前核心结果

- 22 条源码事实完成机器检查、可追溯性和作者签字；BLIS/OpenBLAS 记录 4 类显式冲突。
- 1256 个已测候选的 Checker 预测与运行路径完全一致，协议内 agreement 为 1.000。
- Chapter 5 已实现真实 packing 和 `bli_sgemm_haswell_asm_6x16` 调用；7 个 direct/adapt 动态形状均正确。
- 正式 Chapter 6 覆盖 36 个预声明 f32 workload、固定预算、5 个随机种子、优化动态 MLIR 和完整 BLIS 对照。
- 严格同池实验中，i7 上 B4 相对 B2 在 budget 5/10 分别为 1.058x/1.035x，置信区间均高于 1；i9 上为 0.992x/0.999x，区间跨 1，因此“两环境均显著获益”的预注册条件失败。
- Data-only 在 budget 5 相对 no-prior 为 1.049x，Expert+Data 相对 Data-only 为 1.009x 且区间跨 1；当前 BLIS 软性能特征没有证明额外价值。
- i9 exact-shape 池通过严格导入：870 条 correctness、290 个测量组；生成池/完整 BLIS 几何比为 0.5448，95% CI [0.4833, 0.6104]，0/10 workload 获胜。
- K230 exact-shape 池通过严格导入：429 条 correctness；生成 adapter/完整 OpenBLAS 几何比为 0.6730，95% CI [0.6193, 0.7253]，0/10 workload 获胜。
- K230 MLIR wrapper closure 有 45 条正确结果，C adapter/MLIR adapter 几何时间比为 0.9887，95% CI [0.9765, 1.0009]。
- 校准使平均 time-to-95%-oracle 从 7.90 次候选测量降至 3.08 次，但 591 条校准样本的成本无法在 12 个 holdout workload 内摊销。

## 5. 逐项实验说明

### 5.1 `historical.host_mlir_aot`

- **目的**：验证早期通用 Transform Dialect GEMM 能完成 host AOT、正确性检查和计时。
- **链路**：静态 linalg.matmul -> Transform tiling/vectorization -> LLVM dialect -> LLVM IR -> host executable。
- **设备/协议**：x86 主机；按 `config/aot_cases.csv` 的 shape 和 tile 执行。
- **结果**：形成可运行的 MLIR AOT 基线，但不证明 BLIS 微内核替换。
- **结果路径**：`jlq/thesis/experiments/results/mlir_aot_benchmark.csv`；`jlq/thesis/experiments/results/mlir_aot_benchmark_summary.md`。
- **复现**：`bash jlq/thesis/experiments/scripts/run_mlir_aot_benchmark.sh`。

### 5.2 `historical.native_cpp_tile_sanity`

- **目的**：用原生 C++ 分块循环检查 tile 参数和计时框架。
- **链路**：C++ GEMM -> 编译器优化 -> host executable -> correctness/timing。
- **设备/协议**：x86 主机；历史 sanity benchmark。
- **结果**：只保留为原生循环参照，不进入 MLIR 方法的主性能论证。
- **结果路径**：`jlq/thesis/experiments/results/cpu_initial_results.csv`；`jlq/thesis/experiments/results/cpu_benchmark_summary.md`。
- **复现**：`bash jlq/thesis/experiments/scripts/run_cpu_benchmark.sh`。

### 5.3 `historical.qemu_rvv_correctness`

- **目的**：验证标量与 RVV ELF 在模拟器上的功能正确性。
- **链路**：C/LLVM -> RV64GC/RV64GCV ELF -> QEMU user-mode -> correctness log。
- **设备/协议**：QEMU，不是真实 RISC-V 板。
- **结果**：提供模拟器 correctness 证据，不支持板端性能结论。
- **结果路径**：`jlq/thesis/experiments/results/qemu_correctness_check.md`；`jlq/thesis/experiments/outputs/rvv/`。
- **复现**：`bash jlq/thesis/experiments/scripts/run_qemu_correctness.sh`。

### 5.4 `historical.rvv_toolchain`

- **目的**：确认工具链可生成 RVV 指令。
- **链路**：SAXPY C loop -> `rv64gcv` object -> objdump/vectorizer log。
- **设备/协议**：交叉编译工具链静态检查。
- **结果**：确认 RVV codegen，不证明运行正确性或速度。
- **结果路径**：`jlq/thesis/experiments/results/rvv_toolchain_check.md`；`jlq/thesis/experiments/outputs/rvv/rvv_saxpy.objdump.txt`。
- **复现**：`bash jlq/thesis/experiments/scripts/run_rvv_toolchain_check.sh`。

### 5.5 `historical.transform_rvv_codegen`

- **目的**：验证 Transform Dialect 参数可以进入 RVV codegen。
- **链路**：linalg.matmul -> Transform -> vector/LLVM lowering -> RV64GCV object/disassembly。
- **设备/协议**：静态生成；未以真实板端性能为目标。
- **结果**：形成 IR 快照和指令计数，保留为附录 codegen 证据。
- **结果路径**：`jlq/thesis/experiments/results/transform_demo_check.md`；`jlq/thesis/experiments/results/transform_metrics.tsv`。
- **复现**：`bash jlq/thesis/experiments/scripts/run_transform_demo.sh`。

### 5.6 `paper.transform_dialect_section_4_5`

- **目的**：提取《The MLIR Transform Dialect》4.5 节中 Transform 与 BaCO 接口的可复用设计。
- **链路**：论文核心文件 -> 参数化 Transform IR -> search settings -> 课题接口映射。
- **设备/协议**：文献材料，不是本地性能实验。
- **结果**：确认调优器通过参数化 Transform sequence 驱动候选的设计来源；缺失原论文支持文件时不宣称完整复现。
- **结果路径**：`jlq/thesis/experiments/4.5/REUSABLE_NOTES.md`；`jlq/thesis/experiments/4.5/parametric_transform.mlir`；`jlq/thesis/experiments/4.5/search_settings.json`。
- **复现**：无独立复现命令，作为 source-grounded reference 使用。

### 5.7 `thesis.chapter3_rules`

- **目的**：建立 BLIS Fact/Contract/Rule schema，完成专家事实抽取、验证和初步 MLIR 研究。
- **链路**：BLIS source -> extractor -> facts/contracts/rules -> checker -> 8-shape preliminary MLIR/AOT -> space/fallback/compile statistics。
- **设备/协议**：i7-10750H WSL2；16 条人工核对全部签字。
- **结果**：事实可追溯、合法空间显著缩小；初步链路中的正确 Transform 候选仍观察为 fallback，因此不把该数据写成 BLIS replacement。
- **结果路径**：`jlq/thesis/experiments/chapter3_rules/processed/preliminary_summary.json`；`jlq/thesis/experiments/chapter3_rules/reports/chapter3_preliminary_results.md`；`jlq/thesis/experiments/chapter3_rules/verification/validation_report.json`。
- **复现**：`python3 jlq/thesis/experiments/chapter3_rules/scripts/run_chapter3.py`。

### 5.8 `thesis.chapter3_multisource`

- **目的**：检验只从 BLIS 提取是否会把后端特定经验误写成通用知识。
- **链路**：固定版本 BLIS/OpenBLAS -> 多源 facts -> conflict detection -> hard/soft 分类 -> OpenBLAS CBLAS runtime probe。
- **设备/协议**：x86 host；4 个 OpenBLAS shape、28 次真实 trial。
- **结果**：硬兼容性知识可条件迁移，blocking 等性能值必须保留来源并作为软提示；OpenBLAS probe 全部通过。
- **结果路径**：`jlq/thesis/experiments/chapter3_multisource/data/multisource_facts.yaml`；`jlq/thesis/experiments/chapter3_multisource/data/conflicts.yaml`；`jlq/thesis/experiments/chapter3_multisource/processed/summary.json`；`jlq/thesis/experiments/chapter3_multisource/reports/multisource_results.md`。
- **复现**：`python3 jlq/thesis/experiments/chapter3_multisource/scripts/run_multisource.py --skip-openblas-build`。

### 5.9 `thesis.chapter4_space`

- **目的**：生成并量化 B1 Generic、B2 Contract-only、B3 Expert-core 和 B4 Expert+Shell 搜索空间。
- **链路**：task+Contract+rules -> finite candidate generation -> checker -> provenance -> BaCO lookup/callback。
- **设备/协议**：i7-10750H WSL2；6-task filtering funnel 与 bounded BaCO smoke。
- **结果**：空间构造、复杂度、来源和调优器接口完整；旧 path 示例因当时缺少真实 adapter 仍为 fallback。
- **结果路径**：`jlq/thesis/experiments/chapter4_space/processed/space_summary.json`；`jlq/thesis/experiments/chapter4_space/processed/baco_tuning_summary.json`；`jlq/thesis/experiments/chapter4_space/processed/transform_paths_summary.json`；`jlq/thesis/experiments/chapter4_space/reports/chapter4_results.md`。
- **复现**：`python3 jlq/thesis/experiments/chapter4_space/scripts/run_chapter4.py`。

### 5.10 `thesis.chapter5_blis_adapter`

- **目的**：补齐真实 BLIS packing、microkernel call、fringe adapt 与动态形状边界。
- **链路**：checked schedule -> pack A/B -> `bli_sgemm_haswell_asm_6x16` -> direct/adapt -> accumulation/correctness -> dynamic multishape timing。
- **设备/协议**：i7-10750H WSL2，row-major f32，单线程；7 个 direct/adapt 动态 shape。
- **结果**：真实 BLIS 6x16 调用与 M/N/K fringe 正确；相对声明的 scalar-loop dynamic fallback 几何加速 15.90x，不能表述为相对完整 BLIS 或优化动态 MLIR 的加速。
- **结果路径**：`jlq/thesis/experiments/chapter5_blis_adapter/processed/chapter5_summary.json`；`jlq/thesis/experiments/chapter5_blis_adapter/processed/dynamic_multishape_summary.json`；`jlq/thesis/experiments/chapter5_blis_adapter/reports/chapter5_results.md`；`jlq/thesis/experiments/chapter5_blis_adapter/reports/dynamic_multishape_results.md`。
- **复现**：`python3 jlq/thesis/experiments/chapter5_blis_adapter/scripts/run_chapter5_full.py`。

### 5.11 `thesis.chapter4_5_integrated`

- **目的**：闭合 Chapter 4 候选/BaCO 与 Chapter 5 真实 evaluator。
- **链路**：Expert+Shell candidates -> unmodified BaCO callback -> checker -> direct/adapt/fallback evaluator -> real BLIS microkernel -> result trace。
- **设备/协议**：i7-10750H WSL2；6 次 integration smoke evaluation。
- **结果**：预测的 direct/adapt/fallback 与运行观察一致，BaCO 确实驱动真实 microkernel evaluator；6 点数据不作为正式收敛比较。
- **结果路径**：`jlq/thesis/experiments/chapter4_5_integrated/raw/path_matrix.csv`；`jlq/thesis/experiments/chapter4_5_integrated/raw/baco_callback_log.jsonl`；`jlq/thesis/experiments/chapter4_5_integrated/processed/integrated_summary.json`；`jlq/thesis/experiments/chapter4_5_integrated/reports/integrated_results.md`。
- **复现**：`python3 jlq/thesis/experiments/chapter4_5_integrated/scripts/run_integrated_pipeline.py`。

### 5.12 `thesis.chapter6_evaluation`

- **目的**：对搜索空间质量、搜索效率、性能边界、消融、holdout 和系统开销进行正式评估。
- **链路**：36 workloads -> B1-B4/B0-B5 candidate corpus -> correctness/path measurement -> 5-seed equal-budget BaCO replay -> baselines/ablations/holdout/overhead -> figures。
- **设备/协议**：i7-10750H WSL2，单线程 row-major f32；budget 25，5 seeds；含优化动态 MLIR 与完整 `bli_sgemm` 对照。
- **结果**：Checker 在测试 Contract 内完全一致；packing 消融使 normalized performance 从 0.800 降至 0.046；结果只表示单主机协议，不表示跨主机置信区间。
- **结果路径**：`jlq/thesis/experiments/chapter6_evaluation/processed/chapter6_summary.json`；`jlq/thesis/experiments/chapter6_evaluation/processed/fixed_budget_summary.csv`；`jlq/thesis/experiments/chapter6_evaluation/processed/holdout_zero_shot.csv`；`jlq/thesis/experiments/chapter6_evaluation/reports/chapter6_results.md`。
- **复现**：`python3 jlq/thesis/experiments/chapter6_evaluation/scripts/run_chapter6.py`。

### 5.13 `thesis.chapter6_online_prior`

- **目的**：区分静态专家排序、离线目标校准、在线校准和误导先验。
- **链路**：1008-case real corpus -> design/validation/holdout split -> static/offline/online/misleading prior -> fixed-budget replay -> rank correlation/bootstrap。
- **设备/协议**：i7-10750H WSL2，row-major f32，同主机 real-measurement replay。
- **结果**：budget 5 上 offline/online 相对 random 为 1.192x/1.155x；在线反馈能从误导先验恢复，但在已有强离线模型时不保证继续提升。
- **结果路径**：`jlq/thesis/experiments/chapter6_online_prior/processed/online_prior_summary.json`；`jlq/thesis/experiments/chapter6_online_prior/processed/rank_correlations.csv`；`jlq/thesis/experiments/chapter6_online_prior/raw/online_prior_traces.csv`；`jlq/thesis/experiments/chapter6_online_prior/reports/online_prior_results.md`。
- **复现**：`python3 jlq/thesis/experiments/chapter6_online_prior/scripts/run_online_prior.py --skip-measure`。

### 5.14 `thesis.cgo_local_extension`

- **目的**：增加 f64 Contract、真正在线 subprocess 测量、Optuna TPE 和多源先验对照。
- **链路**：f64 BLIS 6x8 Contract -> fresh-process objective -> random/offline/online/Optuna -> source-labelled prior ablation。
- **设备/协议**：i7-10750H WSL2，单线程 f64；36 shapes、3132 Contract trials、7500 fresh tuner objectives。
- **结果**：budget 5 的 offline/online 均显著优于 random，但未显著优于 Optuna；BLIS-only 与 calibrated 优于 naive source merging。
- **结果路径**：`jlq/thesis/experiments/cgo_extension/processed/cgo_extension_summary.json`；`jlq/thesis/experiments/cgo_extension/processed/f64_contract_summary.json`；`jlq/thesis/experiments/cgo_extension/processed/paired_bootstrap_comparisons.csv`；`jlq/thesis/experiments/cgo_extension/reports/cgo_extension_results.md`。
- **复现**：`python3 jlq/thesis/experiments/cgo_extension/scripts/run_local_extension.py`。

### 5.15 `thesis.x86_cross_host`

- **目的**：检验硬 Contract 与低预算搜索趋势能否跨两台 x86 主机复制，以及绝对性能排序是否稳定。
- **链路**：固定代码/Contract/domain/budget -> i7 与 i9 独立运行 -> strict archive import -> paired cross-host report。
- **设备/协议**：i7-10750H WSL2 与 i9-14900 Ubuntu 原生 Linux，单线程 f64 BLIS 6x8。
- **结果**：两机 3132 Contract trials 均 path-match；i9 budget 5 online 相对 Optuna 为 1.065x，95% CI [1.044, 1.089]；生成池/完整 BLIS 从 i7 的 1.064x 反转为 i9 的 0.804x。
- **结果路径**：`jlq/thesis/experiments/x86_cross_host/processed/cross_host_summary.json`；`jlq/thesis/experiments/x86_cross_host/reports/cross_host_results.md`；`jlq/thesis/experiments/x86_cross_host/processed/latest_import.json`。
- **复现**：`python3 jlq/thesis/experiments/x86_cross_host/scripts/build_cross_host_report.py`。

### 5.16 `thesis.chapter6_same_pool_prior`

- **目的**：修复 B2/B3/B4 候选池不一致、重复预算、参数不活跃和数据泄漏风险。
- **链路**：两环境完整 f64 corpus -> canonical common pool -> liveness audit -> holdout-safe prior fit -> unique no-replacement BaCO replay -> cluster bootstrap。
- **设备/协议**：i7-10750H WSL2 与 i9-14900 Linux；23-26 个 active schedules/workload，budgets 5/10，5 seeds。
- **结果**：liveness、严格同池、唯一预算、无泄漏和 oracle invariance 均 PASS；i7 的 B4/B2 显著大于 1，i9 区间跨 1，整体预注册两环境 acceptance 为 FAIL。
- **结果路径**：`jlq/thesis/experiments/chapter6_same_pool_prior/processed/acceptance_summary.json`；`jlq/thesis/experiments/chapter6_same_pool_prior/processed/parameter_liveness.csv`；`jlq/thesis/experiments/chapter6_same_pool_prior/processed/paired_comparisons.csv`；`jlq/thesis/experiments/chapter6_same_pool_prior/reports/acceptance_report.md`。
- **复现**：`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 jlq/thesis/experiments/chapter6_same_pool_prior/scripts/run_experiment.py`。脚本因未满足预注册科学门槛返回非零，不表示运行故障。

### 5.17 `thesis.chapter6_termination_validation`

- **目的**：执行 Data-only/Expert+Data、time-to-95%-oracle/校准成本和第二 microkernel 三个终止验证。
- **链路**：same-pool holdout -> no-prior/Data-only/Expert+Data -> paired CI -> calibration amortization -> f64 6x8 Contract plug-in audit。
- **设备/协议**：i7-10750H WSL2，单线程 f64，12 holdout workloads。
- **结果**：Data-only 有低预算收益；Expert+Data 无显著增量；591-row calibration 在 12 workload 内不摊销；第二 BLIS Haswell Contract 无需修改核心 generator 即可工作，但它不是独立 backend。
- **结果路径**：`jlq/thesis/experiments/chapter6_termination_validation/processed/acceptance_summary.json`；`jlq/thesis/experiments/chapter6_termination_validation/processed/time_to_95_summary.csv`；`jlq/thesis/experiments/chapter6_termination_validation/processed/calibration_costs.csv`；`jlq/thesis/experiments/chapter6_termination_validation/processed/second_microkernel_audit.json`；`jlq/thesis/experiments/chapter6_termination_validation/reports/termination_validation_report.md`。
- **复现**：`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 jlq/thesis/experiments/chapter6_termination_validation/scripts/run_termination_validation.py`。

### 5.18 `thesis.k230_rvv_backend`

- **目的**：在物理 K230 上比较 scalar、显式 RVV schedules 和完整 OpenBLAS，并观察固定先验的跨架构可靠性。
- **链路**：candidate schedules -> RV64GCV ELF -> SD card/sharefs -> RT-Smart serial run -> strict CSV import -> aggregation。
- **设备/协议**：K230 C908，8 workloads，含不整除 fringe shape，560 条正确 timing rows。
- **结果**：最佳显式 RVV schedule 相对进程内 scalar 几何加速 2.29x，完整 OpenBLAS 为 13.47x；没有固定来源 schedule 支配所有 workload。
- **结果路径**：`jlq/thesis/experiments/k230_rvv_backend/processed/k230_board_summary.json`；`jlq/thesis/experiments/k230_rvv_backend/reports/k230_elf_results.md`；`jlq/thesis/experiments/k230_rvv_backend/provenance/elf_manifest.json`。
- **复现**：`python3 jlq/thesis/experiments/k230_rvv_backend/scripts/run_board_via_serial.py --port /dev/ttyACM1 --output-dir jlq/thesis/experiments/k230_rvv_backend/raw/board_results`，随后运行 `import_board_results.py`。

### 5.19 `thesis.chapter6_external_validation`

- **目的**：对原生 i9 exact-shape BLIS Contract 池和物理 K230 OpenBLAS/RV64GCV 独立 backend 池做冻结外部验证。
- **链路**：frozen generator/package -> target execution -> returned archive/serial CSV -> SHA-256+manifest+binary+coverage audit -> correctness/path/stability -> library boundary。
- **设备/协议**：i9-14900 Ubuntu Linux 与 K230 C908 RT-Smart，单线程 row-major f32，各 10 workloads。
- **结果**：i9 870/870 correctness，生成池/BLIS 为 0.5448 [0.4833, 0.6104]；K230 429/429 correctness，生成 adapter/OpenBLAS 为 0.6730 [0.6193, 0.7253]。两者均 0/10 获胜，形成完整库性能边界而非 speedup claim。
- **i9 结果路径**：`jlq/thesis/experiments/chapter6_external_validation/processed/i9_external_summary.json`；`jlq/thesis/experiments/chapter6_external_validation/processed/i9_external_aggregates.csv`；`jlq/thesis/experiments/chapter6_external_validation/reports/i9_external_results.md`；`jlq/thesis/experiments/chapter6_external_validation/provenance/i9_external_import_manifest.json`。
- **K230 结果路径**：`jlq/thesis/experiments/chapter6_external_validation/processed/k230_external_summary.json`；`jlq/thesis/experiments/chapter6_external_validation/processed/k230_external_aggregates.csv`；`jlq/thesis/experiments/chapter6_external_validation/reports/k230_external_results.md`；`jlq/thesis/experiments/chapter6_external_validation/provenance/k230_external_manifest.json`。
- **原始返回**：`jlq/thesis/experiments/chapter6_external_validation/returned/i9/chapter6-i9-result-20260722T085806Z.tar.gz`，SHA-256 `4d3dc241b12e26bb7da20ee18b07613f8cf38ab449b219194196044d1f21b8c5`；K230 原始串口 CSV 位于 `board_results/`。
- **复现分析**：i9 使用 `python3 jlq/thesis/experiments/chapter6_external_validation/scripts/import_i9_external_results.py <archive>`；K230 使用 `python3 jlq/thesis/experiments/chapter6_external_validation/scripts/import_k230_external_results.py jlq/thesis/experiments/chapter6_external_validation/board_results`。

### 5.20 `thesis.chapter6_application_validation`

- **目的**：把真实 Qwen projection trace、MLIR wrapper closure 和目标 exact-shape 测量连接起来。
- **链路**：Qwen control-flow trace -> 8 canonical workloads -> parameter liveness -> linalg+Transform -> LLVM IR -> OpenBLAS RV64GCV adapter ELF -> K230 closure -> i9/K230 trace-weighted projection。
- **设备/协议**：Qwen trace 本地提取；K230 3 个预声明 direct/fringe case、45 条 board rows；目标投影使用 i9 与 K230 完整 exact-shape 池。
- **结果**：24-block core projection call/FLOP 覆盖 100%；K230 wrapper parity 通过；i9/K230 weighted analysis 状态 PASS。结果是 GEMM 调用轨迹投影，不是端到端模型 latency。
- **结果路径**：`jlq/thesis/experiments/chapter6_application_validation/processed/qwen_trace_summary.json`；`jlq/thesis/experiments/chapter6_application_validation/processed/k230_mlir_closure_summary.json`；`jlq/thesis/experiments/chapter6_application_validation/processed/trace_weighted_summary.json`；`jlq/thesis/experiments/chapter6_application_validation/reports/k230_mlir_closure_results.md`；`jlq/thesis/experiments/chapter6_application_validation/reports/trace_weighted_results.md`；`jlq/thesis/experiments/chapter6_application_validation/reports/application_validation_status.md`。
- **复现分析**：`python3 jlq/thesis/experiments/chapter6_application_validation/scripts/analyze_trace_weighted_results.py --i9-root jlq/thesis/experiments/chapter6_external_validation --k230-root jlq/thesis/experiments/chapter6_external_validation`。

### 5.21 `thesis.transformer_region_go_nogo`

- **目的**：判断 QKV、Gate/Up fan-out 中共享 activation packing 是否值得成为后续主线。
- **链路**：Qwen dimensions -> persistent packed weights -> shared/separate activation packing -> complete BLIS microkernel paths -> go/no-go statistics。
- **设备/协议**：i7-10750H WSL2，单线程 row-major f32，Qwen2.5-0.5B 代表 shape。
- **结果**：在当前 Contract 下拒绝“共享 activation packing”作为独立主贡献；保留为负结果边界，未覆盖低精度、融合 epilogue 或完整 Transformer block。
- **结果路径**：`jlq/thesis/experiments/transformer_region_go_nogo/processed/go_nogo_summary.json`；`jlq/thesis/experiments/transformer_region_go_nogo/raw/region_trials.csv`；`jlq/thesis/experiments/transformer_region_go_nogo/reports/go_nogo_results.md`。
- **复现**：`python3 jlq/thesis/experiments/transformer_region_go_nogo/scripts/run_go_nogo.py`。

## 6. 论文使用边界

- 可以主张：硬兼容性知识能生成合法的 packing/call/direct/adapt 路径，并在第二 BLIS Contract 与独立 OpenBLAS/RV64GCV package 上复用核心空间生成逻辑。
- 可以主张：目标数据校准在部分主机和低预算下提高样本效率，但收益具有环境依赖。
- 必须主张：当前 BLIS-derived 软性能特征相对 Data-only 没有证明额外价值，且校准成本在冻结 horizon 内未摊销。
- 不可主张：生成 schedule 超过完整 BLIS/OpenBLAS；跨全部 x86/RISC-V 的普适性能；多线程、任意 layout/stride/batch；端到端模型加速。
- Chapter 5 的 15.90x 仅相对 scalar-loop dynamic fallback；完整库对照应使用 Chapter 6 external validation。

## 7. GitHub 同步与大文件边界

- GitHub 快照同步脚本、配置、测试、机器可读摘要、报告、provenance、关键原始 CSV 和最新 i9 返回归档。
- 本地编译缓存、工具链、重复解压树、离线部署大包、ELF/object 和高分辨率 TIFF 不进入普通 Git；它们由 provenance 哈希和本地路径追踪。
- 特别排除 `x86_cross_host/dist/thesis-x86-14900-offline-bundle.tar.gz` 及其 `build/offline_cache`，因为这些是可重建基础设施，不是论文结论的最小证据。
- 远端快照的文件清单和 SHA-256 记录在仓库根目录 `SNAPSHOT_MANIFEST.json`。
