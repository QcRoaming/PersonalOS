# PersonalOS

PersonalOS 是一个轻量、Git 驱动的个人连续性系统。它不保存聊天原文，而是保存能让下一个窗口、下一台设备或下一个账号继续工作的最小语义状态：稳定画像、主线与支线、当前检查点、任务状态、已验证知识、实验元数据、决策、阻塞和下一步。

## 能达到什么程度

它可以让不同 Codex 窗口、Codex CLI、VS Code 扩展、设备和 ChatGPT 账号从同一个 GitHub 私有仓库恢复状态。

它不能让网页端直接看到 VS Code 容器中尚未提交的文件，也不能绕过新账号的 GitHub 授权。跨端可见性的硬边界是：

~~~text
VS Code / Codex CLI 的实验结果
        │  compact checkpoint / registry metadata
        ▼
本机 PersonalOS 工作副本
        │  validate + commit + rebase + push
        ▼
GitHub 私有仓库（唯一事实源）
        │  GitHub connector / git pull
        ▼
网页新窗口、新账号、其他设备
~~~

因此，“已经在本地记录”不等于“其他端已经知道”；只有成功推送的提交才是跨账号状态。

## 当前权威配置

- 仓库：QcRoaming/PersonalOS-v1
- PersonalOS 根目录：仓库中的 PersonalOS/
- 权威源：private_git
- 本地同步：语义检查点 → 生成视图 → 校验 → commit → rebase → push
- 网页读取：新账号授权 GitHub 连接器后读取默认分支

## 文件职责

| 文件 | 职责 | 是否事实源 |
|---|---|---|
| PERSONAL.md | 跨项目稳定画像、偏好和硬约束 | 是 |
| ROUTES.md | 主线、支线、隔离、依赖和存储路由 | 是 |
| lanes/*.md | 每条工作线的检查点、任务、决策、阻塞和知识阶段 | 是 |
| registries/experiments.json | 实验元数据、证据路径、哈希和最近成功运行 | 是 |
| HANDOFF.md | 最近活动、当前检查点、Doing、Next 和最新实验的恢复包 | 否，自动生成 |
| KNOWLEDGE.md | 所有 Lane 的知识主题与阶段索引 | 否，自动生成 |
| DASHBOARD.md | 全局任务总览 | 否，自动生成 |
| EXPERIMENTS.md | 实验注册表的人类可读视图 | 否，自动生成 |
| START_HERE.md | 新窗口、新设备和新账号的固定启动入口 | 协议 |
| AGENTS.md | 仓库内 Codex 读写边界 | 协议 |
| skill/personal-os/SKILL.md | 可安装到本机的便携 Skill 源 | 协议 |
| pending/*.delta.md | 并行窗口尚未合并的语义增量 | 临时 |

## 为什么 v1 会出现不同步

旧方案同时依赖聊天记忆、账号内 Skill/Library 镜像和本地 Markdown。它们有三个断点：

1. ChatGPT 记忆、Library 和已安装 Skill 通常属于账号或当前产品表面，换账号后不能作为共享数据库。
2. 网页端不能读取 VS Code 容器的本地文件；实验注册表即使刷新了，没有 Git push 仍然不可见。
3. 只有 Lane 文件而没有稳定的 Handoff 与知识索引，新窗口不知道哪条线最近更新，也不容易快速恢复跨领域学习阶段。

v2 将 GitHub 私有仓库设为唯一事实源，并把“开始、检查点、结束同步”做成脚本命令。

## 新设备：Codex CLI 或 VS Code

Linux、WSL 或容器：

~~~bash
git clone https://github.com/QcRoaming/PersonalOS-v1.git ~/personal-os
cd ~/personal-os

python3 PersonalOS/scripts/personal_os.py install PersonalOS
python3 PersonalOS/scripts/personal_os.py doctor PersonalOS
~~~

install 会创建：

- ~/.personal-os-root：PersonalOS 根目录指针；
- ~/.codex/AGENTS.md：所有本地仓库都能继承的全局协议；
- ~/.agents/skills/personal-os/SKILL.md：Codex CLI 与 IDE 扩展可发现的全局 Skill。

这是 Codex 当前的作用域分工：全局 AGENTS.md 位于 Codex home，用户级 Skill 位于 ~/.agents/skills。安装后重启 Codex CLI，或执行 VS Code 的 Developer: Reload Window / 重启 Codex 扩展，让新会话重建指令链。

可选环境变量：

~~~bash
export PERSONAL_OS_ROOT="$HOME/personal-os/PersonalOS"
~~~

持久写入 Bash：

~~~bash
echo 'export PERSONAL_OS_ROOT="$HOME/personal-os/PersonalOS"' >> ~/.bashrc
~~~

PowerShell：

~~~powershell
git clone https://github.com/QcRoaming/PersonalOS-v1.git "$HOME\personal-os"
Set-Location "$HOME\personal-os"
python PersonalOS\scripts\personal_os.py install PersonalOS
python PersonalOS\scripts\personal_os.py doctor PersonalOS

[Environment]::SetEnvironmentVariable(
  "PERSONAL_OS_ROOT",
  "$HOME\personal-os\PersonalOS",
  "User"
)
~~~

如果 VS Code 连接的是 WSL、SSH 或 Docker 容器，clone 和 install 必须在 Codex 实际运行的那个 Linux 环境中执行；宿主 Windows 的 HOME 与容器中的 /root 不是同一个文件系统。

## 新窗口：同一台设备

启动本地任务时：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" start \
  "$PERSONAL_OS_ROOT" --pull --query "继续主线"
~~~

该命令只在工作区干净时 fast-forward pull，然后输出一个 Lane 的最小上下文包。也可以显式选择：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" start \
  "$PERSONAL_OS_ROOT" --lane learning.inference
~~~

在 VS Code Codex 对话框中可以直接说：

> 使用 personal-os，先同步权威仓库，然后继续主线。只加载当前 Lane 和声明的依赖。

## 新账号：ChatGPT 网页

旧账号的聊天记录、Memory、Library 和个人 Skill 不会自动迁移。恢复流程必须从外部事实源开始：

1. 新账号安装或启用 GitHub 连接器。
2. 授权它读取私有仓库 QcRoaming/PersonalOS-v1。若使用另一个 GitHub 身份，先让该身份获得仓库读取权限。
3. 最小授权范围只选择这个仓库。
4. 在新对话发送下面的启动消息。

> 请把 GitHub 私有仓库 QcRoaming/PersonalOS-v1 的 PersonalOS/ 作为我的唯一个人状态源。先读取 PersonalOS/START_HERE.md、PersonalOS/HANDOFF.md、PersonalOS/PERSONAL.md 和 PersonalOS/ROUTES.md；根据我的本次请求只选择一个 Lane，再读取该 Lane及 ROUTES.md 明确声明的依赖小节。不要依赖旧聊天记忆，不要加载无关 Lane。先告诉我当前检查点、正在做什么、下一步和最近实验状态，再继续任务。

若连接器提示无权访问，先修复授权；不要让新账号根据 README 或旧对话猜测当前实验状态。

## VS Code 实验如何同步到网页

原始 CSV、IR、二进制、图表和构建目录继续保存在 /buddy-mlir 等实验工作区。PersonalOS 只同步体积小、可审查的元数据和结论边界。

实验生成器成功后，刷新注册表：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/experiment_registry.py" refresh \
  --workspace-root /buddy-mlir \
  --completed-id thesis.chapter6_evaluation
~~~

该命令会更新 experiments.json、EXPERIMENTS.md、HANDOFF.md、KNOWLEDGE.md 和 DASHBOARD.md，但此时仍然只是本地可见。

确认后推送：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" sync \
  "$PERSONAL_OS_ROOT" --push \
  --message "同步 Chapter 6 实验检查点"
~~~

如果某个稳定实验入口明确允许自动发布，可显式使用：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/experiment_registry.py" refresh \
  --workspace-root /buddy-mlir \
  --completed-id thesis.chapter6_evaluation \
  --sync-push
~~~

--sync-push 会产生外部 Git 提交，只应在实验完整成功且当前工作副本属于 PersonalOS 权威仓库时使用。

## 记录任务进度和知识阶段

结构化检查点示例：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" checkpoint \
  "$PERSONAL_OS_ROOT" \
  --lane research.kernel_aware_gemm \
  --base-version 8 \
  --summary "第六章正式评估完成，当前转入第四至六章正文写作" \
  --doing "按正式 evaluator 结果撰写第六章" \
  --next "先完成表 6-1 至表 6-4 的正文解释" \
  --evidence "680 次调优与 17000 条轨迹已完成" \
  --artifact "QcRoaming/buddy-mlir@COMMIT:jlq/thesis/experiments/chapter6_evaluation" \
  --knowledge "BaCO 固定预算评估|verified|五种子与固定回调预算结果已冻结|扩展第二主机"
~~~

知识阶段只允许：

~~~text
unknown → exposed → understood → applied → verified
                               ↘ stale（旧证据需复验）
~~~

“问过”最多说明 exposed；能够解释但未实践通常是 understood；有代码或实验是 applied；可重复测试或直接证据才是 verified。

checkpoint 更新一个 Lane、递增 version、记录精确活动时间，并重建三个全局视图。随后仍需运行 sync --push。

## 日常闭环

每次会话：

1. start --pull：先拿到远程最新状态并选择一个 Lane。
2. 完成实际工作；普通问答和临时猜测不记录。
3. 有语义变化时 checkpoint；实验则先 refresh registry。
4. 执行 check 或 doctor。
5. sync --push：提交、rebase 并推送。
6. 网页端重新读取 HANDOFF.md；不要以旧窗口缓存为准。

常用检查：

~~~bash
python3 scripts/personal_os.py views .
python3 scripts/personal_os.py check .
python3 scripts/personal_os.py doctor .
python3 scripts/experiment_registry.py check
python3 -m unittest discover -s tests -v
~~~

## 多窗口和冲突

- 同一工作副本一次只允许一个 checkpoint 写入；.personal-os.lock 防止短时间并发覆盖。
- 每个窗口开始前 pull；每个完整语义单元单独提交。
- checkpoint 可传 --base-version。如果远端或另一窗口已升级 Lane version，命令拒绝覆盖。
- sync 使用 rebase，不 force-push。冲突时保留双方语义，必要时写 pending/*.delta.md 再人工合并。
- 不同 Lane 的上下文默认隔离；跨 Lane 只能读取 ROUTES.md 明确声明的依赖小节。

## 隐私和存储边界

仓库必须保持 private。不要写入：

- GitHub token、API key、SSH private key、Cookie 或密码；
- 聊天原文和完整提示词历史；
- 未确认的人格推断或敏感画像；
- 大型原始实验数据、构建目录和二进制。

实验原件留在项目仓库、对象存储或本地工作区；PersonalOS 只保存稳定 ID、版本/commit、相对路径、哈希、核心指标、结论边界和复现命令。若新账号也需要直接检查原始文件，它还必须获得对应项目仓库或存储的访问权限。

## 故障判断

| 现象 | 原因 | 处理 |
|---|---|---|
| 网页看不到刚完成的 VS Code 实验 | 本地 registry 或 Lane 尚未 push | 运行 sync --push，再让网页读取最新 HANDOFF.md |
| 新账号什么都不知道 | GitHub 连接器未安装、未授权或未选中私有仓库 | 完成授权后发送固定启动消息 |
| VS Code 新窗口没有触发 personal-os | install 未执行，或 Codex 未重启 | 运行 install，检查 ~/.codex/AGENTS.md 与 ~/.agents/skills，然后重启 |
| pull 被拒绝 | 本地工作区有未提交变化 | 先 checkpoint / commit，或明确处理本地变化 |
| push rebase 冲突 | 另一设备已更新同一文件 | 不强推；按 Lane version 合并语义增量 |
| 网页能看元数据但打不开原始实验 | 原始数据只在本地工作区或另一私有仓库 | 授权对应存储，或只使用已同步的证据摘要 |
