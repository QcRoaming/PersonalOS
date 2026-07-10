# PersonalOS Agent Protocol

Treat this directory as structured state, not as a note dump.

## Read protocol

1. Read `PERSONAL.md` and `ROUTES.md` for continuity work.
2. Route the current request to exactly one lane.
3. Read only that lane file.
4. Read another lane only when `ROUTES.md` declares a dependency relevant to the request.
5. For generic one-off questions, do not load or update a lane.

## Context firewall

- Global preferences may flow into every lane.
- Lane-local facts must not flow sideways by default.
- Cross-lane information must use an explicit dependency or pointer.
- Store details in their owning lane; store only a pointer in dependent lanes.
- Do not copy the same fact into multiple authoritative files.

## Write boundary

Persist only semantic state changes:

- task creation or state transition;
- verified deliverable or experiment result;
- durable decision with future consequences;
- blocker or next action;
- explicit stable preference;
- knowledge-stage change supported by evidence.

Do not persist raw conversations, ordinary explanations, temporary guesses, unaccepted suggestions, one-off examples, or resolved errors without future impact. Discussion alone is not evidence of mastery.

Apply explicit user controls:

- `同步状态`: commit the current semantic delta.
- `这次不记录` or `这只是临时讨论`: do not write state.
- `把它提升为主线`: require confirmation before changing topology.

## Safe update protocol

1. Read the lane `version` before editing.
2. Build one compact delta for the completed work unit.
3. Patch only the owning lane and bump `version` by one.
4. Update `ROUTES.md` only for topology, priority, dependency, or storage changes.
5. Update `PERSONAL.md` only for explicit or repeatedly confirmed global facts.
6. Run `python3 scripts/personal_os.py check .`.
7. Run `python3 scripts/personal_os.py dashboard .` after a durable change.

If the lane version changed after it was read, do not overwrite it. Write `pending/<timestamp>-<session>.delta.md` with `lane`, `base_version`, and the proposed changes. Merge against the latest lane, then delete the processed delta.

## Recommendation boundary

- Recommend within the active lane by default.
- Compare all lanes only when the user requests global prioritization.
- Respect `priority`, `role`, blockers, prerequisites, and explicit user intent.

