# TCL 65R635 validation

Date: November 13, 2026 (Pacific).
Platform: TCL 65R635, Roku A114X, Roku OS 16.0.4 build 853.
No serial, MAC, account, profile, network name, or viewing-title data is recorded here.

## Native compatibility probe

A small channel exercised the same `roAppManager.LaunchApp` call before this fork was
implemented. Its compiler, package integrity, source/resource boundaries and on-TV
startup passed. ECP foreground identity changed from the test channel to Netflix
and Hulu after selecting their tiles, and the user confirmed both play normally.

| App | Installed ID | Version | User playback | Back/Home |
| --- | --- | --- | --- | --- |
| Netflix | 12 | 5.1.130088008 | Normal | Back did not exit; Home returned to Roku Home; accepted by user |
| Hulu | 2285 | 7.8.0 | Normal | Back worked; Home/reopening available |

The test channel was reopened from Roku Home and launched Hulu afterward. Automatic
reopening after power-on is explicitly excluded from acceptance. The probe package
SHA256 is `9e4e472dc2504292c3ae9f8d8545f21e216542355a7e24414823166caa3ee1d1`.

## Hardened build

Version 1.2.1 was installed with the official developer installer. The installer
confirmed 119,582 bytes and Install Success, and ECP confirmed CleanYourRoku 1.2.1.
The actual on-TV screenshot showed the local app grid, correct clock/date, both
local logos, and complete focus borders. Both tiles launched the expected app,
Home returned to Roku Home, and the custom channel reopened afterward.

BrighterScript 0.73.8 validation and all 10 package/configuration/connector/logo
boundary tests passed. The personal package SHA256 is
`522f9ac98ba89c2415216e1fa2f80bbc8f263ac32ab2c6de6cd228098954dda9`.
Personal logos stay local, so a clean-source build with placeholder artwork has a
different package hash. Runtime emitted one benign unused catch-variable warning;
no startup error prevented the UI or either launch path.

The final least-access check restores the original ECP Limited mode and verifies
native app launches using the physical remote. Its result is recorded separately
from the computer-driven checks performed with ECP Enabled.
