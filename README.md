# CleanYourRoku TCL

A self-contained Roku home channel for the TCL 65R635, forked from
[UXDreamer/CleanYourRoku](https://github.com/UXDreamer/CleanYourRoku).
The interface has a focused app grid, local artwork, and an optional clock/date.
Netflix and Hulu are the default apps. Channel resources stay in the package;
Roku OS and streaming services retain their own network behavior.

## What this fork changes

- Bundled artwork and validated local configuration; no external asset URLs.
- No phone-remote HTTP server, room-audio classifier, cloud API keys, or media-server credentials.
- Native app launching restricted to numeric IDs in the packaged app list, with a local error message on failure.
- An explicit packaging allowlist excludes scripts, private logos from other apps, environment files, personal media, and legacy site content.
- Pinned compiler dependencies, hash-pinned optional artwork tooling, security tests, and a deterministic ZIP with source hashes.

The custom channel runs on the TV. The physical Home button still opens Roku Home.
Automatic reopening at power-on is outside this build. The channel does not remove
system software or enforce network-wide ad/tracker blocking. See [privacy and security](docs/privacy-security.md).

## Build

Python 3.10+ and Node.js 24 are required for building and static validation.
Generated original artwork is already committed. Nothing installs or deploys automatically.

```sh
npm ci --ignore-scripts --no-audit --no-fund
python3 scripts/build.py
npm run check
npm test
```

The package is `out/cleanyourroku-tcl.zip`; `out/package-manifest.json` records
its SHA256 and all included file hashes. A fresh clone uses generic local tile art.
Actual streaming-app logos can be fetched from your own TV for a personal build:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-artwork.txt
.venv/bin/python scripts/pull_logos.py --host "<TV_IP>"
python3 scripts/build.py
npm run check
npm test
```

Replace `<TV_IP>` with the TV's private IPv4 address. The fetcher verifies the TCL
model, reads only device/app metadata and configured icons, blocks redirects/proxies,
limits responses, and converts supported images into metadata-free local PNGs.
Logos stay git-ignored. Pillow is used only on the computer for these optional tools;
it is not installed on the TV. Run `.venv/bin/python scripts/generate_artwork.py`
only to regenerate the bundled original art.

## Customize

Edit `launcher.json`: choose app order/names/IDs, title, clock visibility, 12/24-hour
format, date visibility, and the focus accent color. Resource URLs and credentials
are deliberately absent from the configuration. Rebuild and validate after editing.

## Install and undo

Use the TV's Development Application Installer to upload the ZIP and install or
replace it. It occupies Roku's one developer-app slot. Keep the developer password
in your own browser. [Installation notes](docs/roku-setup.md) cover the required
local development access and rollback.

## Compatibility

The native launch path was tested on a TCL 65R635 running Roku OS 16.0.4 build 853.
The user confirmed Netflix and Hulu playback. Netflix's physical Back button did
not exit; Home returned to Roku Home. Hulu's Back button worked. This accepted
Netflix limitation is preserved. [Validation record](docs/tcl-65r635-validation.md).
Other devices and future Roku versions require their own validation because the
native `roAppManager.LaunchApp` method is not in the current public API reference.

## Credits and license

MIT, copyright 2026 Damien Pressley; see [LICENSE](LICENSE). This fork keeps the
original project attribution. The Android/Google TV inspiration is
[Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv).
Brand icons belong to their owners and are fetched locally, not distributed here.
The old website/research assets remain outside the app build as upstream history.
