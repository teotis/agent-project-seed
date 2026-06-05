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

## Verify Setup

```bash
make preflight     # Run project health check
make test          # Run tests
python3 tools/panel.py  # Print status panel
```
