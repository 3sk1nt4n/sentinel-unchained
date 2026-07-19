# OpenAI-native vNext release handoff

This is the comprehensive engineering, Docker, product, demo, benchmark, and
hackathon handoff for Sentinel Unchained's OpenAI-native vNext. It is the
canonical long-form companion to the judge-first [README](../README.md) and the
living [hackathon handover](../HACKATHON_HANDOVER.md).

## 1. Release identity and provenance

### Published vNext foundation

| Field | Value |
|---|---|
| Repository | `https://github.com/3sk1nt4n/sentinel-unchained` |
| Reviewed base | `2b256a7bfd170388d2a8497dd3289af248abae18` |
| Foundation commit | `ed4d3f540a27171c04a7321f4f85efea23d905de` |
| Commit message | `Build OpenAI-native Sentinel vNext` |
| Working branch | `agent/openai-native-vnext` |
| Default branch | `main`, fast-forwarded to the same foundation commit on 2026-07-18 |
| Publication behavior | Fast-forward only; no force-push, history rewrite, credential, evidence image, or generated case bundle |
| Foundation diff | 35 files, 9,674 insertions, 904 deletions |
| Retained successful `/feedback` ID | `019f61e5-5755-7a02-adb4-618d32baab27` |
| Current Docker/README follow-up thread | `019f76f3-a19f-71d1-81b2-eed6305857f6` — not a successful `/feedback` receipt unless submitted from this thread |

The exact foundation commit is visible at
[`ed4d3f5`](https://github.com/3sk1nt4n/sentinel-unchained/commit/ed4d3f540a27171c04a7321f4f85efea23d905de).
The default repository page now follows `main`; release-facing follow-ups must
land there so judges do not have to discover a side branch.

### Docker and user-experience follow-up

The follow-up containing this document adds:

- a judge-first README and new branded hero;
- a one-request GPT-5.6 Luna typed-tool canary;
- `OPENAI_API_KEY_FILE` support for mounted secrets;
- a multi-stage Linux/AMD64 Docker build and full test target;
- a hardened offline Compose service and opt-in live-smoke service;
- a committed non-sensitive synthetic profile fixture;
- synchronized handoff, scope, and Docker disclosure.

The controlling follow-up identity is always the Git commit containing this
document (`git rev-parse HEAD`) and the matching public `main`. Do not substitute
an uncommitted container image for a release identity.

## 2. Validation gates

### Foundation gate

The published foundation passed the following under CPython 3.11.9:

| Gate | Result |
|---|---|
| Full offline suite | 267/267 passed |
| Focused verifier/evidence/tool review | 124/124 passed |
| Ruff lint and formatting | Passed |
| Dependency integrity | `pip check` clean |
| Wheel and source distribution | Built; wheel also built from the sdist path |
| Git whitespace | Passed |
| CLI help | Passed |
| `sentinel doctor --json` without key | Expected exit `2`; no secret printed |
| Secret/private-key scan | Passed |
| Independent final P0/P1 review | No remaining release blocker found |

At that point the reviewed implementation contained 17 source modules, 32
Python files across source and tests, 13,383 physical source lines, 12,259
nonblank source lines, and 267 passing tests.

### Docker and UX follow-up gate

The current follow-up was tested on Docker Engine 29.5.3, Linux/AMD64, through
Docker Desktop/WSL2 with Compose v5.1.4:

| Gate | Result |
|---|---|
| Multi-stage `test` image | Passed |
| Linux CPython | 3.11.9 |
| Full suite inside the image | 274 tests passed |
| Ruff lint | Passed |
| Ruff format check | 49 Python files formatted |
| `pip check` | Clean |
| Minimal runtime build | Passed |
| Runtime size at pre-publication test | 129,150,798 bytes |
| Runtime user | `10001:10001`, non-root |
| Entrypoint | `/usr/bin/tini -- sentinel` |
| Runtime Git | Absent; Git is builder-only |
| Offline help | Passed and lists `smoke-openai` |
| No-key doctor | Expected exit `2`; Python/dependencies ready; no secret printed |
| Synthetic profile | `logs-only`, `E001`, zero OpenAI calls |
| Synthetic pre/post custody | Match |
| Offline service network | `network_mode: none` |
| Root filesystem/evidence | Read-only |
| Linux capabilities | All dropped |
| `no-new-privileges` | Enabled |
| Image environment/history credential scan | Passed |

No authorized `OPENAI_API_KEY` was present, so the real Luna request was not
sent. The canary's offline/mock contract is verified; its authentic provider
receipt remains pending and must not be described as complete.

Current reviewed implementation size after the follow-up: 17 source modules,
13,591 physical source lines, 12,448 nonblank source lines, 32 Python files
across source and tests, and 274 passing tests. The judge-first README is 395
lines; this canonical comprehensive handoff is intentionally longer.

## 3. Completed engineering jobs

### 1. Reviewed both starting points

The work established exact baselines for
[Sentinel Ensemble Qwen](https://github.com/3sk1nt4n/Sentinel-Ensemble-Qwen)
and Sentinel Unchained before changing architecture. The untouched Unchained
baseline passed 129 tests, Ruff, dependency checks, and package builds. The
detailed defect and design disposition is in
[OPENAI_VNEXT_REVIEW.md](OPENAI_VNEXT_REVIEW.md).

### 2. Built a deterministic evidence front door

Before any model call, code enumerates regular files, rejects unsafe discovery
conditions, hashes every input, classifies bounded content probes, derives
OS/evidence shape/filesystems/readiness/symbols/tool families, assigns stable
public IDs such as `E001`, withholds local paths from the model-visible profile,
and emits an honest capability label.

The verifier independently recalculates route shape, OS reconciliation,
filesystem values, and conflict warnings. Post-run custody rehashes the complete
set and fails closed on identity, size, timestamp, content, membership, mount
release, or digest changes.

### 3. Corrected the custody namespace

Initial and final custody now use the same public evidence-ID namespace. Every
eligible tool receives controller-owned `(evidence_id, sha256)` references, and
the verifier binds those references through request, start, execution,
completion, retained output, finding span, review citation, and report.

### 4. Made multi-image behavior honest

The current scheduler supports at most one ready memory image and one ready disk
image per case. Two same-class ready images now fail closed with a split-case
instruction rather than silently analyzing the first while implying case-wide
coverage.

### 5. Implemented the GPT-5.6 opening book

GPT-5.6 chooses one to six currently available typed tools. Code requires unique
call IDs and names, closed schemas, valid JSON, exact argument keys and JSON
types, and the route-specific allowlist. Any unknown, duplicate, malformed,
over-limit, or mistyped call rejects the whole opening; no valid-looking subset
executes.

### 6. Made the opening genuinely parallel

Code reserves all opening slots atomically and then runs the validated batch
concurrently. Regression tests prove separate calls reach a synchronization
barrier before either finishes. Reservation failure starts no executor and
forces a non-complete result.

### 7. Replaced transcript replay with stateless packets

Each adaptive turn receives a bounded packet containing the canonical profile,
visible case ledger, deterministic receipt index, budget snapshot, latest
observation IDs, and only the matching bounded observations. It does not replay
the full response transcript or opaque reasoning objects. Every nonterminal
turn supplies a visible UTF-8 ledger update capped at 8,192 bytes.

### 8. Enforced one adaptive tool per turn

After the parallel opening, each adaptive response may request at most one typed
tool. This makes each state change inspectable:

```text
PLAN -> one ACT -> OBSERVE -> visible UPDATE -> next bounded turn
```

### 9. Enforced literal `DONE`

Investigation ends only when the raw assistant message is exactly the four ASCII
characters `DONE`: no whitespace, newline, Markdown, commentary, or function
call in the same response.

### 10. Forced structured investigation serialization

After literal `DONE`, a separate mandatory structured call serializes status,
case notes, findings, proposed statuses, severity, cited tool calls, supporting
quotes, IOCs, limitations, and unresolved questions. GPT-5.6 cannot finish with
an arbitrary Markdown report.

### 11. Added exact content-addressed evidence spans

Each accepted quote becomes an evidence span containing a stable span ID, tool
call ID, full artifact SHA-256, UTF-8 byte start/end, exact text, and occurrence
count across the complete output. The verifier reopens the retained artifact,
checks its identity/digest, reads the exact bytes, compares text, recounts
occurrences, and checks the finding/tool relation. Coverage includes a valid
supporting quote after byte 3,000.

### 12. Added a fresh downgrade-only reviewer

A new GPT-5.6 request sees only verified controller state, not investigator
reasoning history. It may preserve or downgrade an existing finding. It cannot
upgrade, create IDs, cite unrelated receipts, quote outside accepted spans,
omit rationale, or silently remove its result. This is a monotonic review
lattice, not a claim of external ground truth.

### 13. Replaced free-form report authority

GPT-5.6 submits a bounded structured report draft. Deterministic code owns the
authoritative finding table, status transitions, span/tool references, IOCs,
limitations, unresolved questions, status, and safe Markdown structure.
Model-authored prose is labeled nonauthoritative.

### 14. Added exact deterministic report proof

Strict verification reconstructs `report.md` from verified profile,
investigation, spans, reviewer verdicts, and structured draft, then requires
byte-for-byte equality. Rewriting the report and recomputing manifest hashes is
not enough to pass.

### 15. Added a static proof viewer

Every finalized bundle contains deterministic `viewer.html`: no JavaScript,
external fonts/images/frames/resources, live links, or network requests;
dynamic content is escaped; a restrictive CSP is embedded. It presents
inventory, custody, findings, transitions, receipts, citations, and limitations
without a server or rebuild.

### 16. Added an independent positive viewer policy

The verifier independently rejects scripts, frames, images, objects, forms,
active media/CSS, external URLs, event handlers, unexpected elements or
attributes, altered CSP, and malformed structure. It also rerenders the viewer
from verified state and requires exact bytes.

### 17. Made `sentinel view` verification-gated

`sentinel view <bundle>` verifies before opening. A bundle claiming `COMPLETE`
automatically receives complete strict lifecycle verification even if the user
omitted strict flags.

### 18. Expanded the verifier into a protocol checker

The verifier reconstructs canonical profile/route/custody, configured caps,
exact opening and adaptive inputs, ledger, receipt index, budgets, observations,
model views, serializer/reviewer/report inputs, typed schemas/arguments,
response/request identity, phase options, output ceilings, retry eligibility and
timeouts, code-owned cost estimates, cumulative usage, lifecycle counts,
report/viewer bytes, final custody, and terminal status.

`COMPLETE` cannot contain capped or rejected receipts. Output usage cannot exceed
the paired request maximum. Retry reasons/timeouts and lifecycle counts bind the
actual audited collections.

### 19. Removed duplicate raw-response authority

Provider output items are used internally by the adapter but are not retained in
the audit as a competing proof representation. The audit authority is the
normalized message, validated function calls, model/request/response identity,
status, and normalized usage.

### 20. Added bounded, audited retry behavior

SDK implicit retries remain disabled. Controller code allows at most two
transient retries for connection/timeout failures and HTTP 408/409/429/5xx,
with audited failure, eligibility, delay, timeout, recovery, skipped, and
terminal events. A model dispatch may retry; a forensic action is never repeated
because a model dispatch retried.

### 21. Added request/output budget parity

Every provider response is audited and charged before controller use. A response
reporting output above the request's actual bounded maximum is still recorded
and charged, then rejected. Equality at the ceiling remains valid.

### 22. Added reproducible local Sol cost accounting

The proof path uses a code-owned GPT-5.6 Sol price table. The verifier recomputes
per-call and cumulative estimated cost, token counters, final model usage, and
terminal budget. Price-looking environment variables cannot zero the estimate.
The result is a deterministic cap estimate, not an OpenAI invoice.

### 23. Added explicit phase policies

| Phase | Reasoning | Verbosity | Preferred output maximum | Typed-call ceiling |
|---|---|---|---:|---:|
| Opening | Low | Low | 2,048 | 6 |
| Adaptive investigation | Medium | Low | 4,096 | 1 |
| Investigation serialization | Medium | Low | 12,288 | 1 |
| Fresh reviewer | High | Low | 12,288 | 1 |
| Report draft | Low | Medium | 8,192 | 1 |

Budget preflight may reduce output further. Requests use `store=false`, no prior
response ID, bounded current-turn inputs, implicit caching, and code-owned caps.

### 24. Hardened the private tool-worker boundary

Production reference tools run in fixed private child processes with a fixed
module entrypoint, Python safe-path mode, no shell, allowlisted operations and
executables, bounded JSON I/O, wall time, process-tree ownership, Windows Job
Object or POSIX process-group termination, credential/proxy/agent scrubbing,
path replacement, and deterministic output retention.

The complete accepted output is content-addressed. The model receives at most
65,536 UTF-8 bytes plus an explicit receipt describing complete bytes/digest,
selected prefix, rule, and truncation state.

### 25. Added a user-facing CLI and container preflight

The lifecycle is:

```text
sentinel doctor
sentinel profile <evidence> --json
sentinel smoke-openai --json
sentinel run <evidence> --caps strict
sentinel verify <bundle> --require-complete --require-live-gpt56
sentinel view <bundle>
```

Readiness is checked before evidence I/O, secrets are never printed, progress is
phase-oriented, exit codes are stable, split-case errors are actionable, and
the final CLI prints exact next commands. Docker adds an offline/no-network
profile and a separate secret-mounted Luna canary without weakening the Sol
proof path.

## 4. Architecture and authority boundary

### GPT-5.6 authority

- choose bounded investigative strategy;
- update the visible case ledger;
- choose one adaptive typed action;
- serialize proposed findings;
- perform fresh preserve-or-downgrade review;
- draft bounded nonauthoritative narrative.

### Deterministic code authority

- classify and route evidence;
- hash and recheck custody;
- expose eligible tools and schemas;
- validate names, JSON, types, references, and caps;
- execute fixed tools and retain full outputs;
- resolve exact evidence spans;
- constrain verdict transitions;
- render authoritative report/viewer;
- seal and independently verify the bundle.

### End-to-end flow

```text
evidence folder
      |
      v
PROFILE + ROUTE + INITIAL SHA-256 CUSTODY
      |
      v
GPT-5.6 OPENING BOOK: choose 1–6 typed tools
      |
      v
ALL-OR-NONE VALIDATION + PARALLEL DETERMINISTIC EXECUTION
      |
      v
STATELESS PLAN -> ACT -> OBSERVE -> VISIBLE UPDATE
      |             exactly one adaptive action
      v
RAW LITERAL DONE
      |
      v
FORCED STRUCTURED INVESTIGATION SERIALIZATION
      |
      v
FRESH GPT-5.6 DOWNGRADE-ONLY REVIEW
      |
      v
STRUCTURED REPORT DRAFT
      |
      v
DETERMINISTIC REPORT + INERT VIEWER + PROOF MANIFEST
      |
      v
FINAL SHA-256 CUSTODY + INDEPENDENT STRICT VERIFICATION
```

## 5. Comparison: baseline, Qwen Ensemble, and vNext

| Area | Reviewed Unchained baseline | Qwen Ensemble direction | OpenAI-native vNext |
|---|---|---|---|
| Primary value | Strong deterministic/native substrate | Broad forensic catalog and ensemble reference | Bounded autonomy plus independently checkable proof |
| Strategy | Adaptive model loop | Multiple model/ensemble roles | Parallel opening plus one-action stateless loop |
| Opening | Less complete proof binding | Ensemble orchestration | 1–6 all-or-none typed calls, actually concurrent |
| Context | Growing transcript/tool replay | More orchestration context | Compact stateless packets + latest observations |
| Later actions | Weaker transition binding | Broader multi-role exchange | Exactly one typed adaptive action per turn |
| Termination | Less exact boundary | Ensemble completion behavior | Raw response must equal literal `DONE` |
| Grounding | Model-supplied references | Model-centered synthesis | Code-resolved full-artifact UTF-8 spans |
| Reviewer | Weaker monotonic proof | Reviewer roles | Fresh context, preserve or downgrade only |
| Report | Free-form Markdown influential | Model-authored synthesis | Structured draft; code owns rows/citations/status |
| Custody | Initial/final namespace mismatch | Not the ensemble's central strength | Canonical public IDs from prehash through posthash |
| Tool binding | Evidence input partly out-of-band | Broad typed catalog | Every receipt binds evidence ID + initial digest |
| Large output | Legitimate netscan could exceed old ceiling | Provider delivery less explicit | Full retention + explicit bounded model-view receipt |
| Proof | Hash chain/artifacts, incomplete lifecycle binding | Not an independent proof protocol | Exact packet, receipt, span, cost, report, viewer, custody reconstruction |
| UX | Runner/developer oriented | Guided but large ensemble surface | Judge-first README + doctor/profile/run/verify/view + static viewer |
| Performance thesis | Growing context/sequential behavior | Extra ensemble calls/context | Six-way opening, stateless turns, phase budgets, implicit cache |
| Honest limitation | Needed stronger boundaries | Breadth could outrun proof | Explicitly separates consistency, authenticity, and semantic truth |

Qwen remains valuable as the commit-pinned typed forensic-tool reference and a
demonstration of breadth. vNext wins on a thinner, more legible model layer,
smaller proof surface, exact grounding, and a judge experience that can be
explained in one breath.

## 6. Why this can win

### The memorable thesis

> Sentinel turns GPT-5.6 into a bounded forensic strategist while deterministic
> code preserves evidence authority, and every completed investigation produces
> a content-addressed proof bundle that can be independently checked offline.

Do not pitch “another LLM connected to forensic tools.” Pitch the separation of
strategy from authority.

### Why judges can understand it quickly

```text
GPT-5.6 chooses what to inspect.
Code decides what is legal.
Tools produce retained evidence.
GPT-5.6 proposes conclusions.
A fresh reviewer can only preserve or reduce them.
Code renders and verifies the proof.
```

This is easier to defend than several free-form agents reviewing one another.
It also highlights what the model is **not** allowed to do.

### Why it is designed to be faster

1. Up to six high-value opening tools run concurrently.
2. There is no ensemble conversation before each forensic action.
3. Adaptive requests do not replay accumulated provider history.
4. Only current controller state and latest observations are resent.
5. Phase-specific reasoning/output policies avoid uniform over-spending.
6. Stable prefixes support implicit prompt caching.
7. Hashing, routing, validation, span resolution, report rows, and proof
   construction consume no model tokens.
8. Hard call/token/cost/wall caps prevent runaway work.

This is a performance thesis, not a measured result. “Faster than Qwen” becomes
allowed language only after the frozen same-evidence benchmark.

### Why it is more defensible

```text
finding
  -> cited tool call
  -> verified receipt
  -> content-addressed full output
  -> exact UTF-8 byte range
  -> exact quote
  -> fresh downgrade-only verdict
  -> deterministic report row
```

If a link is absent, altered, unrelated, outside retained output, or unsupported,
strict verification fails.

### Why it is friendlier

The operator needs five verbs: `doctor`, `profile`, `run`, `verify`, and `view`.
The README gives three risk/cost lanes. The judge can inspect a retained bundle
without Python, an API key, evidence, a forensic workstation, or a running
server. The static viewer presents what happened while the verifier establishes
whether the bundle is internally consistent.

### Why honest limits improve the score

The project states that it does not yet prove provider authenticity, semantic
truth, a measured Qwen win, full multi-image scheduling, privileged Docker
mount parity, external anchoring, or an authentic completed vNext case. That
restraint makes the claims that **are** checkable more credible.

## 7. Three-minute judge demo

| Time | Show | Narration |
|---:|---|---|
| 0:00–0:20 | Evidence folder | “Autonomous forensic agents are easy to demo and hard to trust. Sentinel separates strategy from evidence authority.” |
| 0:20–0:40 | `doctor` + `profile --json` | Highlight route, SHA-256, readiness, tools, capability label, and zero model calls. |
| 0:40–1:10 | Opening audit/progress | Show GPT-5.6 selecting 1–6 calls, all-or-none validation, concurrent starts, and evidence IDs instead of local paths. |
| 1:10–1:35 | One adaptive transition | Show `PLAN -> one ACT -> OBSERVE -> UPDATE` and the bounded stateless request. |
| 1:35–2:00 | Span + review | Show artifact digest, exact byte-located quote, investigator proposal, and a reviewer preserve/downgrade. A real downgrade is the strongest visual. |
| 2:00–2:30 | Strict verify | Run `--require-complete --require-live-gpt56`; explain reconstruction, not just hash checking. |
| 2:30–2:50 | Static viewer | Show inventory, custody, receipts, findings, status transitions, citations, and limitations. |
| 2:50–3:00 | Close | “GPT-5.6 decides where to look; deterministic code proves what actually happened inside the investigation.” |

Use only an authentic retained bundle. A replay is fine when visibly labeled as
a replay of that authentic bundle. Never present a synthetic fixture as the
primary evidence run.

## 8. Frozen benchmark contract

Freeze the exact code SHA, prompts, model alias/snapshot, typed schemas, eligible
tool catalog, caps, retries, prices, evidence digest, reference facts, evaluator,
metric definitions, and run-selection rule before measurement.

| Metric | Why it matters |
|---|---|
| End-to-end wall time | Direct speed result |
| Time to first useful observation | Perceived responsiveness |
| Model request count | Orchestration overhead |
| Forensic tool-call count | Investigation efficiency |
| Input and output tokens | Context/generation efficiency |
| Estimated and provider-recorded cost | Practical operating cost |
| Proposed/correct/unsupported findings | Utility and hallucination burden |
| Precision, recall, F1 | Frozen semantic quality |
| Severity correctness | Triage usefulness |
| Exact citation resolution | Evidence integrity |
| Custody result | Evidence preservation |
| Strict verifier result | Protocol correctness |
| Human review time | User friendliness |

Use multiple retained runs; report median and spread. Preserve every valid
post-freeze run and preregister any selection rule. Do not cherry-pick the
fastest or best-looking result.

The desired headline shape is:

```text
same evidence
same available forensic tools
X% fewer input tokens
Y% lower median wall time
equal or better frozen-reference F1
100% exact citation resolution
100% custody and strict-verifier pass rate
```

Do not fill in `X`, `Y`, or any semantic win until measured.

## 9. Docker and cheap-model preflight

### What the container proves now

- Linux/AMD64 CPython 3.11 packaging and dependency resolution;
- a final runtime that installs from pre-resolved wheels with no Git;
- a non-root CLI under read-only/capability-free Compose policy;
- offline help, doctor behavior, evidence profiling, public IDs, and custody;
- raw Volatility/Sleuth Kit substrate availability;
- the mocked one-request Luna typed-tool contract.

### What it does not prove

- an authentic OpenAI request (no authorized key was available);
- a complete Sol investigation lifecycle;
- Windows DC01 symbol/tool parity;
- mounted E01/FUSE/loop/device analysis;
- equivalent performance on Docker Desktop binds;
- a Linux dependency lock or pinned final base-image digest;
- external proof of the OCI revision/digest.

### Offline acceptance commands

```powershell
docker build --target test -t sentinel-unchained:test .
docker build --target runtime -t sentinel-unchained:local .
docker compose run --rm offline --help
docker compose run --rm offline profile /evidence --json
```

### Authentic cheap canary command

```powershell
$env:OPENAI_API_KEY_FILE = "C:\Secure\openai_api_key"
docker compose --profile live run --rm live-smoke
```

The canary is one Luna Responses request with a forced strict function call,
low reasoning/verbosity, 128 output tokens maximum, `store=false`, no evidence,
and no proof bundle. It must return provider model, response/request IDs, valid
usage, and the exact fixed tool arguments.

OpenAI's current model guidance says the `gpt-5.6` alias routes to Sol, Terra
offers strong performance at a lower price, and Luna targets efficient
high-volume work. The canary therefore uses Luna, while the audited forensic
run remains Sol-only because its phase options, price table, and strict proof
policy are explicitly Sol-bound. See the official
[latest-model guide](https://developers.openai.com/api/docs/guides/latest-model)
and [pricing page](https://developers.openai.com/api/docs/pricing).

### Safe container boundary

The default uses non-root UID/GID 10001, read-only root and evidence, all
capabilities dropped, `no-new-privileges`, bounded PIDs, Tini, tmpfs scratch,
no Docker socket, no host PID, and no privileged mode. Offline has no network;
live-smoke has egress by necessity. The API key is a mounted Compose secret, not
an image layer or ordinary container environment value.

Filesystem mounting is intentionally absent. Enabling loop devices, FUSE,
device mapper, or `CAP_SYS_ADMIN` would weaken the isolation story. Use raw
Sleuth Kit operations or a deliberately configured native forensic host. Never
add `--privileged` merely to make a demo pass.

## 10. Current scorecard

| Area | State |
|---|---|
| OpenAI-native architecture | Green |
| Deterministic profile/route/custody | Green offline + container profile |
| Parallel typed opening | Green offline |
| Stateless adaptive loop | Green offline |
| Literal `DONE` + forced serializer | Green offline |
| Exact evidence spans | Green offline |
| Downgrade-only reviewer | Green offline |
| Deterministic report/viewer | Green offline |
| Independent strict verifier | Green offline |
| CLI usability | Green offline |
| Python package/release checks | Green |
| Public `main` and vNext branch | Green |
| Docker test/runtime packaging | Green locally |
| Docker no-key profile/custody | Green locally |
| Authentic Luna connectivity receipt | Pending authorized key |
| Authentic completed GPT-5.6 Sol vNext run | Pending |
| Same-evidence Qwen benchmark | Pending |
| Frozen semantic accuracy score | Pending |
| Human/cross-browser authentic viewer QA | Pending |
| OS-enforced parser sandbox | Future production hardening |
| Signed/timestamped external proof anchor | Future production hardening |
| Hosted authentic artifact and submission video | Pending |

## 11. Honest limitations and forbidden claims

Do not claim any of the following yet:

- “GPT-5.6 completed the authentic case.”
- “Sentinel is faster/cheaper/more accurate than Qwen.”
- “The offline verifier authenticates OpenAI.”
- “The reviewer is independent ground truth.”
- “The local cost estimate is the provider invoice.”
- “The Docker image supports every evidence route on any OS.”
- “Read-only process policy is a complete OS sandbox.”
- “SHA-256 custody defeats privileged concurrent path replacement.”
- “A local hash chain is externally immutable or timestamped.”
- “Exact citation presence proves the forensic interpretation.”

Additional engineering limits:

1. Same-class multi-image cases fail closed instead of scheduling all images.
2. Heavy opening tools are bounded but not resource-class scheduled.
3. Per-call worker startup remains measurable overhead.
4. Docker safe mode does not mount E01/NTFS/APFS filesystems.
5. A Linux/AMD64 lock and final base-image digest remain freeze tasks.
6. Docker Desktop/OneDrive binds can distort performance.
7. Authentic viewer visual QA remains pending.

## 12. Fastest path to a credible submission

1. **Publish and freeze.** Bind code SHA, prompt bundle, Sol alias/snapshot,
   tool catalog/schemas, caps, retry policy, price table, evidence hash, scoring
   facts, run-selection rule, renderer/viewer policy, and model-view ceilings.
2. **Run the Luna canary.** Preserve its provider model, request/response IDs,
   usage, timestamp, and command. Label it nonqualifying.
3. **Run a harmless synthetic Sol lifecycle.** Exercise opening, tool call,
   adaptive turn, literal `DONE`, serializer, reviewer, report, custody, strict
   verify, and viewer before spending the primary evidence run.
4. **Run and retain the authentic frozen case.** Preserve all audit entries,
   full tool outputs, provider metadata, usage, local estimates, report, viewer,
   manifest, checksum, verifier output, and post-run custody receipt.
5. **Run the same-evidence Qwen comparison.** Match evidence, tool eligibility,
   caps, and scoring as closely as architectures allow; disclose differences.
6. **Score semantics separately.** The proof verifier cannot establish factual
   correctness. Use a frozen, disclosed evaluator for precision/recall/F1,
   severity, unsupported claims, and evidence relevance.
7. **Complete visual QA.** Chrome/Edge, Firefox, narrow width, offline, long
   hashes/paths/tables, Unicode, print, and empty states.
8. **Record the three-minute demo.** Show the authentic retained bundle and
   disclose any replay.
9. **Publish judge links.** Default `main`, judge quickstart, authentic viewer,
   checksum/verifier result, benchmark, video, and submission page.

## 13. Copy-ready winning language

### One line

> GPT-5.6 decides where to look; deterministic code proves what actually
> happened inside the investigation.

### Trust-boundary line

> The model chooses strategy. Code owns evidence, execution, caps, citations,
> custody, and the authoritative report.

### Full closing line

> Sentinel is not an LLM pretending to be evidence. It is GPT-5.6 directing a
> bounded investigation whose actions, citations, custody, and final report can
> be checked independently.

### Answer to “why not just use an ensemble?”

> More agents can create more opinions. Sentinel spends model intelligence on
> strategy and interpretation, then uses deterministic receipts and a monotonic
> fresh review to make the result smaller, faster to inspect, and harder to
> overstate.

### Answer to “does the verifier prove the finding is true?”

> No. It proves the declared controller lifecycle, tool/output binding, exact
> citation support, report/viewer reconstruction, usage, and custody within the
> local trust boundary. Semantic correctness is measured separately and remains
> a human responsibility.

## Bottom line

vNext is materially stronger than both reviewed starting points in OpenAI-native
orchestration, six-way opening concurrency, bounded stateless context, typed
execution, exact evidence grounding, monotonic review, deterministic report
authority, offline proof, CLI clarity, Docker preflight, and judge-facing UX.

The engineering can support a winning submission. The remaining difference
between an excellent prototype and a hackathon winner is retained evidence:
freeze it, run one authentic Sol lifecycle, benchmark it fairly, score it
against frozen facts, and show the verified bundle in a tight three-minute
story.
