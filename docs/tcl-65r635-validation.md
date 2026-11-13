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

Source/package tests and actual deployment results are recorded before delivery.
A successful probe does not replace rechecking the final native UI and app launches.
