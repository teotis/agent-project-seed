# New Machine Setup

After cloning this repository, run the initialization command to set up project metadata:

```bash
python3 tools/project.py init --name "Your Project Name"
```

This renames the package, updates `AGENTS.md`, `control/state.md`, and `control/ledger.md`, and activates the Claude Code settings.

## Environment Variables

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

## Claude Code Settings

The init command copies `.claude/settings.example.json` to `.claude/settings.json` automatically. To customize permissions or hooks, edit `.claude/settings.json` (not the example file).

The example settings include a `UserPromptSubmit` status-panel hook. It injects
a short Chinese project snapshot only on the first prompt of a session, unless a
handoff flow explicitly requests `panel_mode=handoff`.

## Codex Hooks (Optional)

For end-of-turn guarded commits in Codex, add the notify hook to your user config:

```bash
# Edit ~/.codex/config.toml and add:
notify = [
  "python3",
  "/absolute/path/to/this/project/tools/hooks/codex_notify.py"
]
```

Replace the path with this repository's actual absolute path.

For cross-project Codex App usage, also consider installing a user-level
`clean-checkpoint-first` skill and Stop hook under `~/.codex`. That user-level
layer should enforce the general checkpoint rule: if a session creates new
tracked dirty changes, it must either commit a local checkpoint or clearly report
why VCS closeout is blocked. Keep this separate from `AGENTS.md` so copied
projects inherit a small shared contract while the repeatable workflow lives in
skills and hooks.

For new-session context in Codex, use `.codex/hooks.json` as the project-level
hook example. It loads the same Chinese status panel from `tools/panel.py`.

Suggested layering:

- `AGENTS.md`: project invariants and short workflow pointer.
- User or repo skill: repair/verification/local-commit workflow.
- Stop hook: mechanical dirty-workspace and closeout checks.
- Permissions/rules: push/reset/remove/staging risk boundaries.
- Worktrees: isolated fixes for independent issues before final integration.

## Verify Setup

```bash
make preflight     # Run project health check
make test          # Run tests
python3 tools/panel.py  # Print status panel
```
