# camoufox-server

A container image that runs [Camoufox](https://github.com/daijro/camoufox) as a
remote Playwright server: connect over a websocket and drive a stealth Firefox.

Camoufox is a patched Firefox (no Chromium) built to resist bot detection. It
fakes fingerprints, timezone, locale and geolocation and patches a lot of the
tells automated browsers leak. The image bakes the browser in at build time, so
there's no download on cold start.

## Version pins

Two things are pinned separately in the Dockerfile:

- **`cloverlabs-camoufox`** (the python wrapper), not the original `camoufox`
  package. The original has had no PyPI release since 0.4.11 (Firefox 135, Jan
  2025); the fork is the current maintainer's and the upstream README points to
  it. It still pulls the official browser binaries.
- **The browser build** from [daijro/camoufox](https://github.com/daijro/camoufox)
  releases, currently Firefox 150. Since wrapper 0.5.x the pip version no longer
  implies a browser version, so it gets its own pin.

There's also a playwright pin and a patch for an upstream `camoufox sync` bug.
Both are commented in the Dockerfile; recheck them when bumping versions.

## What this won't do

Camoufox is probably the best free anti-detection browser going, and it's good.
It still won't beat the serious commercial stacks. Cloudflare Turnstile,
DataDome and PerimeterX will catch you plenty, especially at scale or from
datacentre IPs. It's an arms race and you're not going to win it outright with a
browser. Where your traffic comes out matters as much as the browser - use
residential or mobile egress and don't hammer sites.

## What you get

- `ghcr.io/rjocoleman/camoufox-server:<browser-version>` (e.g. `:150.0.2`) and
  `:latest`
- Listens on `0.0.0.0:3000` with a stable ws path (`camoufox` by default)
- Runs as a non-root user (uid 1000)
- Built for `linux/amd64` and `linux/arm64`

## Run it

```sh
docker build -t camoufox-server .
docker run --rm -p 3000:3000 camoufox-server
# -> ws://localhost:3000/camoufox
```

Override the port and ws path at run time:

```sh
docker run --rm -p 8000:8000 -e PORT=8000 -e WS_PATH=my-path camoufox-server
# -> ws://localhost:8000/my-path
```

Connect from a Playwright client - note it's `firefox.connect`, not `chromium`:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://<host>:3000/camoufox")
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
```

## Why a launcher script instead of `camoufox server`

The bare `camoufox server` CLI takes no flags: it binds a random port and ws
path and prints them to stdout, which is no use behind a fixed Service.
`launch-server.py` calls the same `launch_server()` with host, port and ws-path
pinned so the endpoint never moves.

It runs headless by default. For a bit more stealth, add Xvfb and switch
`launch-server.py` to `headless="virtual"`.

## How CI tracks upstream

`build.yml` builds and pushes the multi-arch image to GHCR on pushes to `main`,
daily, and on manual dispatch. `track-upstream.yml` checks PyPI and the
daijro/camoufox releases daily and opens a bump PR when either moves.

Review those PRs rather than auto-merging: a new Firefox build can shift
fingerprints, and a new wrapper can invalidate the playwright pin or the sync
patch.

## Disclaimer and trademarks

"Firefox" is a trademark of the Mozilla Foundation and "Playwright" is a
trademark of Microsoft. Camoufox is a separate open-source project (see
[daijro/camoufox](https://github.com/daijro/camoufox)). This image is
unofficial and unaffiliated with any of them - it just packages upstream
releases into a container.

It drives a browser against live sites. It's tested and works, but there's no
warranty and no guarantee it behaves on a browser build it hasn't seen. Use it
at your own risk.

## How this was built

Built largely with AI assistance (Claude) and tested against the 150.0.2 image
on amd64 and arm64. Working, but a spare-time project - no warranty, no support
promises.

## Licence

MIT. See [LICENSE](LICENSE).
