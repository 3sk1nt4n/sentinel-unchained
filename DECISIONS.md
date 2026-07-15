# Sentinel Unchained — Design Decisions

This is the design contract for the Python 3.11 prototype. It records the
choices made without interrupting the kickoff for questions.

Status date: 2026-07-14.

## D-001 — Product boundary

Sentinel Unchained investigates captured evidence and produces an auditable
report. GPT-5.6 plans, acts, interprets, judges, and reports. The product does
not remediate systems, delete artifacts, isolate hosts, disable accounts, or
turn model conclusions into destructive authority.

The system deliberately has no deterministic semantic validator. Code may
prove which bytes a tool returned and which receipt a finding cited; code does
not prove that an intrusion occurred or that an artifact is malicious.

## D-002 — Package and CLI contract

The distribution is `sentinel-unchained`; the import package is `unchained`,
using the source-layout path `src/unchained`. The canonical entry point is:

```text
python -m unchained /path/to/evidence [--caps default|strict]
```

The main module boundaries are:

| Module | Responsibility |
|---|---|
| `unchained.evidence` | Content probes, OS/shape route, read-only mount/access, symbol readiness, pre/post hashes, profile and case card |
| `unchained.tools` | Strict function schemas, eligibility checks, trusted execution, concurrent opening batch |
| `unchained.audit` | Single-writer append-only JSONL and hash-chain verification |
| `unchained.caps` | Atomic hard-cap accounting and cost estimation |
| `unchained.model` | Narrow OpenAI Responses API adapter and offline-fake protocol |
| `unchained.prompts` | Project-owned authoritative investigator and hostile-evidence instructions |
| `unchained.agent` | Opening book, single-tool loop, literal-DONE transition, structured serialization, fresh judge, report request |
| `unchained.cli` / `unchained.__main__` | Run setup, status, custody recheck, artifacts, and exit-code propagation |
| `unchained.models` | Dependency-free typed records shared by the runtime |

Extra helpers may exist, but orchestration from the prior Qwen project must not
enter this call graph.

## D-003 — Prior-project dependency boundary

Reuse is by pip-installed direct Git dependency, pinned to a full commit:

```text
sift-sentinel @ git+https://github.com/3sk1nt4n/Sentinel-Ensemble-Qwen.git@9f309c6134e857f7b86f3e6b9c6709ce954944a5
```

Allowed reuse is limited to evidence-mounting support and typed forensic tool
functions under `src/sift_sentinel`. Imports occur lazily inside adapters.
Unchained code must not import, copy, or invoke the old pipeline/coordinator,
deterministic validator, Qwen prompts, report/finalizer code, or generic
interfaces that accept model-supplied commands, binaries, paths, plugins, or
raw argument vectors.

The authoritative investigator instructions in `src/unchained/prompts.py` are
owned by Sentinel Unchained. They are neither copied nor imported from Qwen.
Phase-specific protocol text may wrap them, but the prior project's prompt
layer never enters the model request.

Pinning makes the reviewed dependency revision repeatable. Updating it is an
explicit security/design change requiring adapter review and tests.

## D-004 — The four deterministic safety domains

Four named domains form the deterministic safety floor:

1. `evidence.py` protects evidence and produces the route/profile.
2. `tools.py` exposes and executes only typed forensic functions.
3. `audit.py` records the complete ordered model/tool run.
4. `caps.py` enforces hard resource ceilings.

Supporting deterministic controller/API/CLI code also enforces schema validity,
tool eligibility, lifecycle, status, containment, citation shape, report safety,
cleanup, and protocol. The four-domain framing does not mean that only four
modules or four individual behaviors are deterministic. These controls must not
quietly become a forensic truth engine. They may reject malformed model output
or illegal tool calls; they may not promote a finding to `CONFIRMED` based on
handcrafted maliciousness rules.

## D-005 — Evidence classification, custody, and routing

The profiler recursively inventories regular input files and classifies them
from content signatures, filesystem structures, and memory banners—not file
extensions. It detects:

- OS: Windows, Linux, macOS, or unknown;
- shape: memory-only, disk-only, both, or an honest degraded/unknown route;
- filesystem: NTFS, APFS/HFS+, ext4/xfs, or unknown;
- size, health, symbol readiness, pre-run SHA-256, available tool families,
  and a capability label.

Disk and memory OS hints are cross-checked. A conflict is reported instead of
silently selecting a fully capable route. Evidence is mounted or accessed
strictly read-only, and generated files live outside the evidence folder.

Every discovered input is SHA-256 hashed before model-directed analysis and
re-hashed after all analysis work. Any mismatch aborts as a custody error; it
is not softened into a successful or merely incomplete finding.

The CLI constructs `RunBudget` after validating cap configuration and before it
creates the `EvidenceSession` or starts Step 0. File-set enumeration checks the
budget before traversal and at every directory/file; initial streaming hashes
check before reading and after each chunk. Content classifiers and fixed
forensic probes check it, probe subprocesses are bounded by remaining wall
time, and Linux/macOS symbol searches check each root and walked directory.
This remains cooperative deadline enforcement around individual synchronous
filesystem operations and kernel reads, which can block between checks.

Inventory never follows or silently skips symlinked evidence. A symlinked input
or descendant, a nonregular traversal entry, and any walk/stat failure close
initial discovery as invalid. The final inventory uses the same complete-set
rule; an enumeration failure there becomes a fatal custody error.

Linux/macOS memory is not made available merely because a plausible symbol file
exists. Its evidence-specific `pslist` probe must resolve successfully. A
present-but-failing table is labeled `configured-unverified`, marked
`UNAVAILABLE`, and omitted from the memory tool route while disk work continues.
Windows may use Volatility's supported automatic-symbol path: with a runtime
present, a failed `windows.info` readiness probe remains routable only as
degraded `auto-download-pending`, and the capability label explicitly says
`Windows symbol auto-download/probe pending` rather than `memory ready`. A
missing Windows runtime still makes memory unavailable. Missing or unresolved
capability is profile data, never a fabricated zero-result tool run.

Capability labels are fixed honestly as Windows **tested**, Linux
**experimental**, and macOS **best effort**, with per-run degradation noted.
These labels describe the evidence OS, not universal host support. In
particular, the current E01/NTFS mount route requires Linux or WSL, root, and
readable `/proc/self/mountinfo`, and the pinned backend's native
`ewfmount`/libewf and `ntfs-3g` helpers; it is not a native-Windows mount
implementation. The reference route deliberately requires direct root rather
than delegating this stateful backend through `sudo`.

Each allowlisted pinned method (`raw@0`, `ntfs_offsets`, or `dmpad`) runs in a
fresh fixed `[sys.executable, "-P", "-m", "unchained.evidence",
"--internal-reference-mount-worker"]` process, never in the profiler process.
It uses `shell=False`, a new POSIX session, a private scratch working directory,
a bounded JSON protocol, the remaining Step 0 wall allowance, and a minimal
environment with scratch-local home/cache/temp paths and no inherited Python
import override, OpenAI/cloud/provider credential, key/token/secret/password,
proxy, SSH-agent, or GPG-agent variable. The worker alone imports and owns
`RealProbes`; a successful worker remains live until it receives the fixed
cleanup action.

Before launch the parent records loop state and whether the run-specific
device-mapper name pre-exists. Timeout/protocol failure sends `SIGTERM` to the
worker process group, allows a bounded cleanup interval, and escalates to group
`SIGKILL`. The parent then independently cleans and verifies mounts below the
run's mount/scratch roots, the run-specific mapper name, and new loops backed by
the evidence/scratch roots while loop inventory remains knowable. `dmpad` is
refused unless the loop baseline and `losetup`/`dmsetup` controls are available.
Normal close asks the live owner to clean up, then repeats external cleanup and
verification. Unverified release preserves recovery paths and is a fatal
containment failure, including when it supersedes an already-fired cap.

This is lifecycle/resource containment, not a root sandbox. A deliberately
detached POSIX process can escape group signaling, uninterruptible kernel I/O
can outlive bounded reap attempts, and the verification scope cannot prove the
absence of arbitrary effects outside the defined run-owned mount, loop, and
mapper resources. The pinned backend/native helpers retain root network and
filesystem authority and the controls depend on Linux mountinfo plus trusted,
available `umount`, `losetup`, and `dmsetup` utilities.

Linux ext4/xfs and HFS+ direct mounts use fixed native `mount`/`umount` argv
with root or non-interactive `sudo`: respectively `ro,noload,loop`,
`ro,norecovery,loop`, and `ro,loop`, with a detected partition offset when
needed. APFS best effort uses fixed `apfs-fuse -o ro` argv. These commands run
in a new process group with a remaining-wall timeout and accept a mount only
after independent read-only verification. A rejected/capped attempt and normal
close use fixed `umount` and require the mountpoint to verify inactive; failure
is fatal. Unlike the reference worker, the direct route does not baseline
arbitrary loop/device-mapper deltas and relies on the native helper/kernel to
release ancillary state. Fixed probe/mount/cleanup subprocesses inherit needed
runtime settings only after stripping Python import overrides, provider/cloud
credentials, API-key/token/secret/password/private-key/credential variables,
proxies, and SSH/GPG agent sockets. They also force `PYTHONSAFEPATH=1`.

Fixed Sleuth Kit probes require available `fsstat`, `img_stat`, or `mmls`
binaries. Volatility 3 and the Windows Registry adapters require their declared
Python runtimes, `volatility3` and `python-registry`. The prototype exposes no
Plaso adapter and never includes Plaso in `available_tool_families`. Standalone
logs-only folders are outside the CLI investigation contract; log parsers are
used only when a supported mounted-disk route provides their artifacts. Linux
disk support is limited to the content route, best-effort read-only mount, and
fixed TSK metadata probes actually present. Linux remains experimental and
macOS remains best effort.

## D-006 — Typed tool authority and no shell

The model receives only strict OpenAI function schemas derived from registered
tools eligible for the detected OS/evidence shape. Every property is typed,
unknown properties are rejected, and evidence location plus native executable
selection remain trusted-runner state.

The model cannot provide a shell string, binary path, working directory,
environment mutation, output path, plugin identifier, pipe, redirection, or
raw CLI arguments. It receives no general shell and no internet or browsing
tool; its forensic access is read-only. Some pinned forensic functions may
internally launch native parsers with argument vectors; that does not grant
command-construction authority to the model.

Turn 0 may select at most six eligible function names. Distinctness is by name,
not argument tuple, so a second call to the same function with another PID is
rejected and receipted rather than executed. The runner reserves accepted calls
atomically, executes them concurrently, and returns all results together.
Afterward, `parallel_tool_calls=false` and the controller accepts no more than
one forensic tool call per investigator turn.

Tool denial, timeout, or failure is returned as an explicit observation and
audited; it is not rewritten as an empty successful result. If a single or
opening-batch reservation hits a cap before launch, no denied executor starts.
Every already-issued call nevertheless gets ordered `tool.started` and
`tool.completed` events, status `capped`, and a canonical error output with its
SHA-256/excerpt, so the audit has no unexplained model call.

Production Qwen metadata discovery, parser calls, and registered Sleuth Kit tool
execution use a fixed private worker rather than importing Qwen or executing
parser bodies in the parent/thread-pool process. The parent launches
`python -P -m unchained._tool_worker` with `shell=False` and an environment
stripped of Python import overrides,
OpenAI/provider/cloud credentials, API-key/token/secret/password/private-key/
credential variables, proxies, and SSH/GPG agent sockets. It forces
`PYTHONSAFEPATH=1` and sends one sealed JSON request on standard input. The
worker owns exact direct-function, Volatility-plugin, and TSK action/binary
allowlists; a module, callable import target, raw plugin path, arbitrary binary,
command, or evidence path cannot be supplied by the model. The model may select
only a logical tool name already present in its typed schema and provide that
schema's validated arguments. The remaining run-wall allowance bounds the
parent protocol read and is also passed into the worker's Qwen timeout
configuration.

For the pinned event-log parser, the worker enables its priority-preserving
return gate at 500,000 bytes. The parent independently accepts no more than one
newline-terminated 2,000,000-byte worker envelope. An oversized or unterminated
reply becomes an explicit error observation and complete tool receipt. Apart
from that event-log gate and outer protocol-envelope bound, sub-limit forensic
output is returned raw rather than summarized by deterministic code.

The worker emits one JSON response line and then deliberately waits on standard
input instead of exiting. The parent consequently retains a live, unique tree
leader and destroys the owned tree after every response as well as on timeout.
On POSIX, each child starts in its own session and the parent sends `SIGKILL` to
that process group while the leader is still alive. Windows creates a new
no-window process group and assigns the waiting worker to a
`KILL_ON_JOB_CLOSE` Job Object before sending its JSON request. Assignment
failure is fail-closed; every completion explicitly terminates and closes the
Job Object.

These controls cannot manufacture a perfect portable sandbox. They contain the
owned process lifecycle; they do not create a network, filesystem, namespace,
seccomp, or privilege sandbox. Qwen/TSK code retains the host authority of the
account running Unchained, including root authority when applicable, although
unrelated credentials are withheld from its environment. A POSIX
descendant that deliberately creates a different process group or session can
escape the original group kill, and uninterruptible kernel I/O can delay
reaping. Windows provides the stronger descendant boundary and refuses to
execute Qwen code if it cannot establish that boundary, but still depends on
the operating system's Job Object assignment, termination, and handle-close
semantics.

Step 0's deterministic Sleuth Kit probes remain separate fixed
`[binary, evidence_path]` subprocesses with `shell=False`, a new process group,
a scrubbed environment, and a remaining-wall timeout. Registered TSK functions
used by the model take the private-worker path above. Arbitrary
`ToolDefinition` executors injected by offline tests or embedding callers still
run in-process; the production CLI's `ToolRegistry.from_reference` path does not
use those fake executors.

## D-007 — Authoritative prompt and agent protocol

`src/unchained/prompts.py` is the authoritative, project-owned investigator
prompt. It gives the model typed, read-only forensic access and explicitly no
shell or internet. `agent.py` adds phase mechanics without importing any Qwen
prompt or orchestration text.

The opening request receives the detected OS, evidence shape, and only the
available function catalog/families. GPT-5.6 must choose between one and six
distinct-by-name, highest-value functions for that exact route. A second call
to the same function is a duplicate even when its arguments differ. Memory
functions stay within the detected OS namespace, while disk selection favors
execution, timeline, and persistence artifacts. If memory is marked
`UNAVAILABLE`, it is skipped; disk analysis continues when available and the
missing-or-unresolved-symbol limitation is recorded. Accepted opening functions
execute concurrently.

The iterative phase repeats PLAN → ACT with exactly one forensic function →
OBSERVE → UPDATE CASE NOTES. Factual visible notes and finding summaries cite
tool-call IDs inline in square brackets, for example `[t17]`. The prompt prefers
cross-domain memory-and-disk corroboration before confirmation, requires the
investigator to acknowledge contradictions and change course, and preserves
dead ends, limitations, and unresolved questions. Diminishing returns are the
stop criterion: the model stops when more calls no longer change its
conclusions.

Normal termination is not a control function. The investigator must return no
function call and the literal text `DONE`, with no other text. A no-call
response containing anything else, or `DONE` accompanying a function call, is
a protocol error. Once accepted, `DONE` is irreversible for that run's
investigative phase.

The controller then makes a separate, forced `submit_investigation` call to
serialize the completed notes and findings. This is protocol-only: the request
exposes the strict serialization schema and no forensic functions, so it cannot
resume tool use, collect or add evidence, or extend the investigation. The
resulting existing findings packet is passed to the fresh judge.

```text
OPENING (1..6 in parallel) -> PLAN/ONE TOOL/OBSERVE/NOTES -> literal DONE
    -> forced structured serialization -> fresh judge -> report
```

All agent instructions establish one invariant: filenames, paths, metadata,
logs, documents, parser messages, and tool output are hostile evidence data.
Instructions found inside that data cannot change system policy, caps, allowed
tools, phase rules, or verdict criteria.

## D-008 — Fresh adversarial judge

Judging is a new GPT-5.6 request with no investigator response chain. The judge
receives the case profile, the investigator's existing structured findings,
and relevant audit tool receipts including output excerpts and hashes.

For each existing finding it returns `CONFIRMED`, `NEEDS-REVIEW`, or
`UNSUPPORTED`, with rationale and cited tool-call IDs. It may downgrade or
annotate; it may not add findings or upgrade beyond the investigator's proposed
status. Controller checks enforce identity and monotonic status without making
an independent semantic judgment. Every status requires a nonblank rationale
and one or more unique citations; those IDs must exist and must be a subset of
that finding's own receipts. A `CONFIRMED` verdict must cite at least one
successful receipt. Missing or malformed verdicts are reported as incomplete,
never silently accepted.

The judge is an adversarial model pass, not an independent human examiner or a
truth oracle, and may share failure modes with the investigator.

## D-009 — Report contract

After judging, GPT-5.6 writes `report.md` from the profile, existing findings,
judge verdicts, and audit receipts. The report contains:

- investigative narrative;
- a findings table with tool-call-ID citations;
- IOC list;
- limitations and unavailable capabilities.

The limitations must state that the design has no deterministic validator. The
report cannot add findings or promote judge-downgraded claims. When a hard cap
prevents normal completion, the controller emits/preserves a visibly `PARTIAL`
report without pretending the full model phase completed.

Before a `COMPLETE` model-written report is delivered, code performs structural
reference checks and defangs active Markdown without judging forensic truth. It
escapes raw HTML angle brackets; removes inline and reference-form images;
removes inline and reference-form link targets plus reference definitions;
rewrites bare HTTP(S) text to `hxxp(s)`; and blocks `javascript:`, `data:`, and
`file:` schemes. Every controller-generated `PARTIAL`, `FATAL`, or `INVALID`
fallback independently renders hostile provider, parser, mount, cap, and
configuration diagnostics as a single inert line: control characters and
newlines are made visible, active Markdown/HTML is removed, and punctuation is
escaped. The model-written report precedes the final deterministic custody pass,
so it cannot claim final custody success; the CLI/audit records that result and
may replace the terminal status with `FATAL`. The resulting text remains
untrusted output for analyst review.

## D-010 — Audit semantics

`audit.jsonl` has one trusted application writer. Every canonical UTF-8 JSON
record includes a run ID, monotonic sequence, UTC timestamp, elapsed time,
previous-record hash, event payload, and entry hash. Events cover every model
request and normalized response, every tool start/completion and typed
argument, output SHA-256 plus its first 2 KiB, token usage, timestamps, and
running cost estimate. Cap and terminal-status events are also recorded.

The writer uses append mode, a process lock, flush/`fsync`, and end-to-end
sequence/hash verification. Calls denied by a prelaunch cap still receive a
paired start/completion receipt with deterministic `capped` output, so every
model-issued call remains accounted for. This is application-level append-only
and hash-chained. It detects many accidental or local edits but is not immutable
against an administrator able to replace the entire writable run directory;
stronger tamper evidence would require signing or an external anchor.

Runtime provider credentials and unrelated host secrets are not intentionally
included in model input or audit data. Evidence-derived content itself can
contain secrets and is deliberately sent to the model and recorded in excerpts.

## D-011 — Hard caps and cost estimate

The default hard caps are exactly:

| Cap | Default | Strict profile |
|---|---:|---:|
| `MAX_TOOL_CALLS` | 60 | 20 |
| `MAX_TOTAL_TOKENS` | 400,000 | 100,000 |
| `MAX_WALL_SECONDS` | 1,800 | 600 |
| `MAX_COST_USD` | 10.00 | 2.50 |

Only those four cap values are configurable from the environment, using each
exact name or its `UNCHAINED_`-prefixed alias. Price-like environment variables
are ignored. Tool-call reservations are atomic so the opening batch cannot race
past its allowance. Token and cost counters use observed API usage. The
code-owned GPT-5.6 Sol rates are $5.00/M uncached input, $0.50/M cached
input, $6.25/M cache-write, and $30.00/M output tokens. Cache writes therefore
cost 1.25x uncached input. A request with more than 272,000 input tokens applies
2x input and 1.5x output pricing to its full request.

Live requests disable prompt caching, so model-request preflight prices
estimated input at the ordinary uncached GPT-5.6 Sol rate. After a response,
provider-reported cached-input and cache-write usage fields remain audited and
are priced defensively if unexpectedly nonzero. These code-owned rates produce
a local safety estimate based on the published GPT-5.6 Sol rules; provider
usage and billing are authoritative, and pricing or usage-field semantics may
change.
Source:
[GPT-5.6 Sol model and pricing](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

Every live provider response must include nonnegative integer `input_tokens`,
`output_tokens`, and `total_tokens`; optional cached-input, cache-write, and
reasoning counters must also be nonnegative when present. The provider total
must equal input plus output. Missing, negative, or inconsistent usage is
audited as a usage-protocol failure and rejected before that response can
advance the investigation. In a mandatory agent phase this normally produces a
`PARTIAL` result and exit `3`, subject to the later cleanup/custody override.

Any cap firing terminates further agent work gracefully, marks the preserved
report and run `PARTIAL`, rechecks evidence custody, and normally exits `3`.
Failure to contain or release a mount, or a custody mismatch during that final
work, supersedes the earlier cap result as `FATAL`/exit `1`.

The wall cap begins before Step 0 and is checked during inventory, hashing,
classification, and symbol work. Remaining wall time bounds OpenAI requests,
fixed forensic probe/mount subprocesses, isolated reference-mount workers, and
private Qwen/TSK tool workers as described in D-005 and D-006. No new agent work
starts after it fires.

Teardown and final custody are intentionally not abandoned at the deadline.
The CLI always attempts mount cleanup in `finally`; once Step 0 produced a
complete baseline, it performs a complete fresh file-set/identity/metadata and
SHA-256 comparison without consulting the already-fired budget. Cleanup and
custody can therefore make process time exceed `MAX_WALL_SECONDS`. Mount
release failure or custody mismatch changes the terminal result to `FATAL`. If
the cap interrupts Step 0 before a baseline exists, cleanup still runs, but a
final comparison is impossible and is not fabricated.

## D-012 — OpenAI API choice

Use the OpenAI Responses API with model ID read from `UNCHAINED_MODEL` and the
credential from `OPENAI_API_KEY`. The model adapter follows the Responses
function loop: receive `function_call`, execute locally, and return
`function_call_output` with the matching call ID. Strict schemas are used.

The live adapter accepts only the `gpt-5.6` alias and GPT-5.6 Sol IDs/snapshots
whose IDs begin `gpt-5.6-sol`. Terra, Luna, and all other model families are
rejected during configuration; Sol pricing is therefore the sole built-in
pricing contract.

All requests use `store=false` and do not rely on provider-stored response
state; the API is instructed not to retain a stored Response object for later
retrieval. Investigator continuity is maintained by replaying prior user inputs
and every response output item locally. Requests include
`reasoning.encrypted_content`, and returned encrypted reasoning items are
replayed with those outputs. Opening, fresh judge, and report phases use
`reasoning.context="current_turn"`; the stable-goal investigation loop and its
post-`DONE` structured serializer use `reasoning.context="all_turns"`. The judge
remains fresh because it receives a new packet rather than the investigator
response chain.

Requests set `prompt_cache_options.mode="explicit"` and contain no explicit
cache breakpoint. Under GPT-5.6's cache rules, this disables cache reads and
writes and avoids prompt-cache storage and write charges. It does not keep
forensic content local: evidence-derived profiles and raw tool output are sent
to OpenAI for inference. Provider and organization retention, Zero Data
Retention eligibility, residency, and access controls remain external
deployment boundaries.

The tested `openai==2.31.0` `Responses.create` signature has a typed
`reasoning` parameter but no typed top-level keyword for GPT-5.6's experimental
`prompt_cache_options`. The adapter therefore supplies the latter through the
SDK-supported [`extra_body` request option](https://github.com/openai/openai-python#undocumented-request-params).
This is an SDK compatibility mechanism, not the name of an API request field:
the SDK merges the mapping into the outgoing JSON body, where
`prompt_cache_options` and `reasoning` are top-level properties. No
`extra_body` property is sent on the wire.

These state choices follow the
[GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model)
and
[prompt-caching contract](https://developers.openai.com/api/docs/guides/prompt-caching)
current at the status date above; they require review when the API changes.

Turn-0 calls allow parallel function requests; iterative and judge control
requests enforce at most one function call. Request/response IDs and mandatory
validated usage are audited. The provider URL and API secret are never made
model-controlled tool arguments.

## D-013 — Status and artifacts

Each run has an isolated writable directory at
`<working-directory>/unchained-runs/<UTC-timestamp>-<id>/`, with `report.md`,
`audit.jsonl`, and `profile.json`. If the working directory is the evidence
folder or is nested beneath it, the run-directory base moves to the evidence
folder's parent. Findings cite tool-call IDs that correspond to completed tool
events. Additional typed state artifacts may be written for recovery and
inspection, but they do not replace the required report and audit.

| Status | Exit | Meaning |
|---|---:|---|
| `COMPLETE` | 0 | Required phases completed within policy; no accuracy guarantee. |
| `FATAL` | 1 | Custody or unrecoverable runtime invariant failed. |
| `INVALID` | 2 | Input/configuration was invalid before meaningful analysis. |
| `PARTIAL` | 3 | A cap fired, or a mandatory investigator/judge/report phase could not safely complete because of a model/provider/tool protocol failure; preserved output is explicitly incomplete. |

Absent a later cleanup, containment, or custody failure, every cap produces
`PARTIAL`/exit `3`. The broader protocol case keeps usable receipts without
mislabeling an incomplete required model phase as complete. An unrecoverable
runtime failure, inability to release or verify run-owned mount resources, or a
custody mismatch supersedes an earlier partial result as `FATAL`/exit `1`.

## D-014 — Offline verification strategy

The test suite performs no network calls. Its behavioral coverage includes:

- all four cap paths, real opening overlap, distinct-by-function-name opening
  enforcement, and complete deterministic receipts for issued calls capped
  before launch;
- complete, hash-valid, ordered audit events under concurrency, literal `DONE`
  plus forced serialization, protocol-error preservation, and a fresh judge
  downgrading a deliberately unsupported finding while enforcing nonblank
  rationale and finding-scoped receipt citations for every verdict;
- mandatory nonnegative and internally consistent provider usage, plus
  code-owned price rates that price-like environment variables cannot zero;
- the real OpenAI 2.31.0 SDK over `httpx.MockTransport`, proving
  `reasoning.context` and `prompt_cache_options` survive wire serialization
  without a network call;
- cooperative, fail-closed Step 0 inventory/symbol deadlines (including symlink
  and walk-error rejection), Linux/macOS configured-but-unverified symbol
  rejection, and Windows' degraded-auto-download-pending route;
- reference-mount prelaunch deadline checks, timeout containment, fail-closed
  resource verification, fixed `-P` invocation, hostile-working-directory
  resistance, and credential-free child environments;
- private parser/TSK-worker allowlisting, credential scrubbing, event-log return
  gating, blocked-child reap, and oversized-protocol-response rejection; and
- one-line hostile-diagnostic fallback defanging plus removal of inline and
  reference links/images and dangerous schemes from complete reports.

The fake forensic executors used to prove opening parallelism are intentionally
in-process. Their behavior validates dependency injection, ordering, and cap
accounting; it is not evidence that arbitrary in-process Python functions can
be preempted. Production Qwen parser and registered TSK execution are covered by
the isolated-worker tests and boundary above.

Ruff and type hints/docstrings keep the implementation reviewable, but static
quality checks do not validate forensic truth.

## D-015 — Trust and threat boundaries

Evidence bytes, names, metadata, parser output, tool output, and all model
output are untrusted. The deterministic floor is the application's trusted
control boundary. The pinned dependency and native forensic tools remain
supply-chain/parser attack surface even though their callable interfaces are
constrained. The OpenAI API is an external service boundary. The host kernel,
administrator, hypervisor, and storage administrator are outside the
application's guarantees.

The pre/post custody pass checks the exact discovered path set plus file
identity, size, modification time, and SHA-256. It detects persistent changes,
but external tools reopen evidence by path. Any actor with concurrent
write/rename access to the evidence directory could temporarily replace an
evidence path during analysis and restore the original object and metadata
before final verification. Preventing that path-swap and restore attack requires
an externally protected evidence device/store or stronger OS-level handle
isolation and is outside this prototype's guarantee.

## D-016 — Session 1 `/feedback` ID

**Status: captured from the successful Session 1 feedback upload on
2026-07-14.**

OpenAI Build Week `/feedback` Codex Session ID:

```text
019f61e5-5755-7a02-adb4-618d32baab27
```

The upload confirmation identified this value as the thread ID. This is the
project thread where the majority of Sentinel Unchained's core functionality
was implemented, so the same exact value is the one recorded for the Devpost
submission field. Re-evaluate this fact after material later core work and run
`/feedback` near submission; the qualifying majority-core thread controls, not
the historical “Session 1” label by itself.

## D-017 — Living hackathon handover and evidence-backed status

**Status: accepted on 2026-07-14 before Prompt 3.**

`HACKATHON_HANDOVER.md` is the living source of truth for Build Week execution
state, verified rules, proof gaps, delivery gates, risks, and next-session work.
`README.md` remains the product/setup contract, and `DECISIONS.md` remains the
durable architecture contract.

Status terms are evidence-gated. `IMPLEMENTED` means code exists; `VERIFIED`
requires a dated command, inspection, test, or reproduction; `DEMONSTRATED`
requires a retained, judge-accessible artifact proving the real workflow. Code
existence or conversation prose alone cannot promote an item to complete.

Every material session must update the handover's state transitions, blockers,
evidence, delivery gate, change log, and single next action. Architecture changes
also update this file; user-facing setup/product changes also update the README.

Current live Official Rules and the logged-in submission form override cached
search results, generated plugin output, old conversations, and stale event
pages. This is necessary because search indexes can still surface the unrelated
2025 gpt-oss event for the current Devpost domain.

## D-018 — Corrected Build Week master plan and evaluation method

**Status: accepted on 2026-07-14 after the deep rules, code, strategy, dataset,
and judge-experience audit.**

`docs/HACKATHON_MASTER_PLAN.md` is the strategic plan. It owns the product
positioning, truthful scope matrices, experimental method, proof-bundle
contract, no-rebuild judge path, prompts, schedule, and submission doctrine.
`HACKATHON_HANDOVER.md` continues to own live status and evidence. The files have
different jobs and must not become competing completion ledgers.

The project is a controlled-autonomy case study and evaluation harness, not a
clean causal ablation of Sentinel Ensemble. A Qwen-versus-GPT-5.6 comparison
changes too many variables to isolate the deterministic validator. Qwen results
may appear only as labeled historical context unless a genuinely controlled
comparison is built later.

The primary measurement is within each Unchained run: investigator proposals,
fresh-context downgrade-only review, and frozen-reference adjudication against
an evidence-observable atomic-fact rubric. The adjudication is labeled
independent or project-authored according to who performs it. The fresh GPT-5.6
reviewer is not independent truth. DC01 is a public known-answer benchmark with
possible training contamination, not an unseen dataset.

The flagship is frozen to one Windows route. Linux/macOS breadth, Plaso, Qwen
reruns, generalized Docker portability, and dashboard work do not outrank the
authentic run, durable outputs, provider-returned model proof, frozen-reference
evaluation, browser viewer, video, and submission gates.

## D-019 - Winner roadmap, public experiment freeze, and two-axis evaluation

**Status: accepted on 2026-07-14 after a second deep strategy and scientific
validity audit.**

`docs/WINNER_ROADMAP.md` is the active sequencing and priority overlay above the
detailed master plan. It does not replace the handover or architecture record.

The project is publicly positioned as a trust-measurement harness for
model-directed investigators, demonstrated on DFIR. One case measures
receipt-grounded reliability under one frozen protocol; it does not establish
how much autonomous investigators in general can be trusted. The investigator
is model-directed inside deterministic authority, custody, protocol, audit, and
budget boundaries, not unsupervised.

No GPT-5.6 investigation of DC01 may occur before the complete experiment is
publicly frozen. Pre-freeze rehearsals use fake typed tools, synthetic receipts,
generic data, or an explicitly unscored case. Deterministic native tools may be
smoked directly on DC01 to prove the substrate. This order prevents DC01 model
behavior from silently tuning prompts, catalog, rubric, thresholds, metrics, or
run selection.

The freeze binds code, prompts, tool catalog, dependencies, evidence hashes,
rubric, scorer, caps, retry policy, model alias, price table, metric definitions,
infrastructure-fault criteria, and the primary-run selection rule. A public
remote commit and server-timestamped digest check provide the intended external
time anchor. A local Git timestamp alone is not called immutable or
unimpeachable.

The first post-freeze run without a predeclared infrastructure fault is the
primary result even when its semantic performance is weak. Later valid runs are
disclosed replicates. Any protocol change creates and retains a new freeze
version. A disappointing finding set, reviewer escape, or low score is not an
infrastructure fault.

Evaluation has two separate axes: factual correctness and receipt sufficiency.
Exact span occurrence and artifact hashing prove citation integrity, not
semantic entailment. Normalized deterministic matching is limited to objective
fields under frozen rules. Interpretive, relational, causal, maliciousness, and
absence claims require blinded human or explicitly project-authored reference
adjudication. Project-authored evaluation is never described as independent.

The required no-rebuild path is a hosted static viewer plus an offline viewer
or release bundle, supported by a no-network verifier. A screencast is
supplemental evidence, not a test path. Without the original evidence bytes,
the lightweight verifier validates the retained custody record and bundle
integrity rather than independently rehashing the original evidence.

## D-020 - P0 report and partition-routing hardening

**Status: implemented and verified offline on 2026-07-14.**

Model-authored Markdown is reduced to a link-free safe subset by making every
attacker-controlled square bracket inert after escaping existing ampersands and
raw HTML delimiters. This structurally disables inline, reference, nested,
escaped, and malformed Markdown links and images while preserving readable
headings, lists, emphasis, tables, and visible tool citations. Adversarial tests
render through CommonMark and reject active elements or URL-bearing attributes.

Filesystem classification now retains the exact byte offset whose fixed probe
identified the filesystem. That value is carried into the model-safe evidence
record, read-only mount decision, and trusted TSK executor. The model cannot
supply or alter it. `tsk_fsstat` is withheld when no exact matched offset is
known. When known, trusted code converts it into the sealed sector argument used
by `fsstat -o`. A partitioned APFS route is withheld when its available backend
cannot accept the classified offset rather than silently mounting offset zero.

Printable text logs are recognized before generic memory-banner scanning.
Therefore a Linux boot log containing `Linux version` remains a log and cannot
manufacture a memory artifact or a strong disk-memory OS conflict. Native
memory signatures remain higher-confidence classifications.
