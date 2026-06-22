# Browser Control Setup

Last updated: 2026-06-22

## Purpose

Browser control was added so future Codex sessions can operate Colab or other
web tools when shell/API access is not enough.

Prefer shell commands and local scripts whenever possible. Use browser control
only for workflows that truly need a GUI login or notebook UI.

## Installed Path

Playwright was installed outside the robot repos:

```text
/home/lsd/robots/browser-control
```

The Node package lives at:

```text
/home/lsd/robots/browser-control/node_modules/playwright
```

Override this path with `PLAYWRIGHT_PACKAGE_PATH` if needed.

## Launch Command

The most reliable launch path so far is a Playwright-managed persistent Chrome
session:

```bash
cd /home/lsd/robots/open-duck-mini-rdkx5
node scripts/launch_colab_chrome.js
```

The helper keeps Chrome alive and prints:

```text
PLAYWRIGHT_COLAB_READY
CDP=http://127.0.0.1:9223
PROFILE=/home/lsd/robots/browser-control/playwright-chrome-profile
```

Leave that process running while using the browser.

## CDP Probe

Check that the browser is reachable:

```bash
curl -fsS http://127.0.0.1:9223/json/version
```

Inspect open pages:

```bash
node - <<'JS'
const { chromium } = require('/home/lsd/robots/browser-control/node_modules/playwright');
(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const pages = browser.contexts().flatMap(c => c.pages());
  console.log(JSON.stringify({
    pages: pages.length,
    urls: pages.map(p => p.url()),
    titles: await Promise.all(pages.map(p => p.title().catch(e => String(e)))),
  }, null, 2));
  // Do not call browser.close(); it closes the live operator browser.
})();
JS
```

## Current Caveat

The Playwright-managed Chrome profile can open Colab and expose a CDP endpoint,
but Google currently rejects sign-in from that automation-launched profile with:

```text
Couldn’t sign you in
This browser or app may not be secure.
```

Rob confirmed the same message in the visible browser. Because of that, do not
block project work on the browser path. Continue local CPU/CUDA/ROCm work when
browser login is not available.

## Related Setup

CUA desktop automation is documented in:

```text
docs/CUA_COMPUTER_USE_SETUP.md
```

CUA reports healthy screen/accessibility support, but in this session it did
not list the Playwright-managed Chrome window. Use CDP for browser inspection
when possible.

## Safety

Do not use browser or GUI automation for robot-moving tests. Robot hardware
tests still require explicit operator approval and physical presence.
