# Privacy and security of this fork

The reviewed channel uses local resources and local configuration. It contains no
network transfer/socket component, external image URL, microphone feature, analytics,
viewing-history log, cloud classifier, or account/API-key field. Normal streaming
apps run separately and retain their own data collection.

## Controls enforced by this build

- Configuration accepts only documented fields and 1-12 uniquely identified apps.
- App IDs are numeric; runtime launch requests must match the packaged allowlist.
- Artwork paths are generated locally and checked again by the tile renderer.
- Package entries come from an explicit list. Unknown source files, scripts, secrets,
  personal media, and old website files do not enter the ZIP.
- Builds reject external URI literals, non-local XML resource attributes, unreviewed
  component creation, dynamic component names/code execution, and linked/out-of-root sources.
- Optional icon fetches use an explicit private IPv4 address, exact TCL model check,
  read-only endpoint allowlist, no proxies/redirects, bounded responses, bounded image
  dimensions, and fresh PNG output without input metadata.

These are source/build controls for this reviewed app. They are not a Roku-wide
runtime network firewall. A malicious code change could change the controls; review
source changes and package hashes. The Roku OS independently controls app permissions.

## Device-wide tracking and advertising

Enforce domain blocking through the existing router/DNS service or a maintained
local resolver such as AdGuard Home or Pi-hole. Start with TV-specific rules and
verify Netflix/Hulu playback and updates after each batch. Avoid a blanket Roku-domain
block; retain a rollback to the original TV DNS policy. Keep diagnostic DNS logs short.

DNS cannot reliably separate ads delivered from the same host as desired content,
or prevent a streaming provider learning which authenticated content it serves.
No router/DNS rule has been applied or verified by installing this channel. The
interface intentionally has no unverified protection-status badge.

## Local development access

Sideloading exposes Roku's development installer/debug services to reachable LAN
clients. Use a unique developer password and a trusted management network. Never
forward these ports to the Internet. ECP Enabled was used for testing and one-time
icon fetching; Permissive was unnecessary. Reducing external-control access after
validation should be tested with the actual native channel and required features.
Disabling developer mode may remove access to the sideloaded channel; retain the
built ZIP/source for recovery. This fork cannot close OS services itself.
