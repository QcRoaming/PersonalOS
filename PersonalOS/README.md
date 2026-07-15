# PersonalOS

PersonalOS 是一套轻量、可移植的个人状态文件系统。它不保存聊天原文，只保存会影响后续工作的长期状态：个人偏好、主线与支线、任务进度、知识阶段、关键决策和阻塞项。

## 文件职责

- `PERSONAL.md`：只保存跨项目长期成立的画像、偏好和硬约束。
- `ROUTES.md`：保存主线、支线、隔离关系、依赖和存储位置。
- `DASHBOARD.md`：由脚本生成的全局视图，不作为事实源。
- `EXPERIMENTS.md`：由注册表生成的实验总览，不手工编辑。
- `lanes/*.md`：每条线的唯一当前状态。
- `registries/experiments.json`：第三章至第五章、Chapter 4-5 集成、4.5 和历史实验的机器可读事实源。
- `pending/*.delta.md`：并行窗口产生的未合并状态增量；合并后删除。
- `AGENTS.md`：本地 Codex CLI/IDE 使用的读写协议。
- `scripts/personal_os.py`：检查结构、选择支线和重建总览。
- `scripts/experiment_registry.py`：刷新实验路径、体积、指纹、证据哈希、论文用途和最近成功运行状态。

## 日常用法

可以直接使用这些表达：

- `继续主线`
- `切换到推理框架支线`
- `给我本支线下一步`
- `给我全局下一步`
- `同步状态`
- `这次不记录`
- `这只是临时讨论`

系统默认只读取一个活动支线。只有 `ROUTES.md` 中存在明确依赖时，才读取另一条线的相关小节。

## 本地检查

```bash
python3 scripts/personal_os.py check .
python3 scripts/personal_os.py route . "继续复现 Transform Dialect 4.5 baseline"
python3 scripts/personal_os.py dashboard .
python3 scripts/experiment_registry.py check
```

脚本只依赖 Python 标准库。

## 实验注册表

PersonalOS 只维护实验元数据和证据指针，原始 CSV、IR、二进制、图表和构建目录仍保存在 `/buddy-mlir/jlq/thesis/experiments/`。论文用途由工作区的 `data/paper_evidence_selection.json` 维护，并在刷新时同步为 `primary_main_text`、`supporting_main_text`、`appendix_only` 或 `reference_only`。刷新命令为：

```bash
python3 scripts/experiment_registry.py refresh --workspace-root /buddy-mlir
```

Chapter 3、Chapter 4、Chapter 5、Chapter 4-5 集成和已登记的历史实验生成脚本在完整成功后会自动执行刷新，并记录对应条目的 `last_successful_run_utc`。4.5 当前只有提取材料，没有可声明成功的独立复现入口，因此只进行手工元数据刷新。新增稳定实验时，同时更新注册表和工作区论文证据筛选清单，再让生成入口调用：

```bash
python3 "$PERSONAL_OS_ROOT/scripts/experiment_registry.py" refresh \
  --workspace-root /buddy-mlir \
  --completed-id <experiment-id>
```

若机器上没有 PersonalOS，实验生成器可以明确跳过索引刷新；若注册表脚本存在但刷新失败，生成入口应返回失败，避免静默留下过期索引。

## 多机器与 IDE

最终把整个目录放在 `QcRoaming/personal-os` 中，并将其设为唯一权威源。首次发布采用本地 Git，不依赖 ChatGPT GitHub App 的 Contents 权限。

如果尚未在本机登录 GitHub CLI，先执行：

```bash
gh auth login
```

选择 `GitHub.com`、`HTTPS`，并允许 GitHub CLI 配置 Git 凭据。

下载并解压 `PersonalOS.zip` 后，在 WSL 中执行首次发布：

```bash
git clone https://github.com/QcRoaming/personal-os.git ~/personal-os
cp -a /path/to/extracted/PersonalOS/. ~/personal-os/
cd ~/personal-os
git add .
git commit -m "Initialize PersonalOS"
git branch -M main
git push -u origin main
```

首次发布完成后，每台机器只保留该仓库的工作副本：

```bash
git clone https://github.com/QcRoaming/personal-os.git ~/personal-os
export PERSONAL_OS_ROOT="$HOME/personal-os"
```

PowerShell 用户可以设置用户级环境变量：

```powershell
[Environment]::SetEnvironmentVariable("PERSONAL_OS_ROOT", "$HOME\personal-os", "User")
```

在 Codex CLI 或 IDE 中使用同一账户的 `personal-os` Skill。Skill 优先读取 `PERSONAL_OS_ROOT`，其次读取当前目录中的 PersonalOS，最后才使用持久文件副本。

多端工作前先拉取，完成一个语义检查点后再提交并推送。不要让不同机器分别维护独立的 `PERSONAL.md`。

## 当前同步状态

- 持久文件副本：已初始化。
- 本地便携目录：已初始化。
- 私人远程仓库：已指定 `QcRoaming/personal-os`；选择本地 Git 首次推送，推送确认前不切换权威源。
