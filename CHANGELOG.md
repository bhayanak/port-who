# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-11

### Added

- Interactive TUI mode with Textual — DataTable, filter bar, detail panel
- Non-interactive Rich table output for scripting and piping
- Port scanning via psutil (TCP + UDP listening sockets)
- Process enrichment: CPU%, memory, full command line, user, creation time
- One-key kill with confirmation dialog (SIGTERM default, SIGKILL with `--force`)
- `port-who check <port>` — quick single-port lookup
- `port-who kill <port>` — kill process on a port with safety checks
- `port-who list` — non-interactive listing with `--format json|csv|table`
- `--watch` mode with configurable refresh interval
- `--filter` by process name
- System-critical process protection (refuses to kill init, sshd, etc.)
- Root/sudo detection with warning
- Cross-platform support: macOS + Linux
- CI pipeline: lint (Ruff), test (pytest + coverage), security (Trivy, pip-audit, SBOM)
- PyPI release pipeline with trusted publishing
