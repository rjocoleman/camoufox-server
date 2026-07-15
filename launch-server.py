"""
Launch Camoufox as a remote Playwright server with a stable endpoint.

The `camoufox server` CLI calls launch_server() with no arguments, so it binds
a random port and a random ws path. That is fine for a laptop but useless for a
container behind a fixed Service. We call the same launch_server() directly and
pin host, port and ws-path so clients always connect to the same URL:

    ws://<host>:<port>/<ws-path>

launch_server() accepts the same keyword arguments as Camoufox() plus any
Playwright launchServer option (port, host, ws_path). Those extra options pass
straight through to Playwright's firefox.launchServer under the hood.
"""

import os

from camoufox.server import launch_server


def main() -> None:
    port = int(os.environ.get("PORT", "3000"))
    ws_path = os.environ.get("WS_PATH", "camoufox")

    # headless=True keeps the image small and avoids needing an X server. It is
    # slightly more detectable than a real display; if you need maximum stealth,
    # add Xvfb to the image and switch this to headless="virtual".
    launch_server(
        headless=True,
        host="0.0.0.0",  # nosec B104 - the container is meant to be reachable on the pod network
        port=port,
        ws_path=ws_path,
    )


if __name__ == "__main__":
    main()
