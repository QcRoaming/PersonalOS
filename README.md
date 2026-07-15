# PersonalOS

PersonalOS 是一个面向长期协作的、文件驱动的个人状态系统。它将稳定偏好、主线与支线、任务交接、已验证知识和实验元数据保存在可审查的 Markdown/JSON 文件中，而不是保存聊天原文。

仓库的实际 PersonalOS 根目录是 [`PersonalOS/`](PersonalOS/)。

## 适用场景

- 在 Codex、IDE 和多台机器之间延续同一项目状态。
- 将研究、写作、环境配置等工作分成相互隔离的 Lane。
- 为论文实验保存可复现的元数据、证据位置和用途边界；原始数据、IR、二进制和图表仍留在各自工作区。

## 快速开始

```bash
git clone https://github.com/QcRoaming/PersonalOS-v1.git ~/personal-os
export PERSONAL_OS_ROOT="$HOME/personal-os/PersonalOS"
cd "$PERSONAL_OS_ROOT"

python3 scripts/personal_os.py check .
python3 scripts/personal_os.py dashboard .
```

在 PowerShell 中，可设置用户级环境变量：

```powershell
[Environment]::SetEnvironmentVariable(
  "PERSONAL_OS_ROOT",
  "$HOME\\personal-os\\PersonalOS",
  "User"
)
```

## 目录结构

```text
PersonalOS/
├── PERSONAL.md       # 跨项目的稳定偏好和硬约束
├── ROUTES.md         # 主线、支线、依赖与存储路由
├── DASHBOARD.md      # 自动生成的状态总览；不手工编辑
├── lanes/            # 每条工作线的当前状态
├── registries/       # 机器可读的实验元数据
├── EXPERIMENTS.md    # 由实验注册表生成的可读总览
├── pending/          # 并行窗口待合并的状态增量
└── scripts/          # 校验、路由和注册表维护工具
```

## 使用原则

- 每次对话只选择一条活动 Lane；按 `ROUTES.md` 的 Routing Hints 选择，并且只导入其中声明的依赖小节。
- 只持久化会影响后续工作的稳定状态，不保存聊天原文、凭据或认证信息。
- 更新 Lane 前先检查其 `version`；完成修改后执行结构检查并重建仪表盘（`DASHBOARD.md`）。
- 多机协作时先拉取，再在一个语义检查点提交和推送；不要静默覆盖另一个副本。

完整的文件职责、实验注册表用法与本地维护命令见 [`PersonalOS/README.md`](PersonalOS/README.md)。
