# PersonalOS

PersonalOS 是一个面向长期协作的、文件驱动的个人状态系统。它把稳定偏好、主线与支线、最近进度、任务交接、已验证知识和实验元数据保存在 GitHub 私有仓库中，而不是依赖聊天原文或单个账号的记忆。

实际 PersonalOS 根目录是 [PersonalOS/](PersonalOS/)，新窗口、新设备或新账号从 [PersonalOS/START_HERE.md](PersonalOS/START_HERE.md) 开始。

## 能解决什么

- 在 Codex CLI、VS Code 扩展、ChatGPT 网页和多台机器之间恢复同一工作状态。
- 更换 ChatGPT 账号后，通过重新授权同一 GitHub 私有仓库恢复个人画像、当前任务、最近实验和学习阶段。
- 在任意窗口输入精确命令“导入”时，启动隔离的文本/语音转写归档流程；完整性由数据导出或用户提供的逐字稿保证。
- 将研究、写作、环境配置和独立学习拆成相互隔离的 Lane。
- 只同步实验元数据、证据位置、哈希和结论边界；原始数据仍留在各自工作区。

跨端可见性的边界是 Git push：本地未提交的 VS Code 实验不会自动出现在网页端。

## 新设备快速开始

~~~bash
git clone https://github.com/QcRoaming/PersonalOS-v1.git ~/personal-os
cd ~/personal-os
python3 PersonalOS/scripts/personal_os.py install PersonalOS
python3 PersonalOS/scripts/personal_os.py doctor PersonalOS
~~~

install 会配置本机根目录指针、全局 ~/.codex/AGENTS.md 和用户级 ~/.agents/skills/personal-os/SKILL.md。之后重启 Codex CLI 或 VS Code 的 Codex 扩展。

## 新账号快速开始

1. 在新账号中授权 GitHub 连接器读取私有仓库 QcRoaming/PersonalOS-v1。
2. 让新对话先读取 PersonalOS/START_HERE.md、HANDOFF.md、PERSONAL.md 和 ROUTES.md。
3. 根据本次请求只选择一个 Lane，不使用旧聊天记忆猜测状态。

完整的新账号、新设备、VS Code 实验同步、知识阶段、冲突处理和隐私说明见 [PersonalOS/README.md](PersonalOS/README.md)。

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
└── scripts/          # 状态闭环、实验注册和会话归档工具
~~~
