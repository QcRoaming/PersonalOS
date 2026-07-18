# PersonalOS

PersonalOS 是一个面向长期协作的、文件驱动的个人状态系统。它把稳定偏好、主线与支线、最近进度、任务交接、已验证知识和实验元数据保存在 GitHub 私有仓库中，而不是依赖聊天原文或单个账号的记忆。

实际 PersonalOS 根目录是 [PersonalOS/](PersonalOS/)，新窗口、新设备或新账号从 [PersonalOS/START_HERE.md](PersonalOS/START_HERE.md) 开始。

## 当前状态

以下是 2026-07-18 的发布前验证快照；动态状态请查看 `HANDOFF.md`、`DASHBOARD.md` 和权威 Lane/注册表：

- `start → checkpoint/registry refresh → views/check → sync --push` 已实现并通过测试；
- 6 条 Lane 结构有效，17 条实验注册记录与生成视图一致；
- install、doctor、Git commit/rebase/push、Lane version 冲突保护均已验证；
- 会话归档支持 `exact_export`、`provided_transcript` 和 `visible_context_only`，自动化测试通过，当前真实归档数为 0；
- 14 项单元测试全部通过。

仍待真实环境验收的是：ChatGPT 文本/语音窗口导入、第二个 ChatGPT 账号恢复，以及第二台设备的 push/pull 往返。[PersonalOS/HANDOFF.md](PersonalOS/HANDOFF.md) 是恢复摘要；权威动态事实由 `PERSONAL.md`、`ROUTES.md`、各 `lanes/*.md` 和注册表拥有。

## 能解决什么

- 为 Codex CLI、VS Code 扩展、ChatGPT 网页和多台机器提供同一套状态恢复协议；本地闭环已验证，真实跨账号和多设备恢复仍待验收。
- 新 ChatGPT 账号可在授权同一 GitHub 私有仓库后按固定入口读取状态；当前不把它表述为已经完成端到端验收。
- 在具有权威仓库写权限的执行环境中，精确命令“导入”可启动隔离的文本/语音转写归档；只读网页连接器需要转交本地 CLI，完整性仍由数据导出或用户逐字稿保证。
- 将研究、写作、环境配置和独立学习拆成相互隔离的 Lane。
- 只同步实验元数据、证据位置、哈希和结论边界；原始数据仍留在各自工作区。

跨端可见性的边界是 Git push：本地未提交的 VS Code 实验不会自动出现在网页端。

## 新设备快速开始

~~~bash
git clone https://github.com/QcRoaming/PersonalOS-v1.git ~/personal-os
cd ~/personal-os
export PERSONAL_OS_ROOT="$PWD/PersonalOS"
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" install "$PERSONAL_OS_ROOT"
python3 "$PERSONAL_OS_ROOT/scripts/personal_os.py" doctor "$PERSONAL_OS_ROOT"
~~~

install 会配置本机根目录指针、全局 ~/.codex/AGENTS.md 和用户级 ~/.agents/skills/personal-os/SKILL.md。之后重启 Codex CLI 或 VS Code 的 Codex 扩展。

## 新账号快速开始

1. 在新账号中授权 GitHub 连接器读取私有仓库 QcRoaming/PersonalOS-v1。
2. 让新对话先读取 PersonalOS/START_HERE.md、HANDOFF.md、PERSONAL.md 和 ROUTES.md。
3. 根据本次请求只选择一个 Lane，不使用旧聊天记忆猜测状态。

本页只负责项目概览和快速开始。完整的新账号、新设备、VS Code 实验同步、知识阶段、冲突处理和隐私说明见 [PersonalOS/README.md](PersonalOS/README.md)。

## 核心文件

~~~text
PersonalOS/
├── START_HERE.md     # 新窗口、新设备和新账号入口
├── PERSONAL.md       # 跨项目稳定画像和约束
├── ROUTES.md         # Lane、依赖与权威存储路由
├── lanes/            # 每条工作线的当前事实
├── HANDOFF.md        # 自动生成的最近进度恢复包
├── KNOWLEDGE.md      # 自动生成的跨领域知识阶段索引
├── DASHBOARD.md      # 自动生成的任务总览
├── registries/       # 机器可读实验元数据
├── EXPERIMENTS.md    # 自动生成的实验总览
├── archives/         # 显式“导入”创建的会话与语音转写归档
├── ARCHIVES.md       # 自动生成的会话归档索引
├── skill/            # 可安装的便携 PersonalOS Skill
├── scripts/          # 状态闭环、实验注册和会话归档工具
└── tests/            # 安装、状态、注册表与归档测试
~~~
