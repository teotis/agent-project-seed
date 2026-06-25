# New Machine Setup

After cloning this repository, run the initialization command to set up project metadata:

macOS/Linux:

```bash
python3 tools/project.py init --name "Your Project Name"
```

Windows PowerShell:

```powershell
py -3 tools/project.py init --name "Your Project Name"
```

This turns the copied template into a project workspace. It renames the package,
rewrites the project-facing README, updates `AGENTS.md` and `control/state.md`,
resets `control/ledger.md` to the new project's first record, writes
`control/init_manifest.md`, activates the Claude Code settings, and keeps the
project-level Codex hooks ready for the status panel and clean-checkpoint gate.

After initialization, review `control/init_manifest.md` first. It lists the
files updated automatically and the remaining project-specific edits to make.

## Claude Code New-Session Defaults

For the smoothest Claude Code path, use Claude Code v2.1.140 or newer, then set
user-level new sessions to `auto` permission review:

macOS/Linux:

```bash
python3 tools/project.py configure-claude
```

Windows PowerShell:

```powershell
py -3 tools/project.py configure-claude
```

The command edits only the user-level Claude settings JSON
(`~/.claude/settings.json` on macOS/Linux or `%USERPROFILE%\.claude\settings.json`
on Windows) and preserves existing `allow`/`deny` rules. It checks
`claude --version` and refuses to write if it cannot verify that the installed
Claude Code is v2.1.140 or newer. Use `--dry-run` to preview the target file
without writing it.

## Portable User Skills

This seed includes a portable skill bundle in `agent-assets/user-skills/`.
Skills are treated as universal packages; the install target only chooses which
user skill directory receives the copy. Skill packages live under one flat
`skills/` directory; the manifest chooses install profiles.

Inspect the bundle:

macOS/Linux:

```bash
python3 tools/project.py list-user-skills
python3 tools/project.py list-user-skills --profile recommended
```

Windows PowerShell:

```powershell
py -3 tools/project.py list-user-skills
py -3 tools/project.py list-user-skills --profile recommended
```

Install the default recommended set:

macOS/Linux:

```bash
python3 tools/project.py install-user-skills --target codex
python3 tools/project.py install-user-skills --target claude
```

Windows PowerShell:

```powershell
py -3 tools/project.py install-user-skills --target codex
py -3 tools/project.py install-user-skills --target claude
```

Install everything bundled by this seed:

macOS/Linux:

```bash
python3 tools/project.py install-user-skills --target all --profile all --force
```

Windows PowerShell:

```powershell
py -3 tools/project.py install-user-skills --target all --profile all --force
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

macOS/Linux:

```bash
python3 tools/project.py task init --name "Complex Refactor" \
  --package 01-contract-characterization \
  --package 02-implementation
```

Windows PowerShell:

```powershell
py -3 tools/project.py task init --name "Complex Refactor" `
  --package 01-contract-characterization `
  --package 02-implementation
```

The generated `control/tasks/<slug>/status.tsv` is the live source of truth for
package execution state. Reports and chat summaries should be refreshed from it,
not treated as authoritative when they disagree.

## Governance Lifecycle (Optional)

Do not enable lifecycle tracking by default for every copied project. One-off
projects can finish with normal checkpoint commits and a clean handoff; they do
not need a standing governance file.

Use project scale as the trigger:

- `one-off`: skip `control/governance.md`; delete or archive temporary rules,
  scripts, and reports at handoff.
- `lightweight`: keep important keep/defer/retire decisions in
  `control/ledger.md`.
- `sustained`: generate `control/governance.md` and classify durable rules,
  verification scripts, reports, and agent workflows as `Protect`, `Pilot`,
  `Defer`, or `Retire`.

macOS/Linux:

```bash
python3 tools/project.py governance init --profile sustained
```

Windows PowerShell:

```powershell
py -3 tools/project.py governance init --profile sustained
```

This command only creates `control/governance.md`. It does not add hooks,
delete files, schedule reviews, or make `tools/project.py check` stricter.

## Environment Variables

macOS/Linux:

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
# Edit .env and fill in your API keys
```

## Claude Code Settings

Initialized projects include `.claude/settings.json` as the default project-level Claude Code configuration. To customize permissions or hooks, edit `.claude/settings.json` (not the example file).

The project settings include:

- `UserPromptSubmit`: injects a short Chinese project snapshot only on the first prompt of a session, unless a handoff flow explicitly requests `panel_mode=handoff`.
- `Stop`: runs `tools/project.py commit` to create a guarded local checkpoint commit when allowed changes are present.

This is the default Claude Code path and does not require user-level hook setup.
User-level hook/config setup is optional; use it only when you want similar
behavior outside repositories that carry this project-level configuration.

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

For optional end-of-turn guarded commits in Codex, add the notify hook to your user config.

macOS/Linux:

```bash
# Edit ~/.codex/config.toml and add:
notify = [
  "python3",
  "/absolute/path/to/this/project/tools/hooks/codex_notify.py"
]
```

Windows:

```toml
# Edit %USERPROFILE%\.codex\config.toml and add:
notify = [
  "py",
  "-3",
  "C:\\absolute\\path\\to\\this\\project\\tools\\hooks\\codex_notify.py"
]
```

Replace the path with this repository's actual absolute path. The repository
also includes `.codex/config.windows.example.toml` and
`.codex/hooks.windows.json` for Windows-specific Codex setup, plus
`.claude/settings.windows.example.json` for Claude Code.

For cross-project Codex App usage outside repositories created from this seed,
also consider installing a user-level `clean-checkpoint-first` skill and Stop
hook under `~/.codex` on macOS/Linux or `%USERPROFILE%\.codex` on Windows.

Suggested layering:

- `AGENTS.md`: project invariants and short workflow pointer.
- User or repo skill: repair/verification/local-commit workflow.
- Stop hook: mechanical dirty-workspace and closeout checks.
- Permissions/rules: push/reset/remove/staging risk boundaries.
- Worktrees: isolated fixes for independent issues before final integration.

## Verify Setup

macOS/Linux:

```bash
make preflight     # Run project health check
make test          # Run tests
python3 tools/panel.py  # Print status panel
python3 tools/project.py configure-claude
python3 tools/project.py list-user-skills
python3 tools/project.py governance init --profile sustained
codex mcp get context7
claude mcp get context7
```

Windows PowerShell:

```powershell
py -3 tools/project.py check
py -3 -m pytest
py -3 tools/panel.py
py -3 tools/project.py configure-claude
py -3 tools/project.py list-user-skills
py -3 tools/project.py governance init --profile sustained
codex mcp get context7
claude mcp get context7
```
