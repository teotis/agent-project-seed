# New Machine Setup

After cloning this repository, run the initialization command to set up project metadata:

```bash
python3 tools/project.py init --name "Your Project Name"
```

This turns the copied template into a project workspace. It renames the package,
rewrites the project-facing README, updates `AGENTS.md` and `control/state.md`,
resets `control/ledger.md` to the new project's first record, writes
`control/init_manifest.md`, activates the Claude Code settings, and keeps the
project-level Codex hooks ready for the status panel and clean-checkpoint gate.

After initialization, review `control/init_manifest.md` first. It lists the
files updated automatically and the remaining project-specific edits to make.

## Portable User Skills

This seed includes a portable skill bundle in `agent-assets/user-skills/`.
Skills are treated as universal packages; the install target only chooses which
user skill directory receives the copy.

Inspect the bundle:

```bash
python3 tools/project.py list-user-skills
python3 tools/project.py list-user-skills --group superpowers
```

Install the default core set:

```bash
python3 tools/project.py install-user-skills --target codex --group core
python3 tools/project.py install-user-skills --target claude --group core
```

Install everything bundled by this seed:

```bash
python3 tools/project.py install-user-skills --target all --group all --force
```

The installer intentionally does not migrate private user config such as API
keys, MCP tokens, model provider credentials, conversation logs, hook state, or
database files.

## Standard MCP Checks

Context7 is the standard documentation MCP for this seed. It should be present
in both Codex and Claude user-level configuration when the new environment is
intended to support library/framework documentation lookup.

Check it after installing or copying user-level agent configuration:

```bash
codex mcp get context7
claude mcp get context7
```

If either check fails, configure MCP in the user's home directory. Do not put
API keys, MCP tokens, or model provider credentials in this repository.

## Complex Tasks (Optional)

Fresh projects should stay light. Use `control/state.md`, `control/ledger.md`,
and checkpoint commits for normal work.

When a task grows into multiple dependent packages, branches, worktrees, agents,
or handoff sessions, create a live state surface on demand:

```bash
python3 tools/project.py task init --name "Complex Refactor" \
  --package 01-contract-characterization \
  --package 02-implementation
```

The generated `control/tasks/<slug>/status.tsv` is the live source of truth for
package execution state. Reports and chat summaries should be refreshed from it,
not treated as authoritative when they disagree.

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

## Codex Hooks

Initialized projects include `.codex/hooks.json` by default. It records a
tracked-dirty baseline at session start, updates the latest tracked-dirty state
after tool use, and blocks Stop if the session leaves new tracked dirty changes
without a local checkpoint. It also loads the same Chinese status panel from
`tools/panel.py`.

The value of the clean-checkpoint hook is simple: it catches newly created
tracked dirty files at the end of a session. It records the starting tracked
dirty baseline, then blocks Stop only when the session leaves additional tracked
dirt uncommitted. It does not auto-commit, push, delete, or rewrite files.

For optional end-of-turn guarded commits in Codex, add the notify hook to your user config:

```bash
# Edit ~/.codex/config.toml and add:
notify = [
  "python3",
  "/absolute/path/to/this/project/tools/hooks/codex_notify.py"
]
```

Replace the path with this repository's actual absolute path.

For cross-project Codex App usage outside repositories created from this seed,
also consider installing a user-level `clean-checkpoint-first` skill and Stop
hook under `~/.codex`.

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
python3 tools/project.py list-user-skills
codex mcp get context7
claude mcp get context7
```
