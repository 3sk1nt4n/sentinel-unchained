# Sentinel Unchained: quick install and run

This is the shortest reliable path for a fresh Windows 10 or Windows 11 AMD64
machine. The Build Week flagship is Windows memory evidence. Native Windows E01
or NTFS mounting is not part of the primary path.

There are two separate judge paths:

1. No-key verification of a completed proof bundle.
2. An authentic GPT-5.6 investigation using Python 3.11, public evidence, and
   a funded OpenAI project key.

Never present a fake-model test or replay as an authentic GPT-5.6 run.

## 1. Install prerequisites

Install Git for Windows and official CPython 3.11 AMD64:

- <https://git-scm.com/download/win>
- <https://www.python.org/downloads/release/python-3119/>

Enable **Add python.exe to PATH** during Python installation, then open a new
PowerShell window:

```powershell
git --version
py -3.11 --version
```

The validated flagship uses Python 3.11.9. Do not mix Python 3.12 or newer,
Conda, or global packages into the proof environment.

## 2. Clone and install

Run each block from a new PowerShell window:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\src" | Out-Null
Set-Location "$env:USERPROFILE\src"
git clone https://github.com/3sk1nt4n/sentinel-unchained.git
Set-Location .\sentinel-unchained
git status --short
```

Create the virtual environment outside OneDrive:

```powershell
$venv = "$env:LOCALAPPDATA\venvs\sentinel-unchained-py311"
py -3.11 -m venv $venv
$python = "$venv\Scripts\python.exe"
$env:PIP_REQUIRE_VIRTUALENV = "true"
& $python -m pip install --upgrade pip setuptools wheel
& $python -m pip install -r requirements/bootstrap.txt
& $python -m pip install -c requirements/constraints.windows-amd64-cp311.txt -e ".[dev]"
& $python -m pip check
```

Expected final line:

```text
No broken requirements found.
```

## 3. Run the no-key quality gate

This checks the installation and does not call OpenAI or inspect forensic
evidence:

```powershell
& $python -m pytest
& $python -m ruff check .
& $python -m ruff format --check .
& $python -m build
& "$venv\Scripts\vol.exe" -h
```

The validated tree has 128 passing tests. A failure should be fixed or reported
with its environment details. Do not silently switch interpreters.

## 4. Verify a completed proof bundle without rebuilding

For a supplied completed run:

```powershell
& $python -m unchained verify-run C:\path\to\completed-run
```

For strict submission-strength verification:

```powershell
& $python -m unchained verify-run C:\path\to\completed-run `
    --require-complete --require-live-gpt56
```

The current synthetic `INVALID` fixture must fail the strict command. That is
intentional and proves the verifier does not confuse a fake or incomplete run
with an authentic complete run.

## 5. Configure an authentic run

Create a funded project key at:

<https://platform.openai.com/api-keys>

Store it only in the Windows user environment or a secure secret manager. Do
not paste it into chat, Git, a screenshot, or a command saved in history.

After closing old terminals and opening a new PowerShell window, check presence
only:

```powershell
if ($env:OPENAI_API_KEY) {
    "OPENAI_API_KEY is present"
} else {
    "OPENAI_API_KEY is absent"
}
```

Set the requested model and hard caps:

```powershell
$env:UNCHAINED_MODEL = "gpt-5.6"
$env:MAX_TOOL_CALLS = "60"
$env:MAX_TOTAL_TOKENS = "400000"
$env:MAX_WALL_SECONDS = "1800"
$env:MAX_COST_USD = "10"
```

Codex build credits and API runtime billing are separate. Runtime calls use the
funded OpenAI project associated with the key.

## 6. Acquire permitted public evidence outside Git

Use the official DFIR Madness source page:

<https://dfirmadness.com/the-stolen-szechuan-sauce/>

Download only permitted public evidence. Do not commit the archive, extracted
memory image, raw tool output, or private acquisition paths. Keep evidence in a
separate directory, for example:

```text
C:\Evidence\sentinel\dc01\
```

The directory should contain the extracted Windows memory image. The program
profiles content rather than trusting a filename extension and prints a case
card containing OS, shape, readiness, sizes, hashes, and available tools.

## 7. Run the bounded investigator

```powershell
Set-Location "$env:USERPROFILE\src\sentinel-unchained"
$python = "$env:LOCALAPPDATA\venvs\sentinel-unchained-py311\Scripts\python.exe"
& $python -m unchained C:\Evidence\sentinel\dc01 --caps default
```

The run creates `unchained-runs\<run-id>\` beside the repository. A complete
run contains a report, append-only audit log, manifest, summary, environment
record, custody receipts, and retained content-addressed tool outputs.

Exit meanings:

- `0`: complete lifecycle finished.
- `1`: deterministic fatal invariant or cleanup failure.
- `2`: invalid input or configuration. This is not a forensic finding.
- `3`: a hard cap fired. The result is `PARTIAL`, not complete.

## 8. Verify the run

```powershell
$run = (Get-ChildItem .\unchained-runs -Directory |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1).FullName
& $python -m unchained verify-run $run --require-complete --require-live-gpt56
```

The strict verification must establish provider-returned model identity,
response IDs, usage, cost metadata, artifact hashes, quote resolution, custody,
cleanup, and an authentic complete terminal state. If any check fails, retain
the failed run and report its actual state.

## 9. Host and evidence capability truth

| Host and evidence | Status | User-facing claim |
|---|---|---|
| Windows AMD64 plus Windows memory | **TESTED** | Primary route, symbols and typed tools demonstrated |
| Windows plus E01 or NTFS disk | **NOT PRIMARY** | Native Windows disk mounting is not promised |
| Linux plus Windows memory | **EXPERIMENTAL** | Verify Volatility and symbols on that host |
| Linux memory | **EXPERIMENTAL** | Matching kernel symbols are required |
| macOS memory | **BEST-EFFORT** | Not part of the scored flagship |
| Linux or macOS disk | **FUTURE/BEST-EFFORT** | Filesystem helpers vary and are not primary evidence |

## 10. Architecture to implementation map

| Diagram stage | Implementation | Output |
|---|---|---|
| Profile and route | `src/unchained/evidence.py` | Case card, capability profile, hashes |
| Typed runner | `tools.py`, `_tool_worker.py` | Function calls, retained output, delivery receipt |
| Opening book and loop | `agent.py`, `model.py` | Parallel opening, plan-act-observe turns, notes |
| Audit | `audit.py` | Ordered append-only `audit.jsonl` |
| Caps | `caps.py` | Graceful partial stop and cap receipt |
| Judge | `agent.py`, `prompts.py` | Preserve or downgrade with exact quotes |
| Report and proof | `artifacts.py`, `verify.py`, CLI | `report.md`, manifest, summary, verifier result |

## 11. Review of the Qwen and SANS examples

The Qwen repository is the best sample for onboarding because it exposes a
three-step run path, a dedicated judge quickstart, setup scripts, architecture
documents, public-case provenance, and explicit status tables:

<https://github.com/3sk1nt4n/Sentinel-Ensemble-Qwen>

Unchained adopts those communication strengths while tightening the experiment:

- no model shell or generic command executor;
- content-based evidence classification;
- fixed private-worker and model-view byte ceilings;
- full accepted output separated from bounded model delivery;
- case-insensitive success and exception path scrubbing;
- requested and provider-returned model identity separated;
- custody, quote, and artifact hashes independently verified;
- factual correctness separated from receipt support;
- authentic proof kept distinct from replay.

Only the reviewed typed forensic layer is reused from Qwen, pinned in
`pyproject.toml`. The Qwen pipeline, validator, prompts, and report code are not
imported. The older Sentinel-Ensemble repository is contextual prior work, not
the Unchained implementation.

## 12. Troubleshooting

**Python not found:** install official 3.11 AMD64, reopen PowerShell, and run
`py -0p`.

**`pip check` fails:** recreate only the virtual environment outside the repo
using the exact constrained install above.

**API key absent:** set it in the Windows user environment, close old terminals,
open a new terminal, and run the presence-only check again.

**Symbols unavailable:** do not claim memory findings. The router must label
memory `UNAVAILABLE` and continue only with a supported route.

**Exit code 3:** a hard cap fired. Inspect `audit.jsonl` and preserve the
partial bundle.

**Large tool output:** use the full retained artifact and its completeness
receipt. Never call a prefix the complete native output.
