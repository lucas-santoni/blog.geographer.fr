---
title: "Nightly encrypted offsite backup of $HOME on macOS"
slug: macos-restic-b2
date: 2026-05-12
description: "A practical guide to setting up restic, resticprofile, and Backblaze B2 for nightly encrypted offsite backups on macOS, with the launchd, TCC, and codesigning details that aren't in the docs."
---

I wanted unattended, encrypted, offsite backups of `$HOME` on my MacBook Pro:
nightly, deduplicated, secrets in Keychain, retention managed for me and the
laptop firing the job on its own while I sleep.

This post walks the setup top to bottom. We start with the building blocks
and run a backup by hand. Then we wire it into launchd so it runs every
night. After that, _operational polish_: notifications and the small things
that make the setup pleasant. And finally, the repo layout.

The code is on GitHub at
[lucas-santoni/macos-backup-restic-b2](https://github.com/lucas-santoni/macos-backup-restic-b2).

The backups are uploaded to Backblaze B2 but the same setup works against any
other restic backend (S3, SFTP, REST server...) with minor adjustments to the
credentials section.

Versions used: `restic 0.18.1`, `resticprofile 0.33.1`, macOS 26.4.1
(Tahoe) on an M1 MacBook Pro.

## The building blocks

This section is an overview of the tools we are going to work with. It includes
the pros and cons of each tool, plus the alternatives I considered.

### restic

**[restic](https://restic.net/)** is an encrypted backup tool that
deduplicates data automatically: identical chunks of content are stored
only once, across files and across snapshots. Snapshots are stored in a
content-addressed repository (each chunk is keyed by a hash of its
content) on whatever backend we point it at (local disk, SFTP, S3, B2, REST
server...). Encryption is mandatory and uses a passphrase set on `init`. Deduplication
works via content-defined chunking, so renames are free and a daily snapshot of
a mostly-unchanged tree adds only the diff.

Limitations: command-line only, no GUI. Browsing a snapshot's contents is
possible via `restic mount`, but that uses FUSE, which on macOS means installing
macFUSE, and performance on large trees is mediocre. For most restore work I
just use `restic restore --include` to a temp directory and poke around there.
For a polished consumer UX, restic isn't the right pick.

Other alternatives I considered:

- **[Borg](https://www.borgbackup.org/)** is battle-tested and the feature
  overlap is large, but it has no native cloud backends. Putting a Borg repo in
  object storage means using something like rclone or running a Borg server on
  a remote box.
- **[Time Machine](https://support.apple.com/en-us/HT201250)** encrypts at
  rest on an encrypted APFS volume but isn't offsite without third-party
  glue, and it's tied to a directly-attached or
  [Bonjour](https://developer.apple.com/bonjour/)-discoverable drive.
- **[Backblaze Computer Backup](https://www.backblaze.com/cloud-backup.html)**
  is Backblaze's managed consumer product: a flat monthly fee per
  computer, unlimited storage, native macOS client. It's the
  no-fuss option for someone who doesn't want to learn restic at all.
  Trade-offs: it only backs up user files (no full-system snapshots), it
  requires their daemon running on a supported OS, and the flat fee tilts
  unfavorably for small data sets. I was also wary of the client itself: there
  are regular bug reports around the macOS app. For my use case, metered B2
  storage ends up cheaper, and I wanted something more flexible.

### resticprofile

**[resticprofile](https://creativeprojects.github.io/resticprofile/)**
wraps restic in a TOML configuration model and a scheduler. Instead of
typing the same long restic invocation every night, we declare
`[profiles.default.backup]` once in a configuration file, with all the flags,
and call `resticprofile -n default backup`.

For the nightly automation, resticprofile doesn't run a daemon of its own; it
delegates to the OS's scheduler. Once a profile has a `schedule` directive,
running `resticprofile schedule` generates the appropriate scheduler
configuration (a launchd plist on macOS) and registers it with the OS. From then
on, the OS scheduler is what wakes the machine up (or catches the next wake,
more on this later) at the configured time and runs `resticprofile
run-schedule <command>@<profile>`, which in turn runs `restic <command>` with
the flags from the profile.

After each scheduled run completes, resticprofile inspects the exit code
and invokes the matching `run-after` (success) or `run-after-fail`
(failure) hook. The notification piece we wire up later hangs off those
hooks.

The alternative is a hand-rolled wrapper plus cron, which works fine and is a
few dozen lines. The trade-off is that we eventually rebuild most of
resticprofile's features (logging, hooks, multi-profile config) badly. For a
single profile and a single schedule, the DIY approach is defensible. Once we
want forget + prune + check (more on these later) on their own schedules with
notification hooks per command, resticprofile is most likely the right path.

### Backblaze B2

**[Backblaze B2](https://www.backblaze.com/cloud-storage)** is the
destination bucket. Restic has first-class B2 support: a URL of the form
`b2:bucket:/prefix` and two environment variables (`B2_ACCOUNT_ID`,
`B2_ACCOUNT_KEY`) are all the configuration there is.

I picked B2 over AWS S3 because it's cheaper for backup workloads at this
scale, and because the onboarding is simpler. Cloudflare R2, Wasabi, and
other S3-compatible backends are also valid as restic supports the S3 API
out of the box.

Self-hosting [rest-server](https://github.com/restic/rest-server) is the
zero-third-party option, given a spare box somewhere with redundant disks.
It removes the cloud dependency and adds the operational one: someone (you 🫵🏻)
has to own the disks and the uptime.

## A backup we run by hand

Goal of this section: end with a working command we can type to back up
`$HOME` to B2, encrypted, with a sensible exclude list. No scheduling yet!

### Install

```bash
brew install restic resticprofile
```

Both ship as static binaries, so no dependencies to chase.

### Create a B2 bucket and an application key

In Backblaze's web UI: create a private bucket, then create an application key
scoped to that bucket. Backblaze returns an `applicationKeyId` and an
`applicationKey`. Save them now, as the web UI never shows the key string again.

### Generate a passphrase and store secrets in Keychain

The repository passphrase encrypts everything in the bucket and there's no
recovery path: if it's lost, the backup is unrecoverable. I generated something
long enough and put a copy in my password manager.

We now have three secrets to keep around: this passphrase, the B2 application
key ID, and the B2 application key. Putting them in plaintext on disk (a
`.env`, a config file...) somewhat defeats the point of encrypting the backup
in the first place. macOS's built-in Keychain is the right home for them.

Keychain is the system-wide encrypted secrets store that macOS already
uses for Wi-Fi passwords, Safari logins, certificates, SSH keys, and
similar. The *login* keychain (the one we want here) unlocks
automatically at user login and stays unlocked while the session is
active. Entries are encrypted on disk and per-entry ACLs control which
processes can read them. There's a GUI app (Keychain Access) for browsing, but
everything we need is available from the built-in `security` command.

Add the three entries:

```bash
security add-generic-password -a "$USER" -s restic-repo-password -w
security add-generic-password -a "$USER" -s restic-b2-key-id     -w
security add-generic-password -a "$USER" -s restic-b2-app-key    -w
```

`-a "$USER"` sets the account name (used for searching). `-s <name>` is
the service name, which is what we'll look up by. `-w` without a value tells
`security` to prompt for the secret interactively, so it never lands in shell
history (it won't appear on-screen when typed either).

Read one back to confirm:

```
$ security find-generic-password -a "$USER" -s restic-repo-password -w
your-passphrase-here
```

If a mistake slips in (typo, wrong service name), delete the entry and
re-add it:

```bash
security delete-generic-password -a "$USER" -s restic-repo-password
```

The first time we do this, macOS may show a Keychain access prompt for
the entry. Click **Always Allow** so subsequent reads go through without
further prompting. For interactive use from the terminal, clicking **Allow**
each time would also work, since there's someone in front of the screen to
dismiss the prompt. For the nightly schedule we set up later, **Always Allow**
is mandatory: when the scheduled job runs while the laptop is unattended, there is
no one to answer the prompt, and the read fails. The backup ends up blocked on
a permission dialog.

From now on, no secret needs to be typed or pasted anywhere. The next
section initializes the repository by reading the three values straight
out of Keychain, and the automation we build later wires the same lookup
into the scheduled job.

### Initialize the restic repository

For a B2 setup, restic reads three environment variables: the passphrase
(`RESTIC_PASSWORD`), the B2 key ID (`B2_ACCOUNT_ID`), and the B2 key string
(`B2_ACCOUNT_KEY`). Pull them from Keychain into the current shell, then run the
init:

```bash
export RESTIC_PASSWORD=$(security find-generic-password -a "$USER" -s restic-repo-password -w)
export B2_ACCOUNT_ID=$(security find-generic-password -a "$USER" -s restic-b2-key-id     -w)
export B2_ACCOUNT_KEY=$(security find-generic-password -a "$USER" -s restic-b2-app-key   -w)
restic init --repo "b2:your-bucket:/your-prefix"
```

This creates the repository structure (a few `keys/` entries and a
`config` file) inside the bucket. From now on every restic command needs
those three variables in the environment, and we can always rerun the
three `export` lines to populate them.

### Write a minimal `profiles.toml`

I keep mine at `~/Documents/backups/config/profiles.toml`:

```toml
version = "2"

[global]
default-command = "snapshots"
initialize = false

[profiles.default]
repository = "b2:your-bucket:/your-prefix"

  [profiles.default.backup]
  source = ["/Users/your-username"]
  exclude-file = "/Users/your-username/Documents/backups/config/excludes.txt"
  exclude-caches = true
  one-file-system = true
  tag = ["scheduled"]

  [profiles.default.forget]
  keep-daily = 30
  keep-monthly = 9999
  prune = false

  [profiles.default.prune]

  [profiles.default.check]
  read-data-subset = "5%"
```

A few comments on this file below...

Retention: 30 daily snapshots, then one per calendar month kept indefinitely.
Restic doesn't accept `inf` or `all` here, so 9999 months (about 833 years) is
the conventional way to express "forever".

`one-file-system` keeps the backup from following mounts into `/Volumes`.

`exclude-caches` honors the [`CACHEDIR.TAG`
standard](https://bford.info/cachedir/): any directory containing a
`CACHEDIR.TAG` file (a small text file with a specific magic signature) is
treated as a cache and skipped. Cargo, various build tools, and other utilities
drop this file in their cache directories automatically, so those get excluded
without having to enumerate each one.

Finally, the `exclude-file` directive points at a file we haven't written yet
so that's next!

### Write `excludes.txt`

A starter list:

```
# Build artifacts
**/node_modules
**/.cache
**/.venv
**/__pycache__

# macOS system files restic can't read even with Full Disk Access
**/Library/Application Support/FileProvider
**/Library/Group Containers/group.com.apple.secure-control-center-preferences
**/Library/Group Containers/group.com.apple.CoreSpeech
**/Library/Daemon Containers/*/Data/com.apple.milod
**/Library/Biome
**/Library/DuetExpertCenter

# Big sparse files that explode logical size
**/Library/Group Containers/HUAQ24HBR6.dev.orbstack
**/Library/Containers/com.docker.docker
```

**Full Disk Access** (FDA, from here on) is the macOS permission that lets a
process read protected user data. It's granted per-binary and we'll actually
set it up a bit later. But even with FDA, certain system-owned files remain
unreadable to any user process (SQLite write-ahead logs held by daemons,
entitled-only event streams, ML stores), which is why those paths get excluded
outright. I'm discovering new locations from time to time and adding them to
this list, although it has been stable for a few weeks now.

<aside class="note" data-type="NOTE">

The first run of this backup, before [OrbStack](https://orbstack.dev/) was excluded,
produced this notification the next morning: `processed 43147 files,
8.015 TiB in 25:03, 554.388 MiB stored`. The numbers can't both be right
on a 1 TB drive. I went hunting and found a single file:
`/Users/lucas/Library/Group Containers/HUAQ24HBR6.dev.orbstack/data/data.img.raw`,
an 8-TiB-capable sparse raw image with about 700 MiB physically allocated.
The remaining terabytes are unwritten zero blocks that APFS doesn't back
with real storage. Restic walks the file at logical size, then content-defined
chunking deduplicates the multi-terabyte run of zeros down to almost nothing.
Yet, it's best to exclude this file to avoid any confusion!

</aside>

### Run a backup

```bash
resticprofile -n default --config ~/Documents/backups/config/profiles.toml backup
```

First run uploads the whole home directory (minus excludes) so plan for it:
depending on data size and internet speed, anywhere from a few minutes to
several hours. Subsequent runs upload only the diff and finish in minutes, if
not seconds.

### Verify

```bash
resticprofile -n default --config ~/Documents/backups/config/profiles.toml snapshots
```

Should list one snapshot tagged `scheduled`.

### Restore a file

```bash
resticprofile -n default --config ~/Documents/backups/config/profiles.toml \
    restore latest --target /tmp/restore --include ~/some/path
```

This dumps the matching path into `/tmp/restore`. It's worth exploring this now
and making sure the restoration flow works before any incident occurs.

### Prune cycle

```bash
resticprofile -n default --config ~/Documents/backups/config/profiles.toml forget
resticprofile -n default --config ~/Documents/backups/config/profiles.toml prune
```

`forget` applies the retention policy and marks snapshots as deleted. `prune`
reclaims the actual storage. Considering the amount of data we are managing,
this is cheap enough and we can afford to run it regularly.

We have a working baseline with manual backups. Now let's automate!

## Make it run every night

We have at least two options on macOS: cron or launchd. cron most likely works
fine (I haven't tested it) but it's less _integrated_ with macOS (cron jobs
don't appear in the macOS's Login Items UI, for example). launchd seems like
it's the right tool for this, but it's also where the platform-specific
complexity lives. Resticprofile knows how to generate launchd plists; the rest
of this section is the long list of things we'll have to fix on top of what it
generates.

### What `resticprofile schedule` gives us

Add a `schedule` directive to each command in `profiles.toml`:

```toml
  [profiles.default.backup]
  # ... existing config ...
  schedule = "*-*-* 02:30:00"
  schedule-permission = "user"
  schedule-lock-mode = "default"
  schedule-log = "/Users/your-username/Documents/backups/logs/backup.log"
  schedule-capture-environment = false

  [profiles.default.forget]
  schedule = "*-*-* 03:00:00"
  # ...

  [profiles.default.prune]
  schedule = "Sun *-*-* 04:00:00"
  # ...

  [profiles.default.check]
  schedule = "Sun *-*-* 05:00:00"
  # ...
```

The schedule strings are [systemd-calendar format](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html#Calendar%20Events).
Backup runs at 02:30 daily, forget at 03:00 daily, prune and check on
Sundays. Install with:

```bash
resticprofile --config ~/Documents/backups/config/profiles.toml schedule --all
```

This generates four launchd plists, one per scheduled command (backup,
forget, prune, check), and drops them into `~/Library/LaunchAgents/`,
the per-user directory where launchd looks for job definitions. It then
registers each one with the running launchd instance via `launchctl
bootstrap`, so the jobs become active immediately (no logout / login
or reboot required). A plist here is just an Apple property-list XML file
describing when to run the job, what binary to execute, and the runtime
environment. We'll dissect one in a moment. On any non-macOS UNIX (where
resticprofile generates systemd units instead) we're basically done at
this point. On macOS, various things still need fixing.

<aside class="note" data-type="NOTE">

`schedule-capture-environment = false` is the line that keeps secrets
off disk. Without it, `resticprofile schedule` copies every exported
environment variable from the calling shell into the generated plist's
`EnvironmentVariables` dictionary, on the assumption that the
launchd-spawned process will need them at run time. With
`RESTIC_PASSWORD`, `B2_ACCOUNT_ID`, and `B2_ACCOUNT_KEY` exported from
the earlier `restic init` step, that would put the secrets on disk in
plaintext inside `~/Library/LaunchAgents/<label>.plist`, defeating the
point of putting them in Keychain. Setting the directive to `false`
tells resticprofile to capture nothing at all.

</aside>

With the secrets kept out of the plist, the next question is how the
scheduled job picks them up at runtime. Restic and resticprofile still
need `RESTIC_PASSWORD`, `B2_ACCOUNT_ID`, and `B2_ACCOUNT_KEY` set in the
environment when they actually run; we've just made sure those values
aren't sitting in the plist on disk. Something has to fetch them from
Keychain at exec time and put them in the environment, fresh, every time
the job fires. resticprofile doesn't do this itself, so we wrap it in a
small script that does.

### A wrapper script that bridges Keychain to environment

The [wrapper](https://github.com/lucas-santoni/macos-backup-restic-b2/blob/main/bin/restic-wrap.sh.tmpl)
reads the three Keychain entries we stored earlier
(`restic-repo-password`, `restic-b2-key-id`, `restic-b2-app-key`),
exports them as the environment variables restic expects, then execs
resticprofile with whatever arguments it was called with. Both
interactive use (`restic-wrap.sh -n default snapshots`) and the
scheduled launchd plists call this same script, so there's exactly one
place where the Keychain reads live.

```zsh
#!/bin/zsh
set -e

export PATH="/opt/homebrew/bin:$PATH"

fetch_secret() {
  local var_name="$1" service="$2" out
  out="$(security find-generic-password -a "$USER" -s "$service" -w 2>&1)"
  if [[ $? -ne 0 || -z "$out" ]]; then
    echo "restic-wrap: keychain read failed for $service: $out" >&2
    exit 11
  fi
  export "$var_name=$out"
}

fetch_secret RESTIC_PASSWORD restic-repo-password
fetch_secret B2_ACCOUNT_ID   restic-b2-key-id
fetch_secret B2_ACCOUNT_KEY  restic-b2-app-key
export RESTIC_CACHE_DIR="$HOME/Documents/backups/cache"

if [[ "$*" != *"--config"* ]]; then
  set -- --config "$HOME/Documents/backups/config/profiles.toml" "$@"
fi

if [[ "$*" != *"--log"* ]]; then
  for arg in "$@"; do
    case "$arg" in
      run-schedule)
        break ;;
      backup|forget|prune|check)
        set -- --log "$HOME/Documents/backups/logs/$arg.log" "$@"
        break ;;
      *.backup|*.forget|*.prune|*.check)
        set -- --log "$HOME/Documents/backups/logs/${arg##*.}.log" "$@"
        break ;;
    esac
  done
fi

exec /opt/homebrew/bin/resticprofile "$@"
```

Three things worth pointing out...

**`PATH` is rewritten because launchd's default doesn't include
Homebrew.** A launchd-spawned process inherits a minimal `PATH`
(`/usr/bin:/bin:/usr/sbin:/sbin`), with no `/opt/homebrew/bin`.
Resticprofile invokes `restic` by name, so the scheduled job fails with
`cannot find restic` until we prepend Homebrew's bin directory.

**`fetch_secret` exists because of a zsh-specific footgun with `set -e`.**
It does not propagate command-substitution failures. An earlier version of
the wrapper used:

```zsh
export RESTIC_PASSWORD="$(security find-generic-password -a "$USER" -s restic-repo-password -w)"
```

When `security` failed (which it did, for reasons we'll get to), this
exported `RESTIC_PASSWORD=""` and let the script continue. Restic then
attempted to open the repository with an empty password and printed
`Fatal: an empty password is not allowed by default`.

**`--log` and `--config` are injected only when the caller didn't pass
them.** Interactive use shouldn't have to type the absolute config path.  The
launchd plists already pass `--config`, and `run-schedule` already wires the
`schedule-log` directive, so injecting `--log` on the schedule code path would
double up and the notify hook (more on this later) would read the wrong section.

<aside class="note" data-type="NOTE">

The `--log` injection logic above didn't exist in the first
version of the wrapper. The notify script reads from
`~/Documents/backups/logs/backup.log` to pull the snapshot ID and metrics
into the message body. With no `--log` flag on direct invocations, that
log file only got written when launchd fired the schedule. The day I ran a
manual backup to verify a fix, the notification arrived seconds later, but
its payload was the *previous* scheduled run's snapshot ID, because the
file hadn't been updated since. The fix is the conditional `--log`
injection: set it for direct commands (`backup`, `forget`, `prune`,
`check`), skip for `run-schedule` (which already has it), leave read-only
commands like `snapshots` alone so they keep printing to the terminal.

</aside>

### Patching the plists launchd will run

launchd reads a `.plist` file at `~/Library/LaunchAgents/<label>.plist`
for each agent it manages, describing when to fire the job and what to
exec. resticprofile generates one per scheduled command, but the default
needs a few tweaks before it's usable for our setup. Here's what
resticprofile gives us:

```
$ plutil -p ~/Library/LaunchAgents/local.resticprofile.default.backup.plist
{
  "EnvironmentVariables" => { ... }       # empty (schedule-capture-environment = false)
  "Label"                => "local.resticprofile.default.backup"
  "LimitLoadToSessionType" => "Background"
  "Program"              => "/opt/homebrew/bin/resticprofile"
  "ProgramArguments"     => [
    "/opt/homebrew/bin/resticprofile", "--no-prio", "--no-ansi",
    "--config", "/Users/lucas/Documents/backups/config/profiles.toml",
    "run-schedule", "backup@default"
  ]
  "StartCalendarInterval" => [ { "Hour" => 2, "Minute" => 30 } ]
}
```

And a small [Python patcher](https://github.com/lucas-santoni/macos-backup-restic-b2/blob/main/bin/schedule-install.sh.tmpl)
that rewrites it in place:

```python
import plistlib, sys

path = sys.argv[1]
launcher = sys.argv[2]
wrapper = sys.argv[3]

with open(path, "rb") as f:
    p = plistlib.load(f)

p["Program"] = launcher
p["ProgramArguments"][0] = launcher
p["ProgramArguments"].insert(1, wrapper)
p.pop("EnvironmentVariables", None)
p.pop("LimitLoadToSessionType", None)
p["StandardErrorPath"] = "/Users/.../logs/launchd-backup.err.log"
p["StandardOutPath"]   = "/Users/.../logs/launchd-backup.out.log"

with open(path, "wb") as f:
    plistlib.dump(p, f)
```

Invoke once per agent, passing the launchd plist, the launcher binary
inside the bundle (which doesn't exist yet, we'll build it in the next
sub-section), and the wrapper script:

```bash
python patch.py \
  "$HOME/Library/LaunchAgents/local.resticprofile.default.backup.plist" \
  "$HOME/Documents/backups/bundles/Hercules Backup.app/Contents/MacOS/Hercules Backup" \
  "$HOME/Documents/backups/bin/restic-wrap.sh"
```

One line in the patcher deserves a callout:
`p.pop("LimitLoadToSessionType", None)`. resticprofile sets that key to
`"Background"` by default, which would load the agent into the
`user/<uid>` launchd domain. That domain has no access to the user's
login Keychain, so the wrapper's `security find-generic-password` calls
would return empty strings. Stripping the key lets us bootstrap each
agent into `gui/<uid>` instead. Once the bundle (next sub-section) is
in place, reload each agent with:

```bash
launchctl bootout "user/$UID/$LABEL" 2>/dev/null || true
launchctl bootout "gui/$UID/$LABEL"  2>/dev/null || true
launchctl bootstrap "gui/$UID" "$PLIST"
```

<aside class="note" data-type="NOTE">

The wrong-domain symptom is silent: `security` exits 0 with empty
stdout, not with an error. The wrapper's `fetch_secret` helper catches
this only because of its `[[ -z "$out" ]]` check, and the trace is only
visible because the patcher sets `StandardErrorPath` on the plist.
Without those two, restic eventually fails with `Account ID
($B2_ACCOUNT_ID) is empty` and the diagnostic trail starts much
further downstream.

</aside>

After patching, the plist references a launcher binary that doesn't exist
yet. We build that next!

### The `.app` bundle, AMFI, and codesigning

This is the most goofy-looking 🤪 part of the setup. A backup script ending up
inside an `.app` bundle, codesigned, feels disproportionate to the task. I
tried to avoid this as much as possible but after a lot of iterations, I
actually don't think there is a way around it.

The rest of this sub-section walks through, in order: the three concrete
issues we hit when we hand the manual setup to launchd,
the macOS security mechanisms behind those issues, the architecture
to address these issues, and finally the build and signing steps.

**The Issues**

1. **launchd can't read the wrapper script from `~/Documents/`.** The
   scheduled run dies with `can't open input file:
   .../restic-wrap.sh`, even though permissions and ownership are correct
   and the same command works fine from a Terminal session.

2. **launchd refuses to run the wrapper as `Program`.** Pointing the
   launchd plist's `Program` at `restic-wrap.sh` kills the process at
   launch with `OS_REASON_CODESIGNING`, before anything in the script
   gets to run.

**Security Mechanisms**

- **TCC** causes (1). TCC mediates access to privacy-sensitive resources,
  including the protected home folders (`~/Documents/`, `~/Desktop/`,
  `~/Downloads/`) and the broader Full Disk Access category (FDA, the one
  we end up using here because it covers everything under `$HOME`). Terminal
  can hold an FDA grant in System Settings, which is the case
  on my machine, hence why manual runs work. launchd has no
  equivalent option: launchd itself isn't TCC-grantable, and a process it
  spawns has no signed code identity for TCC to attach a grant to unless we
  give it one. That gap is exactly what the bundle architecture fills. The
  important property: TCC grants are keyed by *code identity* (an identifier
  plus a cdhash, a cryptographic hash of the signed code pages that
  fingerprints the exact bytes of the binary) rather than path, and the
  identity TCC checks is the *responsible process* at the top of the exec
  chain, not the syscalling process. We need a stable, signed code identity to
  grant FDA to, sitting at the top of the chain.

- **AMFI** causes (2). AMFI is the kernel-level codesigning enforcer.
  It refuses launchd `Program`s pointing at unsigned or user-signed
  shell scripts and kills them with `OS_REASON_CODESIGNING`. Apple-signed
  binaries (and properly signed user binaries) pass. The launchd
  `Program` has to be a signed Mach-O.

**The architecture** which solves all the problems above is a small `.app`
bundle per scheduled command, ad-hoc-codesigned, containing a 20-line
Mach-O launcher whose only job is to exec `/bin/zsh` with the wrapper
script as argument. The bundles live at `~/Documents/backups/bundles/`
alongside the wrappers (`bin/`), configs (`config/`), and logs (`logs/`).
That's just because I like having everything in one place, not a constraint:
launchd's exec of the launcher binary isn't TCC-gated according to my testing.

This architecture works for the following reasons:

- **(1) FDA stability + chain propagation.** The bundle's cdhash is a
  function of its signed contents, and we control when those change.
  `brew upgrade` may update restic, resticprofile or even zsh but it does not
  touch the bundle, so the cdhash holds and the FDA grant we attach to it in
  System Settings survives upgrades. At runtime, TCC walks up the exec chain
  (launcher → zsh → resticprofile → restic) and finds the bundle's launcher as
  the responsible process, so the FDA grant applies to every read in the chain:
  zsh opening the wrapper script, resticprofile reading `profiles.toml` and
  `excludes.txt`, restic walking `$HOME`. One grant on the bundle covers all of
  it.

- **(2) AMFI passes the launcher.** The launchd `Program` is now a real Mach-O
  binary, signed, so AMFI lets it run. The launcher then execs `/bin/zsh` which
  fires the rest. AMFI's check is against the launchd-launched binary only, so
  zsh interpreting the wrapper script afterward is fine.

<aside class="note" data-type="NOTE">

**TCC** stands for Transparency, Consent, and Control. It mediates access to a
broader set of privacy-sensitive resources than just the FDA category we
exercise here: contacts, calendar, photos, camera, location, various
`~/Library` subtrees, the home folders, etc. Any time macOS surfaces an "X
wants access to your Y" prompt, that's TCC. Decisions live in a per-user SQLite
database at `~/Library/Application Support/com.apple.TCC/TCC.db` and a
system-wide one at `/Library/Application Support/com.apple.TCC/`, and are
consulted on each subsequent access. Each record carries a `csreq` field: a
binary blob encoding the requester's [Designated
Requirement](https://developer.apple.com/documentation/security/code_signing_services),
which is what the runtime identity check matches against.

</aside>

<aside class="note" data-type="NOTE">

**AMFI** stands for Apple Mobile File Integrity. The "Mobile" is a
historical artifact: AMFI started on iOS and was ported to macOS. Worth knowing
for this section: AMFI checks the *launch target* only, not what the launched
binary subsequently does.

</aside>

Now that we know what we want, **let's build the bundle**! Layout for the
`backup` agent (the other three are identical except for names):

```
Hercules Backup.app/
└── Contents/
    ├── Info.plist
    └── MacOS/
        └── Hercules Backup
```

The [launcher binary](https://github.com/lucas-santoni/macos-backup-restic-b2/blob/main/bin/launcher.c)
is twenty lines of C:

```c
#include <unistd.h>

int main(int argc, char **argv) {
    (void)argc;
    argv[0] = "/bin/zsh";
    execv("/bin/zsh", argv);
    return 127;
}
```

Compiled for Apple Silicon (swap or add `-arch` flags for other
architectures):

```bash
clang -O2 -arch arm64 -o "Hercules Backup" bin/launcher.c
```

The launcher swaps `argv[0]` for `/bin/zsh` and execs zsh. The plist's
`ProgramArguments` is arranged as `[<launcher>, <wrapper-script>,
--no-prio, --no-ansi, --config, ..., run-schedule, backup@default]`, so
zsh inherits a modified argv that reads as a normal `zsh <wrapper>
<args...>` invocation and runs the wrapper.

Every `.app` bundle carries a metadata file at `Contents/Info.plist`,
and macOS won't recognize the directory as a bundle without one. It's
where the bundle declares its identifier (used by LaunchServices and TCC
to refer to the bundle) and which binary inside `Contents/MacOS/` to
treat as the executable. Ours is minimal:

```xml
<plist version="1.0">
<dict>
  <key>CFBundleIdentifier</key>     <string>com.your-name.hercules.backup</string>
  <key>CFBundleExecutable</key>      <string>Hercules Backup</string>
  <key>CFBundlePackageType</key>     <string>APPL</string>
</dict>
</plist>
```

**Now that we have our bundles ready, let's sign them!** The example
commands below are for the `backup` bundle; `forget`, `prune`, and `check`
get the same treatment with their respective identifiers and paths.

Ad-hoc codesigning gives the bundle a valid Designated Requirement that
TCC can record and match against at runtime. Without signing, the DR is
malformed; TCC writes the grant but every subsequent lookup fails to
match, and the visible symptom is a fresh stack of "X wants to access
files in your Documents folder" prompts every morning even after
clicking Allow the day before.

```bash
codesign --force --deep --sign - \
  --identifier "com.your-name.hercules.backup" \
  "$HOME/Documents/backups/bundles/Hercules Backup.app"
```

`--sign -` is the ad-hoc form (no Apple Developer certificate needed).
`--deep` signs everything inside the bundle, including the inner launcher.
`--identifier` sets the signature's identifier to match the bundle ID. This is
important as clang's default linker signature otherwise uses `launcher` as a
placeholder, which TCC won't match against.

<aside class="note" data-type="NOTE">

**Designated Requirement (DR)** is a code-signing concept: a structured
expression embedded in the signature that defines what counts as "this
same code" at runtime. For an ad-hoc signature like ours, the DR is
generated automatically from the `--identifier` we passed and the
cdhash(es) of the signed code.

This matters because TCC stores its grants keyed by DR. When a process
inside the bundle tries to read a protected resource, TCC evaluates
the stored DR against the running process's identity. Match → the
grant applies. No match, or a malformed DR (which is what an unsigned
bundle produces) → the grant doesn't apply, and the user gets
re-prompted on the next access, even though the row in `TCC.db` shows
`auth_value=2` (granted). The verify output below shows the DR our
`codesign` invocation produced.

</aside>

Verify:

```
$ codesign -d --requirements - "Hercules Backup.app"
Executable=.../Hercules Backup.app/Contents/MacOS/Hercules Backup
designated => cdhash H"d7c6db3a73b30f7b7e40a4d985a9bf9dd824dd6f"
              or cdhash H"f31bc07c..."
```

Two cdhashes joined by `or`: the bundle's structural cdhash and the inner
Mach-O's cdhash. TCC checks both on every read.

At this point each scheduled command has its own signed `.app` bundle,
each launchd plist points at the launcher inside its bundle, and one FDA
grant per bundle in System Settings is enough to unblock the whole exec
chain (launcher → zsh → wrapper → resticprofile → restic) across
`~/Documents/`.

To wire up those FDA grants: open `System Settings → Privacy & Security → Full
Disk Access`, click the `+` button, and add each of the four `.app` bundles
from `~/Documents/backups/bundles/` in turn. macOS asks for Touch ID or the
admin password the first time. The grant is keyed to the bundle's Designated
Requirement, so it survives reboots and `brew upgrade` runs. However,
rebuilding a bundle invalidates it (the cdhash changes) and the bundle has to
be re-added.

### Sleep, DarkWake, and the lock race

macOS doesn't wake a sleeping Mac to fire a user-agent schedule, so the
logical conclusion is:

> If the laptop is asleep at 02:30, the job is silently skipped, and the
> next firing is the next time the laptop is awake past the next scheduled
> time.

At least that's what seemed logical to me and what I thought happened. But
it turns out MBPs actually sleep with one eye open!

en macOS, closing the lid (or letting the screen turn off on battery)
puts the machine into a layered sleep state. It alternates between
deep sleep and short DarkWake intervals every 15-30 minutes. Each DarkWake
lasts a few seconds to half a minute, brings the CPU online, services
background tasks (including launchd schedules!), and goes back to sleep. The
display stays off the entire time. We can see it in `pmset -g log`:

```
$ pmset -g log | grep -E "Sleep|DarkWake" | tail -8
2026-05-14 02:14:33 +0200 Sleep                          : Entering Sleep state Using Batt (Charge:91%)
2026-05-14 02:29:58 +0200 DarkWake from Deep Idle [CDNP] : due to RTC/SleepService Using Batt (Charge:91%) 5 secs
2026-05-14 02:30:03 +0200 Sleep                          : 'Sleep Service Back to Sleep' (917 secs)
2026-05-14 02:45:20 +0200 DarkWake from Deep Idle [CDNP] : due to RTC/SleepService Using Batt (Charge:90%) 8 secs
2026-05-14 02:45:28 +0200 Sleep                          : 'Sleep Service Back to Sleep' (892 secs)
2026-05-14 03:00:20 +0200 DarkWake from Deep Idle [CDNP] : due to RTC/SleepService Using Batt (Charge:90%) 6 secs
2026-05-14 03:00:26 +0200 Sleep                          : 'Sleep Service Back to Sleep' (914 secs)
2026-05-14 03:15:40 +0200 DarkWake from Deep Idle [CDNP] : due to RTC/SleepService Using Batt (Charge:90%) 4 secs
```

This shows about one hour of the laptop "asleep": four DarkWake intervals of a
few seconds each, roughly 15 minutes apart, with deep sleep in between. The
02:30 DarkWake is when the scheduled backup fires.

So at 02:30, lid closed, the backup *does* fire. It just fires during the
next DarkWake, runs for two to twenty seconds, and gets suspended (not
killed) when the laptop goes back to sleep. The next DarkWake resumes it.
Restic accumulates active CPU time across many such slices.

<aside class="note" data-type="NOTE">

The first time I noticed this, the backup's wall-clock
duration was 7h13m and the active duration restic reported was 3:21.
That's not a bug; that's the laptop spending 99% of those seven hours
asleep. 😴

</aside>

The interesting consequence is the lock race. Backup is scheduled at 02:30,
forget at 03:00. On a Mac that's awake at 02:30, backup finishes well under 30
minutes and the schedule is fine. With DarkWake-fragmented execution, backup
might still be running (suspended, mostly) at 03:00. Both restic and
resticprofile use locks but the default behavior is "fail immediately if
locked" which is not ideal in case the laptop is asleep of if a backup takes
longer than usual for whatever reason.

The fix is two directives, as there are two locks:

```toml
[profiles.default.backup]
lock-wait = "4h"     # resticprofile's profile lock
retry-lock = "4h"    # forwarded to restic as --retry-lock=4h
```

`lock-wait` is resticprofile's directive for its own profile lock (prevents
two `resticprofile` invocations from running concurrently). `retry-lock` is
forwarded to `restic backup` itself and covers restic's repository lock,
which is a different lock living inside the B2 bucket. Both have to be
set, on every command that touches the repo, because there is no "the job
that holds" and "the job that waits": on wake, either can hold and either
can wait.

One last related gotcha. The directive `schedule-lock-mode` has three
valid values: `default`, `fail`, `ignore`. `default` is *not* "wait the
default timeout." It is closer to "don't run a second instance if one is
already going" and doesn't poll. The directive that controls polling is
`lock-wait`. Leave `schedule-lock-mode` on `default` and let `lock-wait` do the
actual work.

## Operational polish

This section covers notifications as well as some cosmetics.

### Notifications

The system has been running cleanly for two nights when I realize I have no
idea whether it has run at all. The log directory is the only signal, and
I don't really want to check logs every morning. 😬

I run a small JSON-receiver gateway on a hosted box. The
[`restic-notify.sh`](https://github.com/lucas-santoni/macos-backup-restic-b2/blob/main/bin/restic-notify.sh.tmpl)
script POSTs to it with a Bearer token (also stored in Keychain, this thing is
super convenient!) and the gateway pushes to Telegram. Any HTTP-accepting
notifier works: [ntfy.sh](https://ntfy.sh) is the easiest drop-in, Slack
webhooks work, Pushover works, an email-by-HTTP service works.

Resticprofile allows us to run something after the success or the failure of
any command:

```toml
[profiles.default.backup]
run-after      = ["/Users/your-username/Documents/backups/bin/restic-notify.sh success"]
run-after-fail = ["/Users/your-username/Documents/backups/bin/restic-notify.sh failure"]
```

Two things worth noting:

**`run-after` only fires on success while `run-after-fail` only on failure.**
One might be tempted to chain a `check` in `run-after` as a post-backup
verification. But if `check` then fails, the notification doesn't fire and we
lose visibility. Notifications should be the *last* thing in any chain, never
dependent on a fragile predecessor. It's best to run `check` on its own
schedule.

**Exit code 3 from `restic backup` is not a failure.** Restic distinguishes
three exit codes:

- `0`: success
- `1`: generic failure (can't open repo, network down, credentials wrong)
- `3`: "snapshot was saved, but some source files couldn't be read"

The third shows up regularly on macOS, because there are system files that even
FDA-granted processes cannot read, as we discussed before.

Resticprofile treats exit 3 as a non-zero exit and fires `run-after-fail`,
so the notify script needs to recognize this case and render it as a
warning rather than a failure. Something like:

```python
if outcome == "failure" and command == "backup" and err_exit == "3":
    level = "warning"
    title = f"Restic {command} completed with warnings"
```

<aside class="note" data-type="NOTE">

Exit code 3 is also where I find out about new unreadable locations. Each
warning notification names specific paths in the log so I add them to
`excludes.txt`.

</aside>

### Login Items row names

By default, the `System Settings → General → Login Items & Extensions` pane
labels each launchd agent row with the basename of the plist's `Program`. With
four agents all pointing at the same launcher path, that pane shows four
identical rows with no way to tell backup from forget from prune from check.
The toggle next to each row becomes useless: turning one off is basically a
coin flip on which scheduled command stops running.

Two small additions on top of what we built above fix this. First, add
`CFBundleName` to each bundle's `Contents/Info.plist`:

```xml
<key>CFBundleName</key>  <string>Hercules Backup</string>
```

Second, append one line to the plist patcher from earlier, so that
each agent's `~/Library/LaunchAgents/<label>.plist` carries an
`AssociatedBundleIdentifiers` pointing at the matching bundle:

```python
p["AssociatedBundleIdentifiers"] = ["com.your-name.hercules.backup"]
```

macOS resolves the `AssociatedBundleIdentifiers` to the bundle, reads
the bundle's `CFBundleName`, and renders that as the row label. Four
distinctly-named bundles, four named rows, four working toggles.

### Custom icons

I wanted to setup custom icons in place of the generic "exec" macOS icon for
our .app bundles. These icons are visible multiple places: in Finder when
browsing the folder containing the bundles, in the "Open at Login" Settings
window, in the TCC grants window, etc.

In the end I got something which works everywhere, **except for the Open at
Login window**. I don't know why but I never managed to override this icon. I
even ended up reversing a _commercial_ .app bundle which manages to display a
custom icon in this window (Tailscale) and the only difference I can see is
that the commercial binary has been signed using a paid certificate you get by
subscribing to Apple Developer. I'm not ready to pay just to customise icons
(I'm not even sure that's the root cause) so I just gave up.

Anyways, here is how to customise the icon of an .app bundle programatically,
starting from an emoji...

In order to avoid designing (or stealing) something, I decided to start from an
emoji and render 💾 into a 1024x1024 PNG, then assemble an `.icns` from it.
Here is [`emoji-to-icns.sh`](https://github.com/lucas-santoni/macos-backup-restic-b2/blob/main/bin/emoji-to-icns.sh),
a zsh wrapper that embeds a small Swift program and leverages various
built-in CLI tools to produce the final `.icns`:

```bash
#!/bin/zsh
# emoji-to-icns.sh <emoji> <output.icns>
set -euo pipefail
emoji="$1"; out="$2"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/render.swift" <<'SWIFT'
import AppKit
let emoji = CommandLine.arguments[1]
let outPath = CommandLine.arguments[2]
let size: CGFloat = 1024
let image = NSImage(size: NSSize(width: size, height: size))
image.lockFocus()
let font = NSFont(name: "Apple Color Emoji", size: size * 0.8)!
let attrs: [NSAttributedString.Key: Any] = [.font: font]
let s = emoji as NSString
let bbox = s.size(withAttributes: attrs)
s.draw(at: NSPoint(x: (size - bbox.width) / 2,
                   y: (size - bbox.height) / 2),
       withAttributes: attrs)
image.unlockFocus()
let tiff = image.tiffRepresentation!
let rep  = NSBitmapImageRep(data: tiff)!
let data = rep.representation(using: .png, properties: [:])!
try data.write(to: URL(fileURLWithPath: outPath))
SWIFT

swift "$tmp/render.swift" "$emoji" "$tmp/icon_1024.png"

set_dir="$tmp/icon.iconset"
mkdir "$set_dir"
for s in 16 32 128 256 512; do
  sips -z $s        $s        "$tmp/icon_1024.png" --out "$set_dir/icon_${s}x${s}.png"
  sips -z $((s*2))  $((s*2))  "$tmp/icon_1024.png" --out "$set_dir/icon_${s}x${s}@2x.png"
done
cp "$tmp/icon_1024.png" "$set_dir/icon_512x512@2x.png"
iconutil -c icns "$set_dir" -o "$out"
```

Run it with the emoji and the destination path:

```bash
./emoji-to-icns.sh 💾 icon.icns
```

Drop `icon.icns` into the bundle's `Contents/Resources/` and reference it
from `Info.plist`:

```xml
<key>CFBundleIconFile</key>  <string>icon.icns</string>
```

## The repo

Everything in this post is published at
[github.com/lucas-santoni/macos-backup-restic-b2](https://github.com/lucas-santoni/macos-backup-restic-b2).
On my Mac it lives at `~/Documents/backups/`, but the path doesn't matter.
The repo only commits the templates and the per-machine example:

```
macos-backup-restic-b2/
├── README.md
├── site.conf.example            # per-machine values, copy → site.conf
├── bin/
│   ├── configure.sh             # renders bin/*.tmpl + config/*.tmpl
│   ├── install-bundles.sh.tmpl  # builds + signs the four .app bundles
│   ├── schedule-install.sh.tmpl # idempotent launchd installer/patcher
│   ├── restic-wrap.sh.tmpl      # Keychain → env → resticprofile
│   ├── restic-notify.sh.tmpl    # posts notification JSON via gateway
│   ├── launcher.c               # tiny Mach-O launcher stub
│   ├── emoji-to-icns.sh         # renders 💾 to icon.icns
│   └── test-notify.sh           # fixture-driven smoke test for notify
└── config/
    ├── profiles.toml.tmpl       # resticprofile schedules, retention, hooks
    └── excludes.txt             # backup exclusions
```

Everything else is generated locally and gitignored: `site.conf` itself,
the rendered `.sh` and `.toml` files next to their templates, the four
`.app` bundles built into `bundles/`, plus `logs/` and `cache/`. This
matters because `site.conf` contains values you don't want on GitHub
(B2 bucket URL, bundle ID prefix, notification endpoint) and the rendered
scripts inline those values verbatim.

`site.conf` itself holds the five values that vary per machine (username,
B2 bucket URL, bundle ID prefix, bundle display-name prefix, notification
endpoint). `bin/configure.sh` renders the `.tmpl` files against those
values, producing the runnable scripts and configs.

To adapt: clone, copy `site.conf.example` to `site.conf`, edit, run
`bin/configure.sh`, then the two install scripts in order
(`install-bundles.sh`, `schedule-install.sh`).
