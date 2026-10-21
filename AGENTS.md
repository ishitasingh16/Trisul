# NAVIS — Root AI Rules

This file applies to **every AI interaction** across the entire NAVIS repository.

## Identify Yourself First

At the start of every session, **ask the human which Head you are assisting**:
- Head 1 — AI & Perception (Brain)
- Head 2 — Robotics & Simulation (Body)
- Head 3 — Platform & Integration (Interface)

Then strictly follow the department boundaries defined in `.agents/rules/ai-core-rules.md`.

## Mandatory Rules (Always Active)

1. **Do NOT run any git commands** (commit, push, pull, merge, branch, checkout, etc.) unless the human explicitly asks.
2. **Do NOT modify files outside the active Head's assigned packages** without explicit human permission.
3. **Do NOT change ROS 2 message definitions, topic names, or TF frame names** without confirming that all three Heads agree.
4. **Follow the UI design system** in `.agents/rules/ui-design-rules.md` for all visual/frontend work.
5. **Preserve all existing comments and documentation** unless directly asked to modify them.
6. **When in doubt, ask.** Do not guess intent, architecture decisions, or cross-department changes.

## Read These Before Working

- `.agents/rules/ai-core-rules.md` — Detailed behavioral rules
- `.agents/rules/ui-design-rules.md` — Color palette, typography, design system
- `.agents/tasks/head1-ai-perception.md` — Head 1 tasks and ownership
- `.agents/tasks/head2-robotics-simulation.md` — Head 2 tasks and ownership
- `.agents/tasks/head3-platform-integration.md` — Head 3 tasks and ownership
