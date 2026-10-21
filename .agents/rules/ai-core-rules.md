# NAVIS — AI Core Rules

These rules are **non-negotiable**. The AI assistant must follow them at all times across the entire NAVIS project.

---

## Rule 1: Git & GitHub — Hands Off

- **NEVER** run `git add`, `git commit`, `git push`, `git merge`, `git rebase`, `git checkout`, `git branch`, `git stash`, `git reset`, `git pull`, or any other git command **unless the human explicitly asks**.
- **NEVER** create, delete, or modify `.gitignore`, `.gitattributes`, or any file inside `.git/`.
- **NEVER** interact with GitHub (creating issues, PRs, releases, modifying repo settings) unless the human gives a direct, unambiguous instruction.
- If a task logically requires a git operation (e.g., "save this work"), **ask the human** instead of running the command yourself.
- You may run **read-only** git commands (`git status`, `git log`, `git diff`, `git remote get-url`) only when needed to understand the codebase context. Never modify state.

---

## Rule 2: Department Boundaries — Stay in Your Lane

The NAVIS project has three departments (Heads). Each AI session is assigned to assist **one specific Head** at a time.

| Head | Department | Packages Owned |
|------|-----------|----------------|
| **Head 1** — AI & Perception | `navis_perception`, `navis_world_model`, `navis_training` |
| **Head 2** — Robotics & Simulation | `navis_description`, `navis_navigation`, `navis_control`, Webots worlds |
| **Head 3** — Platform & Integration | `navis_bringup`, `navis_dashboard`, `navis_msgs`, `navis_interfaces`, launch files |

### Strict Boundaries

- **Only write, edit, or delete files inside the packages assigned to the active Head.**
- If a task requires modifying a file owned by another Head, **stop and inform the human**:
  > "This change requires editing `<file>` which belongs to Head X's department. Should I proceed, or should Head X handle this?"
- **Never silently modify another Head's files.** Even if you know the fix, ask first.
- Cross-department work is allowed **only when the human explicitly grants permission** in that conversation.

### Shared Files (Require Any Head's Permission)

These files affect everyone and require explicit human approval before modification:

- `navis_msgs/` — message definitions (interface contract)
- `navis_interfaces/` — shared constants
- `navis_bringup/config/nav2_params.yaml` — Nav2 configuration
- Any `package.xml` or `CMakeLists.txt` that changes dependencies
- The ROS 2 Interface Contract (topic names, TF frames, message types)

---

## Rule 3: Ask Before Acting on Ambiguity

- If a task is unclear, **ask for clarification** instead of guessing.
- If a task could break another Head's work, **flag it** before proceeding.
- If you are unsure which Head owns a file, **ask**.

---

## Rule 4: No Unsolicited Refactoring

- Do not rename files, folders, topics, or variables across the project unless asked.
- Do not restructure the project directory layout unless asked.
- Do not "improve" code in packages that are not assigned to the active Head.

---

## Rule 5: Document What You Change

- When creating or modifying any file, include a brief comment or docstring explaining **what** and **why**.
- Preserve all existing comments and docstrings unrelated to your changes.
