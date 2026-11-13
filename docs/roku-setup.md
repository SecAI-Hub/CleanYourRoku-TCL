# Install the native channel

Build and validate the ZIP using the repository README before touching the TV.
Check for an existing developer app; Roku has one slot and replacing it overwrites
that app. This fork does not change firmware or remove streaming apps.

Enable Roku's official developer mode with the remote sequence Home three times,
Up twice, then Right, Left, Right, Left, Right. Review the agreement yourself,
choose the installer/restart action and set a unique developer password.

Open the TV's installer URL on the trusted local network. The username is `rokudev`;
enter the password directly in the browser. Upload `out/cleanyourroku-tcl.zip` and
choose installation with zip, or replacement when updating this same channel.
Never paste credentials in chat or include them in scripts, issues, or commits.

The computer-side icon fetcher and diagnostic tools used ECP Enabled. The running
channel uses its native launch method rather than ECP, and needs no computer-side
server. Permissive is not a default instruction in this fork.

After installation, select each configured streaming app and verify normal startup
and playback. Check the real remote's navigation and Home button, then reopen the
custom channel manually. Report the actual Back destination; apps handle it differently.
No automatic startup/reopen behavior is required or promised.

To undo, delete this developer app through the installer. This does not delete
Netflix or Hulu. The original application remains available as the upstream source
revision noted in the validation record. Retain a previous built ZIP for rollback
before replacing a working version. Developer mode can be disabled when sideloading
is no longer needed.
