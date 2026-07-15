---
name: personal-os
description: Recover and maintain the user's cross-window, cross-device, and cross-account PersonalOS state. Use for continue, next, sync, remember, prior progress, current work, task status, experiment status, learning stage, lane changes, or global reviews.
---

# PersonalOS

Treat the canonical private Git repository as deterministic state. Never substitute model memory for an available canonical file.

## Locate the canonical root

Use this order:

1. PERSONAL_OS_ROOT.
2. The path stored in ~/.personal-os-root.
3. The current directory or nearest parent containing PERSONAL.md, ROUTES.md, and lanes/.
4. With an authorized GitHub connector, repository QcRoaming/PersonalOS-v1, subdirectory PersonalOS/.

If the canonical source is unavailable, report the blocker. Do not silently promote a local mirror or chat memory.

## Start a continuity turn

1. Local CLI/IDE: when the worktree is clean, run personal_os.py start ROOT --pull --query REQUEST.
2. Web/remote: fetch the newest default-branch versions of START_HERE.md, HANDOFF.md, PERSONAL.md, and ROUTES.md.
3. Select exactly one Lane. Read only that Lane and dependency sections explicitly named in ROUTES.md.
4. Use KNOWLEDGE.md only for an explicit cross-domain learning review.
5. Use EXPERIMENTS.md or one registry entry only when experiment evidence is relevant.

## Persist only semantic deltas

Persist a compact change when a task state, verified artifact or experiment, durable decision, blocker, next action, explicit stable preference, or evidence-backed knowledge stage changes.

Do not store raw conversations, ordinary questions, speculative conclusions, secrets, large artifacts, or discussion alone as mastery evidence.

Local CLI/IDE should use personal_os.py checkpoint, then personal_os.py sync --push. Web writes must update the canonical repository first. Never force-push or overwrite a newer Lane version.

Knowledge stages are unknown → exposed → understood → applied → verified; use stale for evidence that needs revalidation.

## Context firewall

- Global preferences may flow to every Lane.
- Lane-local tasks, experiments, knowledge and recommendations do not flow sideways.
- Raw experiment files remain in the owning workspace; PersonalOS stores compact results and immutable artifact pointers.
- A new account is recovered through GitHub authorization and START_HERE.md, not through the old account's memory or Library.
