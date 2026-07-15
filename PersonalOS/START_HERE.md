# PersonalOS 启动入口

这个文件用于新窗口、新设备或新账号在没有旧聊天记录的情况下恢复上下文。

## 唯一事实源

- GitHub 私有仓库：QcRoaming/PersonalOS-v1
- PersonalOS 根目录：PersonalOS/
- 权威状态：远程仓库默认分支的最新提交
- 聊天记忆、旧账号 Library、本地未推送文件都不是跨账号事实源

只有被提交并推送到该仓库的状态，才能被另一台设备或另一个账号可靠读取。

## 新账号的第一条消息

先在新账号中安装并授权 GitHub 连接器访问 QcRoaming/PersonalOS-v1，再发送：

> 请把 GitHub 私有仓库 QcRoaming/PersonalOS-v1 的 PersonalOS/ 作为我的唯一个人状态源。先读取 PersonalOS/START_HERE.md、PersonalOS/HANDOFF.md、PersonalOS/PERSONAL.md 和 PersonalOS/ROUTES.md；根据我的本次请求只选择一个 Lane，再读取该 Lane 及 ROUTES.md 明确声明的依赖小节。不要依赖旧聊天记忆，不要加载无关 Lane。先告诉我当前检查点、正在做什么、下一步和最近实验状态，再继续任务。

如果新账号没有仓库权限，必须先授权；不要让模型用猜测补全状态。

## 新设备的第一次操作

~~~bash
git clone https://github.com/QcRoaming/PersonalOS-v1.git ~/personal-os
cd ~/personal-os
python3 PersonalOS/scripts/personal_os.py install PersonalOS
python3 PersonalOS/scripts/personal_os.py doctor PersonalOS
~~~

安装命令会写入：

- ~/.personal-os-root：本机根目录指针；
- ~/.codex/AGENTS.md：跨仓库全局加载协议；
- ~/.agents/skills/personal-os/SKILL.md：Codex CLI/IDE 可发现的全局 Skill。

完成后重启 Codex CLI 或 VS Code 的 Codex 扩展。

## 每次工作的闭环

开始：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" start "$PERSONAL_OS_ROOT" --pull --query "继续主线"
~~~

产生稳定任务进度、实验结果、决策、阻塞或知识阶段变化后：

~~~bash
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" checkpoint "$PERSONAL_OS_ROOT" \
  --lane research.kernel_aware_gemm \
  --summary "当前已经推进到的准确位置" \
  --evidence "可验证结果或测试" \
  --artifact "仓库@commit:相对路径" \
  --next "下一项可执行动作"

python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" sync "$PERSONAL_OS_ROOT" \
  --push --message "同步 GEMM 实验检查点"
~~~

网页端只有在最后一步成功后才能读到本地的新状态。

## 读取边界

- HANDOFF.md 是跨窗口恢复摘要，不是事实源。
- KNOWLEDGE.md 是跨领域知识索引，只在全局学习回顾时读取。
- EXPERIMENTS.md 是实验元数据索引；原始 CSV、IR、二进制和图表仍属于实验工作区。
- lanes/*.md 各自拥有任务、决策、阻塞和知识状态，默认互不横向传播。
- 不保存聊天原文、账号令牌、SSH key、Cookie、环境变量秘密或大型实验数据。
