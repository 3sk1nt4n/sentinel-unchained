# Sentinel Unchained

<p align="center"><img src="docs/assets/emblem.svg" width="120" alt="Sentinel Unchained emblem"></p>
<p align="center"><strong>Autonomous DFIR on GPT-5.6</strong><br><em>read-only, capped, fully audited.</em></p>

> **Build Week planning and execution sources:**
> [docs/WINNER_ROADMAP.md](docs/WINNER_ROADMAP.md) controls priority, sequence,
> positioning, and go/no-go gates.
> [docs/HACKATHON_MASTER_PLAN.md](docs/HACKATHON_MASTER_PLAN.md) records the
> detailed experiment, proof, prompts, judge path, and submission contracts.
> [HACKATHON_HANDOVER.md](HACKATHON_HANDOVER.md) records current evidence-backed
> status, risks, and the next action. All three must stay synchronized with
> every material strategy or status change.

Sentinel Unchained is a developer-facing trust-measurement harness for
model-directed investigators, with DFIR as its testbed. GPT-5.6
chooses typed forensic work, interprets results, maintains case notes, proposes
findings, receives a fresh downgrade-only review, and writes the narrative.
Deterministic code retains evidence custody, execution authority, protocol,
audit receipts, and resource limits. A frozen reference evaluation and retained
proof bundle are designed to measure factual correctness and receipt sufficiency
without treating the model or its reviewer as ground truth.

**New user quickstart:** [`JUDGE-QUICKSTART.md`](JUDGE-QUICKSTART.md) is the
copy-paste Windows installation, no-key verification path, authentic run path,
capability matrix, troubleshooting guide, and implementation map. Start there
if you need to run this repository on a fresh computer.

**Architecture:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) shows the
deterministic safety floor, GPT-5.6 trust boundary, receipts, caps, and the
observed pre-freeze rehearsal.

This is a complementary controlled-autonomy experiment, not a repudiation of
Sentinel Ensemble's production-oriented deterministic trust layer. It measures
what happens in a reproducible model-directed case when adaptive semantic agency
operates inside constrained authority. It is not presented as a one-variable
causal ablation of the prior system.

The project intentionally has **no deterministic semantic validator**. Code
protects custody, constrains execution, records the run, and enforces budgets;
it does not decide whether a finding is true. Findings and reports remain model
judgments that require human review.

> Prototype status: this working tree contains the OpenAI-native vNext control
> plane, but no retained authentic end-to-end GPT-5.6 run exists yet. Windows is
> the implemented flagship **evidence-OS** path. Linux is experimental, macOS is
> best effort, and non-Windows disk analysis is limited to fixed metadata probes.
> A capability label describes what was actually available in each run; it must
> never imply that unavailable analysis ran.

### Current proof snapshot

The engineering substrate is locally reproducible and the native Windows-memory
leg has a real smoke result, but the GPT-5.6 experiment is not yet demonstrated.
The current working tree passes 267 offline tests and adds exact byte-located
evidence spans, stateless investigation packets, deterministic report and viewer
rerendering, lifecycle-complete verification, evidence-bound tool receipts, and
a user-facing `sentinel` CLI. The reviewed source has 17 modules across 32 Python
files, totaling 13,383 physical and 12,259 nonblank source lines. The two
reviewed upstream baselines and the complete vNext findings are recorded in
[`docs/OPENAI_VNEXT_REVIEW.md`](docs/OPENAI_VNEXT_REVIEW.md).

| Claim | Current evidence-backed state |
|---|---|
| Project implementation | One import-safe controller with deterministic custody, typed authority, a bounded GPT-5.6 state machine, exact spans, deterministic reporting, and a static viewer |
| Offline quality gate | 267 tests, Ruff check/format, `pip check`, wheel build, and sdist build pass in CPython 3.11.9; 17 source modules, 32 Python files, 13,383 physical source lines, and 12,259 nonblank source lines |
| Reproducible runtime | CPython 3.11.9 AMD64 in two clean virtual environments outside OneDrive; `pip check` clean |
| Dependency record | Exact Windows CPython 3.11 constraints and `pylock` committed |
| Forensic substrate | `windows.info` resolved symbols; sealed registry exposes 14 Windows-memory tools; real `vol_pstree`, `vol_psscan`, and high-volume `vol_netscan` smokes succeeded |
| Proof machinery | Exact accepted tool outputs, byte ranges, evidence-bound receipts, lifecycle automaton, manifest, summary, environment record, detached checksum, deterministic viewer, and offline verifier implemented |
| Synthetic lifecycle proof | One empty-evidence bundle verifies internally as `INVALID`; it contains no evidence bytes, findings, native plugin rows, or model response |
| Authentic experiment | **NOT YET PROVEN**: no authentic GPT-5.6 run, public freeze, or frozen-reference scored bundle |

The offline verifier proves bundle integrity, recorded lifecycle consistency,
exact citation resolution, and recorded provider metadata. It cannot independently
authenticate OpenAI from locally written response IDs or usage fields. The
strict flags reject incomplete or fake-marked fixtures, but provider authenticity
still requires an authentic retained run plus external provider or operator
attestation. The separate native smoke is pre-freeze local engineering proof,
not a public, scored, or model-directed run.

### Honest limits of the current result

The control plane is designed to reduce avoidable latency through a six-tool
maximum parallel opening, stateless bounded packets, implicit-cache-compatible
stable prefixes, and one adaptive tool per turn. There is no retained authentic
GPT-5.6 run or controlled latency/cost benchmark yet, so "faster" remains a
design objective, not a measured result or guarantee. The verifier proves local
bundle integrity, not provider authorship or forensic truth. Production
hardening still needs OS-enforced child network/filesystem isolation, stable
evidence handles or immutable snapshots, and an external signature, timestamp,
or WORM anchor. The current adapters also fail closed on multiple ready images
of one class; persistent sandboxed workers and resource-aware opening scheduling
remain future performance work. Finally, a same-user or administrator can race a
verified pathname before an external browser opens it. These boundaries are not
changed by the passing offline suite.

## Build Week contribution boundary

Only submission-period additions are evaluated. The boundary is explicit:

**Prior work, used as MIT-licensed context:** selected typed forensic tool
functions, fixed forensic plugin metadata, and selected evidence-mounting
substrate from the author's
[Sentinel-Ensemble-Qwen](https://github.com/3sk1nt4n/Sentinel-Ensemble-Qwen)
repository at commit
`9f309c6134e857f7b86f3e6b9c6709ce954944a5`.

**Built for Sentinel Unchained during this submission period:** the evidence
profiler and capability router; constrained Responses API adapter; model-chosen
parallel opening; adaptive one-tool loop; literal-DONE and forced-finalization
protocol; fresh-context downgrade-only reviewer with exact quote receipts;
custody, audit, caps, containment, report-safety, and bounded provider-retry
integration; content-addressed exact tool-output retention; provider-returned
identity and usage receipts; proof-bundle construction; a standard-library
offline verifier; Unchained tests; prompts; and documentation.

The deterministic static viewer is now implemented and sealed into every
finalized bundle. The public experiment freeze, frozen reference rubric and
disclosed scoring, authentic real-evidence GPT-5.6 bundle, hosted publication,
video, and submission remain future gates. They are not claimed as completed
merely because their contracts or offline implementations exist.

The prior pipeline, semantic validator, prompts, reports, metrics, findings, and
runs are not claimed as new Unchained work. See
[BUILD_PROVENANCE.md](BUILD_PROVENANCE.md) for the dated boundary and exact
limitations of the initial Git baseline.

## How Codex contributed

The current majority-core Codex thread implemented and reviewed the Unchained
controller, typed authority boundary, evidence lifecycle, audit and cap
semantics, model protocol, report safety, and offline tests. Codex also performed
live-rules verification, official API-contract review, adversarial code review,
experiment-method review, judge-experience review, and the C1 security and
partition-routing hardening. The successful thread ID is retained below and in
the provenance record. Local commits `5309e5c`, `7b05d6a`, `6e696a0`, and
`207a039` bind the provider/reviewer hardening, self-verifying proof-bundle plus
Python 3.11 work, real Windows-memory Gate A hardening, and synchronized winner
documentation. They are local content bindings, not independent public
timestamps.

The human owner chose the product thesis, Developer Tools track, DFIR testbed,
benchmark, safety boundary, scope cuts, evaluation claims, and final submission
decisions. Codex accelerated implementation and verification; it did not turn
fake-model tests into runtime proof or make the unfinished authentic run,
authentic viewer demonstration, hosted path, video, or submission complete.

## Deterministic floor

Four deterministic safety domains form the control plane. Supporting controller
code enforces their protocol without making semantic forensic judgments:

1. `unchained.evidence` discovers evidence, classifies it by content, detects
   OS and evidence shape, establishes read-only access, checks memory-symbol
   readiness, hashes every input before and after analysis, and emits the case
   profile/card. A pre/post mismatch aborts as a custody error. Linux/macOS
   memory is unavailable when symbols are missing **or merely configured but
   unable to resolve this evidence's process-list probe**; an otherwise usable
   disk investigation continues.
2. `unchained.tools` exposes only registered, typed forensic functions as
   strict OpenAI function schemas. The model cannot select a binary, provide
   an evidence path, construct a command string, or access a shell. The trusted
   runner can execute an opening batch concurrently. Before accepting output,
   the private worker recursively removes runner-local evidence and mount paths
   and replaces path references with the public evidence ID. Matching is
   case-insensitive so Windows path variants are covered, and the same scrub is
   applied to worker exception strings before an error receipt crosses the
   boundary. The complete sanitized result is retained. If it exceeds 65,536
   UTF-8 bytes, the investigator receives a
   separately marked, native-order prefix view no larger than 65,536 bytes,
   including the complete accepted-output byte count and SHA-256 plus
   `model_view_complete=false`.
3. `unchained.audit` is the sole writer of append-only `audit.jsonl`. Before a
   tool completion is accepted, it verifies the output digest and atomically
   retains the exact complete sanitized UTF-8 bytes in a content-addressed
   `tool-outputs/` artifact. The audit receipt records that artifact's path,
   SHA-256, byte count, encoding, media type, completeness, and a distinct
   UTF-8-safe excerpt of at most 2,048 bytes. That 2,048-byte receipt excerpt is
   not the 65,536-byte investigator view and neither is the complete retained
   artifact. Model receipts separately preserve the requested model,
   provider-returned model, response ID, request ID, validated usage,
   timestamps, and running cost estimate.
4. `unchained.caps` atomically enforces tool-call, token, wall-clock, and cost
   limits. A fired cap stops the agent gracefully and normally labels the report
   `PARTIAL` with exit code `3`; a later cleanup, containment, or custody failure
   supersedes that partial result as `FATAL`.

The CLI creates the `RunBudget` before Step 0 starts profiling evidence, so the
wall deadline includes file inventory, initial custody hashing, content
classification, forensic probes, symbol readiness, and mounting, not just
model/tool turns.

Inventory never follows symlinks: a symlinked input or descendant, a nonregular
traversal entry, or any walk/stat failure closes preflight rather than silently
omitting evidence. The final inventory applies the same rule and converts any
such failure into a custody error.

Everything forensic above that floor is model-directed:

```text
PROFILE + ROUTE
       |
       v
OPENING BOOK: GPT-5.6 selects one to six eligible tools; run in parallel
       |
       v
PLAN -> ACT (one typed tool) -> OBSERVE -> UPDATE CASE NOTES -> repeat/DONE
       |
       v
LITERAL DONE -> forced structured serialization (no forensic tools)
       |
       v
FRESH JUDGE: preserve or downgrade existing findings from exact spans
       |
       v
GPT-5.6 STRUCTURED DRAFT -> DETERMINISTIC REPORT + VIEWER + PROOF BUNDLE
       |
       v
POST-RUN SHA-256 CUSTODY VERIFICATION
```

All filenames, paths, artifact text, parser output, and tool output are treated
as hostile evidence data. Prompts explicitly prohibit following instructions
found in that data or allowing it to alter policy, caps, tool eligibility, or
verdict rules.

## Investigator prompt contract

[`src/unchained/prompts.py`](src/unchained/prompts.py) is the project-owned,
authoritative investigator prompt. It is not copied from, imported from, or
delegated to the Qwen project. `unchained.agent` combines that prompt with
phase-specific protocol instructions and the hostile-evidence rule.

In the opening book, GPT-5.6 receives the detected OS, evidence shape, and only
the tool families actually available for that route. It must choose between one
and six distinct, high-information **function names** for that OS and shape;
calling the same function with another PID or argument is still a duplicate.
Opening validation is all-or-none: zero calls, more than six calls, a duplicate,
an unavailable name, invalid arguments, or any other invalid selection rejects
the entire batch before an opening executor starts. A `COMPLETE` run therefore
has one to six distinct valid opening calls and exactly zero rejected opening
calls. Windows, Linux, and macOS memory choices stay within their respective
namespaces; disk choices favor execution, timeline, and persistence artifacts.
If the profile marks memory `UNAVAILABLE`, the model must skip memory tools,
continue with disk when possible, and record the limitation. A valid opening
batch reserves all cap slots atomically and runs in parallel. If that reservation
is capped, no executor starts, but every model-issued call still receives paired
audit events and a deterministic `capped` result payload with an output hash.

The investigator has typed, read-only forensic functions only: no shell, no
internet or browsing tool, and no authority to modify evidence. After opening,
each turn follows PLAN → ACT with at most one forensic function → OBSERVE →
UPDATE CASE NOTES. Factual statements must cite exact tool-call IDs inline,
such as `[t17]`. The prompt prefers cross-domain memory-and-disk corroboration,
requires contradictions to be acknowledged with an explicit course correction,
and retains dead ends rather than silently dropping them. It stops on
diminishing returns, when further calls have stopped changing the conclusions.

The only normal loop terminator is a response with no function call whose raw
text is exactly the four ASCII characters `DONE`. Leading or trailing whitespace,
a newline, extra text, a different no-call response, or `DONE` alongside a tool
call is a protocol error. After accepting `DONE`, the controller performs a
separate, forced `submit_investigation`
serialization. That request exposes only the strict serialization schema, with
no forensic functions, so it cannot resume the investigation, collect or add new
evidence, or take another forensic action. It only converts the already-finished
notes, supported or contradicted hypotheses, dead ends, limitations, and
findings into the structure consumed by the fresh judge.

The forced serializer must supply exact supporting quotes for each finding.
Controller code resolves each quote against the complete retained tool output
and records an artifact digest, byte start/end, occurrence count, and stable span
ID. The fresh judge receives only the existing findings and their exact evidence
spans. It may preserve or downgrade; it cannot add a finding or upgrade the
investigator's proposed status. Every verdict must cite a known span and return
a quote contained inside that span. `sentinel verify` reopens the content-addressed
artifact and checks the digest, byte range, decoded text, span ID, finding
relationship, and judge quote. This proves traceability, not that the quote
semantically entails the claim.

## Requirements, host support, and installation

- CPython `>=3.11,<3.12`; the validated flagship interpreter is official
  CPython 3.11.9 AMD64 on Windows
- Git, for the pinned direct dependency
- `OPENAI_API_KEY` only for an authentic model run
- `UNCHAINED_MODEL` set to `gpt-5.6` for an authentic model run
- Volatility 3 for memory analysis and `python-registry` for the Windows
  Registry parsers; both are declared Python dependencies
- Native forensic utilities required by the evidence route

An optional future Windows E01/NTFS disk route currently needs a Linux host or
WSL, direct root execution, readable Linux `/proc/self/mountinfo`, and the
native helpers used by the pinned mount backend, notably `ewfmount`/libewf and
`ntfs-3g`. Native Windows cannot perform that mount path. Paired disk is
explicitly outside the Build Week primary and is not a remaining gate.
Sleuth Kit's fixed read-only metadata probes require `fsstat`, `img_stat`,
and/or `mmls` on `PATH`. Linux ext4/xfs and HFS+ mounting uses the host
`mount`/`umount` tools with root or non-interactive `sudo`; APFS best effort
uses `apfs-fuse` when present.

Those direct raw-filesystem mounts use fixed argument vectors and no shell:
ext4 uses `ro,noload,loop`, xfs uses `ro,norecovery,loop`, HFS+ uses `ro,loop`,
and APFS uses `apfs-fuse -o ro`. A mount is accepted only after the resulting
mountpoint independently verifies read-only. A failed, rejected, or capped
attempt is unmounted when active and must verify inactive; normal close runs a
fixed `umount` and makes the same check. Failure to prove release is fatal.

Accordingly, “Windows tested” currently means the demonstrated Windows
**memory-evidence** route. It does not promise E01 mounting on native Windows or
claim that every combination of host, filesystem, symbol table, and native tool
has been validated. The Build Week primary is frozen to memory-only and works
without a disk mount when its Volatility runtime and symbols are ready.

Memory readiness is fail-closed except for Windows' explicit automatic-symbol
path. Linux/macOS symbols that exist on disk but do not resolve the
evidence-specific `pslist` probe are labeled `configured-unverified`, marked
`UNAVAILABLE`, and not exposed as memory tools. If the Windows Volatility
runtime exists but its `windows.info` readiness probe fails, the image remains
routable only as degraded `auto-download-pending`; its capability label says
`Windows symbol auto-download/probe pending` rather than claiming memory ready.
A missing Windows Volatility runtime still makes memory unavailable.

Create the virtual environment outside OneDrive and install against the exact
validated constraints:

```powershell
$venv = "$env:LOCALAPPDATA\venvs\sentinel-unchained-py311"
py -3.11 -m venv $venv
$python = "$venv\Scripts\python.exe"
$env:PIP_REQUIRE_VIRTUALENV = "true"
& $python -m pip install -r requirements/bootstrap.txt
& $python -m pip install -c requirements/constraints.windows-amd64-cp311.txt -e ".[dev]"
& $python -m pip check
```

The same dependency set was independently installed and checked in a second
clean environment named `sentinel-unchained-py311-lockcheck`. The conventional
constraints file is the pip installation input. The committed
`requirements/pylock.windows-amd64-cp311.toml` is the stronger source and hash
record, and each proof bundle records its digest plus whether installed versions
match it. A `pylock` file is not a legacy pip `-r` requirements file. See
[`requirements/README.md`](requirements/README.md) for the exact reproduction
and validation contract.

The distribution name is `sentinel-unchained`; its Python import package is
`unchained` (stored under `src/unchained`). The canonical installed command is
`sentinel`; `sentinel-unchained` and `python -m unchained` are compatibility
entry points.

`pyproject.toml` installs the prior project as a direct Git dependency pinned
to the reviewed full commit:

```text
sift-sentinel @ git+https://github.com/3sk1nt4n/Sentinel-Ensemble-Qwen.git@9f309c6134e857f7b86f3e6b9c6709ce954944a5
```

Only its evidence-mounting support and typed forensic tool functions are
adapted, and imports are lazy so basic CLI/configuration work does not trigger
the old package's heavy module side effects. Unchained code does **not** import,
copy, or invoke the Qwen pipeline, coordinator, validator, prompts, report
code, or generic command-execution interfaces. The model sees only Unchained's
reviewed typed schemas and the project-owned prompt above; it never receives
the dependency's orchestration or prompt layer.

### Flagship Windows memory path

The preferred route is the existing reviewed typed adapter over Volatility 3's
cross-platform `vol` console entry point. Trusted code owns the plugin mapping,
evidence path, fixed argument vector, timeout, child-process boundary, and
output receipt; the model sees only strict function schemas and never a command
or path. The clean CPython 3.11.9 environment proves that `vol -h` starts and
that the pinned dependency catalog exposes exactly 25 direct tools plus 5
dynamic Volatility tools.

The real pre-freeze native smoke is now green:

| Artifact or check | Verified value |
|---|---|
| Official DC01 memory archive size | 561,424,278 bytes |
| Archive MD5 | `64A4E2CB47138084A5C2878066B2D7B1`, matching the publisher-listed value |
| Archive SHA-256 | `86658D85D8254E8D30DCCC4F50D9C2A8B550A101D2E78A6D932316849E37AD80` |
| Extracted memory size | 2,147,483,648 bytes |
| Extracted memory SHA-256 | `8079A7459B1739CAF7D4FBF6DDE5EB0AE7A9D24DBDE657DEBF4D5202C8DC6B62` |
| Readiness | `windows.info` resolved the exact symbols; profile marked memory ready |
| Sealed catalog | 14 Windows-memory functions exposed for this profile |
| Authoritative process batch | `gate-a-final-20260715T015251Z`; wall time 5,968 ms |
| `vol_pstree` | 40 records; 15,277 sanitized accepted bytes; SHA-256 `E2E70D5164939F5A735C450ECC0F2C268E48F22AE4A4DAB76A92FA67F04ECAC6` |
| `vol_psscan` | 72 records; 16,526 sanitized accepted bytes; SHA-256 `836951C95FDCC131064B52CFC229BB3753E389567FCB534174AC3F40D14A7FE4` |
| First `vol_netscan` attempt | Honest error receipt: legitimate response exceeded the old 2,000,000-byte worker boundary |
| Successful `vol_netscan` regression | Run `gate-a-netscan-20260715T014947Z`; 19,685 records |
| Full sanitized `vol_netscan` output | 3,961,843 accepted bytes; SHA-256 `EFCED1AF66F99EC2064D14F30A5F018D90E5C169027672BE9E3C0110122CB421` |
| Deterministic `vol_netscan` delivery-view check | Candidate investigator payload exactly 65,536 bytes; 55,732 native-order prefix characters; `model_view_complete=false`; full accepted bytes/hash included; no model received it |
| Output privacy | Public evidence ID `E001` present; runner-local evidence path absent |
| Custody | Post-smoke evidence hash matched the pre-smoke hash |

The evidence, extracted memory, and smoke output remain outside the repository.
This establishes the local Gate A native-execution leg only. It is not a public
proof artifact, scored run, or GPT-5.6 investigation. No model or API was used
for these deterministic native smokes.

Earlier `vol_pstree` and `vol_psscan` hashes were produced before output-path
sanitization. They remain honest diagnostic artifacts outside the repository,
but the post-sanitizer batch above replaces them as the current public-safe
local values.

The native smokes exposed and fixed three integration defects: Windows fixed
direct tools were incorrectly filtered through the Linux/macOS dynamic-plugin
catalog; the absolute-venv evidence probe did not find the adjacent `vol.exe`
when it was absent from inherited `PATH`; and the legitimate `netscan` response
exceeded the original fixed 2,000,000-byte worker boundary. Regression tests
cover all three, including path removal, the 16,000,000-byte transport ceiling,
and deterministic construction of the explicit 65,536-byte candidate
investigator view. No investigator or model received that Gate A payload. A
direct Volatility Python API rewrite remains unnecessary unless the reviewed
typed console path later reproduces a different blocking failure.

A final privacy hardening applies that recursive path scrub to worker exception
strings as well as successful values and matches Windows paths
case-insensitively. A subprocess regression proves that a case-variant private
path in an exception becomes the sealed public evidence ID before the parent
accepts the error receipt. This was an offline deterministic check; it invoked
no investigator, model, or API.

## Configure and run

After installation, start with deterministic checks that make no OpenAI call:

```powershell
sentinel doctor
sentinel profile C:\path\to\evidence
```

Then configure the funded model run and launch it:

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:UNCHAINED_MODEL = "gpt-5.6"
sentinel run C:\path\to\evidence --caps default
```

The user-facing lifecycle is:

```text
sentinel doctor [--json]
sentinel profile <evidence-file-or-folder> [--mount] [--json]
sentinel run <evidence-file-or-folder> [--caps default|strict]
sentinel verify <run-directory> [--require-complete] [--require-live-gpt56]
sentinel view <run-directory> [--no-open]
```

`python -m unchained ...` and `sentinel-unchained ...` remain compatibility
entry points. A live run validates the model and key before reading evidence or
creating a run directory. `doctor` never prints the key. `profile` inventories,
routes, and verifies its custody pass without contacting OpenAI.

The input contract accepts a folder containing a memory image and/or disk
image, and discovery uses content rather than filename extensions. The scored
Build Week primary is intentionally narrower: one demonstrated Windows
memory-only route. Windows E01/NTFS disk remains implemented but unproven future
validation, not part of the primary. Linux Volatility 3 and fixed Sleuth Kit
metadata probes are experimental; macOS Volatility/APFS-HFS+ support is best
effort. **Plaso is not exposed by this prototype and is never advertised as an
available family.** A standalone logs-only folder is not a supported CLI
investigation route; log parsers are used against artifacts exposed by a
supported mounted-disk route. Evidence roots and descendants must be regular,
non-symlink files/directories that can be enumerated completely.

### Responses state, reasoning, and data boundary

Every API request sets `store=false`; the implementation does not depend on a
provider-stored response chain. Each adaptive turn is a fresh, stateless packet
containing the public profile, a compact controller-owned case ledger, receipt
index, remaining budget, and only the latest observation. It does not replay the
provider transcript or encrypted reasoning items. The finalizer receives the
retained observations once, while the fresh judge receives only findings and
their resolved evidence spans. Every phase uses
`reasoning.context="current_turn"`, with phase-specific effort, verbosity,
output-token, and tool-call limits. See the
[official GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model).

Raw SDK/provider `output_items` are adapter-local transport data. The adapter
normalizes them into the controller-visible message and parsed function calls;
the raw items are neither retained as an independent proof authority nor
replayed on a later turn. This avoids two contradictory representations of one
response in the bundle. Strict verification binds the canonical normalized
message/function calls to the resulting controller actions and receipts.

Requests set `prompt_cache_options.mode="implicit"`, matching GPT-5.6's
automatic prompt-cache path. Stable matching prefixes such as the phase
instructions, typed catalog, and public case profile may therefore be reused;
cache hits are an optimization, not a correctness assumption or a measured
benchmark claim. Provider-reported reads and writes remain audited and priced.
See the
[official prompt-caching guide](https://developers.openai.com/api/docs/guides/prompt-caching).

For the tested `openai==2.31.0` compatibility target, `Responses.create` does
not expose GPT-5.6's experimental `prompt_cache_options` as a typed top-level
Python keyword. The adapter passes that mapping through the OpenAI Python SDK's
supported [`extra_body` request option](https://github.com/openai/openai-python#undocumented-request-params).
`extra_body` is only the SDK call's compatibility escape hatch: the SDK merges
its contents into the outgoing JSON, whose top level contains
`prompt_cache_options` alongside the independently typed `reasoning` object.
The wire body does **not** contain an `extra_body` field.

This is not an assertion that content never leaves the machine: evidence-derived
profiles, bounded observation text, and exact cited span text are transmitted to
OpenAI for inference.
Provider and organization retention, Zero Data Retention eligibility, data
residency, and access policy remain external deployment boundaries that an
operator must review.

Default hard limits are:

| Environment variable | Default | Strict profile |
|---|---:|---:|
| `MAX_TOOL_CALLS` | 60 | 20 |
| `MAX_TOTAL_TOKENS` | 400,000 | 100,000 |
| `MAX_WALL_SECONDS` | 1,800 | 600 |
| `MAX_COST_USD` | 10.00 | 2.50 |

Each value can be overridden with the exact variable above or its
`UNCHAINED_`-prefixed alias. The local GPT-5.6 Sol estimator understands
$5.00/M uncached input tokens, $0.50/M cached input tokens, $6.25/M
cache-write tokens, and $30.00/M output tokens. The cache-write rate is 1.25
times uncached input. For a request above 272,000 input tokens, it applies 2x
input and 1.5x output pricing to the full request, matching the published
[GPT-5.6 Sol pricing rules](https://developers.openai.com/api/docs/models/gpt-5.6-sol).
The live adapter accepts only the `gpt-5.6` alias or a GPT-5.6 Sol model ID or
snapshot (`gpt-5.6-sol...`); it rejects Terra, Luna, and other model families.
Only the four cap values in the table are environment-overridable. The Sol
price rates are code-owned; price-like environment variables are ignored so an
operator cannot zero the rate table and silently bypass `MAX_COST_USD`.

Implicit caching can miss and may also report cache writes. Preflight therefore
prices every estimated input token at the ordinary uncached GPT-5.6 Sol rate;
the hard cap never assumes a future hit. After each response, the audit records
provider-reported cached-input and cache-write fields and the cost calculator
reconciles both. For a `COMPLETE` lifecycle, strict verification independently
recomputes every local call and cumulative estimate from the audited token counts
and code-owned price table, then binds the totals to the final budget snapshot
and configured token, cost, tool, and wall caps. This is local safety accounting,
not a reconstruction or authentication of an OpenAI invoice. Provider-side usage
and billing remain authoritative, and pricing, tokenizer behavior, cache
retention policy, or API usage fields can change.

Usage accounting is mandatory for every live provider response. `input_tokens`,
`output_tokens`, and `total_tokens` must be present nonnegative integers;
cached-input, cache-write, and reasoning counters must also be nonnegative when
present. The provider total must equal input plus output. Missing, negative, or
inconsistent usage is audited as a usage-protocol failure and rejected before
the response can advance the investigation. In the CLI agent flow that ends the
mandatory model phase as `PARTIAL` with exit `3`, subject to the later
cleanup/custody safety override described below.

The configured `UNCHAINED_MODEL` value proves only what was requested. Every
accepted live response must also expose the provider-returned `response.model`,
which is stored separately as `provider_model` together with the response ID,
request ID, status, and usage. A missing or non-GPT-5.6 provider identity is a
protocol failure. No current retained bundle satisfies this live-provider gate.

## Outputs and status

Each run writes an isolated directory at
`<working-directory>/unchained-runs/<UTC-timestamp>-<id>/`. If the working
directory is the evidence folder or is nested beneath it, the base moves to the
evidence folder's parent so outputs are not written into evidence. A finalized
bundle contains:

```text
report.md         narrative or explicit PARTIAL/FATAL/INVALID fallback
viewer.html       inert, deterministic, self-contained local proof view
audit.jsonl       ordered, hash-chained lifecycle and proof receipts
environment.json allowlisted runtime, dependency, Git, prompt, catalog, and cap facts
summary.json     audit-derived status, timing, usage, tool, finding, and custody counters
manifest.json    explicit artifact allowlist with hashes, sizes, audit tip, and terminal state
manifest.sha256 detached SHA-256 for manifest.json
profile.json      model-safe profile when evidence profiling succeeded
tool-outputs/     exact content-addressed sanitized accepted outputs when tools completed
```

Tool output is not merely represented by a digest and excerpt. The exact full
sanitized accepted UTF-8 bytes are stored before `tool.completed` is appended.
Storage is atomic, duplicate-content safe, and fail-closed on a digest conflict,
unsafe path, symlink, or nonregular target. The 2,048-byte audit excerpt is only
a compact audit field; the judge no longer depends on it. The investigator sees
at most a receipt-bearing 65,536-byte model view. Findings cite controller-
resolved byte spans from the full artifact, and both the verifier and static
viewer use those exact retained spans.

The report header visibly states the terminal status: `COMPLETE`, `PARTIAL`,
`FATAL`, or `INVALID`. A completed model report's limitations section must
disclose unavailable capabilities, tool failures, and that there is no
deterministic validator by design. The final custody result is a later
deterministic CLI/audit event, not a model-authored claim, and a failure replaces
the terminal result with `FATAL`. Finding citations use tool-call IDs that can
be checked against `audit.jsonl`.

| Exit | Meaning |
|---:|---|
| `0` | Completed within policy; not an accuracy guarantee. |
| `1` | Fatal runtime or custody failure. |
| `2` | Invalid input or configuration. |
| `3` | `PARTIAL`: a cap fired, or a mandatory investigator/judge/report phase could not complete safely because of a model/provider/tool protocol failure. |

Absent a later cleanup or custody safety failure, every fired cap produces
`PARTIAL` and exit `3`. Exit `3` is intentionally a little broader:
malformed/incomplete model output, invalid provider usage, or another
provider/tool protocol failure in a mandatory agent phase also preserves an
explicitly incomplete artifact instead of claiming success. An inability to
contain or release a mount, another unrecoverable runtime failure, or a custody
mismatch overrides an earlier partial result as `FATAL`/exit `1`.

The OpenAI SDK's implicit retry layer is disabled with `max_retries=0` so retry
behavior remains visible. Trusted controller code permits at most two retries,
for at most three dispatch attempts, only for connection/time-out failures,
HTTP 408/409/429, or HTTP 5xx. It audits every failed attempt, scheduled delay,
and eventual success or exhaustion; applies 0.25-second then 0.5-second bounded
backoff; and stops when wall time is insufficient. A returned response is never
retried for malformed usage, wrong provider model, schema, or protocol. The
controller receives only the final accepted response, so discarded dispatch
attempts cannot cause a forensic tool to execute twice.

GPT-5.6 does not author the authoritative Markdown table. It submits a strict
report draft containing narrative fields and exact finding/span references.
Controller code validates those references and deterministically renders status,
findings, verdict transitions, citations, IOCs, limitations, and custody fields.
Model prose is labeled **model-authored, nonauthoritative**, defanged before
rendering, and cannot add a row, alter a verdict, or invent a citation through
formatting. Its exact normalized UTF-8 report bytes are bound into
`report.completed`. Verification reconstructs that report from the verified
canonical profile, investigator packet, judge verdicts, evidence spans, and
submitted draft, then requires an exact byte match. The static viewer escapes all
dynamic text, contains no script or external resource, and carries a restrictive
CSP. It too is deterministically rerendered from verified bundle state and
byte-compared, in addition to its independent inert-HTML policy. Reports remain
analyst-facing output and need human review.

The audit hash chain makes accidental/local modification detectable, but a
privileged actor who can rewrite the whole run directory is outside this
application's trust boundary. It is append-only at the application level, not
externally anchored immutable storage. Likewise, pre/post SHA-256, file
identity, size, and timestamp checks detect end-state changes but cannot defeat
an actor with concurrent write/rename access to the evidence directory who
swaps an evidence path during a tool run and restores the original object and
metadata before final verification. Use an externally protected evidence store
for that threat model.

### Verify a retained bundle without rebuilding

The verifier uses only the Python standard library. It imports neither the
OpenAI SDK nor the forensic dependency, contacts no network service, and does
not rerun a tool:

```powershell
sentinel verify C:\path\to\run-bundle
sentinel view C:\path\to\run-bundle
```

That base command validates the declared terminal state, including an honestly
finalized `INVALID`, `PARTIAL`, or `FATAL` run. It checks normalized paths,
non-symlink regular files, every manifest hash and byte count, the detached
manifest checksum, audit sequence and hash chain, exact sanitized accepted tool
outputs, identity-and-digest-verified semantic rereads, recomputed span
occurrence counts, receipt excerpts, finding citations, mandatory exact reviewer
quotes, downgrade-only review semantics, terminal consistency, recorded custody
receipts, and the proof viewer's inert HTML/CSP policy. For every viewer-bearing
bundle it also rerenders the viewer from the verified status, profile, rebuilt
summary, report, and audit prefix and requires the exact bytes.

`sentinel view` never treats browser launch as a shortcut around proof checking.
It verifies first, and when a bundle declares `COMPLETE` it automatically forces
the complete strict lifecycle verifier before opening the manifest-declared
viewer, even if the caller did not pass strict flags.

For a complete lifecycle with recorded GPT-5.6 metadata, enable both strict
offline gates:

```powershell
sentinel verify C:\path\to\run-bundle `
    --require-complete --require-live-gpt56
```

The strict command requires `COMPLETE` and binds the entire ordered opening,
investigation, finalization, judge, and report transaction graph. A model
transaction is retry-aware: one request/options pair may contain only the
bounded audited transient-failure/scheduled-retry pairs permitted by controller
policy before its one accepted response. It reconstructs every exact phase
input—including adaptive ledger, receipt index, budget, latest observation,
finalizer observations, judge packet, and report packet—and binds each accepted
response's output usage to its requested maximum. Retry transport classes,
status codes, backoff, and nonincreasing timeouts are code-bounded. The verifier
validates the immutable strict tool catalog and phase options; all-or-none
opening selection with one to six distinct valid calls and no `capped` or
`rejected` receipt in `COMPLETE`; bool-safe JSON Schema value types for every
typed argument; model call IDs, names, and arguments
against tool receipts; every visible case-ledger update; raw text exactly equal
to the four ASCII characters `DONE`; forced serializer arguments against
`investigator.finished`; judgment arguments against downgrade-only
`judge.completed`; and report-draft references and prose against a freshly
rerendered exact report. It requires `profile.json` to be canonical JSON equal to
the profiled event, round-trips the public profile, deterministically rederives
OS, shape, filesystems, and route-conflict warnings from its evidence inventory,
binds its evidence IDs,
hashes, sizes, and count to initial custody, rebuilds canonical `summary.json`,
and rerenders exact `viewer.html`. It also binds every root and nested artifact
descriptor to the manifest; recomputes each local GPT-5.6 call/cumulative cost
from audited usage and the code-owned prices; binds final usage, cost, and tool
totals and lifecycle counts to the budget snapshot, serialized collections, and
configured caps; checks provider-returned
GPT-5.6 identity, unique response/request IDs, positive usage, and no fake/replay
markers. Raw provider `output_items` are not a proof field. These are locally
recorded fields and locally recomputed estimates; offline verification neither
authenticates them with OpenAI nor validates provider billing.
The current empty-evidence `INVALID` bundle passes the base integrity command
and correctly fails the strict command. Neither command independently rehashes
original evidence bytes that are deliberately absent from the bundle. The
verifier checks the recorded pre/post custody receipts and warns about that
boundary.

### Deadline enforcement and process cleanup

Step 0 cooperatively checks the same budget used by the agent. The file inventory
checks before traversal and for every encountered directory/file; initial
SHA-256 reads check before hashing and after every chunk; content classification
and fixed forensic probes check the budget; probe subprocess deadlines are
shortened to the remaining wall time; and Linux/macOS symbol searches check each
root and walked directory. Individual synchronous filesystem calls, regular-file
reads, or uninterruptible kernel I/O can still block between cooperative checks.

The pinned `RealProbes` E01/NTFS mount ladder is no longer an in-process,
unbounded Step 0 call. On Linux/WSL it is eligible only under direct root with
`/proc/self/mountinfo`, and each `raw@0`, `ntfs_offsets`, or `dmpad` attempt gets
a new fixed child:
`[sys.executable, "-P", "-m", "unchained.evidence",
"--internal-reference-mount-worker"]`. The child runs from a private scratch
directory with `shell=False` and a minimal environment whose home/cache/temp
paths point to that scratch directory and which contains no inherited OpenAI,
cloud, token, secret, password, credential, proxy, SSH-agent, GPG-agent, or
Python import-path variables; it also forces `PYTHONSAFEPATH=1`. It accepts one
bounded JSON mount request and one allowlisted method. The parent's reply wait
is bounded by the smaller of 120 seconds and the run's remaining wall time.

Before launch the parent records the loop-device baseline and whether the
run-specific device-mapper name already exists. A successful worker stays alive
as the `RealProbes` cleanup owner until teardown.
On timeout or a bad protocol reply, the parent sends `SIGTERM` to the POSIX
process group, allows a bounded cleanup interval, escalates to group `SIGKILL`,
and independently cleans and verifies run-owned mounts below the mount/scratch
roots, the run-specific device-mapper name, and, while loop inventory remains
knowable, new loop devices backed by the evidence or scratch tree. `dmpad` is
refused unless loop state is knowable and `losetup`/`dmsetup` are available.
Normal teardown first requests cleanup from
the live owner, then performs the same external verification. If release cannot
be proven, paths are preserved for recovery and the run fails closed as
`FATAL`, even if a wall cap fired first.

This mount worker is process-lifecycle containment, not a privilege, network,
filesystem-namespace, seccomp, or parser sandbox. The pinned backend and native
helpers still execute with root authority. A descendant that deliberately
creates another process group/session can escape group signaling;
uninterruptible kernel I/O can outlive bounded waits; and verification covers
the defined run-owned mount, loop, and device-mapper resources rather than every
possible root-level side effect. It also depends on Linux mountinfo and the
native `umount`, `losetup`, and `dmsetup` controls remaining trustworthy and
available.

The direct ext4/xfs/HFS+/APFS route remains separate from `RealProbes`. Its
fixed subprocess receives the remaining-wall timeout and runs in a new process
group; timeout uses bounded `SIGTERM` then `SIGKILL`. Rejected/capped attempts
and normal close use fixed `umount` calls and accept cleanup only when the
mountpoint is inactive. Unlike the reference-worker containment pass, this
direct route does not baseline arbitrary loop/device-mapper deltas and relies
on the native mount/FUSE helpers and kernel to release their ancillary state.

In the production CLI route, Qwen metadata discovery and Python parser
**execution** do not occur in the parent or opening-batch worker threads. Each
catalog or parser request launches the fixed private child command
`python -P -m unchained._tool_worker`, sends one allowlisted JSON request on
standard input, and receives one JSON envelope. The command and callable
allowlist are code-owned, `shell=False`, and the parent passes the current
remaining wall time as both the outer process deadline and the inner Qwen
timeout. The opening thread pool only supervises up to six such isolated
children concurrently. Each child inherits needed runtime settings but strips
Python import overrides plus OpenAI/provider/cloud credentials, any variable
named like an API key, token, secret, password, private key, or credential,
proxy settings, and SSH/GPG agent sockets, and it forces `PYTHONSAFEPATH=1`.

The worker enables the pinned event-log parser's priority-preserving return gate
at 500,000 bytes. Results below that parser gate remain raw. Independently, the
parent accepts at most one newline-terminated 16,000,000-byte worker envelope.
The old 2,000,000-byte boundary rejected a legitimate high-volume `netscan`
result during the first live parallel smoke, so the bound was raised only after
that reproduced failure and protected with regression tests. An oversized or
unterminated response still becomes an explicit error observation and complete
tool receipt instead of being buffered without bound.

Before any result leaves the private worker, runner-local evidence and mount
paths are recursively removed or replaced with the sealed public evidence ID.
Matching is case-insensitive, including Windows case variants, and exception
strings pass through the same scrub before an error receipt is accepted. The
complete sanitized accepted result is content-addressed. The investigator input
is independently bounded by `ToolResult.model_output()` to 65,536 UTF-8 bytes;
large results include a native-order prefix plus an explicit delivery receipt
with the full accepted byte count, SHA-256, prefix character count, and
`model_view_complete=false`. The fresh reviewer receives only controller-resolved
evidence spans from the complete retained output; it is no longer limited to the
2,048-byte audit excerpt.

The worker writes one JSON response line and then deliberately remains alive.
The parent therefore retains an unambiguous process-tree owner and destroys the
owned tree after every response as well as on timeout. On POSIX, each child
starts in a new session and the parent sends `SIGKILL` to that process group
while its leader is still alive. On Windows, the child starts in a new, hidden
process group and must be assigned to a `KILL_ON_JOB_CLOSE` Job Object before it
receives the JSON request; assignment failure is fail-closed. Every completion
terminates and closes that Job Object. No command shell is used on either
platform.

The remaining OS-level caveat is narrower than an in-process parser-thread
overrun: on POSIX, a descendant that deliberately creates a different process
group or session can escape the original group kill. Reaping can also be delayed
if the worker leader is stuck in uninterruptible kernel I/O. Windows Job Objects
provide a stronger descendant boundary, but the implementation still depends
on the operating system honoring job assignment, termination, and handle-close
semantics. This is process-lifecycle containment, not a network/filesystem or
privilege sandbox: the parser can use the host authority of the account running
Unchained (including root, if applicable), although unrelated credentials are
withheld from its environment.

Registered Sleuth Kit tools use the same private-worker boundary through an
exact, code-owned `tsk` action and an allowlist limited to `fsstat`, `img_stat`,
and `mmls`; the evidence path remains runner-owned. Step 0's deterministic TSK
and Volatility probes, and direct mount/cleanup commands, remain separate fixed
subprocesses. They use code-owned argument vectors, `shell=False`, new process
groups, remaining-wall timeouts, and the same Python-import, credential, proxy,
and agent-variable scrub. Tool definitions injected by the offline fake harness
(or an embedding caller using `ToolRegistry` directly) remain in-process; they
are for testing/injection and do not receive the production child-process
cancellation guarantee.

Cleanup and final custody are intentionally outside the fired budget. The CLI
always attempts mount teardown in `finally`. Once Step 0 has produced a complete
pre-run baseline, it then performs the full post-run file-set, identity,
metadata, and SHA-256 verification even if a cap already fired. Those operations
may make process wall time exceed `MAX_WALL_SECONDS`; a release failure or hash
mismatch becomes `FATAL`. If Step 0 itself is capped before a complete baseline
exists, teardown is still attempted, but there is no valid baseline against
which a final custody comparison can be made.

## Development checks

```powershell
& $python -m pip check
& $python -m pytest
& $python -m ruff check .
& $python -m ruff format --check .
& $python -m build
& "$env:LOCALAPPDATA\venvs\sentinel-unchained-py311\Scripts\vol.exe" -h
& $python -c "from unchained.tools import _load_qwen_catalog; c=_load_qwen_catalog(None); print(len(c['direct']), len(c['volatility_plugins']))"
```

At the current reviewed working tree, the expected catalog output is `25 5`.
The verified vNext quality snapshot is 267 collected and passing tests, clean
Ruff check and format check, successful wheel/sdist builds, and clean `pip check`
in the primary CPython 3.11.9 environment. The source snapshot contains 17
modules across 32 Python files, with 13,383 physical and 12,259 nonblank source
lines. The real `vol_pstree`, `vol_psscan`, and post-fix high-volume
`vol_netscan` smokes described above also pass.
These are operational checks. They do not replace the public experiment freeze
or an authentic GPT-5.6 bundle. The repository history is now publicly anchored
at the remote `origin/main`, while the earlier C2 commit snapshot
remains 123 tests and is preserved as such in provenance.

Tests run without network access. Their behavioral coverage includes:

- all four cap paths, opening overlap, all-or-none distinct-by-name opening
  enforcement with zero rejected calls in `COMPLETE`, complete `capped` receipts
  for calls denied before launch, ordered/hash-valid audit records, exact atomic
  tool-output artifacts, concurrent duplicate retention, persistence-failure
  receipts, raw four-ASCII-character `DONE` plus forced serialization, judge
  downgrade and mandatory rationale, finding-scoped citations, and exact quoted
  spans;
- mandatory, nonnegative, internally consistent live provider usage and
  provider-returned model identity; retry-aware transaction windows that bind
  bounded audited transient retries to their accepted response without duplicate
  tool execution; and recomputed call/cumulative/final-budget estimates from
  code-owned price rates that price-like environment variables cannot zero;
- the real OpenAI Python SDK over `httpx.MockTransport`, proving
  `reasoning.context` and `prompt_cache_options` survive wire serialization
  without making a network request, including implicit-cache default and
  explicit-mode override behavior;
- bounded and fail-closed Step 0 inventory/symbol work (including symlink and
  walk-error rejection), Linux/macOS configured-but-unverified symbol rejection,
  and the degraded Windows auto-download-pending route;
- reference-mount prelaunch budget checks, timeout containment, fail-closed
  resource verification, fixed `-P` launch, hostile-CWD resistance, and
  credential-free child environments;
- parser/TSK-worker credential scrubbing, event-log return-gate configuration,
  exact TSK allowlisting, blocked-child reap, import allowlisting,
  recursive case-insensitive runner-local-path replacement across successful
  values and exception strings, subprocess error-path coverage, the fixed
  16,000,000-byte worker ceiling, oversized-response rejection, and an explicit
  65,536-byte large-output model view that preserves the full accepted byte/hash
  receipt;
- one-line hostile-diagnostic fallback defanging plus removal of inline and
  reference links/images and dangerous schemes from complete reports;
- atomic manifest, canonical profile, rebuilt summary, environment, and
  detached-checksum construction; exact deterministic report/viewer rerendering;
  a positive inert-viewer policy covering active tags, attributes, CSS, CSP, and
  malformed structure; and a standard-library verifier that rejects fully
  re-chained semantic tampering across model/tool bindings, visible ledgers,
  serializer/judge/report arguments, artifact descriptors, report/viewer
  authority, profile/custody identity, span counts, citations, quotes, terminal
  state, cost/budget accounting, custody receipts, or live-model metadata.

See [DECISIONS.md](DECISIONS.md) for the architecture contract and dependency
boundary. See [docs/HACKATHON_MASTER_PLAN.md](docs/HACKATHON_MASTER_PLAN.md) for
the current winner strategy, experiment, proof bundle, judge path, prompts, and
submission doctrine. See [HACKATHON_HANDOVER.md](HACKATHON_HANDOVER.md) for the
current implementation/proof ledger, delivery gates, and next action.

**OpenAI Build Week `/feedback` Codex Session ID:**
`019f61e5-5755-7a02-adb4-618d32baab27`

This ID was returned by a successful feedback upload from the Session 1 thread
where the majority of Sentinel Unchained's core functionality has currently
been built. Use that exact value in the corresponding Devpost submission field
only while this remains the true majority-core thread. Re-run `/feedback` near
submission after material core work and update this value if the qualifying
thread changes.
