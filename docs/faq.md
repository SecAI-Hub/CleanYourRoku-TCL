# Frequently asked questions

## Does Home open this channel?

Home opens Roku Home. Open CleanYourRoku from the app grid. There is no always-on
computer watcher or remote-control server in this fork.

## Does Back return to the channel?

It depends on the streaming app and Roku firmware. On the tested TCL, Netflix's
Back button did not exit; Home worked. Hulu Back worked. A native API method returning
success is not proof of usable playback, so real app checks are recorded separately.

## Why are app logos generic after cloning?

Logos are not distributed. Fetch them from your own TCL using the optional read-only
helper in the README, then rebuild. All runtime artwork remains local.

## Is tracking blocked across the whole TV?

This channel removes its own external artwork requests and optional cloud features.
Whole-device blocking requires network enforcement described in privacy-security.md.

## A helper returns HTTP 403

Confirm that development/testing access is enabled for the intended device and that
the IP is correct. ECP Enabled was sufficient for this TV; do not automatically switch
to Permissive. Keep the stronger local-network boundary whenever it works.
