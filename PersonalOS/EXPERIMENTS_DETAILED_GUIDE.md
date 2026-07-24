# 全部实验详细说明

> 更新时间：2026-07-24。本文覆盖 PersonalOS 注册表中的 22 个条目，其中包括 21 组本地实验和 1 组论文参考材料，作为实验链路、设备、协议、结果和证据路径的统一入口。本次更新已纳入规范化 Contract 候选池上的冻结离线 BaCO replay。

## 1. 阅读与路径约定

- 本地工作区根目录为 `/buddy-mlir`，下文路径均相对该目录，例如 `jlq/thesis/experiments/chapter6_evaluation`。
- `processed/` 保存机器可读汇总，`reports/` 保存论文可读报告，`provenance/` 保存哈希、版本和导入清单，`raw/` 或 `board_results/` 保存原始测量。
- 总结论入口是 `jlq/thesis/experiments/FINAL_EXPERIMENT_AUDIT.md`。
- 正文证据筛选入口是 `jlq/thesis/experiments/PAPER_EVIDENCE_CATALOG.md`。
- PersonalOS 机器可读注册表位于 `/root/personal-os/PersonalOS/registries/experiments.json`。
- 当前注册实验数为 22，i9-14900 与物理 K230 的冻结目标实验均已返回；冻结的学位论文实验边界内没有待执行硬件实验。

## 2. 总体实验链路

1. 从固定版本的 BLIS 和 OpenBLAS 源码提取微内核尺寸、打包格式、布局约束和缓存分块提示，并记录源码位置与冲突。
2. 将知识分为 Fact、Microkernel Contract 和 Expert Rule。硬 Contract 只描述合法性，软规则只提供排序或采样偏置。
3. 输入 GEMM 的 dtype、M/N/K、布局和目标设备，生成 Generic、Contract-only、Expert-core、Expert+Shell 等候选池。
4. Compatibility Checker 将候选判定为 direct、adapt、fallback 或 reject，并记录每条判定的来源。
5. 调优器在固定候选池和唯一测量预算下选择 tile_m、tile_n、tile_k、packing 等参数；Transform Dialect 将参数物化到 linalg 变换链。
6. 对不被目标执行路径消费的参数进行规范化；离线 replay 只从冻结实测表读取 BaCO 已选择 token 的目标值，不重新编译或进行硬件测量，并按预先冻结协议报告所有结果方向。
7. 合法候选经 packing/call adapter 调用 BLIS 或 OpenBLAS 微内核；不整除 M/N/K 通过 fringe adapt 处理，不满足 Contract 的候选进入 fallback。
8. IR 继续 lowering 到 LLVM IR，链接运行时或目标库，生成 x86 可执行文件或 RV64GCV ELF。
9. 目标机运行 correctness、path、wall-time、GFLOP/s 和稳定性测量；返回包经过 SHA-256、清单、可执行文件和结果覆盖审计。
10. 固定预算比较、D90、time-to-90/95%-oracle、bootstrap 置信区间、消融和校准成本分析生成论文证据。

## 3. 设备与环境矩阵

| 标识 | 设备/环境 | 主要用途 | 关键边界 |
|---|---|---|---|
| `i7_10750h_wsl2` | Intel Core i7-10750H，6C/12T，WSL2，AVX2/FMA | 主要开发主机；Chapter 3-6、f32/f64、BaCO/Optuna、消融 | WSL 定时资格审计失败的 exact-shape 数据只作诊断；其他冻结实验按各自协议使用 |
| `i9_14900_linux` | Intel Core i9-14900，Ubuntu 20.04 原生 Linux，单核绑核 | 第二 x86 主机；跨主机 f64、Transformer exact-shape、同池先验复制 | 单线程、row-major；`perf stat` 因权限不可用，主结果使用 wall time |
| `k230_c908` | K230/C908，RV64GCV，RT-Smart；Linux 侧负责存储/部署 | 物理 RISC-V 正确性、RVV/OpenBLAS、MLIR wrapper closure、exact-shape 池 | 单块开发板和固定工具链，不外推到全部 RISC-V |
| `qemu_riscv64` | QEMU user-mode RV64 | 历史 correctness 与工具链检查 | 不用于真实性能结论 |
| `host_mlir_aot` | x86 主机 MLIR/LLVM AOT | 历史 Transform 到 LLVM 的闭环验证 | 不是 BLIS 替换或正式性能证据 |

## 4. 当前核心结果

- 22 条源码事实完成机器检查和证据分级，其中抽取出的 16 条人工核对项全部签字；BLIS/OpenBLAS 记录 4 类显式冲突。
- 1256 个已测候选的 Checker 预测与运行路径完全一致，协议内 agreement 为 1.000。
- Chapter 5 已实现真实 packing 和 `bli_sgemm_haswell_asm_6x16` 调用；7 个 direct/adapt 动态形状均正确。
- 正式 Chapter 6 覆盖 36 个预声明 f32 workload、固定预算、5 个随机种子、优化动态 MLIR 和完整 BLIS 对照。
- 严格同池实验中，i7 上 B4 相对 B2 在 budget 5/10 分别为 1.058x/1.035x，置信区间均高于 1；i9 上为 0.992x/0.999x，区间跨 1，因此“两环境均显著获益”的预注册条件失败。
- Data-only 在 budget 5 相对 no-prior 为 1.049x，Expert+Data 相对 Data-only 为 1.009x 且区间跨 1；当前 BLIS 软性能特征没有证明额外价值。
- i9 exact-shape 池通过严格导入：870 条 correctness、290 个测量组；生成池/完整 BLIS 几何比为 0.5448，95% CI [0.4833, 0.6104]，0/10 workload 获胜。
- K230 exact-shape 池通过严格导入：429 条 correctness；生成 adapter/完整 OpenBLAS 几何比为 0.6730，95% CI [0.6193, 0.7253]，0/10 workload 获胜。
- K230 MLIR wrapper closure 有 45 条正确结果，C adapter/MLIR adapter 几何时间比为 0.9887，95% CI [0.9765, 1.0009]。
- 校准使平均 time-to-95%-oracle 从 7.90 次候选测量降至 3.08 次，但 591 条校准样本的成本无法在 12 个 holdout workload 内摊销。
- 新增 Contract/空间补充审计：30 个独立 gold case 中 24 个危险变异全部被拒绝或安全降级；36x2600 静态分类后，将微内核路径不活跃的 `vectorize` 规范为 false，Contract 空间由平均 208.7 个候选降至 104.4 个、callable density 为 1.000、规范化 IR 重复率为 0。冻结规范化候选池上的离线 BaCO replay 得到最终 D90=0.1875、time-to-90%-pool-best=8.0；旧 0.1964/11.5 仅作为规范化前消融结果保留。

## 5. 逐项实验说明

### 5.1 `historical.host_mlir_aot`

- **定位**：已归档的早期功能与计时基线，不属于冻结的 Chapter 3 或 Chapter 6 数据。
- **研究问题**：参数化 Transform tiling 能否经 MLIR/LLVM AOT 生成可运行矩阵乘，并在相同 shape 上优于未分块 lowering。
- **输入与变量**：row-major f32，`128x128x128` 和 `256x256x256`；每个 shape 比较 default、`16x16x32`、`32x32x32` 三种 schedule，共 6 个 case。case 清单位于 `jlq/thesis/experiments/config/aot_cases.csv`。
- **对照**：同一 MLIR payload 的 default lowering；没有 BLIS、OpenBLAS 或 microkernel 对照。
- **链路**：静态 `linalg.matmul` -> Transform tiling/vectorization -> LLVM dialect -> LLVM IR -> `clang++ -O3 -march=native` -> host executable。
- **设备与软件**：Intel Core i7-10750H；LLVM/Clang 21.0.0git；显式栈上限 65536 KiB。
- **执行协议**：每个 case 预热 3 次、记录 11 个样本、每个样本调用内核 5 次；只计 AOT 内核调用，输入生成、reference、清零和正确性检查不进入计时。报告 median/min/max/mean/stddev/p90、GFLOP/s、lowering 时间和 native compile 时间。
- **正确性判据**：逐元素与 reference 比较，要求 `abs_diff <= 1e-3 + 1e-4*abs(reference)`；6/6 case 为 `PASS`。
- **量化结果**：128 shape 从 default 2.429 ms 降至 `16x16x32` 的 1.022 ms，约 2.38x；256 shape 从 23.861 ms 降至 `32x32x32` 的 9.506 ms，约 2.51x。最优吞吐分别为 4.103 和 3.530 GFLOP/s。
- **结论边界**：只证明通用 Transform/AOT 闭环与分块有效；LLVM IR 中没有 BLIS 调用，不能作为 library replacement 证据。
- **结果路径**：`jlq/thesis/experiments/results/mlir_aot_benchmark.csv`；`jlq/thesis/experiments/results/mlir_aot_benchmark_summary.md`。
- **复现层级**：完整执行，`bash jlq/thesis/experiments/scripts/run_mlir_aot_benchmark.sh`。

### 5.2 `historical.native_cpp_tile_sanity`

- **定位**：已归档的原生循环 sanity check，用来排除 tile 参数和计时框架的基础错误。
- **研究问题**：在不经过 MLIR 的情况下，相同 tile 值能否正确执行，并呈现符合预期的分块收益方向。
- **输入与变量**：row-major f32，`128^3` 和 `256^3`；default `i-j-k`、`16x16x32`、`32x32x32` 共 6 个 case。
- **对照**：同一 C++ 程序内的 default `i-j-k` 三重循环。
- **链路**：C++ GEMM -> `clang++ -O3 -march=native -std=c++17` -> host executable -> `steady_clock` timing。
- **设备与软件**：Intel Core i7-10750H；Clang 21.0.0git。
- **执行协议**：128 shape 预热 2 次、记录 11 次；256 shape 预热 1 次、记录 7 次；报告 median 和 min。输入在计时外确定性生成，每次计时前清零输出。
- **正确性判据**：与 default 结果计算 `max_abs_diff`；6 个 case 均记录为 0。该历史程序没有设置失败阈值或 `PASS/FAIL` 状态，因此这里只能报告“观测误差为 0”，不能追溯为后期正式 correctness gate。
- **量化结果**：128 shape 的 `32x32x32` 为 1.612 ms，相对 default 2.023 ms 约 1.25x；256 shape 为 18.781 ms，相对 24.584 ms 约 1.31x。
- **结论边界**：只说明原生循环分块和计时程序工作正常，不是 MLIR、BLIS 或调优器性能证据。
- **结果路径**：`jlq/thesis/experiments/results/cpu_initial_results.csv`；`jlq/thesis/experiments/results/cpu_benchmark_summary.md`。
- **复现层级**：完整执行，`bash jlq/thesis/experiments/scripts/run_cpu_benchmark.sh`。

### 5.3 `historical.qemu_rvv_correctness`

- **定位**：已归档的 RV64GC/RV64GCV 模拟器正确性检查。
- **研究问题**：同一确定性 SAXPY-like 加法内核生成 scalar 与 RVV ELF 后，能否在 QEMU user-mode 中返回相同正确结果。
- **输入与变量**：长度 64 的 f32 数组，`a[i]=i`、`b[i]=2i+1`，目标结果 `c[i]=3i+1`；变量是 `-march=rv64gc` 与 `-march=rv64gcv`。
- **对照**：标量 RV64GC ELF；RVV 版本使用 `vlen=128, elen=64` 的模拟 CPU。
- **链路**：freestanding C -> Clang 21 `-O3 -nostdlib -static -ffreestanding` -> ELF -> QEMU 9.2.1 -> exit code。
- **执行协议与判据**：程序逐元素精确比较 64 个结果；无误差则 exit 0。scalar 与 RVV 各运行一次，二者均 exit 0。
- **量化结果**：2/2 ELF 通过；RVV objdump 中有 14 个 RVV-like 指令命中，vectorizer 报告 `vscale x 4`。
- **统计方法**：功能检查，不计时、不做重复实验或置信区间。
- **结论边界**：只证明当前 QEMU/工具链组合的执行正确性，不支持真实板端性能或通用 RVV 兼容性结论。
- **结果路径**：`jlq/thesis/experiments/results/qemu_correctness_check.md`；`jlq/thesis/experiments/outputs/rvv/`。
- **复现层级**：完整执行，`bash jlq/thesis/experiments/scripts/run_qemu_correctness.sh`。

### 5.4 `historical.rvv_toolchain`

- **定位**：已归档的静态工具链能力检查。
- **研究问题**：本地 LLVM 是否注册 RISC-V target，并能把简单 SAXPY loop 自动向量化为 RVV 指令。
- **输入与变量**：单个 f32 SAXPY C loop；固定 `-target riscv64-unknown-elf -march=rv64gcv -mabi=lp64d -O3`。
- **链路**：C -> Clang 21 object -> `llvm-objdump -d --mattr=+v` -> vectorizer remark 与指令匹配。
- **执行协议**：只编译和反汇编，不运行 object；以编译成功、vectorizer remark 和 objdump 指令命中作为静态证据。
- **量化结果**：LLVM 21.0.0git 成功生成 object；vectorization width 为 `vscale x 4`，objdump 中 6 个 RVV-like 命中，包括 `vsetvli`、向量 load/add/store。
- **结论边界**：不证明 QEMU correctness、目标 ABI 完整性或真实板端性能。
- **结果路径**：`jlq/thesis/experiments/results/rvv_toolchain_check.md`；`jlq/thesis/experiments/outputs/rvv/rvv_saxpy.objdump.txt`。
- **复现层级**：完整静态检查，`bash jlq/thesis/experiments/scripts/run_rvv_toolchain_check.sh`。

### 5.5 `historical.transform_rvv_codegen`

- **定位**：已归档的 Transform-to-RVV 静态闭环证据。
- **研究问题**：Transform Dialect 给出的 tile 参数能否消除 `linalg.matmul`，形成 vector/scf/LLVM IR，并最终生成含 RVV 指令的 object。
- **输入与变量**：4 个 smoke case：`128^3` 的 `16x16x32` 与 `32x32x32`、`256^3` 的 `32x32x32`、Qwen-like `1x4096x11008` 的 `1x32x32`。
- **链路**：linalg payload -> Transform tiling/vectorization -> vector/SCF -> LLVM dialect -> LLVM IR -> riscv64 `+v` object -> objdump metrics。
- **设备与软件**：LLVM/MLIR 21.0.0git；静态交叉生成，不在 QEMU 或 K230 上运行。
- **静态协议与判据**：每个 case 只编译一次，不做 runtime 计时；要求 Transform 后不再含 `linalg.matmul`，存在 `vector.contract`/transfer op，LLVM lowering 成功且 object 含 RVV 指令命中。
- **量化结果**：4/4 case 完成；每个 case 有 1 个 `vector.contract`，RVV `vsetvli` 命中 114-796 次、vector 指令命中 3062-10544 次。`scalable_vector_ops=0` 表示 MLIR 层仍是 fixed-size vector，由 LLVM legalize 为 RVV。
- **统计方法**：静态计数，无 runtime、重复测量或性能统计。
- **结论边界**：证明参数进入 codegen，不证明指令质量、正确执行或 target speedup。
- **结果路径**：`jlq/thesis/experiments/results/transform_demo_check.md`；`jlq/thesis/experiments/results/transform_metrics.tsv`。
- **复现层级**：完整静态生成，`bash jlq/thesis/experiments/scripts/run_transform_demo.sh`。

### 5.6 `paper.transform_dialect_section_4_5`

- **定位**：参考材料与接口来源，不计入本课题本地性能实验；保留注册 ID 只是为了统一索引来源证据。
- **研究问题**：CGO 2025 论文第 4.5 节如何把外部 BaCO 配置写入参数化 Transform script，并把编译/运行结果返回调优器。
- **原论文输入**：固定 f32 batch matmul，`B=6, M=196, N=256, K=2304`。
- **搜索变量**：`tile0`-`tile3` 对应 B/M/N/K，`do_vect` 控制 vectorization；0 表示不对该维分块。按当前 JSON 约束枚举，条件过滤后为 25000 种组合。
- **原协议**：BaCO random design 10 点、200 个 optimization iterations；每个配置实例化 Transform、重新编译、运行 C driver 15 次并返回 runtime 中位数与 `Valid`。driver 没有 warmup、CPU affinity 或数值 reference。
- **链路**：`search_settings.json` -> BaCO config -> 文本实例化 Transform -> `mlir-transform-opt` -> LLVM IR -> clang executable -> runtime/`Valid` -> best-so-far 曲线。
- **论文结果**：第 4.5 节报告最终 1.68x；该数字属于论文原实验，不是本课题测量结果，也不同于第 4.4 节的 libxsmm replacement 结果。
- **可复用内容**：payload/schedule 分离、条件参数、`config -> objective + feasibility` evaluator、编译失败反馈和 best-so-far 曲线。
- **不可直接复用**：本地提取目录缺少 `run_with_timeout.py`、`batch_matmul.c`、`batch_matmul.mlir`，并存在脆弱文本替换、`Valid` 不等于 correctness、无效 runtime=0 和 MemRef descriptor 风险。
- **结论边界**：这些材料支持本课题接口设计来源，不能宣称已复现 1.68x，也不能证明 `transform.to_library` 或实际 library replacement。
- **结果路径**：`jlq/thesis/experiments/4.5/REUSABLE_NOTES.md`；`jlq/thesis/experiments/4.5/parametric_transform.mlir`；`jlq/thesis/experiments/4.5/search_settings.json`。
- **复现层级**：无独立本地复现；只进行 source-grounded extraction 和接口映射。

### 5.7 `thesis.chapter3_rules`

- **定位**：Chapter 3 的主要方法证据，覆盖知识抽取、schema、验证和预备 MLIR 实证。
- **研究问题**：BLIS 源码知识能否被结构化为可追溯 Fact、硬 Microkernel Contract 和软 Expert Rule，并在编译前排除不兼容调度。
- **输入与变量**：BLIS Haswell f32/f64；预备实证含 8 个 f32 shape：4 个 square、3 个 rectangular/projection 和 `192x256x256` anchor。每个 shape 的通用空间为 336 个候选。
- **知识验证**：共 22 条事实、2 个 Contract、5 条 Rule；E1/E2/E3 证据分别为 14/4/4；16 条人工核对全部签字，机器检查与作者确认分开记录；保留 5 个显式 ambiguity。
- **实验链路**：BLIS source -> extractor -> facts/contracts/rules -> checker -> 参数化 Transform -> LLVM IR -> clang AOT -> correctness/path/performance。
- **设备与软件**：Intel Core i7-10750H WSL2，CPU 0，单线程环境，f32 row-major。
- **执行协议**：seed 17；每个 shape 抽样 6 个可执行候选并保留 2 个策略拒绝，共 48 个实际 AOT 候选和 16 个 `STATIC_REJECT`；每个候选预热 1 次、记录 3 次、每次 3 个 inner iterations。
- **正确性与路径判据**：AOT driver 逐元素要求 `abs_diff <= 1e-3 + 1e-4*abs(reference)`；LLVM IR/符号检查决定是否发生 microkernel replacement，不能用 checker 的 predicted path 代替 observed path。
- **量化结果**：规则使每 shape 的 336 点空间缩减 16.7%-37.5%；48/48 编译并正确，16/16 策略拒绝；replacement 0/48、fallback 48/48；相对 default speedup 中位数 1.683x，归一化性能中位数 0.265，native compile 中位数 2955.9 ms/候选。
- **结论边界**：支持知识可追溯性和编译前约束价值；当时尚无 packing/call adapter，因此 100% fallback 是系统边界，不是专家 Contract 失效。
- **结果路径**：`jlq/thesis/experiments/chapter3_rules/data/preliminary_shapes.yaml`；`jlq/thesis/experiments/chapter3_rules/processed/preliminary_summary.json`；`jlq/thesis/experiments/chapter3_rules/reports/chapter3_preliminary_results.md`；`jlq/thesis/experiments/chapter3_rules/verification/validation_report.json`。
- **复现层级**：完整执行，`python3 jlq/thesis/experiments/chapter3_rules/scripts/run_chapter3.py`。

### 5.8 `thesis.chapter3_multisource`

- **定位**：Chapter 3 的多来源反例与知识分类证据。
- **研究问题**：BLIS 与 OpenBLAS 在相同 ISA/dtype 上是否给出一致的 register tile 和 blocking；哪些字段能作为硬兼容知识，哪些只能作为来源标记的软性能提示。
- **固定来源**：BLIS revision `36df51a81cc732eeadbf2e6732941dd5400db47d`；OpenBLAS revision `b338322e9afc063d95e2c117e85bedf28213295a`。
- **输入与变量**：抽取 4 个 SGEMM Contract：BLIS Haswell 6x16、BLIS RVV128 16x4、OpenBLAS Haswell 8x4、OpenBLAS ZVL128B 8x8；比较 register tile 与缓存 blocking。
- **冲突对照**：共 4 类冲突，分别是 Haswell/RVV128 的 register tile 冲突和 cache blocking 冲突。前者保留为 backend-specific hard Contract，后者保留为 source-labelled soft prior。
- **运行验证链路**：固定 OpenBLAS -> 单线程 `cblas_sgemm` -> 4 个 row-major f32 shape -> scalar double-accumulation reference -> timing/正确性。
- **执行协议**：shape 为 `63x67x65`、`192x256x256`、`257x193x129`、`512^3`（按 MxKxN）；每个 shape 先做一次 correctness call，再记录 7 个 trial，共 28 行。OpenBLAS 以 `TARGET=HASWELL, USE_THREAD=0, NUM_THREADS=1` 构建。
- **正确性判据**：`max_abs_error <= 2e-4*max(K,1)`；28/28 trial 正确。
- **量化结果**：4 个 shape 的中位吞吐分别为 45.26、46.68、59.67、55.08 GFLOP/s；抽取 4 facts、4 Contracts、4 conflicts。
- **结论边界**：证明多来源知识不能无条件合并；运行 probe 只验证 OpenBLAS frontend，不验证固定 blocking 的跨库性能迁移。
- **结果路径**：`jlq/thesis/experiments/chapter3_multisource/data/multisource_facts.yaml`；`jlq/thesis/experiments/chapter3_multisource/data/conflicts.yaml`；`jlq/thesis/experiments/chapter3_multisource/processed/summary.json`；`jlq/thesis/experiments/chapter3_multisource/processed/openblas_validation_summary.json`；`jlq/thesis/experiments/chapter3_multisource/reports/multisource_results.md`。
- **复现层级**：完整抽取与已有库验证，`python3 jlq/thesis/experiments/chapter3_multisource/scripts/run_multisource.py --skip-openblas-build`；去掉 `--skip-openblas-build` 才会重新构建 OpenBLAS。

### 5.9 `thesis.chapter4_space`

- **定位**：Chapter 4 的核心空间生成与调优器接口实验。
- **研究问题**：硬 Contract 与软 Expert Rule 分别能将 2600 点通用空间缩小到何种规模；空间是否能无损导出给未修改的 BaCO evaluator。
- **搜索变量**：`tile_m` 13 值、`tile_n` 10 值、`tile_k` 5 值、`pack_mode={none,ab}`、`vectorize={false,true}`，笛卡尔积为 2600。B1 为可执行 Generic，B2 为 Contract-only，B3 为 Expert-core，B4 为 Expert-core 加确定性 10% exploration shell。
- **任务与候选数**：anchor f32 为 `2400/560/224/249`，triple-tail 为 `1584/336/28/32`，small 为 `576/96/43/48`，rect 为 `840/160/80/89`，anchor f64 为 `2400/700/259/288`，feature-mismatch 为 `2400/0/0/0`；顺序均为 B1/B2/B3/B4。
- **链路**：task+Contract+rules -> finite enumeration -> checker direct/adapt/fallback/reject -> expert score/shell -> provenance -> Transform instance -> BaCO token callback。
- **设备与协议**：i7-10750H WSL2，seed 41，CPU 0，单线程。3 个 path case 每个预热 1 次、记录 2 次、inner iterations=2。
- **对照与判据**：feature-mismatch 保留 2400 个 Generic fallback，检验 Contract 空空间不会阻塞通用 lowering；direct/adapt/fallback 的 observed path 由 LLVM IR 中 BLIS 调用决定，correctness 使用完整 reference gate。
- **BaCO smoke**：anchor B4 完整空间 249 点；为限制 IR 膨胀声明 6 点 pool，预算 6，DOE 4，seed 41；6/6 valid，但只有 4 个 unique schedule callback、2 次重复；最佳记录为 `m168_n192_k256_pab_v1`，17.519 ms。
- **量化结果**：anchor f32 的 B2/B3/B4 相对 raw 缩减 78.46%/91.38%/90.42%；triple-tail 为 87.08%/98.92%/98.77%；feature-mismatch 的 Contract 空间为 0。3 个 Transform case 全部正确，但 observed path 均为 fallback。
- **结论边界**：证明空间构造、条件域、来源记录和 BaCO 接口；由于本阶段没有真实 packing/call adapter，不能用其 path 结果宣称 BLIS replacement 或正式收敛优势。
- **结果路径**：`jlq/thesis/experiments/chapter4_space/data/space_configs.json`；`jlq/thesis/experiments/chapter4_space/processed/space_summary.json`；`jlq/thesis/experiments/chapter4_space/processed/baco_tuning_summary.json`；`jlq/thesis/experiments/chapter4_space/processed/transform_paths_summary.json`；`jlq/thesis/experiments/chapter4_space/reports/chapter4_results.md`。
- **复现层级**：完整执行，`python3 jlq/thesis/experiments/chapter4_space/scripts/run_chapter4.py`。

### 5.10 `thesis.chapter5_blis_adapter`

- **定位**：Chapter 5 的真实 BLIS packing/call adapter 与动态 fringe 实验。
- **研究问题**：经过 checker 选择的参数能否生成 BLIS 6x16 所需 A/B panel，调用真实 `bli_sgemm_haswell_asm_6x16`，并对非整除 M/N/K 正确执行 adapt。
- **输入与对照**：row-major f32、单线程。静态 anchor `192x256x256` 比较 vectorized fallback 与 direct BLIS；动态实验比较同一个 scalar-loop dynamic fallback binary 和同一个 dynamic BLIS binary。
- **动态 shape**：direct 为 `48x64x64`、`96x128x128`、`192x256x256`；adapt 为 `48x67x64`、`50x64x70`、`190x250x250`、`19x65x17`，按 MxKxN。
- **链路**：checked schedule -> pack A/B -> BLIS 6x16 main kernel -> K/M/N fringe accumulation/scatter -> full reference -> path/symbol/fringe counters。
- **设备与协议**：i7-10750H WSL2，CPU 0。静态默认预热 3 次、记录 11 次；动态每个 binary/shape 预热 2 次、记录 9 次、独立运行 3 个 trial，共 42 trial rows。
- **正确性判据**：逐元素要求 `abs_diff <= 1e-3 + 1e-4*abs(reference)`；同时检查 LLVM IR wrapper call、链接符号、observed direct/adapt 和 fringe call 解析值。全部 trial 通过。
- **统计方法**：每个 trial 取 9 次中位数；shape 级 speedup 取几何平均；10000 次 shape bootstrap，seed 20260714，重采样单位是 shape 而非 host。
- **量化结果**：静态 direct 为 0.728 ms/34.58 GFLOP/s，相对 fallback 13.561 ms 为 18.63x。动态 7-shape 几何平均 15.905x，95% CI [10.250,22.036]；direct 21.941x，adapt 12.495x。
- **结论边界**：动态 15.905x 的对照是 scalar-loop fallback，不是优化 dynamic MLIR 或完整 `bli_sgemm`；只覆盖 f32 rank-2 row-major、固定 Haswell 6x16 和单线程。
- **结果路径**：`jlq/thesis/experiments/chapter5_blis_adapter/data/dynamic_shapes.json`；`jlq/thesis/experiments/chapter5_blis_adapter/processed/chapter5_summary.json`；`jlq/thesis/experiments/chapter5_blis_adapter/processed/dynamic_multishape_summary.json`；`jlq/thesis/experiments/chapter5_blis_adapter/reports/chapter5_results.md`；`jlq/thesis/experiments/chapter5_blis_adapter/reports/dynamic_multishape_results.md`。
- **复现层级**：完整执行，`python3 jlq/thesis/experiments/chapter5_blis_adapter/scripts/run_chapter5_full.py`；`--quick` 只用于 smoke，不可替代冻结统计。

### 5.11 `thesis.chapter4_5_integrated`

- **定位**：Chapter 4 候选/BaCO 与 Chapter 5 真实 evaluator 的最小集成闭环。
- **研究问题**：未修改的 BaCO callback 是否能消费 Expert+Shell token，并实际触发 direct、adapt 和 fallback 三种运行路径，而不只是离线查询性能表。
- **输入与对照**：3 个路径 case：anchor `192x256x256` + packed/vector candidate 预期 direct；tail `190x250x250` + 同 candidate 预期 adapt；feature-mismatch + `pack=none,vectorize=false` 预期 fallback。
- **BaCO pool**：6 个预声明候选，其中 4 个 `pack=ab` core 和 2 个 `pack=none` shell；预算 6，seed 41，source space 为 249 点 B4。
- **链路**：B4 candidate token -> BaCO callback -> checker -> Transform/LLVM -> real BLIS pack/call 或 generic fallback -> correctness/path/fringe -> objective 回传。
- **执行协议**：i7-10750H WSL2，CPU 0，单线程；每个测量预热 1 次、记录 3 次、inner iterations=1。
- **正确性与路径判据**：使用 Chapter 5 full-reference gate；LLVM IR 和最终符号确认 BLIS replacement，adapt 还核对 fringe call 数。
- **路径矩阵结果**：direct anchor 为 direct、0.441 ms、0 fringe；tail 为 adapt、0.410 ms、752 fringe；feature-mismatch 为 fallback、14.875 ms。3/3 correctness 与 predicted/observed path 均一致。
- **BaCO 结果**：6/6 callback 有效，observed 为 5 direct、1 fallback，5 次真实 microkernel evaluation；最优 `m24_n32_k64_pab_v1` 为 0.441 ms。
- **结论边界**：证明真实 evaluator 集成，不是正式多空间、多 seed 收敛实验；6 点 timing 不用于普遍性能结论。
- **结果路径**：`jlq/thesis/experiments/chapter4_5_integrated/data/integration_config.json`；`jlq/thesis/experiments/chapter4_5_integrated/raw/path_matrix.csv`；`jlq/thesis/experiments/chapter4_5_integrated/raw/baco_callback_log.jsonl`；`jlq/thesis/experiments/chapter4_5_integrated/processed/integrated_summary.json`；`jlq/thesis/experiments/chapter4_5_integrated/reports/integrated_results.md`。
- **复现层级**：完整执行，`python3 jlq/thesis/experiments/chapter4_5_integrated/scripts/run_integrated_pipeline.py`。

### 5.12 `thesis.chapter6_evaluation`

- **定位**：冻结的 Chapter 6 单主机正式评估，回答空间质量、固定预算搜索、基线、消融、holdout 和开销问题。
- **研究问题**：B1 Generic、B2 Contract-only、B3 Expert-core、B4 Expert+Shell 在相同预算下的有效候选密度和 best-so-far 如何；硬/软知识各贡献什么；结果距离优化动态 MLIR 和完整 BLIS 多远。
- **工作负载**：36 个预声明 row-major f32 shape，按 15 design、9 validation、12 holdout 切分，覆盖 square、M/N skinny、small-K、tail 和 model-rect；其中 8 个 tune shape 用于正式 B1-B4 曲线。
- **方法与对照**：B0 为 scalar dynamic MLIR；B1-B4 为同一真实候选语料上的不同空间/先验；B5 为完整 `bli_sgemm`。另有 tile `24x32x64`、vector<8xf32> FMA 的优化 dynamic MLIR baseline。
- **候选与链路**：每个 workload 的冻结 pool 上限 28；8 个 tune shape 每种方法共 224 个候选。每个 objective 都来自真实 Transform -> LLVM -> clang -> BLIS adapter 执行，再做离线 BaCO replay，避免不同 seed 重复编译相同候选。
- **设备与协议**：i7-10750H WSL2，CPU 0，单线程；每个候选预热 2 次、记录 7 次、3 个独立 process trials。完整 reference 判据为 `abs_diff <= 1e-3 + 1e-4*abs(reference)`。
- **搜索协议**：B1-B4 均使用 budget 25、seeds `[11,29,41,73,101]`；BaCO 3.0.0 categorical schedule ID + GPy。共 680 个 run；尽管禁止重复，仍记录到 370 次重复 callback，分析同时保留 callback budget 和 unique candidate 数。数值 jitter fallback 触发 1292 次并单独披露。
- **统计方法**：10000 次 bootstrap，seed 20260714；固定预算区间重采样 workload/seed，不重采样机器；未达到 90%-oracle 的 run 以 26 右删失。
- **空间质量结果**：B1/B2/B3/B4 的 D90 为 2.7%/19.6%/4.5%/6.7%，候选池归一化性能几何均值为 0.082/0.571/0.466/0.445。Checker 在 1256 个已测 candidate/workload 上 agreement=1.000。
- **固定预算结果**：best-at-25 相对 B5 为 B1 0.781 [0.688,0.887]、B2 0.948 [0.858,1.043]、B3 0.791 [0.702,0.889]、B4 0.800 [0.713,0.895]；达到 90%-pool-best 的中位测量数为 10.5/11.5/6.0/7.0。
- **基线与消融**：优化 dynamic MLIR 在 36/36 shape 胜过 scalar，几何加速 7.710x，但只达到完整 BLIS 的 0.184。移除 packing rule 使 B4 normalized gmean 从 0.800 降至 0.046；12-shape zero-shot 相对 B5 为 B1/B2/B3/B4=0.224/0.474/0.282/0.364。
- **结论边界**：该实验显示 B2 在原异构空间协议中最强，不能据此宣称静态 B3/B4 普遍优于 B2。CI 只反映 workload/seed 变化，不反映 host 变化。
- **结果路径**：`jlq/thesis/experiments/chapter6_evaluation/data/experiment_config.json`；`jlq/thesis/experiments/chapter6_evaluation/data/workloads.json`；`jlq/thesis/experiments/chapter6_evaluation/processed/chapter6_summary.json`；`jlq/thesis/experiments/chapter6_evaluation/processed/fixed_budget_summary.csv`；`jlq/thesis/experiments/chapter6_evaluation/processed/holdout_zero_shot.csv`；`jlq/thesis/experiments/chapter6_evaluation/reports/chapter6_results.md`。
- **复现层级**：完整执行，`python3 jlq/thesis/experiments/chapter6_evaluation/scripts/run_chapter6.py`；耗时较长，离线 replay 不代表 objective 未真实测量。

### 5.13 `thesis.chapter6_online_prior`

- **定位**：同主机软先验校准研究，复用 Chapter 6 的真实 f32 候选语料。
- **研究问题**：静态 BLIS score 是否能直接迁移；离线目标数据校准是否改善低预算排序；在线反馈能否纠正误导先验且不破坏硬 Contract。
- **语料与切分**：36 workloads x 28 candidates=1008 case；design 420、validation 252、holdout 336，分别对应 15/9/12 workloads。design 拟合 posterior，validation 选择超参数，holdout label 不参与训练或选择。
- **方法与对照**：C0 seeded random；C1 static BLIS；C2 offline calibrated；C3 每次选择后更新的 online calibrated；C4 reflected/misleading posterior negative control。全部使用相同 Contract-only pool。
- **实验链路**：Chapter 6 真实候选语料 -> design posterior 拟合 -> validation 超参数选择 -> holdout 顺序揭示 objective -> offline/online posterior 更新 -> 固定预算配对统计。
- **测量协议**：继承 Chapter 6 的 CPU 0、单线程、2 warmups、7 repeats、3 process trials；本实验默认从 1008 个真实测量 case 做顺序 replay。budget 25、5 seeds，并报告 checkpoint 5/25。
- **泄漏控制**：holdout outcome 在候选被策略选中后才揭示；用于 fit 和 hyperparameter selection 的 holdout outcome 均为 0。trace 共 13125 行。
- **模型与统计**：57 个特征；validation 选择 prior precision 10.0、Thompson temperature 0.25；报告 Spearman、simple-regret AUC 和 workload bootstrap 95% CI。
- **量化结果**：best-at-5 相对 B5：random 0.493、static 0.503、offline 0.568、online 0.563、misleading 0.357；相对 pool-best 为 0.845/0.863/0.974/0.966/0.613。best-at-25 的前四者均达到 0.993-1.000 pool-best，misleading 恢复到 0.983。
- **排序结果**：holdout mean Spearman 从 static 0.167 提升到 calibrated 0.685；offline/online 相对 random 的 budget-5 配对结果由 CGO extension 正式 bootstrap 为 1.192x/1.155x。
- **结论边界**：支持“目标数据校准提高同主机低预算排序”，不支持“在线一定优于已训练离线 posterior”或跨主机泛化。
- **结果路径**：`jlq/thesis/experiments/chapter6_online_prior/data/online_prior_config.json`；`jlq/thesis/experiments/chapter6_online_prior/processed/online_prior_summary.json`；`jlq/thesis/experiments/chapter6_online_prior/processed/rank_correlations.csv`；`jlq/thesis/experiments/chapter6_online_prior/raw/online_prior_traces.csv`；`jlq/thesis/experiments/chapter6_online_prior/reports/online_prior_results.md`。
- **复现层级**：`python3 jlq/thesis/experiments/chapter6_online_prior/scripts/run_online_prior.py --skip-measure` 只重放已有真实语料；去掉 `--skip-measure` 才包含缺失候选的实际测量。

### 5.14 `thesis.cgo_local_extension`

- **定位**：面向更严格投稿标准的本地扩展，补充第二 dtype/Contract、真正在线 objective 和现有调优器对照。
- **研究问题**：f32 结论能否扩展到 f64 6x8；校准方法在 fresh subprocess 下是否仍优于 random；与 Optuna TPE 相比是否有显著优势；多源性能提示能否直接合并。
- **输入与 Contract**：36 个 row-major f64 workload，BLIS Haswell `bli_dgemm_haswell_asm_6x8`，MR=6、NR=8、K step=4；生成 128 个 candidate binaries、3132 trial rows、1044 aggregate rows。
- **方法与对照**：C0 random、C1 static BLIS、C2 offline calibrated、C3 true-online calibrated；D1 为 Optuna 4.9.0 `TPESampler`，5 个 startup trials；另比较 conflict-aware、BLIS-only、OpenBLAS-only、naive merge 和 calibrated source prior。
- **实验链路**：f64 6x8 Contract -> 候选与 adapter 生成 -> Transform/LLVM/AOT -> fresh subprocess objective -> C0-C3 与 Optuna 同预算搜索 -> 配对 bootstrap 与多源消融。
- **测量协议**：i7-10750H WSL2，CPU 0，单线程；2 warmups、7 repeats、3 process trials；budget 25、seeds `[11,29,41,73,101]`，checkpoint 5/10/15/25。
- **公平预算**：12 个 holdout x 4 方法 x 5 seeds x 25=6000 个 true-online fresh subprocess rows，objective cache hit=0；Optuna 对 535 个重复 callback 做 prune/resample，最终 1500 个唯一 measurement，cache hit=0。
- **正确性与路径**：f64 direct/adapt prediction 与 observed path 完全一致，756 direct、2268 adapt trial rows。
- **统计方法**：60 个 workload-seed pair 做配对 workload bootstrap；speedup>1 表示左方法更好，只有 CI 完全高于 1 才称显著。
- **量化结果**：f64 pool-best/完整 BLIS 几何均值 1.064。budget 5 时 offline/random=1.192 [1.055,1.343]，online/random=1.155 [1.042,1.277]，online/Optuna=1.038 [0.920,1.159]；budget 25 的 online/Optuna=0.973 [0.936,1.006]。
- **多源结果**：budget 5 时 BLIS-only/naive=1.063 [1.029,1.103]，calibrated/naive=1.067 [1.018,1.125]，但 calibrated/BLIS-only=1.003 [0.986,1.021]。
- **结论边界**：证明低预算相对 random 的本地收益和 naive merge 的风险；不证明普遍优于 Optuna，也不把互不兼容的 kernel ABI 合并。
- **结果路径**：`jlq/thesis/experiments/cgo_extension/data/experiment_config.json`；`jlq/thesis/experiments/cgo_extension/processed/cgo_extension_summary.json`；`jlq/thesis/experiments/cgo_extension/processed/f64_contract_summary.json`；`jlq/thesis/experiments/cgo_extension/processed/paired_bootstrap_comparisons.csv`；`jlq/thesis/experiments/cgo_extension/reports/cgo_extension_results.md`。
- **复现层级**：完整执行，`python3 jlq/thesis/experiments/cgo_extension/scripts/run_local_extension.py`。

### 5.15 `thesis.x86_cross_host`

- **定位**：第二 x86 主机复制实验，用于区分硬兼容迁移和性能排序迁移。
- **研究问题**：相同 f64 6x8 Contract 在两机上是否保持 legality/path agreement；本地主机训练或源码导出的性能排序是否保持；budget-5 样本效率趋势能否复制。
- **设备与固定版本**：i7-10750H WSL2 与 i9-14900 Ubuntu 20.04 native Linux，单线程、row-major、CPU 0。固定 Buddy `d7bb40c`、LLVM `09b849a`、BLIS `36df51a`、mimalloc `81a7711`。
- **输入与方法**：两机使用相同 36 个 f64 workload、BLIS Haswell 6x8 Contract、28 点候选域、C0-C3 与 Optuna TPE、budget 25、5 seeds。
- **实验链路**：冻结源码与环境清单 -> i7/i9 各自构建相同候选 -> 目标机 fresh objective -> 结果归档和 SHA-256 校验 -> 同 workload/seed 配对跨主机报告。
- **测量协议**：每个 candidate 2 warmups、7 repeats、3 process trials；两机各 3132 Contract rows、6000 true-online fresh rows、1500 Optuna unique rows，objective cache hit 均为 0。
- **导入完整性**：i9 返回归档 SHA-256 为 `b63499c2209f08b41c0d834bd68e391a636d969c50fffd60c266e18b2970baee`；importer 验证 CPU、revision、清单、结果覆盖和正式 summary。
- **硬知识结果**：两机 direct/adapt predicted/observed agreement 均为 1.000。
- **性能排序结果**：生成 pool-best/完整 BLIS 从 i7 的 1.064 反转为 i9 的 0.804，说明绝对 schedule 排名不是 host-independent 常量。
- **固定预算结果**：online/random budget 5：i7 1.155 [1.042,1.277]，i9 1.060 [1.040,1.082]；online/Optuna budget 5：i7 1.038 [0.920,1.159]，i9 1.065 [1.044,1.089]。budget 25 时 i9 online/random=0.991 [0.984,0.999]。
- **结论边界**：支持硬兼容跨 x86 主机迁移和低预算趋势；不支持 host-independent 排名、普遍优于 Optuna、多线程或所有 x86 泛化。
- **结果路径**：`jlq/thesis/experiments/x86_cross_host/results/thesis-x86-result--20260716T115026Z.tar.gz`；`jlq/thesis/experiments/x86_cross_host/processed/cross_host_summary.json`；`jlq/thesis/experiments/x86_cross_host/reports/cross_host_results.md`；`jlq/thesis/experiments/x86_cross_host/processed/latest_import.json`；`jlq/thesis/experiments/x86_cross_host/TARGET_MACHINE_OPERATION_GUIDE.md`。
- **复现层级**：目标机完整执行按 operation guide；`python3 jlq/thesis/experiments/x86_cross_host/scripts/build_cross_host_report.py` 只使用已导入两机 summary 重建对比报告。

### 5.16 `thesis.chapter6_same_pool_prior`

- **定位**：修复原 B2/B3/B4 非同池问题后的两环境正式 acceptance 实验。
- **研究问题**：在候选池、唯一测量预算和 oracle 全部相同后，static prior 或 calibrated prior 是否仍比无先验 BaCO 有显著低预算收益，并在两台主机复制。
- **环境与语料**：i7-10750H WSL2 和 i9-14900 Linux 的完整 f64 BLIS 6x8 corpus；使用相同 15 design、9 validation、12 holdout workload 切分。
- **活性审计**：只搜索 `tile_m/tile_n/tile_k`；`vectorize` 因 adapter 不消费而移除，`pack_mode=ab`、MR=6、NR=8 为硬 Contract 固定项，predicted path 由 checker 推导。每 workload canonical pool 为 23-26 个 active schedules。
- **严格对照**：B2 无先验 DOE；B3 static-prior warm start；B4 calibrated-prior warm start。三者之后都在同一 pool 上运行 BaCO EI/EI-PIBO，共享 posthoc oracle。
- **实验链路**：参数活性审计 -> 两机 canonical pool 归一化 -> B2/B3/B4 不同 warm start -> 同一 BaCO/acquisition 与唯一预算 -> holdout 泄漏审计 -> 公共 oracle 配对统计。
- **搜索协议**：unique budget 10，checkpoints 5/10，DOE 4，seeds `[11,29,41,73,101]`；BaCO 3.0.0/GPy，禁止 duplicate callback，发现重复即实验失败。
- **校准与泄漏控制**：design fit、validation 选择 model weight 0.25，holdout target 在 BaCO 返回 token 后才读取；prior target 向量的 holdout 项为 `NaN`。两环境 holdout prior reads=0。
- **统计方法**：20000 次 workload-cluster bootstrap，seed 20260718；预注册门槛要求 B4/B2 在 budget 5 或 10 的 CI lower>1，且至少两个环境满足。
- **池效率结果**：i7 B2/B4 relative-to-oracle 为 budget 5 的 0.923/0.976、budget 10 的 0.963/0.997；i9 为 0.982/0.975 和 0.993/0.992。
- **配对结果**：i7 B4/B2 为 1.058 [1.027,1.092]、1.035 [1.011,1.064]；i9 为 0.992 [0.977,1.007]、0.999 [0.990,1.006]。
- **Acceptance**：参数活性、严格同池、唯一预算、零泄漏和公共 oracle 均 `PASS`；双环境收益条件 `FAIL`，因此 overall status=`FAIL`。
- **结论边界**：i7 的本地收益成立，但不能宣称在两个 x86 环境稳定复制；该科学失败不是运行故障。
- **结果路径**：`jlq/thesis/experiments/chapter6_same_pool_prior/data/experiment_config.json`；`jlq/thesis/experiments/chapter6_same_pool_prior/processed/acceptance_summary.json`；`jlq/thesis/experiments/chapter6_same_pool_prior/processed/parameter_liveness.csv`；`jlq/thesis/experiments/chapter6_same_pool_prior/processed/paired_comparisons.csv`；`jlq/thesis/experiments/chapter6_same_pool_prior/reports/acceptance_report.md`。
- **复现层级**：完整 replay，`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 jlq/thesis/experiments/chapter6_same_pool_prior/scripts/run_experiment.py`；因科学门槛未满足而非零退出是预期行为。

### 5.17 `thesis.chapter6_termination_validation`

- **定位**：决定软专家性能规则、校准经济性和第二 Contract 扩展是否继续作为贡献的三个预注册终止实验。
- **研究问题**：Expert+Data 是否显著优于只使用目标数据的 Data-only；前期校准成本能否由后续搜索节省摊销；增加 f64 6x8 是否只需 Contract/kernel/adapter 而不改核心 generator。
- **环境与公共知识**：i7-10750H WSL2，单线程 f64，12 holdout workloads；三方法共享相同 hard Contract、`pack_mode=ab`、MR=6/NR=8、direct/adapt legality 和 canonical pool。
- **方法**：B2 no-prior；D0 Data-only 使用目标数据、geometry 和 workload-family 特征；D1 Expert+Data 在相同数据上增加 `active_static_score` 与 family-static interaction。
- **实验链路**：同池 f64 corpus -> D0/D1 特征训练和 holdout 搜索 -> time-to-95% 轨迹 -> 校准成本/节省测量摊销 -> 未修改 generator 的 f64 6x8 Contract 扩展审计。
- **搜索协议与统计**：DOE 4、5 seeds、checkpoints 5/10，并运行 full-pool trajectory；20000 次 workload-cluster bootstrap，seed 20260719。D1/D0 要在两个 checkpoint 的 CI lower 均大于 1 才通过。
- **Data-only 消融结果**：budget 5 的 D0/D1 oracle fraction 为 0.9682/0.9764，D1/D0=1.0085 [0.9992,1.0266]；budget 10 均为 0.9968，D1/D0=1.0000 [0.9999,1.0000]。专家性能特征增量门槛失败，决策 `STOP`。
- **time-to-95% 结果**：B2 平均/中位/p90 为 7.90/5.0/16.1 次；D0 为 3.08/2.0/8.0；D1 为 3.08/2.5/6.0。
- **成本核算**：D0/D1 都使用 591 个 calibration target rows，完整观测成本 531.95/531.97 s；每个 holdout 平均节省 4.817 次测量，但含编译成本的 break-even 为 2293.6/2339.0 个 workload，无法在冻结的 12 workload 内摊销，决策 `STOP`。
- **第二 Contract 结果**：f64 6x8 使用未修改核心 generator 生成 36 workloads、1008 pool rows（252 direct、756 adapt）；128 binaries、3132 trial rows全部 path-match，决策 `GO`。
- **独立后端边界**：f32 6x16 与 f64 6x8 都属于 BLIS Haswell；该项不是第二 library/ISA，独立 backend 在本实验中为 `NOT_TESTED`。
- **总体状态**：`MIXED`，对应 Expert 增量 STOP、实际摊销 STOP、第二 Contract GO。
- **结果路径**：`jlq/thesis/experiments/chapter6_termination_validation/data/experiment_config.json`；`jlq/thesis/experiments/chapter6_termination_validation/processed/acceptance_summary.json`；`jlq/thesis/experiments/chapter6_termination_validation/processed/time_to_95_summary.csv`；`jlq/thesis/experiments/chapter6_termination_validation/processed/calibration_costs.csv`；`jlq/thesis/experiments/chapter6_termination_validation/processed/second_microkernel_audit.json`；`jlq/thesis/experiments/chapter6_termination_validation/reports/termination_validation_report.md`。
- **复现层级**：完整 replay/audit，`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 jlq/thesis/experiments/chapter6_termination_validation/scripts/run_termination_validation.py`。

### 5.18 `thesis.k230_rvv_backend`

- **定位**：独立于 x86/BLIS 的物理 RISC-V 后端验证，用于检查硬 Contract、候选生成、fringe adapter 和固定性能先验的跨架构行为。
- **研究问题**：相同的合法性知识能否生成可在 K230 C908 上运行的 scalar/RVV/OpenBLAS 路径；x86 库配置中得到的固定 schedule 是否仍能可靠排序 RISC-V 候选。
- **工具链与设备**：物理 K230 C908、RT-Smart；K230 SDK revision `7e302f733311d284be255f0d81d3463b6ae6ee6d`，GCC 12.0.1 prerelease，OpenBLAS revision `b338322e9afc063d95e2c117e85bedf28213295a`，目标为 `RISCV64_ZVL128B`。
- **候选池**：每个 workload 评估 `scalar`、`rvv_generic_16x16x64`、`rvv_generic_32x32x128`、`rvv_blis_16x4x640`、`rvv_openblas_8x8x240`、`rvv_cross_source_16x8x240` 和 `openblas_full` 共 7 个候选；最后一项是完整库边界，不属于生成 schedule。
- **Workload**：8 个矩阵的 `(M,N,K)` 分别为 `(63,65,67)`、`(192,256,256)`、`(257,129,193)`、`(191,513,257)`、`(512,512,512)`、`(768,256,384)`、`(256,768,384)` 和 `(1024,1024,1024)`，同时覆盖整除、三维 fringe、矩形和大矩阵。
- **实验链路**：候选/工作负载配置 -> 三个静态链接 RV64GCV ELF -> SD 卡或 sharefs -> RT-Smart 串口执行 -> 严格 CSV 导入 -> correctness/path/coverage 审计 -> workload-cluster 聚合。
- **测量协议与正确性**：`K230_WARMUPS=1`、`K230_REPS=5`；使用确定性输入和 reference projection，允许误差阈值为 `2e-3`。三次板端导入分别得到 40、240 和 280 行，总计 560/560 行正确，汇总为 112 个 workload-candidate-run 组。
- **性能结果**：每个 workload 选择最佳显式 RVV schedule 后，相对进程内 scalar 的几何平均加速为 2.2875x；完整 OpenBLAS/scalar 为 13.4704x。`rvv_generic_16x16x64` 在 8/8 workload 上的几何平均为 1.932x，而固定 BLIS-derived 候选仅在 5/8 workload 上可比且几何平均为 0.8466x。
- **解释**：硬合法性知识可以迁移到物理 RISC-V 后端，但固定性能排序不能直接迁移；不同 shape 的获胜候选发生变化，因此这组结果支持在线校准或目标端测量，而不支持单一跨架构软先验。
- **结果路径**：`jlq/thesis/experiments/k230_rvv_backend/data/candidates.json`；`jlq/thesis/experiments/k230_rvv_backend/data/workloads.json`；`jlq/thesis/experiments/k230_rvv_backend/processed/k230_board_summary.json`；`jlq/thesis/experiments/k230_rvv_backend/reports/k230_elf_results.md`；`jlq/thesis/experiments/k230_rvv_backend/provenance/elf_manifest.json`。
- **复现层级**：完整板端执行先运行 `python3 jlq/thesis/experiments/k230_rvv_backend/scripts/run_board_via_serial.py --port /dev/ttyACM1 --output-dir jlq/thesis/experiments/k230_rvv_backend/raw/board_results`，再运行 `import_board_results.py`；只运行 importer 只能重建已有 CSV 的分析结论，不能替代物理板测量。

### 5.19 `thesis.chapter6_external_validation`

- **定位**：在开发机之外冻结代码、候选与 protocol 后完成的外部设备验证，回答生成 adapter 与完整专家库之间的真实性能边界。
- **研究问题**：在 i9 原生 Linux 和 K230 RT-Smart 上，Contract 生成池能否保持 correctness/path 一致；其最佳候选距离完整 BLIS/OpenBLAS 还有多大差距。
- **冻结设置与测量协议**：配置于 2026-07-19 冻结；两台设备使用相同的 10 个 Transformer-derived f32 exact-shape workload、row-major 布局和单线程约束。每个进程 `1` 次 warmup、`3` 次计时重复，整个程序独立运行 `3` 个 process trials。
- **i9 候选与规模**：i9-14900 Ubuntu Linux 上每个 workload 有 28 个生成候选，再增加 1 个完整 BLIS 对照；共 280 个生成候选组和 10 个 BLIS 组、870 条 trial rows，涉及 86 个唯一生成二进制。正确性投影阈值为 `3e-3`。
- **K230 候选与规模**：K230 C908/RT-Smart 的 nominal pool 为每 workload 16 个候选，经 Contract 和工具链过滤后保留 133 个可执行 adapter 组，再增加 10 个 OpenBLAS 组；共 143 个组、429 条 trial rows。正确性投影阈值为 `2e-3`，路径分布为 8 个 direct workload 和 2 个 adapt workload。
- **实验链路**：冻结 generator 与 package -> 目标机编译/执行或板端静态 ELF 执行 -> 返回 archive/串口 CSV -> SHA-256、manifest、binary 和 workload coverage 审计 -> correctness/path/stability 检查 -> workload-cluster bootstrap -> 完整库边界。
- **i9 结果**：870/870 行正确，最佳生成池/BLIS 的 workload 几何平均为 0.5447607，95% CI `[0.483328, 0.610395]`，生成池在 0/10 workload 上超过 BLIS。该结果表明合法调度生成成立，但未复现完整 BLIS 的 packing、kernel dispatch 和系统级优化能力。
- **K230 结果**：429/429 行正确，最佳生成 adapter/OpenBLAS 的 workload 几何平均为 0.672973，95% CI `[0.619297, 0.725266]`，同样为 0/10 workload 获胜；独立 backend 接入成立，但不能转述为优于 OpenBLAS。
- **稳定性信息**：两端报告均保留 process-trial CV 和逐 workload 比值；CV 用于识别测量噪声，不用于删除不利 workload。i9 `perf` 计数器不可用，因此报告只使用 wall-clock kernel timing。
- **i9 结果路径**：`jlq/thesis/experiments/chapter6_external_validation/processed/i9_external_summary.json`；`jlq/thesis/experiments/chapter6_external_validation/processed/i9_external_aggregates.csv`；`jlq/thesis/experiments/chapter6_external_validation/reports/i9_external_results.md`；`jlq/thesis/experiments/chapter6_external_validation/provenance/i9_external_import_manifest.json`。
- **K230 结果路径**：`jlq/thesis/experiments/chapter6_external_validation/processed/k230_external_summary.json`；`jlq/thesis/experiments/chapter6_external_validation/processed/k230_external_aggregates.csv`；`jlq/thesis/experiments/chapter6_external_validation/reports/k230_external_results.md`；`jlq/thesis/experiments/chapter6_external_validation/provenance/k230_external_manifest.json`。
- **原始返回**：`jlq/thesis/experiments/chapter6_external_validation/returned/i9/chapter6-i9-result-20260722T085806Z.tar.gz`，SHA-256 `4d3dc241b12e26bb7da20ee18b07613f8cf38ab449b219194196044d1f21b8c5`；K230 原始串口 CSV 位于 `board_results/`。
- **复现层级**：目标端完整执行须使用冻结的 i9 package 或 K230 ELF/serial runner；i9 importer 命令为 `python3 jlq/thesis/experiments/chapter6_external_validation/scripts/import_i9_external_results.py <archive>`，K230 importer 命令为 `python3 jlq/thesis/experiments/chapter6_external_validation/scripts/import_k230_external_results.py jlq/thesis/experiments/chapter6_external_validation/board_results`。这两个命令只做返回结果审计和重分析。

### 5.20 `thesis.chapter6_application_validation`

- **定位**：把微基准候选池连接到真实模型的 GEMM 调用分布，并验证 MLIR 生成 wrapper 在物理 K230 上与手写 C adapter 的功能和计时一致性。
- **研究问题**：实验 workload 是否覆盖真实 Qwen projection 的核心调用；MLIR linalg/Transform/LLVM 链路生成的调用 wrapper 是否改变 kernel 语义或引入显著额外开销；微基准收益在真实调用权重下意味着什么。
- **Trace 输入**：模型为 Qwen2.5-0.5B，共 24 个 Transformer block；采集 decode `batch=8, M=8` 与 prefill `batch=1, sequence=32, M=32` 两个场景。原始记录包含 338 个 linear 调用，其中 336 个属于 block 内核心 projection，归并为 192 个 canonical calls 和 8 个 canonical workload；2 个 `lm_head` 调用单独排除。
- **覆盖审计**：8 个 canonical workload 覆盖 192/192 个核心调用，核心 projection 的 call coverage 和 FLOP coverage 均为 100%；若按全部 linear FLOP 计，覆盖率为 72.44%，未覆盖部分主要来自单独排除的 `lm_head`，因此不得写成整模型算子覆盖 100%。
- **MLIR closure case**：物理 K230 上预注册 `direct_qkv_prefill_m32` (`32x896x1152`, `m32_n8_k128`)、`adapt_qkv_fringe_m17` (`17x897x1153`, `m16_n16_k240`) 和 `adapt_down_fringe_m33` (`33x4865x895`, `m32_n16_k240`) 三个 case，覆盖 direct 以及 M/N/K 非整除 adapter。
- **实验链路**：Qwen control-flow trace -> canonical workload 归并 -> 参数活性检查 -> linalg + Transform 参数化 -> LLVM IR -> C adapter、MLIR wrapper 和 OpenBLAS 三个 RV64GCV 变体 -> K230 串口执行 -> correctness/parity 检查 -> i9/K230 trace-weighted projection。
- **板端协议**：每个 case 的 C adapter、MLIR adapter 和 OpenBLAS 变体各运行 5 个 trials，每次 1 个 warmup，共 3 x 3 x 5 = 45 行；45/45 行正确。wrapper parity 的通过条件是比值 CI 包含 1，或点估计距离 1 不超过 5%。
- **Closure 结果**：C adapter/MLIR adapter 的几何平均比值为 0.9887，95% CI `[0.9765, 1.0009]`，满足 parity；MLIR adapter/OpenBLAS 为 0.7518，说明 wrapper 闭环成立，但生成 adapter 仍低于完整 OpenBLAS。
- **Trace-weighted 结果**：i9 上完整库的 decode/prefill 加权时间为 117.0284/265.4171 ms，pool oracle/library 为 0.4799/0.6415；K230 上完整库为 3595.5689/6953.3778 ms，pool oracle/library 为 0.5630/0.7176。由于生成池在两端均低于完整库，guarded policy 选择 library，最终 library ratio 为 1.0，未产生可摊销 break-even。
- **预算分析边界**：静态与随机策略在 budget 5/10、5 个 seeds 上的结果只用于诊断候选可达性；它们不覆盖模型执行图、内存、attention、通信或端到端 runtime。开发机 WSL 的本地 timing 未通过稳定性门槛，最终投影只使用外部 i9 和物理 K230 数据。
- **结果路径**：`jlq/thesis/experiments/chapter6_application_validation/processed/qwen_trace_summary.json`；`jlq/thesis/experiments/chapter6_application_validation/processed/k230_mlir_closure_summary.json`；`jlq/thesis/experiments/chapter6_application_validation/processed/trace_weighted_summary.json`；`jlq/thesis/experiments/chapter6_application_validation/reports/k230_mlir_closure_results.md`；`jlq/thesis/experiments/chapter6_application_validation/reports/trace_weighted_results.md`；`jlq/thesis/experiments/chapter6_application_validation/reports/application_validation_status.md`。
- **复现层级**：`analyze_trace_weighted_results.py --i9-root ... --k230-root ...` 只重算外部结果的 trace-weighted projection；完整 closure 还需先构建 K230 ELF，并运行 `scripts/run_k230_mlir_via_serial.py --port /dev/ttyACM1 --board-root /sdcard/chapter6-k230-mlir-closure-validation --output-dir board_results` 获取 45 行物理板数据。

### 5.21 `thesis.transformer_region_go_nogo`

- **定位**：对“同一输入激活服务多个 projection 时共享 A packing”这一后续优化方向做预注册的终止性 go/no-go 判断。
- **研究问题**：QKV 与 Gate/Up fan-out 中，复用一次 activation packing 是否能稳定超过独立完整 BLIS、拼接输出后的完整 BLIS，以及每个 region 独立 repack 的微内核路径。
- **Workload**：使用 Qwen2.5-0.5B 维度；QKV region 的三个输出宽度为 896、128、128，Gate/Up 为 4864、4864；每个 region 评估 `M=1,8,64,256`，共 8 个 region-phase case。
- **四个变体**：`independent_blis` 为每个 projection 独立调用 BLIS；`concatenated_blis` 将同 region 输出拼接后调用一次 BLIS；`repacked_a_microkernel` 为每个 projection 重新 packing A；`shared_a_microkernel` 只 packing 一次 A 并在同 region 的微内核路径中复用。
- **实验链路**：Qwen dimensions -> 持久化 packed weights -> 四变体构建 -> 单线程完整 BLIS/微内核执行 -> rotating-order 计时 -> correctness -> case-cluster bootstrap -> 预注册门槛判定。
- **测量协议**：i7-10750H WSL2，CPU 10，单线程 row-major f32；每个变体 2 次 warmup、7 次计时重复、5 个独立 trials，变体顺序轮换；每个 timing sample 以约 5 亿 FLOP 为目标自适应迭代，最大 256 次。总计 8 x 4 x 5 = 160 条 trial rows，160/160 正确。
- **统计与门槛**：按 case 重采样 5000 次，seed 20260717。要判定 `GO`，shared/repacked 与 shared/concatenated 都必须满足几何平均至少 1.05、win fraction 至少 0.75、95% CI lower 大于 1，且每个 region 和 phase 的聚合比值都大于 1。
- **结果**：shared/repacked 为 1.006 `[0.906,1.121]`，仅 4/8 case 获胜；shared/concatenated 为 0.720 `[0.510,0.972]`，仅 1/8 获胜；shared/best-BLIS 为 0.665 `[0.472,0.894]`。concatenated/independent BLIS 为 0.956 `[0.865,1.051]`。
- **机制解释**：可避免的 A packing 时间最高仅占 3.08%，即便把这部分开销理想化为零，理论几何平均上限也只有 1.010、单 case 最大 1.032，低于预注册 1.05 门槛。trial CV 中位数为 0.104、最大 0.352，WSL 噪声扩大了区间，但不足以改变理论上限结论。
- **决策与边界**：状态为 `NO_GO_STRONG_BASELINE_NOT_BEATEN`，拒绝把 shared activation packing 作为当前 f32/BLIS Contract 下的独立主贡献；结果不外推到低精度、融合 epilogue、多线程或完整 Transformer block。
- **结果路径**：`jlq/thesis/experiments/transformer_region_go_nogo/processed/go_nogo_summary.json`；`jlq/thesis/experiments/transformer_region_go_nogo/raw/region_trials.csv`；`jlq/thesis/experiments/transformer_region_go_nogo/reports/go_nogo_results.md`。
- **复现层级**：完整本机重测运行 `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 jlq/thesis/experiments/transformer_region_go_nogo/scripts/run_go_nogo.py`；该脚本会重新编译、测量、聚合并执行 go/no-go 判定，不只是读取已有 CSV。

### 5.22 `thesis.chapter6_contract_space_validation`

- **定位**：对 Contract 安全门、硬约束空间内在价值、package 复用程度和搜索成本摊销进行的补充审计；其中 E1-E3 为本次新静态/结构验证，E4 复用冻结的 i7、i9 和 K230 测量。
- **研究问题**：Contract 是否能拒绝外部构造的单字段不匹配；G0 原始空间、G1 通用合法空间和 C 硬 Contract 空间在候选数、可调用密度与语义重复上有何差别；三个 package 是否真正共用核心 generator；何种部署 horizon 下搜索成本能够摊销。
- **Contract 对象**：BLIS Haswell f32 6x16、BLIS Haswell f64 6x8、OpenBLAS RV64GCV f32 8x8。每个 package 使用冻结的 dtype、ISA、MR/NR/K-step、layout/stride、packing schema、tail/beta、ABI 和 source revision/hash 描述。
- **E1 协议**：独立 oracle 为每个 package 固定 1 个 direct、1 个 adapt 和 8 个单字段危险变异，共 30 case；报告 predicted/expected path、首次拒绝阶段和诊断字段。另在隔离进程中注入 packed-B 顺序错误和 beta/tail 累加错误，由 reference GEMM 检查结果；不执行错误 ISA 或破坏真实函数 ABI。
- **E1 结果**：24/24 个危险变异被拒绝或安全降级，Mutation Score=1.000，false accept=0、false reject=0，path/phase/field accuracy 均为 1.000；两个 buffer fault 均产生可检测的错误结果。静态 checker 不能检测“descriptor 正确但 buffer 内容已损坏”的运行时内存错误。
- **E2 协议**：对 36 个冻结 workload 的 2600 点原始域完成 93,600 次分类；G0 为原始笛卡尔积，G1 为 B1 通用合法空间，C 为 B2 hard-Contract callable 空间。记录 path 比例、callable density、不活跃参数等价率、规范化 Transform schedule 哈希、checker median/p95 和随机顺序首次命中 callable 的试验数。
- **E2 编译证据**：8 个代表 workload x 3 空间 x 32 项=768 条记录均映射到既有真实成功编译 manifest，失败率为 0；这是规范化前的历史真实二进制清单重放，不是 768 次新编译，也不表示每个 stratum 有 32 个唯一规范化候选，更不外推到未编译的 G0 候选。
- **E2 规范化与结果**：`vectorize` 在 G1/C 的 direct/adapt 微内核路径不被消费，因此统一规范为 false；generic/raw Transform 路径仍保留该参数。G0/G1/C 的平均候选数由规范化前 2600.0/1056.2/208.7 变为 2600.0/951.9/104.4，平均缩减率为 0/0.634/0.960，callable density 为 0.080/0.105/1.000，随机顺序的 workload-median 首次 callable 为 10.0/7.0/1.0 次。C 的 IR 重复率由 0.500 降至 0；64/64 个具有两个已编译别名的实测组在去除符号名后得到相同规范化 IR。最终 replay 所选 224 个 schedule 中，166 个具有成对既有 IR 证据，另 58 个没有已编译的 `vectorize=false` 对应项，只依赖已审计的微内核路径参数活性规则，不能表述为逐项 IR 等价验证。
- **E2 冻结 replay 协议**：只对 C 构造 8 个 workload x 28 个候选的规范化实测池。先按 direct/adapt 语义键折叠旧 B2 中的 `vectorize` 别名，再从已有 B1/B2/B3/B4 direct/adapt 实测并集中按原 B2 稳定哈希确定性回填至 28 点；池构造不读取性能。使用 BaCO 3.0、seeds `[11,29,41,73,101]`、budget 25，共 40 条 run 和 1000 次 callback；目标值只在 BaCO 返回 token 后从冻结的 `measurement_aggregates.csv` 读取。整个 replay 不重新编译、不进行硬件性能测量，结果无论改善或下降均按预先冻结协议报告。
- **E2 最终性能结果与边界**：规范化 C 池的最终 D90 为 0.1875，time-to-90%-pool-best 中位数为 8.0 次，40 条 run 中 92.5% 达到阈值，并记录 21 次重复 callback。规范化前消融结果保留为 D90=0.1964、time-to-90%-pool-best=11.5；相较旧结果，最终 D90 下降 0.0089，而 time-to-90% 改善 3.5 次，两种方向均报告。G1 的 D90=0.0268、time-to-90%=10.5 仍是规范化前历史测量，G0 没有既有性能池；本次 replay 不能被描述为新的硬件测量或 G0/G1 的规范化性能结果。
- **E3 审计**：三个 package 的 schema leaf path 交集/并集为 31/34，intersection-over-union 为 0.912；BLIS f32、BLIS f64、OpenBLAS RVV 的共享字段覆盖率分别为 0.969、0.969、0.939。共享 Chapter 4/6 核心中的 package-ID 特判数为 0。既有 before/after 哈希证明 BLIS f64 加入时核心 generator 不变；OpenBLAS RVV 已完成独立库/ISA 的 Contract、adapter 和物理执行，但当前使用 package-local 生成路径。
- **E3 结论**：支持共享 schema 和同一 BLIS 后端第二 dtype 的核心复用，不支持“任意新 package 均零核心修改”的强主张。adapter/config 报告当前树 LOC；由于缺少干净 onboarding commit 和工时日志，不事后估算历史新增 LOC 或人工耗时。
- **E4 协议**：净价值按 `V(H)=sum_j H_j(t_b,j-t_o,j)-C_c-sum_j C_s,j` 计算，其中 `C_c` 是全局模型拟合成本，`C_s,j` 是 shape j 的候选生成、编译、测量和 tuner 成本；现有日志只支持聚合 `sum_j C_s,j`，不事后虚构逐 shape 分摊。只有 `LCB95(V(H))>0` 才判定搜索值得；严格区分 tuning-task、deployment-cycle 和 model-inference horizon。
- **E4 结果**：i7 f64 的 `POST_HOC_DESCRIPTIVE_UPPER_BOUND` 场景中，`C_c=58.239 ms`，聚合 `sum C_s,j=531895.625 ms`；每 deployment cycle 节省 3.207 ms，95% CI [0.717,4.067]，点估计 break-even 为 165,865 cycles，LCB95 break-even 为 741,587 cycles。这里一个 deployment cycle 是对 19 个事后 winning shape 各调用一次的等频合成单位，不是模型 inference，也不是实测部署频率。i9/K230 冻结 Qwen exact-shape trace 每 inference 的生成路径净节省分别为 -275.16 ms 和 -5527.75 ms，即使把搜索成本设为 0 也没有有限 break-even，应选择完整 BLIS/OpenBLAS。
- **旧指标解释**：D0/D1 的 2293.6/2339.0 是含编译成本后需要服务的后续调优 workload 数，不是单矩阵调用次数或模型推理次数。
- **结论边界**：可主张 Contract 提供可诊断的安全门并显著提高 callable density；不可主张硬空间天然更快找到最优、OpenBLAS 已完全接入同一核心 generator，或生成路径普遍优于完整库。
- **结果路径**：`jlq/thesis/experiments/chapter6_contract_space_validation/processed/summary.json`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e1_mutation_results.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e2_space_classification.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e2_normalized_pool.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e2_normalized_baco_traces.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e2_normalized_convergence.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e2_normalized_baco_summary.json`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e2_vectorize_equivalence_audit.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e3_reuse_audit.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/processed/e4_break_even_summary.csv`；`jlq/thesis/experiments/chapter6_contract_space_validation/reports/contract_space_validation_results.md`；`jlq/thesis/experiments/chapter6_contract_space_validation/provenance/manifest.json`。
- **复现层级**：先运行 `python3 jlq/thesis/experiments/chapter6_contract_space_validation/scripts/run_normalized_baco_replay.py` 复现冻结规范化池上的离线 BaCO replay，再运行 `python3 jlq/thesis/experiments/chapter6_contract_space_validation/scripts/run_all.py` 重建 E1-E4 汇总；随后运行 `python3 -m unittest discover -s jlq/thesis/experiments/chapter6_contract_space_validation/tests -v`，当前 4/4 项通过。若只重建 replay 的映射与统计而不重新执行 BaCO，可使用 `run_normalized_baco_replay.py --analyze-only`。上述 replay 和 E4 都不重新采集硬件计时。

## 6. 论文使用边界

- 可以主张：硬兼容性知识能生成合法的 packing/call/direct/adapt 路径；第二 BLIS Contract 复用了核心 generator，OpenBLAS/RV64GCV package 复用了 Contract 语义和 adapter 接口，但目前仍使用 package-local 生成路径。
- 可以主张：目标数据校准在部分主机和低预算下提高样本效率，但收益具有环境依赖。
- 必须主张：当前 BLIS-derived 软性能特征相对 Data-only 没有证明额外价值，且校准成本在冻结 horizon 内未摊销。
- 不可主张：生成 schedule 超过完整 BLIS/OpenBLAS；跨全部 x86/RISC-V 的普适性能；多线程、任意 layout/stride/batch；端到端模型加速。
- Chapter 5 的 15.90x 仅相对 scalar-loop dynamic fallback；完整库对照应使用 Chapter 6 external validation。

## 7. 文档自检记录

本文件生成后按以下规则完成一致性检查：

- **实验覆盖**：PersonalOS 注册表包含 22 个实验 ID，本文件第 5 节包含 22 个实验 ID；两组 ID 完全一致，无遗漏或额外条目。
- **字段完整性**：22 个实验均给出目的、实验链路、设备或执行环境、协议与细节、结果、结果路径和复现入口；文献型 4.5 条目明确标记为非性能实验。
- **路径有效性**：除路径格式占位符 `jlq/thesis/...` 外，作为配置、结果、报告或 provenance 单独列出的 108 个唯一 `jlq/thesis/` 工作区路径全部存在。复现命令中由脚本新建的输出目录，以及部署介质上的 `/sdcard/...` 和 `/sharefs/...`，不纳入主机证据文件存在性检查。
- **关键数值**：i9 的 870 条 correctness 与 0.5448 BLIS 比值、K230 的 429 条 correctness 与 0.6730 OpenBLAS 比值、K230 MLIR closure 的 45 条 correctness 与 0.9887 parity 比值，以及规范化 C 池 replay 的 D90=0.1875、time-to-90%-pool-best=8.0，均与对应 `processed/*.json` 一致；旧 0.1964/11.5 只标记为规范化前消融。
- **科学边界**：同池两环境 acceptance 保留为 `FAIL`，终止验证保留为 `MIXED`；文中没有把生成候选写成超过完整 BLIS/OpenBLAS，也没有把 trace-weighted projection 写成端到端模型加速。
- **存储边界**：本文件只索引实验脚本、原始结果、机器可读摘要、报告和 provenance。编译缓存、工具链、重复解压目录以及可重建离线依赖包不属于论文结论的最小证据。

建议在实验注册表或结果目录发生变化后重新执行上述检查，再更新本文的日期、实验数量和路径数量。
