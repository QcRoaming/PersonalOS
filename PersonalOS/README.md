# PersonalOS

PersonalOS 是一个轻量、Git 驱动的个人连续性系统。它默认不保存聊天原文，只保存能让下一个窗口、下一台设备或下一个账号继续工作的最小语义状态；当用户发送精确的独立命令“导入”时，可以显式启动隔离的原始会话归档流程。

## 从哪里开始

- 第一次使用、新设备或新账号：从 `START_HERE.md` 开始。
- 恢复当前工作：读取 `HANDOFF.md`，再按 `ROUTES.md` 只选择一个 Lane。
- 查看实时事实：以 `PERSONAL.md`、`ROUTES.md`、`lanes/*.md` 和注册表为准。
- 查看全部实验链路、设备、协议、结果和路径：读取 `EXPERIMENTS_DETAILED_GUIDE.md`。
- 理解完整协议与命令：继续阅读本文件。

README 记录稳定设计和操作方法，不承担动态进度事实源的职责。`HANDOFF.md`、`KNOWLEDGE.md`、`DASHBOARD.md`、`EXPERIMENTS.md` 与 `ARCHIVES.md` 由各自的 checkpoint、注册表或归档命令重建，用于反映当前 Git 状态。

## 当前实现状态

下表是 2026-07-18 的发布前验证快照，不替代生成视图或权威状态文件：

| 能力 | 状态 | 当前证据 |
|---|---|---|
| 单 Lane 启动与最小上下文恢复 | 已验证 | `start` 路由、依赖隔离和结构检查通过 |
| 结构化 checkpoint 与生成视图 | 已验证 | Lane version 保护及确定性视图测试通过 |
| 本地安装和环境诊断 | 已验证 | `install` 幂等，`doctor` 通过 |
| Git 同步闭环 | 已验证 | commit、rebase、push 流程通过；禁止 force-push |
| 实验注册表 | 已验证 | 17 条实验记录，生成视图一致 |
| 会话/语音转写归档 | 自动化已验证 | 3 种覆盖级别、触发前截断、哈希和音频复制测试通过；真实归档数为 0 |
| 跨账号恢复 | 协议已实现，待验收 | 待第二个真实 ChatGPT 账号授权私有仓库并恢复 |
| 多设备恢复 | 协议已实现，待验收 | 待第二台设备完成 clone/install/push/pull 往返 |

当前共 14 项单元测试通过。`HANDOFF.md` 提供最近恢复摘要；实时开发事实和待办由 `skills.mcp` Lane 拥有，README 不重复维护会快速变化的任务列表。

## 能达到什么程度

它为不同 Codex 窗口、Codex CLI、VS Code 扩展、设备和 ChatGPT 账号提供从同一个 GitHub 私有仓库恢复状态的协议。当前本地闭环已验证，真实跨账号和第二设备恢复仍待验收。

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

- 仓库：QcRoaming/PersonalOS
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
| EXPERIMENTS_DETAILED_GUIDE.md | 21 项实验的链路、设备、协议、结果路径和结论边界 | 否，由实验总整理同步 |
| archives/conversations/ | 用户通过“导入”显式创建的原始会话与语音转写归档 | 是，独立归档 |
| ARCHIVES.md | 会话归档数量、覆盖级别、完整性和位置索引 | 否，自动生成 |
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
git clone https://github.com/QcRoaming/PersonalOS.git ~/personal-os
cd ~/personal-os
export PERSONAL_OS_ROOT="$PWD/PersonalOS"
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" install "$PERSONAL_OS_ROOT"
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" doctor "$PERSONAL_OS_ROOT"
~~~

install 会创建：

- ~/.personal-os-root：PersonalOS 根目录指针；
- ~/.codex/AGENTS.md：所有本地仓库都能继承的全局协议；
- ~/.agents/skills/personal-os/SKILL.md：Codex CLI 与 IDE 扩展可发现的全局 Skill。

这是 Codex 当前的作用域分工：全局 AGENTS.md 位于 Codex home，用户级 Skill 位于 ~/.agents/skills。安装后重启 Codex CLI，或执行 VS Code 的 Developer: Reload Window / 重启 Codex 扩展，让新会话重建指令链。

上面的 `export` 会立即配置当前 shell。`install` 还会写入 `~/.personal-os-root`，但不会替当前 shell 创建环境变量。若希望后续终端也能直接使用 `$PERSONAL_OS_ROOT`，可持久写入 Bash：

~~~bash
echo 'export PERSONAL_OS_ROOT="$HOME/personal-os/PersonalOS"' >> ~/.bashrc
~~~

PowerShell（同时设置当前进程和后续进程）：

~~~powershell
git clone https://github.com/QcRoaming/PersonalOS.git "$HOME\personal-os"
Set-Location "$HOME\personal-os"
python PersonalOS\scripts\personal_os.py install PersonalOS
python PersonalOS\scripts\personal_os.py doctor PersonalOS

$env:PERSONAL_OS_ROOT = (Resolve-Path "PersonalOS").Path
[Environment]::SetEnvironmentVariable(
  "PERSONAL_OS_ROOT",
  $env:PERSONAL_OS_ROOT,
  "User"
)

python "$env:PERSONAL_OS_ROOT\scripts\personal_os.py" start `
  "$env:PERSONAL_OS_ROOT" --pull --query "继续主线"
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
2. 授权它读取私有仓库 QcRoaming/PersonalOS。若使用另一个 GitHub 身份，先让该身份获得仓库读取权限。
3. 最小授权范围只选择这个仓库。
4. 在新对话发送下面的启动消息。

> 请把 GitHub 私有仓库 QcRoaming/PersonalOS 的 PersonalOS/ 作为我的唯一个人状态源。先读取 PersonalOS/START_HERE.md、PersonalOS/HANDOFF.md、PersonalOS/PERSONAL.md 和 PersonalOS/ROUTES.md；根据我的本次请求只选择一个 Lane，再读取该 Lane及 ROUTES.md 明确声明的依赖小节。不要依赖旧聊天记忆，不要加载无关 Lane。先告诉我当前检查点、正在做什么、下一步和最近实验状态，再继续任务。

若连接器提示无权访问，先修复授权；不要让新账号根据 README 或旧对话猜测当前实验状态。

GitHub 连接器通常只承担读取。如果当前网页会话没有仓库写入和 Git push 能力，它可以恢复状态，但不能把 checkpoint 或会话归档发布回权威仓库；此时必须把写入步骤交给已安装 PersonalOS 的本地 CLI/IDE 环境。

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
read -r -p "输入 start 输出的当前 version: " LANE_BASE_VERSION

python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" checkpoint \
  "$PERSONAL_OS_ROOT" \
  --lane research.kernel_aware_gemm \
  --base-version "$LANE_BASE_VERSION" \
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

## 输入“导入”备份当前窗口

当一条用户消息的全部内容恰好为：

~~~text
导入
~~~

PersonalOS 协议会启动会话归档流程，并把触发消息之前的对话备份到 archives/conversations/。只有当前执行环境能够写入权威仓库时，助手才能直接完成保存和同步；只读网页连接器必须转交本地 CLI。原始对话与 Lane、个人画像、知识阶段完全隔离，日常恢复不会自动读取归档内容。

系统区分三种覆盖级别：

| 覆盖级别 | 含义 |
|---|---|
| exact_export | 从 ChatGPT 官方数据导出中选中并导入完整会话 |
| provided_transcript | 完整保留用户提供的 JSON、Markdown 或文本逐字稿 |
| visible_context_only | 只能看到模型当前上下文的临时恢复，不保证完整，禁止称为完整备份 |

ChatGPT 网页端没有一个可由模型调用的“读取当前 UI 全部历史”接口。因此，仅输入“导入”时，助手只能在权威仓库可写时先把当前实际可见的消息保存为 visible_context_only 临时归档；若连接器只读，则应给出本地导入步骤。随后仍需补充数据导出或逐字稿来升级为完整归档，临时归档不能声称为完整备份。

### 导入 ChatGPT 数据导出

在 ChatGPT 的 Settings → Data controls → Export data 请求导出，解压后找到 conversations.json。当前窗口的 conversation ID 通常可从对话 URL 获取：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/conversation_archive.py" import \
  --root "$PERSONAL_OS_ROOT" \
  --source /path/to/conversations.json \
  --kind chatgpt-export \
  --surface chatgpt_text \
  --conversation-id CONVERSATION_ID \
  --before-trigger "导入"
~~~

脚本会沿当前 active branch 还原消息顺序，并排除最后一条“导入”触发消息。

### 导入语音对话

语音会话结束后，ChatGPT 历史中出现的转写可以按相同方式导入：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/conversation_archive.py" import \
  --root "$PERSONAL_OS_ROOT" \
  --source /path/to/conversations.json \
  --kind chatgpt-export \
  --surface chatgpt_voice \
  --conversation-id CONVERSATION_ID
~~~

这默认是“语音转写备份”，不是原始音频备份。若已经取得音频文件，可显式附加：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/conversation_archive.py" import \
  --root "$PERSONAL_OS_ROOT" \
  --source /path/to/transcript.json \
  --kind transcript \
  --surface chatgpt_voice \
  --audio /path/to/voice-audio.m4a
~~~

每个归档保存源文件 SHA-256、消息 payload SHA-256、覆盖级别、语音/音频状态和 Lane 指针。导入后执行：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/conversation_archive.py" check \
  --root "$PERSONAL_OS_ROOT"
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" sync \
  "$PERSONAL_OS_ROOT" --push --message "归档当前会话"
~~~

注意：ChatGPT 全账号导出文件本身可能包含其他会话和敏感信息。只提交 PersonalOS 生成的单会话归档，不要把原始 conversations.json 放进 Git。

## 日常闭环

每次会话：

1. start --pull：先拿到远程最新状态并选择一个 Lane。
2. 完成实际工作；普通问答和临时猜测不记录，只有精确命令“导入”才进入原始会话归档。
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
- 未经精确“导入”命令授权的聊天原文和完整提示词历史；
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

## 项目维护与验证

修改协议、脚本或 README 后，在 PersonalOS 根目录执行：

~~~bash
python3 scripts/personal_os.py check .
python3 scripts/personal_os.py doctor .
python3 scripts/experiment_registry.py check
python3 scripts/conversation_archive.py check --root .
python3 -m unittest discover -s tests -v
~~~

`HANDOFF.md`、`KNOWLEDGE.md`、`DASHBOARD.md`、`EXPERIMENTS.md`、`ARCHIVES.md` 是生成视图，不应手工维护。功能或协议形成稳定语义检查点后，更新所属 Lane，再用 `sync --push` 提交、rebase 并推送；普通说明性编辑不应伪造用户画像、知识阶段或研究进度。
