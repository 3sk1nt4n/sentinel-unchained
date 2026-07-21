# 🚀 Start here: your first Unchained case

<p align="center">
  <img src="https://img.shields.io/badge/tests-378%2F378%20passing-22c55e" alt="Tests: 378/378 passing">
  <img src="https://img.shields.io/badge/ruff-clean-22c55e" alt="Ruff: clean">
  <img src="https://img.shields.io/badge/Windows-flagship%20lane-0078D6?logo=windows&logoColor=white" alt="Windows flagship lane">
  <img src="https://img.shields.io/badge/Linux-hardened%20container-1793D1?logo=linux&logoColor=white" alt="Linux hardened container">
  <img src="https://img.shields.io/badge/macOS-via%20Docker-000000?logo=apple&logoColor=white" alt="macOS via Docker">
</p>

<p align="center">
  <a href="../README.md">🏠 Overview</a> ·
  <a href="../README.md#for-judges--the-submission-at-a-glance">🏆 For judges</a> ·
  <a href="../README.md#quickstart">⏱️ Quickstart</a> ·
  <a href="ARCHITECTURE.md">🧠 Architecture</a> ·
  <a href="../README.md#proof-status">🧾 Proof status</a> ·
  <a href="../JUDGE-QUICKSTART.md">⚖️ Judge guide</a>
</p>

New to this? You're in the right place. It's really just **two commands**:
install once, then run one word that walks you through everything else.

> [!TIP]
> **Instant win - free, no key, no evidence.** Right after install, from the
> repo root, verify the shipped **COMPLETE** GPT-5.6 Sol investigation:
>
> ```powershell
> sentinel verify examples/public-run-complete --require-complete --require-live-gpt56
> ```
>
> Expected: **VALID** - 37 artifacts, 194 audit entries, from a real Sol run
> (31/31 typed Volatility tools, 20 adaptive turns, 4 findings), checked
> offline on your machine. `sentinel view` on the same path opens the viewer.

> [!NOTE]
> **You can't break anything.** Everything is local and free until the very
> last step, and even then nothing spends money until you pick a package on
> the launch card AND pass the final key step. If a step ever errors, nothing
> bad happened - read the message and try again.

## ✨ The whole thing in two commands

```powershell
# 0) get the project and step into it
git clone https://github.com/3sk1nt4n/Unchained.git; cd Unchained

# 1) install + verify everything (one command)
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1

# 2) start a whole case (one word - it walks you through the rest)
sentinel
```

That second command does **all** of this in order, one simple question at a time:

1. shows a full-color welcome and asks **one question** - where the evidence is;
2. profiles and SHA-256-hashes the case **locally** and prints a verified
   **case card** (no key, no OpenAI, `$0`);
3. stops at **one launch card** with three complete packages:
   `1 = quick Terra test / 2 = full Terra run / 3 = qualifying Sol / Q = quit`;
4. then the **one hidden key step** before the pipeline starts - Enter uses
   the saved key, or paste a new one at a hidden prompt (never echoed);
5. runs the investigation live and verifies the sealed proof bundle.

No flags, no environment variables. Prefer typing a launcher? `.\unchained.ps1`
does exactly the same thing.

---

## 🔐 Step 0 - Keep your OpenAI key safe (once, before the run)

You'll need an OpenAI key for the paid run - never paste it into a chat,
screenshot, or shared terminal.

1. Open <https://platform.openai.com/api-keys>.
2. **Revoke** any key that has ever appeared somewhere public.
3. **Create new secret key** and keep it in a private note for a moment.

> [!IMPORTANT]
> New OpenAI accounts have a low rate limit (~200,000 tokens/minute); a full
> investigation needs more in one burst. Add a little credit and complete
> verification under **Settings → Billing** to raise the limit before the real
> run - this is the single most common reason a run stops early.

---

## 🧰 Step 1 - Install (one command)

Open **PowerShell** (Start → type "PowerShell" → Enter). Either paste the
one-liner:

```powershell
irm https://raw.githubusercontent.com/3sk1nt4n/Unchained/main/get.ps1 | iex
```

…or clone and run the installer directly - **same steps, same result**:

```powershell
git clone https://github.com/3sk1nt4n/Unchained.git
Set-Location .\Unchained
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

`setup.ps1` checks everything and installs what's missing: a private, pinned
Python 3.11 toolchain, all dependencies, the one-word `sentinel` command, plus a
Docker availability check (optional on Windows). **It reads no evidence and
calls OpenAI zero times.** Re-running is safe.

- Re-verify anytime without reinstalling: `.\setup.ps1 -Check`
- Missing Git or Python? Install these, reopen PowerShell, and run it again:
  - Git for Windows: <https://git-scm.com/download/win>
  - CPython **3.11.9 AMD64**: <https://www.python.org/downloads/release/python-3119/>
    (tick **"Add python.exe to PATH"**)

---

## 🕹️ Step 2 - Run one word (it walks you through the rest)

```powershell
sentinel
```

That's the whole experience. One question - **where is the case?** - two easy answers:

- 🧪 **No evidence yet?** Type **`D`** at the case prompt - Unchained guides
  the **public DC01 practice case**: it opens the two direct download links
  (`DC01-memory.zip` + `DC01-E01.zip` from <https://dfirmadness.com/case001/>),
  verifies the publisher MD5s, and prepares the case folder. (Same as `get.ps1`
  menu option 1.)
- 📁 **Your own case?** Paste the path to ONE folder holding ONE host's
  evidence:

  ```text
  C:\Evidence\CASE-A\
  ├─ host-memory.raw    ← one memory image (.raw / .mem / .vmem / .dmp)
  └─ host-disk.E01      ← one disk image (.E01 / .dd / raw)
  ```

Then read the verified case card, pick from the one launch card
(`1 = quick Terra test / 2 = full Terra run / 3 = qualifying Sol / Q = quit`),
and pass the hidden key step (Enter = saved key, or a hidden shape-checked
paste). Nothing spends money until both.

Then **watch it live**: opening tools with timings, the model's reasoning each
turn, findings, the reviewer keeping or downgrading them, and a sealed, verified
bundle. The run prints the exact `verify` and `view` commands when it finishes.

> [!WARNING]
> **One folder = one case** - at most one ready memory image and one ready disk
> image; two of the same kind fail closed - split into separate folders.
> **`.zip` archives are welcome**: the guided flow offers to extract into a
> clean sibling folder and re-profiles automatically; other archive types are
> flagged EXTRACT FIRST - unpack manually. Original evidence bytes stay local;
> OpenAI only receives the bounded public profile and bounded typed-tool outputs.

Each package pairs a model with a set of **hard stop ceilings** - ceilings
are budget stops, never a quality promise:

| Package | Model | Hard ceilings (not a price quote) |
|---|---|---|
| **1 QUICK TEST** - fastest live check | gpt-5.6-terra | 20 tools · 100,000 tokens · 10 min · $2.50 max |
| **2 FULL RUN** - recommended first | gpt-5.6-terra | 60 tools · 400,000 tokens · 30 min · $10 max |
| **3 QUALIFYING** - the official seal | GPT-5.6 Sol | 60 tools · 400,000 tokens · 30 min · $10 max |

Package 1 hits its ceiling early on big cases (honest `PARTIAL`, few findings);
package 2 runs all 13 steps - findings, judge, report - at cheap Terra pricing;
only package 3 produces the Sol bundle that passes `--require-live-gpt56`.

---

## 🧾 Step 3 - Verify and view the proof (free, no key)

The run prints the exact **bundle folder path** at the end. Use it:

```powershell
sentinel verify "C:\path\to\bundle"
sentinel view   "C:\path\to\bundle"
```

- `verify` should say **VALID** - an independent, offline checker rebuilt the
  report and confirmed nothing was tampered with.
- `view` opens a self-contained **proof viewer** in your browser (findings,
  citations, custody, receipts) - no server, no JavaScript, no internet.

For the qualifying Sol bundle, verify strictly:

```powershell
sentinel verify "C:\path\to\bundle" --require-complete --require-live-gpt56
```

🎉 **VALID with those flags is submission-grade proof.**

> [!NOTE]
> The authentic **COMPLETE** Sol bundle ships at `examples/public-run-complete`
> and passes both flags (see the README → Proof status): 4 findings -
> 1 CONFIRMED / 2 NEEDS-REVIEW / 1 UNSUPPORTED. Those same flags correctly
> **fail** the shipped honest-`PARTIAL` fixture (`examples/public-run-partial`,
> 14/14 tools, stopped at `MAX_TOOL_CALLS`; plain `verify` says VALID -
> 20 artifacts, 62 audit entries). That is the verifier refusing to overstate.

> [!IMPORTANT]
> Verification proves the lifecycle, custody, citations, report, and viewer are
> internally consistent. It does **not** prove a model's forensic interpretation
> is true, and it does not authenticate OpenAI. A human analyst owns the final
> judgment.

---

## 🐧 Linux and macOS (same one-command experience)

> [!TIP]
> **Do I need Docker? Only if you want it.**
> - 🪟 **Windows - no Docker at all.** The flagship lane is native PowerShell + CPython 3.11.
> - 🐧 **Linux - your choice.** Native `./setup.sh` (needs Python 3.11; on stock Ubuntu 24.04 add the deadsnakes PPA first: `sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.11 python3.11-venv`) **or** the hardened Docker container via `get.sh`. **Both lanes were executed end to end and verified live on 2026-07-21.**
> - 🍎 **macOS - use the Docker Desktop lane** (the same hardened `linux/amd64` container). Native macOS is not verified on Mac hardware.

On **Linux** the exact same flow runs natively with the Bash mirrors of the two
scripts. On **macOS** the supported route is the hardened Docker lane
(`linux/amd64` emulation); it is not yet verified on Mac hardware.

```bash
git clone https://github.com/3sk1nt4n/Unchained.git && cd Unchained
./setup.sh        # install + verify everything (one command)
./unchained.sh    # start a whole case (walks you through the rest)
```

Prefer full isolation, or nothing installed? The hardened, network-less
container profiles a committed synthetic fixture with **no key, no evidence**:

```bash
docker compose build
docker compose run --rm offline                 # guided welcome, offline
docker compose run --rm offline profile /evidence --json
```

It proves classification and custody with zero OpenAI calls, and honestly says a
real forensic route isn't ready for that toy fixture.

---

## 💸 Advanced: rehearse cheap before the real run

Validate the whole pipeline for a few cents before spending on the flagship:
opt into a clearly-labeled, **nonqualifying** rehearsal with two variables:

```powershell
$env:UNCHAINED_ALLOW_TEST_MODEL = "1"
$env:UNCHAINED_MODEL = "gpt-5.6-terra"
sentinel
```

The banner will warn **"TEST MODEL MODE"** - that's correct. A rehearsal can
never masquerade as the official Sol result and cannot pass
`--require-live-gpt56`. Open a **fresh PowerShell** for the real run; without
those variables, `sentinel` defaults to real GPT-5.6 Sol automatically.

---

## 🚦 When a run stops early

A run can end `PARTIAL` - that's honest, not a failure of you. Read
`summary.json` and the last audit lines. Common causes and fixes:

| You see | What it means | What to do |
|---|---|---|
| `429 Request too large ... TPM` | Your account's per-minute token limit is too low for the serializer packet | Add credit / verify to tier up (Step 0), so your TPM exceeds the request size |
| `MAX_TOTAL_TOKENS` before the report | The full lifecycle exceeded the token cap | Raise it: `$env:MAX_TOTAL_TOKENS = "3000000"` before `sentinel` |
| `MAX_TOOL_CALLS` | The tool budget was too small for the investigation | Pick a full-depth package on the launch card (`2 = full Terra run` or `3 = qualifying Sol`), or raise `MAX_TOOL_CALLS` |
| `ACTION NEEDED` card, no launch offered | Evidence isn't route-ready | Fix the card's "FIX BEFORE LAUNCH" blockers, then run again |

Exit codes, if you script this:

| Exit | Meaning | Junior action |
|---:|---|---|
| `0` | Completed within policy | Read the reported status; not an accuracy guarantee |
| `1` | Fatal runtime/provider/verification/custody failure | Preserve output; don't rely on the result |
| `2` | Invalid input/config or no ready route | Fix the case-card blocker; don't force a launch |
| `3` | `PARTIAL` - a cap or phase stopped safely | Preserve the bundle; report it as partial, never as complete |

---

## 🔎 No key? No evidence? You can still explore

A judge or curious newcomer can inspect the experience and verify a supplied
bundle with nothing at all:

```powershell
sentinel                                      # the guided welcome (safe to explore)
sentinel verify "C:\path\to\supplied-bundle"  # check a bundle offline
sentinel view   "C:\path\to\supplied-bundle"  # open its proof viewer
```

---

## 📌 A tiny cheat sheet to keep

| I want to… | Command |
|---|---|
| Install / repair everything | `.\setup.ps1` (Linux/macOS: `./setup.sh`) |
| Re-verify without reinstalling | `.\setup.ps1 -Check` (Linux/macOS: `./setup.sh --check`) |
| Start a whole case | `sentinel` (Linux/macOS: `./unchained.sh`) |
| Save my key manually | `sentinel key` |
| Confirm my key | `sentinel key --status` |
| Check a bundle | `sentinel verify "<bundle>"` |
| Open the viewer | `sentinel view "<bundle>"` |

**If `sentinel` isn't found** (rare - usually just open a new terminal), the
full path always works:

```powershell
& "$env:LOCALAPPDATA\venvs\sentinel-unchained-py311\Scripts\sentinel.exe"
```

Next: [judge quickstart](../JUDGE-QUICKSTART.md) ·
[architecture](ARCHITECTURE.md) · release handoff
