<p align="center">
  <img src="logo.png" alt="Port Who" width="500" height="250">
</p>

<h1 align="center">Port Who</h1>

<p align="center">
  <strong>Beautiful Port Inspector TUI — see who's using your ports</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/port-who/"><img src="https://img.shields.io/pypi/v/port-who?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/port-who/"><img src="https://img.shields.io/pypi/pyversions/port-who" alt="Python Versions"></a>
  <a href="https://github.com/bhayanak/port-who/actions/workflows/ci.yml"><img src="https://github.com/bhayanak/port-who/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/bhayanak/port-who/blob/main/LICENSE"><img src="https://img.shields.io/github/license/bhayanak/port-who" alt="License"></a>
  <a href="https://github.com/bhayanak/port-who/releases"><img src="https://img.shields.io/github/v/release/bhayanak/port-who" alt="Release"></a>
</p>

---

A gorgeous, fast alternative to `lsof -i` and `netstat`. See which processes are listening on which ports — with CPU/memory usage, one-key kill, live refresh, and beautiful terminal output.

## Why?

- `lsof -i` output is ugly and hard to parse
- Developers constantly debug port conflicts
- No existing tool combines **port listing + process info + kill** in a single TUI
- _"What's on port 3000?"_ is one of the most-asked developer questions

## Features

| Feature | Description |
|---------|-------------|
| **Interactive TUI** | Full Textual app with table, filter, detail panel, kill dialog |
| **Port Listing** | All listening TCP/UDP ports with process info |
| **Process Details** | PID, name, command, user, CPU%, memory |
| **One-Key Kill** | Select process → press `k` → confirm → done |
| **Filter/Search** | Filter by port number or process name |
| **Watch Mode** | Live-updating view with configurable interval |
| **Port Check** | Quick check: `port-who check 3000` |
| **JSON/CSV Export** | Machine-readable output for scripting |
| **Safety Guards** | Refuses to kill system-critical processes |

## Install

```bash
pip install port-who
```

Requires **Python 3.10+**. Works on **macOS** and **Linux**.

## Usage

### Interactive TUI (default)

```bash
port-who
```

### Non-interactive listing

```bash
# Rich table output
port-who list

# JSON output
port-who list --format json

# CSV output
port-who list --format csv

# Filter by process name
port-who list --filter postgres

# Watch mode (live refresh)
port-who list --watch

# TCP only
port-who list --no-udp
```

### Check a specific port

```bash
port-who check 3000
# → Port 3000: node (PID 12345) — node server.js

port-who check 9999
# → ✅ Port 9999 is free.
```

### Kill a process by port

```bash
port-who kill 3000
# → Kill node (PID 12345) on port 3000? [y/N]

# Skip confirmation
port-who kill 3000 --yes

# Force kill (SIGKILL)
port-who kill 3000 --force --yes
```

## TUI Keybindings

| Key | Action |
|-----|--------|
| `/` | Focus filter input |
| `Escape` | Clear filter |
| `k` | Kill selected process |
| `d` | Toggle detail panel |
| `r` | Refresh data |
| `q` | Quit |

## TUI Preview

```
╭─ Port Who ──────────────────────────────────────────────────╮
│ Filter: [________]                                           │
├──────┬──────────┬───────┬──────────┬──────┬─────────┬───────┤
│ Port │ Process  │  PID  │   User   │ CPU% │ Memory  │Status │
├──────┼──────────┼───────┼──────────┼──────┼─────────┼───────┤
│   80 │ nginx    │  1234 │ www      │  0.2 │ 12.3 MB │LISTEN │
│  443 │ nginx    │  1234 │ www      │  0.2 │ 12.3 MB │LISTEN │
│ 3000 │ node     │  5678 │ dev      │  1.5 │ 85.2 MB │LISTEN │
│ 5432 │ postgres │  9012 │ postgres │  0.8 │156.7 MB │LISTEN │
│ 8080 │ java     │  7890 │ dev      │  3.2 │512.0 MB │LISTEN │
├──────┴──────────┴───────┴──────────┴──────┴─────────┴───────┤
│ [k] Kill  [d] Details  [r] Refresh  [/] Filter  [q] Quit    │
╰─────────────────────────────────────────────────────────────╯
```

## Development

```bash
git clone https://github.com/port-who/port-who.git
cd port-who
pip install -e ".[dev]"

# Run tests
pytest --cov=port_who --cov-report=term-missing

# Lint & format
ruff check src/ tests/
ruff format --check src/ tests/
```

See [CONTRIBUTING](docs/CONTRIBUTING.md) for more details.

## License

[MIT](LICENSE) — use it, fork it, improve it.
