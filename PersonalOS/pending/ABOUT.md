# Pending Deltas

此目录只保存尚未合并的语义增量，不保存对话原文。

文件名建议：`YYYYMMDDTHHMMSS-<session>.delta.md`。

```markdown
---
lane: research.kernel_aware_gemm
base_version: 1
session_id: example
created_at: 2026-07-10T12:00:00+09:00
---

- task: example
  change: moved from next to doing
  evidence: explicit user statement or verified artifact
```

合并增量时必须先读取 Lane 最新版本。合并成功后删除对应 delta 文件。

