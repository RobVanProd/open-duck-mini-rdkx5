# CUA Computer-Use Setup

Last updated: 2026-06-22

## Purpose

CUA was installed so future Codex sessions can drive the local desktop/browser
when shell/API access is not enough, for example to operate Colab notebooks.

Use this for GUI/browser workflows only. Prefer shell/API commands whenever
they are sufficient.

## Installed Paths

Repository clone:

```text
/home/lsd/robots/external/cua
```

Isolated Python environment:

```text
/home/lsd/robots/envs/cua
```

Native driver:

```text
/home/lsd/robots/envs/cua/bin/cua-driver
/home/lsd/.cua-driver/packages/current/cua-driver
```

CUA CLI:

```text
/home/lsd/robots/envs/cua/bin/cua
```

Codex MCP registration:

```bash
codex mcp get cua-driver
```

Expected:

```text
command: /home/lsd/robots/envs/cua/bin/cua-driver
args: mcp
enabled: true
```

Skill pack:

```text
/home/lsd/.cua-driver/skills/cua-driver
/home/lsd/.codex/skills/cua-driver -> /home/lsd/.cua-driver/skills/cua-driver
```

## Validation Performed

Commands:

```bash
/home/lsd/robots/envs/cua/bin/cua --help
/home/lsd/robots/envs/cua/bin/cua-driver --version
/home/lsd/robots/envs/cua/bin/cua-driver list-tools
/home/lsd/robots/envs/cua/bin/cua-driver check_permissions
/home/lsd/robots/envs/cua/bin/cua-driver health_report
/home/lsd/robots/envs/cua/bin/cua-driver call get_screen_size '{}'
/home/lsd/robots/envs/cua/bin/cua-driver call list_windows '{}'
```

Observed:

```text
cua-driver 0.6.0
health_report overall: ok
X11 reachable
AT-SPI reachable
screen size: 1920x1080
host target selected for cua do
```

## Current Caveats

The high-level command:

```bash
cua do screenshot --save <path>
```

failed once with an X11 protocol error on this Wayland/XWayland desktop. The
lower-level driver health and `get_screen_size` checks pass, so prefer direct
`cua-driver` tools or the MCP server first.

The current desktop session had no visible browser window during setup. Future
sessions may need to launch or focus Chrome/Firefox before browser automation is
useful.

Current session tools will not automatically refresh after adding the MCP
server. Start a fresh Codex session to expose the `cua-driver` MCP tools.

## Useful Commands

List windows:

```bash
/home/lsd/robots/envs/cua/bin/cua-driver call list_windows '{}'
```

Inspect a window:

```bash
/home/lsd/robots/envs/cua/bin/cua-driver call get_window_state \
  '{"pid":1234,"window_id":5678}'
```

Zoom a window region:

```bash
/home/lsd/robots/envs/cua/bin/cua-driver call zoom \
  '{"window_id":5678,"x1":0,"y1":0,"x2":1200,"y2":800}'
```

Codex MCP config:

```bash
codex mcp add cua-driver -- /home/lsd/robots/envs/cua/bin/cua-driver mcp
```

Host consent for the high-level CUA CLI:

```bash
CUA_TELEMETRY_ENABLED=false /home/lsd/robots/envs/cua/bin/cua do-host-consent
CUA_TELEMETRY_ENABLED=false /home/lsd/robots/envs/cua/bin/cua do switch host
```

## Safety

Do not use GUI automation for robot-moving tests. Robot hardware tests still
require explicit operator approval and physical presence.
