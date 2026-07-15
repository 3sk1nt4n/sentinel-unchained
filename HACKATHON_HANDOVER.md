# Sentinel Unchained — OpenAI Build Week Living Handover

This file is the execution-status source of truth for the OpenAI Build Week
submission. It records verified rules, current proof state, delivery gates,
risks, and the next-session startup procedure.

Priority, sequence, positioning, preregistration, and go/no-go logic are in
[docs/WINNER_ROADMAP.md](docs/WINNER_ROADMAP.md). The detailed product strategy,
experiment, proof contract, prompts, judge path, and submission doctrine are in
[docs/HACKATHON_MASTER_PLAN.md](docs/HACKATHON_MASTER_PLAN.md). Architecture
details remain in [README.md](README.md), and durable technical decisions remain
in [DECISIONS.md](DECISIONS.md). Those files describe what the system is intended
to do. This handover records what is implemented, what has been verified, what
has been demonstrated to a judge, and what is still missing.

> **Update requirement:** every material implementation, verification, artifact,
> scope, schedule, or submission-status change must update this file in the same
> work session. Never mark an item complete merely because corresponding code
> exists.

## Document control

| Field | Current value |
|---|---|
| Last live-rule verification | 2026-07-14 20:20 ET, direct current 2026 Official Rules + overview + resources |
| Last repository verification | 2026-07-14 20:50 ET |
| Current event day | Submission Day 2, not Day 8 |
| Hard deadline | 2026-07-21 17:00 PT / 20:00 ET |
| Time remaining at 2026-07-14 20:50 ET | Approximately 167.2 hours |
| Internal submission deadline | 2026-07-20; July 21 is emergency buffer only |
| Selected track | Developer Tools |
| Current decision | **CONDITIONAL GO with frozen scope; registry alternative parked** |
| Flagship-run readiness | **NOT READY** |
| Submission readiness | **NOT READY** |
| Current `/feedback` Session ID | `019f61e5-5755-7a02-adb4-618d32baab27` |

### Evidence-state vocabulary

Use these terms literally:

- **IMPLEMENTED** — code exists for the behavior.
- **VERIFIED** — a current command, test, inspection, or reproduction proves the
  claimed behavior in a named environment.
- **DEMONSTRATED** — a retained, judge-accessible artifact proves the real
  workflow or product experience.
- **BLOCKED** — a named prerequisite prevents meaningful progress.
- **NOT STARTED** — no qualifying implementation or artifact exists.
- **DECISION** — a human-owned product, scope, or risk decision.

A unit test can verify a controller behavior. It does not demonstrate a genuine
GPT-5.6 forensic investigation. A replay can demonstrate judge accessibility. It
does not prove that GPT-5.6 produced the original run.

## Executive decision

Proceed conditionally with Sentinel Unchained for Build Week. Do not pivot to a
new dynamic model-registry project now. Unchained is no longer a from-scratch
concept: it is a substantial controller prototype with 6,068 physical source
lines, 80 passing tests, clean lint and formatting, a buildable wheel, and a
verified Codex feedback thread. The winner story and experiment are now
governed by the Winner Roadmap and corrected master plan: a trust-measurement
harness for model-directed investigators, not a generic autonomous analyst and
not a clean causal Qwen-versus-GPT-5.6 ablation.

This is nevertheless a hard-scope sprint. The project is not submission-ready
until it has one authentic GPT-5.6 investigation, retained proof artifacts, and
a frictionless judge path. No new breadth work outranks those gates.

The registry alternative remains parked. A failed live-run gate triggers an
explicit go/no-go review; it does not automatically authorize a late pivot. A
new product started after that gate would carry even greater delivery risk.

## Triple-verification policy

Time-sensitive and submission-critical claims must be checked in three ways
where feasible:

1. **Controlling source:** the current direct Official Rules or the relevant
   source file/API contract.
2. **Independent corroboration:** current FAQ/overview, a second code path, or an
   independent inspection.
3. **Operational evidence:** a raw uncached response, current command/test, or
   retained artifact.

For code behavior, prefer the sequence:

```text
source inspection -> focused reproduction/test -> retained artifact or integration run
```

For event rules, prefer:

```text
direct live Official Rules -> current FAQ/overview -> uncached/raw page check
```

Search snippets, old conversations, generated package metadata, and AI summaries
are leads, not controlling evidence.

## Verified 2026 Build Week rules

### Controlling sources

- [OpenAI Build Week landing page](https://openai.com/build-week/)
- [Live Devpost overview](https://openai.devpost.com/)
- [Live Devpost Official Rules](https://openai.devpost.com/rules)
- [Live Devpost FAQ](https://openai.devpost.com/details/faqs)

The direct rules page was fetched without relying on a search cache on July 14,
2026. Its response identified OpenAI Build Week, Codex, GPT-5.6, the four current
tracks, and the July 2026 dates. It contained no `gpt-oss` event text.

### Stale-page warning

Search indexes can still return an ended 2025 OpenAI Open Model Hackathon
snapshot for the same Devpost domain. That unrelated event used gpt-oss and the
categories Best Overall, Robotics, Weirdest Hardware, Local Agent, Fine-Tune,
Wildcard, and For Humanity. Those are not the 2026 Build Week tracks.

When rechecking rules, open the current page directly. Do not accept a search
snippet whose dates are August–September 2025 or whose model requirement is
gpt-oss.

### Dates

The current Official Rules specify:

- Registration: July 9, 2026 at 10:00 PT through July 21 at 17:00 PT.
- Submission: July 13, 2026 at 09:00 PT through July 21 at 17:00 PT.
- Hard deadline: July 21, 2026 at 17:00 PT / 20:00 ET.
- Judging under the Official Rules: July 22 at 10:00 PT through August 5 at
  17:00 PT.
- Winners: on or around August 12, 2026.

The OpenAI landing page reportedly shows judging through August 7, while the
contract-style rules show August 5. Treat the Official Rules as controlling and
keep the repository, video, viewer, test path, and artifacts available through
at least August 12, covering both dates and the winner announcement.

### Tracks

The four current tracks are:

1. Apps for Your Life.
2. Work and Productivity.
3. **Developer Tools.**
4. Education.

Developer Tools explicitly includes testing, DevOps, agentic workflows, and
security. Sentinel Unchained fits that track. The live rules list a $15,000
first-place and $10,000 second-place prize for Developer Tools.

Do not select a track from an old gpt-oss page. Verify the selected track again
in the live submission form before final submission.

### New and existing projects

The current rule requires a pre-existing project to be meaningfully extended
with Codex and/or GPT-5.6 after the submission period began. It also states:

> “Pre-existing Projects will be evaluated only on work added during the
> Submission Period.”

Entrants must clearly distinguish prior and new work with timestamped Codex
logs, dated commit history, or equivalent evidence.

Although the extension sentence uses “and/or,” the overall project requirements
expect meaningful use of both Codex and GPT-5.6. The submission must demonstrate
both.

### Required submission materials

- A working project built with Codex and GPT-5.6.
- One selected track for this project.
- A product description explaining features and operation.
- A public YouTube demo that is less than three minutes.
- Clear audio explaining what was built and how Codex and GPT-5.6 were used.
- A repository URL for judging and testing.
- A public repository with relevant licensing, or a private repository shared
  with both `testing@devpost.com` and `build-week-event@openai.com`.
- README setup, run/test guidance, supported platforms, and sample data or a
  sample-data path where required.
- README disclosure of Codex collaboration, acceleration, and human-owned
  product/engineering/design decisions.
- A `/feedback` Codex Session ID from the primary thread where most core
  functionality was built.
- For Plugins and Developer Tools: installation instructions, supported
  platforms, and a judge path that does not require rebuilding from scratch.

The project/test path must remain free and unrestricted through judging. Judges
are not required to install or test it; they may judge only from the description,
images, and video. Therefore the video and instant viewer are load-bearing, not
optional polish.

### Video interpretation

The Official Rules say **less than three minutes**. The FAQ says three minutes or
under. Use the stricter controlling language and target 2:40–2:50, never exactly
3:00. Include voiceover, English or an English translation, and a visible working
product. Explain both the Codex build workflow and GPT-5.6's runtime role.

### Judging

Stage One is pass/fail for viability, theme fit, and reasonable use of the
required APIs/SDKs.

Stage Two has four equally weighted criteria:

1. Technological Implementation.
2. Design.
3. Potential Impact.
4. Quality of the Idea.

Treat each as effectively one quarter of the score. Additional backend depth
cannot compensate for a missing coherent judge experience or missing impact
proof.

### Multiple submissions

The rules allow one entrant to submit multiple projects only when each is unique
and substantially different, as determined by OpenAI and Devpost. Each project
enters one track and can win at most one prize.

The current strategy remains one polished Build Week Sentinel entry. That is a
delivery decision, not a false claim that multiple submissions are prohibited.

## Product positioning

### Winning thesis

> **Unchained reasoning. Chained evidence.**

> GPT-5.6 drives the investigation; deterministic code chains every action to
> typed authority, evidence custody, protocol, hard budgets, and a verifiable
> receipt. A fresh review can preserve or downgrade findings, never add or
> upgrade them, and the human analyst retains final authority.

### Relationship to Sentinel Ensemble

Sentinel Ensemble is the production-oriented deterministic trust architecture.
Sentinel Unchained is a controlled GPT-5.6 autonomy experiment built on a pinned,
pre-existing forensic foundation. It asks how much adaptive semantic agency can
be admitted safely when deterministic code retains custody, typed authority,
protocol enforcement, audit receipts, and resource limits.

Unchained is a complementary controlled-autonomy case study, not a repudiation
of Ensemble's “code gets the final word” philosophy. It omits the deterministic
**semantic** validator and measures what happens in a reproducible model-directed
case. Because the model, prompts, orchestration, tool policy, and review system
also differ from Qwen, this is not presented as a one-variable causal ablation.
It does not remove deterministic operational controls, and neither the
investigator nor its fresh reviewer is treated as ground truth. Published
support metrics come from a frozen evidence-observable rubric whose
adjudication authorship must be disclosed.

### Prior-work boundary

Pinned prior-project commit:

```text
9f309c6134e857f7b86f3e6b9c6709ce954944a5
```

Pre-existing foundation reused:

- Evidence mounting support.
- Typed forensic tool functions.
- Low-level parsing/tool adapters permitted by the pinned dependency boundary.

Not reused as Unchained proof or orchestration:

- Qwen pipeline or coordinator.
- Deterministic semantic validator.
- Prior prompts.
- Prior report layer.
- Generic command-execution interface.
- Prior demo video, findings, runtime, cost, or accuracy numbers.

Build Week additions to prove with dated Codex logs and commits:

- GPT-5.6 investigator prompt and adaptive loop.
- Responses API state behavior.
- Opening-book concurrency and one-tool investigation protocol.
- Literal `DONE` plus forced structured serialization.
- Fresh, downgrade-only judge.
- Audit chain and receipt handling.
- Tool/token/time/cost caps.
- Report safety and terminal-status behavior.
- CLI lifecycle/containment additions.
- The genuine run, judge viewer/replay, README story, and demo video.

The pre-existing engine is credibility, not something to hide. The submission
must still make the newly evaluated Build Week layer unmistakable.

## Nine non-negotiables carried into Prompt 3

Prompt 3 and every later major prompt must preserve these constraints.

### 1. Use only the current 2026 event rules

Developer Tools is the selected track. Never substitute the 2025 gpt-oss
categories or their older pre-existing-project language.

### 2. Respect the real clock and freeze scope

The event is on Submission Day 2 with approximately 169 hours remaining at this
baseline. The urgency is real even though “Day 8 of 9” was false. Do not add
macOS breadth, Plaso, a large web application, or unrelated product features.

### 3. Separate prior work from judged Build Week work

Create honest dated Git history now. Never backdate. Preserve the pinned prior
commit and document exact reused/new boundaries. Judges evaluate submission-
period additions only.

### 4. Preserve the research-ablation framing

Unchained explores controlled model agency; it does not claim Ensemble's
deterministic-trust philosophy was wrong. Use “fully agentic” only when qualified
as semantic reasoning and typed-tool selection inside deterministic authority,
custody, protocol, and budget controls.

### 5. Require one authentic GPT-5.6 run

No fake-model test, replay, screenshot, or architecture diagram substitutes for
one genuine GPT-5.6 investigation. The flagship must retain `report.md`,
`profile.json`, `audit.jsonl`, complete tool outputs, a manifest, metrics, and a
final custody result.

Do not let GPT-5.6 investigate the scored DC01 case before the code, prompts,
catalog, caps, retries, rubric, scoring rules, fault criteria, and run-selection
rule are publicly frozen and independently server-timestamped. Pre-freeze model
rehearsals use fake tools, synthetic receipts, generic data, or another
explicitly unscored case. Deterministic DC01 native-tool smoke is allowed.

### 6. Keep proof and replay visibly distinct

The authentic run proves GPT-5.6 participation. The no-key replay/static viewer
provides accessibility. Label replay artifacts as replay/verification, never as
a fresh model run.

### 7. Pass the correctness and environment gate before filming

Fix the three reproduced defects, preserve full tool outputs, pin dependencies,
and demonstrate a clean Python 3.11 supported environment with the required
native route. Do not film or publish measured claims from the incomplete active
environment.

### 8. Optimize for the judge's experience

The judge must understand the promise in 20 seconds, experience the product in
under five minutes without rebuilding a forensic lab, and trace one finding to
its receipt and hash. Design and Impact are equal-weight criteria.

### 9. Maintain submission and feedback discipline

Use one polished Build Week entry, a 2:40–2:50 narrated public YouTube video,
incognito link checks, saved submission confirmation, and the successful
`/feedback` ID from the majority-core thread. Change the current ID only when a
later successful upload from the true primary thread returns a different ID.

## Codebase map

The runtime flow is:

```text
CLI / budget
    -> evidence inventory, classification, routing, and pre-run hashes
    -> typed tool registry and bounded private workers
    -> GPT-5.6 opening selection and adaptive investigator loop
    -> literal DONE and structured investigation serialization
    -> fresh downgrade-only judge
    -> report generation and defanging
    -> cleanup and deterministic post-run custody verification
    -> report.md + audit.jsonl + profile.json
```

| Module | Responsibility |
|---|---|
| `src/unchained/cli.py` | Configuration, run directory, lifecycle, statuses, cleanup, final custody |
| `src/unchained/evidence.py` | Inventory, content classification, OS/shape routing, hashes, mounts, readiness probes |
| `src/unchained/tools.py` | Typed tool schemas, allowlisting, caps, execution, receipts |
| `src/unchained/_tool_worker.py` | Fixed private-worker dispatch for approved forensic functions |
| `src/unchained/model.py` | OpenAI Responses adapter, state replay, wire options, usage validation |
| `src/unchained/agent.py` | Opening book, investigator loop, serialization, judge, report safety |
| `src/unchained/audit.py` | Single-writer hash-chained event log and output receipts |
| `src/unchained/caps.py` | Atomic tool/token/time/cost enforcement and cost estimates |
| `src/unchained/models.py` | Typed domain records and schemas |
| `src/unchained/prompts.py` | Project-owned authoritative investigator prompt |
| `src/unchained/__main__.py` | Module CLI entry point |

## Current implementation and proof ledger

Verified on July 14, 2026 unless otherwise stated.

| Capability or artifact | State | Evidence | Next proof/action |
|---|---|---|---|
| Python package | IMPLEMENTED + VERIFIED | Wheel built successfully in a temporary copy | Retain clean Python 3.11 install transcript |
| CLI/controller | IMPLEMENTED + VERIFIED offline | 80 tests pass | Genuine run artifact |
| Opening parallel tools | IMPLEMENTED + VERIFIED offline | Controller tests | Authentic audit trace |
| Literal `DONE` protocol | IMPLEMENTED + VERIFIED offline | Controller tests | Authentic trace |
| Typed/no-shell authority | IMPLEMENTED + VERIFIED offline | Schema and worker tests | Native forensic demo |
| Evidence inventory/custody | IMPLEMENTED + VERIFIED offline | Synthetic tests | Public profile + custody manifest |
| Hard caps | IMPLEMENTED + VERIFIED offline | Cap tests | Recorded `PARTIAL` demo |
| Downgrade-only judge | IMPLEMENTED + VERIFIED offline | Simulated `CONFIRMED -> UNSUPPORTED` test | Authentic model example |
| Hash-chained audit | IMPLEMENTED + VERIFIED offline | Audit tests | Genuine retained audit |
| Provider-returned model identity | NOT IMPLEMENTED | Adapter retains configured model, response/request IDs, status, and usage, but not `response.model` | Add provider model/snapshot to response, audit, and manifest |
| Report safety | IMPLEMENTED + VERIFIED offline | Fail-closed link-free safe subset; six focused rendered CommonMark tests; adversarial bypass inert | Authentic report artifact and viewer-safe rendering |
| Windows route | SUBSTANTIAL, NOT DEMONSTRATED | Controller/synthetic coverage | Clean native end-to-end run |
| Linux/macOS routes | PARTIAL/EXPERIMENTAL | No end-to-end proof | Out of flagship scope |
| Full tool-output retention | NOT IMPLEMENTED | Only hash + first 2 KiB retained | Content-addressed output artifacts |
| Public run bundle | NOT STARTED | No run artifacts found | Authentic GPT-5.6 run |
| Corrected strategic master plan | VERIFIED + SAVED | `docs/HACKATHON_MASTER_PLAN.md`; rules/code/strategy/dataset audits | Keep synchronized when strategy or requirements change |
| Winner priority and sequencing overlay | VERIFIED + SAVED | `docs/WINNER_ROADMAP.md`; benchmark-leakage, adjudication, provenance, viewer, and C0-C7 red-team audit | Follow order; no GPT-5.6 DC01 call before public freeze |
| Static judge viewer | NOT STARTED | Strategy document exists; no viewer implementation or hosted path | Generate from real run |
| No-key replay | NOT STARTED | No replay artifact | Prebuilt verifier/demo |
| Git provenance | IMPLEMENTED LOCALLY, NOT PUBLICLY ANCHORED | Local `main` repository initialized without backdating; no remote | Commit baseline, secret/evidence rescan, then publish/share |
| Build provenance document | IMPLEMENTED | `BUILD_PROVENANCE.md` records prior/new/Codex boundaries and local-timestamp limitation | Record baseline hash and public/freeze URLs when they exist |
| Public experiment preregistration | NOT STARTED | Protocol/rubric/scorer are not yet frozen or remotely timestamped | Complete after C2/C3 and before any GPT-5.6 DC01 call |
| Judge quickstart | NOT STARTED | No `JUDGE-QUICKSTART.md` | Write after replay path exists |
| Demo video | NOT STARTED | No current-project video | Record only after genuine run |
| Devpost submission | NOT STARTED | No confirmation artifact | Draft early; submit July 20 |
| `/feedback` proof | VERIFIED + RETAINED LOCALLY | ID in README/DECISIONS + screenshot | Clean crop; rerun only after material primary-thread work |

### Verified size and quality baseline

- 12 source modules.
- 6,068 physical source lines.
- 7 test modules plus `conftest.py`.
- 2,509 physical test lines excluding `conftest.py`; 2,528 including it.
- 80 tests collected and passing in 1.39 seconds.
- Ruff check and format check: all files pass.
- Branch-enabled line coverage: 54% overall.
- Stronger coverage: `models.py` 97%, `caps.py` 92%, `agent.py` 80%.
- Weak production-path coverage: `tools.py` 56%, `evidence.py` 42%, `cli.py`
  21%, `_tool_worker.py` 11%.

Coverage is diagnostic, not a contest metric. Prioritize real CLI/native
integration coverage rather than chasing an arbitrary percentage.

### Current environment

| Item | Current verified state |
|---|---|
| Active Python | 3.14.3 at `C:\Python314\python.exe` |
| Intended clean proof environment | Python 3.11, not yet demonstrated |
| `openai` in active environment | 2.31.0 |
| Active-environment `pip check` | Fails: `sift-sentinel`, `tiktoken`, and `volatility3` missing |
| API credential in current process | `OPENAI_API_KEY` absent; value was never printed |
| Native Windows forensic commands | `fsstat`, `img_stat`, `mmls`, `ewfmount`, `ntfs-3g`, `vol` absent |
| WSL | Ubuntu on WSL2 available; Python 3.12.3 |
| WSL forensic commands | `fsstat`, `img_stat`, `mmls`, and `vol.py` available |
| WSL mount requirements | `ewfmount` and `ntfs-3g` absent |
| Docker command | Present through Rancher Desktop; daemon route not yet verified |
| Evidence candidates in workspace | None found under common forensic extensions |
| Git repository | Local `main` initialized; no commit or remote yet at this checkpoint |

Tests passing in this environment does not mean the live native route is ready.

## Open correctness and proof blockers

### P0-1 - RESOLVED offline: report Markdown is link-free after rendering

The original bypass was:

```markdown
![a\]](//attacker.invalid/pixel)
```

The sanitizer now escapes existing ampersands and raw HTML delimiters, defangs
network/scheme/autolink forms, and makes every attacker-controlled square
bracket Markdown-inert. This disables every link/image form structurally while
preserving readable headings, lists, emphasis, tables, and visible citations.

Verification: six focused tests render adversarial input through CommonMark and
reject active tags, URL-bearing attributes, raw HTML, dangerous schemes,
protocol-relative targets, encoded delimiters, nested/malformed forms, and the
exact bypass. The full 80-test suite passes. Authentic report output and the
future viewer remain separate demonstration gates.

### P0-2 - RESOLVED offline: exact filesystem offset is sealed end to end

Classification now retains the exact byte offset whose filesystem probe
succeeded. The value propagates through `EvidenceItem`, the mount decision, and
trusted TSK execution. The model cannot supply or change it. `tsk_fsstat` is
withheld when the exact offset is unknown; otherwise trusted code seals the
derived sector into `fsstat -o`. Partitioned APFS is withheld when its available
backend cannot accept the offset.

Verification includes a two-partition fixture whose filesystem exists only on
the second partition, exact later-TSK-match propagation, mount-option proof,
sealed worker argv proof, raw offset zero, and unknown-offset withholding. The
focused evidence/tool suite passes 34 tests and the full suite passes 80.

### P0-3 - RESOLVED offline: text log cannot become memory from a banner

Printable text/log recognition now runs before generic memory-banner scanning,
while native crash-dump and LiME signatures retain priority. A Linux boot log
containing `Linux version` remains a log and cannot manufacture a memory
artifact or a strong disk-memory OS conflict.

Verification includes the boot-log fixture and a Windows disk paired with the
Linux text log. Both focused and full suites pass.

### P0-4 — Full tool outputs are not durable

`audit.jsonl` retains the full-output SHA-256 and first 2 KiB, not the complete
bytes. A later analyst cannot independently inspect or rehash discarded bytes,
and the judge can miss facts after the excerpt.

Persist content-addressed full outputs with relative path, bytes, content type,
encoding, and SHA-256. If not fixed, narrow every public claim to “hash-committed
receipts with bounded excerpts.”

### P0-5 — Authoritative prompt says Windows only

`src/unchained/prompts.py` says the investigator works exclusively over Windows
evidence while the public docs claim Linux/macOS routes. For the flagship,
freeze scope to Windows and make that explicit. Generalize the prompt only if
non-Windows behavior is truly supported and tested.

### P0-6 — Provider retries are disabled

`src/unchained/model.py` constructs the OpenAI client with `max_retries=0`.
Implement a small audited transient-retry policy that respects wall/cost caps,
does not retry protocol errors, and cannot duplicate tool execution.

### P0-7 — Reproducibility is not locked

The package allows a broad OpenAI 2.x range, while the active environment uses
2.31.0 and another clean install can resolve a later version. Pin the exact live-
run SDK/dependencies and retain a lock or constraints file plus the Python 3.11
CI/install result.

### P0-8 — Provider-returned model identity is not retained

`src/unchained/model.py` validates and records the configured model alias, and
retains response ID, request ID, status, and usage. The normalized
`ModelResponse` does not capture the provider-returned `response.model` field,
so an authentic bundle cannot show both the requested alias and the resolved
provider model/snapshot.

Capture the provider-returned model identity for every response without logging
the API key. Preserve it in `audit.jsonl`, `summary.json`, and `manifest.json`
alongside requested model, phase, response ID, request ID, status, usage,
timestamp, and local cost estimate.

Acceptance criterion: a mocked SDK response proves wire-to-model-to-audit
propagation, and the first authentic run retains both requested and
provider-returned model identities for every model phase.

## Flagship-run acceptance gate

The flagship is accepted only when every applicable item below is evidenced.

### Before execution

- [ ] The eight P0 implementation blockers above are fixed or explicitly narrowed
  without overstated claims.
- [ ] Python 3.11 clean environment exists.
- [ ] `python -m pip check` passes.
- [ ] All tests and Ruff pass.
- [ ] The package builds and installs from the exact submission source.
- [ ] The real typed forensic catalog imports.
- [ ] Required native tools for the selected evidence shape pass smoke tests.
- [ ] The public/licensed evidence case and known facts are documented.
- [ ] Evidence SHA-256 and acquisition source are recorded.
- [ ] `OPENAI_API_KEY` is configured outside the repository and never logged.
- [ ] `UNCHAINED_MODEL=gpt-5.6` is explicit.
- [ ] Default/strict caps and maximum expected spend are approved.

### During execution

- [ ] The provider is authentic GPT-5.6, not a fake harness; requested alias and
      provider-returned model/snapshot are both retained.
- [ ] Step 0 produces an honest profile and capability label.
- [ ] Pre-run custody hashes are recorded.
- [ ] Typed tools run without model-selected shell/path/binary authority.
- [ ] Model/tool events and provider request IDs are retained safely.
- [ ] Usage, cost, runtime, and tool status are measured.
- [ ] The investigator terminates through the literal `DONE` protocol.
- [ ] Structured findings are produced.
- [ ] The fresh judge completes with monotonic verdicts.
- [ ] Final report completes.
- [ ] Cleanup succeeds.
- [ ] Post-run custody matches.
- [ ] Terminal status is `COMPLETE` with exit 0.

### Retained proof bundle

```text
examples/public-run/
  report.md
  profile.json
  audit.jsonl
  summary.json
  manifest.json
  tool-outputs/
    <tool-call-id>-<sha256>.*
  viewer/
    index.html
```

The manifest must identify model, request IDs where safe, timestamps, evidence
hash, artifact hashes, exact dependency versions, host/evidence support tuple,
caps, terminal status, and custody result.

### Evaluation against known facts

- [ ] Known facts found.
- [ ] Known facts missed.
- [ ] Unsupported or false claims.
- [ ] Investigator course corrections.
- [ ] Proposed versus final judge statuses.
- [ ] Repeated-run variance if budget permits.
- [ ] Runtime, tokens, provider/local cost estimate, and tool success/failure.

A `PARTIAL` run is useful as a secondary safety demonstration but cannot be the
flagship proof.

## Two-layer judge experience

### Layer 1 — Authentic proof

One genuine GPT-5.6 public-evidence run with complete artifacts proves the model
actually performed the investigation.

### Layer 2 — Frictionless access

Provide a no-key, no-rebuild static viewer and/or prebuilt verifier that lets a
judge inspect the genuine run. It should:

- Verify the audit chain.
- Verify retained tool-output hashes.
- Show investigator versus judge status changes.
- Open finding-scoped receipts.
- Show final custody.
- Require no API key, evidence download, compilation, or native tool install.

Every replay surface must visibly say:

```text
Verification/replay of a retained genuine GPT-5.6 run.
This path does not perform a new model call.
```

The fake-model harness remains useful for deterministic controller testing. It
must never be presented as GPT-5.6 evidence.

## Go/no-go gates

### Gate A - Correctness, proof structure, and environment

Target: July 15, 20:00 ET.

Pass when:

- all three reproduced correctness fixes and regressions pass;
- full-output proof structure and provider-returned identity are substantially
  working;
- honest Git/provenance baseline exists;
- clean Python 3.11 passes install, `pip check`, tests, lint, build, and catalog
  smoke;
- at least one existing native memory function returns real rows without
  GPT-5.6.

If Gate A fails, remove all nonessential feature work and narrow the live route
to Windows memory-only. Do not add a new Volatility adapter unless the existing
reviewed route is first reproduced as incapable of that flagship.

### Gate B - Public experiment freeze

Target: before the first GPT-5.6 investigation of DC01.

Pass when the rubric, two-axis scoring specification, metrics, denominators,
fault criteria, first-valid-run rule, code, prompts, catalog, dependencies,
caps, retries, price table, evidence hashes, and scorer are frozen by digest in
a public commit and tag with server-timestamped verification.

No GPT-5.6 DC01 model rehearsal is allowed before this gate. Deterministic
native-tool smoke remains allowed.

### Gate C - Authentic primary run

Target: July 17, 18:00 ET.

Pass when the first valid post-freeze GPT-5.6 run is `COMPLETE`, retained,
bundle-verified, custody-record-clean, and evaluated for factual correctness and
receipt sufficiency under the frozen rules.

If Gate C fails, stop viewer polish and diagnose only the blocking live path.
Consider a smaller public memory-only route when technically honest. Do not
substitute a fake replay for proof. Convene an explicit go/no-go review before
spending more time or attempting any alternative project.

### Gate D - Judge path

Target: July 18, 20:00 ET.

Pass when an anonymous judge can understand the project in 20 seconds and verify
the genuine run in under five minutes without rebuilding through a hosted
viewer, offline viewer/release bundle, and no-network verifier. A screencast is
supplemental evidence only.

### Gate E - Submission freeze

Target: July 20.

Pass when the public video, repository, viewer/test path, Devpost fields, metrics,
links, licensing, feedback ID, and confirmation checklist are complete.

## Delivery schedule

### July 14 — Baseline, rules, provenance, scope

- [x] Recover the primary Codex session.
- [x] Verify the successful `/feedback` ID and screenshot.
- [x] Resolve 2026 Build Week versus 2025 gpt-oss rule conflict.
- [x] Save and link this living handover.
- [x] Fix the three reproduced correctness/security defects.
- [ ] Design/implement full-output retention.
- [x] Freeze product scope to a Windows flagship with memory-only fallback.
- [x] Initialize local Git honestly; baseline commit still pending.
- [x] Create `BUILD_PROVENANCE.md`.

### July 15 — Clean supported path

- [x] Add and pass P0 adversarial regression tests.
- [ ] Pin dependencies/constraints.
- [ ] Establish Python 3.11 under the chosen Linux/WSL/container host.
- [ ] Install required native tools.
- [ ] Pass `pip check`, tests, Ruff, wheel/install, and real catalog smoke.
- [ ] Add CI for the clean path.
- [ ] Select public evidence and record known facts/hash/source/license.

### July 16 - Native proof and public experiment freeze

- [ ] Complete proof artifacts and clean Python 3.11 native smoke.
- [ ] Build the evidence-observable rubric and two-axis scoring specification.
- [ ] Freeze code, prompts, catalog, caps, retries, dependencies, price table,
  metrics, infrastructure faults, and primary-run selection.
- [ ] Push and tag the freeze; retain server-timestamped digest verification.
- [ ] Do not run GPT-5.6 on DC01 until this freeze passes.

### July 17 - Authentic primary and live-run gate

- [ ] Run the first valid post-freeze GPT-5.6 DC01 investigation as primary.
- [ ] Verify the proof bundle, audit, cleanup, and retained custody record.
- [ ] Evaluate factual correctness and receipt sufficiency under frozen rules.
- [ ] Repeat once if budget and stability permit.
- [ ] Capture one genuine course correction or judge downgrade.
- [ ] Capture one separate cap or custody-failure safety demonstration.
- [ ] Pass Gate C by 18:00 ET.

### July 18 — Judge experience and story

- [ ] Publish the hosted HTTPS receipt/custody viewer.
- [ ] Publish the offline viewer/release bundle and no-network verifier.
- [ ] Write `JUDGE-QUICKSTART.md`.
- [ ] Rewrite the README hero around outcome, proof, measured results, and the
  instant demo.
- [ ] Add architecture and support matrix.
- [ ] Draft Devpost copy and video storyboard.

### July 19 — Video and independent QA

- [ ] Record a narrated 2:40–2:50 demo.
- [ ] Add captions and readable text.
- [ ] Upload publicly to YouTube.
- [ ] Test from a clean environment and an incognito browser.
- [ ] Have one technical and one nontechnical reviewer watch without coaching.
- [ ] Verify every public metric against retained artifacts.

### July 20 — Freeze and submit

- [ ] Run final tests, lint, install/build, verifier, and link checks.
- [ ] Run final `/feedback` in the true primary build thread.
- [ ] Update the ID only if the successful upload returns a different value.
- [ ] Tag the final commit.
- [ ] Complete the Devpost form.
- [ ] Confirm the video is public, narrated, and under three minutes.
- [ ] Check every URL anonymously on desktop and mobile.
- [ ] Submit and save confirmation screenshots/email.
- [ ] Keep all judge assets stable through at least August 12.

### July 21 — Emergency buffer only

No planned scope. Use only for submission-blocking recovery before 20:00 ET.

## Three-minute demo contract

Target runtime: 2:40–2:50.

| Time | Scene | Proof |
|---|---|---|
| 0:00–0:18 | The analyst problem | Captured memory/disk; alert is not an investigation |
| 0:18–0:35 | Promise + architecture | “Unchained reasoning. Chained evidence.” |
| 0:35–0:58 | Deterministic preflight | Real profile, content detection, capabilities, evidence hash |
| 0:58–1:20 | Agentic opening | GPT-5.6 selects typed tools; no shell/path/binary authority |
| 1:20–1:48 | Course correction | Contradictory/insufficient artifact changes the investigation |
| 1:48–2:10 | Signature moment | Investigator status versus fresh judge downgrade |
| 2:10–2:32 | Receipt drill-down | Typed args, full output, hash, audit chain, custody |
| 2:32–2:48 | Measured result | COMPLETE, runtime, cost, tools, findings, downgrades, custody |

Do not show hidden chain-of-thought. Show observable plans, actions, receipts,
status changes, and measured outcomes.

## Submission readiness checklist

### Repository and provenance

- [x] Local Git repository initialized without backdating.
- [ ] Remote published or private access shared with both required addresses.
- [ ] License present and dependency licenses checked.
- [x] Prior/new work boundary documented.
- [x] `BUILD_PROVENANCE.md` created; append public/freeze/run links later.
- [ ] Public experiment freeze and server-timestamped digest proof exist.
- [ ] Submission tag created.

### Product and proof

- [ ] Authentic GPT-5.6 `COMPLETE` run.
- [ ] Public/licensed evidence source and hash.
- [ ] Complete retained artifacts and outputs.
- [ ] Frozen two-axis evaluation and measured scoreboard.
- [ ] Hosted and offline viewer plus no-network no-rebuild path.
- [ ] Support matrix distinguishes evidence OS from host OS.

### README and Devpost

- [ ] Outcome-first hero and tagline.
- [ ] Video and instant-demo links above the fold.
- [ ] Installation and supported platforms.
- [ ] Sample-data/public-run instructions.
- [ ] Codex collaboration and human-owned decisions.
- [ ] GPT-5.6 runtime role.
- [ ] Prior/new work disclosure.
- [ ] Honest limitations and data boundary.
- [ ] Developer Tools selected in the live form.
- [ ] `/feedback` Session ID exact.

### Video and access

- [ ] 2:40–2:50 runtime.
- [ ] Public YouTube visibility.
- [ ] Clear voiceover and captions.
- [ ] Working product visible.
- [ ] Codex build workflow explained.
- [ ] GPT-5.6 role explained.
- [ ] No unlicensed music/assets or exposed secrets.
- [ ] All links pass incognito/mobile checks.

## Risk register

| Risk | Severity | Current mitigation | Exit evidence |
|---|---|---|---|
| No authentic GPT-5.6 run | Critical | Hard Gate C; public freeze then proof before polish | Retained `COMPLETE` bundle |
| No public dated Git provenance | Critical | Local Git initialized without backdating; remote still absent | Public commits/tag + provenance map |
| Benchmark leakage before freeze | Critical | No GPT-5.6 DC01 call before public Gate B | Public freeze + server timestamp + run timestamps |
| Sanitizer bypass | RESOLVED OFFLINE | Link-free safe subset and rendered adversarial tests | Authentic report/viewer demonstration |
| Wrong partition mount | RESOLVED OFFLINE | Exact matched offset sealed end to end | Native paired-disk proof if retained |
| Log misclassified as memory | RESOLVED OFFLINE | Text/log recognition before banner inference | Authentic profile proof |
| Missing full outputs | High | Content-addressed artifacts | `verify-run` rehashes outputs |
| Configured model mistaken for provider proof | High | Retain provider-returned `response.model`, response/request IDs, status, and usage | Authentic audit + manifest show requested and returned identities |
| Native environment incomplete | High | Python 3.11 Linux/WSL/container path | Clean install/catalog/native smoke |
| Fake replay mistaken for proof | High | Visible replay labeling | Authentic manifest + replay banner |
| Prior Qwen work mistaken as new | High | Positive disclosure and dated boundary | `BUILD_PROVENANCE.md` + commits |
| Same-model judge overstated | Medium | Call it fresh-context monotonic review | Honest README/video language |
| Evidence privacy exposure | High | Public case only; no secrets/raw private case | Data review + public manifest |
| Stale 2025 rules reused | High | Direct-current-source policy | Retrieval date + correct track/dates |
| Calendar dilution | Critical | Frozen scope and daily exit gates | Gate A-E status |

## Claims discipline

Safe now:

- 12 source modules and 6,068 physical source lines.
- 80 offline tests pass in the active environment.
- Ruff check and format check pass.
- A wheel builds in the active environment.
- Core control-plane semantics are implemented and tested offline.
- The feedback ID and screenshot are verified.
- All three reproduced C1 correctness/security defects are resolved offline with
  adversarial regressions.
- Local Git and `BUILD_PROVENANCE.md` exist; no public remote timestamp exists.

Not safe yet:

- “End-to-end tested.”
- “Production ready.”
- “Accurate” without known-fact evaluation.
- “Immutable audit.”
- “Full outputs are inspectable.”
- “Independent truth verifier.”
- “Evidence stays local.”
- “Native Windows E01 support.”
- Any Unchained runtime, cost, finding, or accuracy number borrowed from Qwen.

## Commands for the next session

Start in:

```powershell
cd C:\Users\Just\OneDrive\Desktop\Ensemble\sentinel-unchained
```

Read first:

```powershell
Get-Content .\docs\HACKATHON_MASTER_PLAN.md
Get-Content .\HACKATHON_HANDOVER.md
Get-Content .\DECISIONS.md
```

Current baseline checks:

```powershell
python --version
python -m pip check
python -m pytest
python -m ruff check .
git rev-parse --is-inside-work-tree
```

Canonical live command after the gate passes:

```powershell
$env:OPENAI_API_KEY = "<set securely; never commit>"
$env:UNCHAINED_MODEL = "gpt-5.6"
python -m unchained C:\path\to\public-evidence --caps default
```

Do not execute the live command until the flagship pre-execution checklist is
complete.

## Current prompt readiness

The P0 correctness prompt has completed. Do not paste the retired project
kickoff and do not repeat C1. The next major implementation block is the C2
proof-artifact prompt in `docs/HACKATHON_MASTER_PLAN.md`. The corrected C3
through C7 prompts and mandatory preregistration order are in
`docs/WINNER_ROADMAP.md`.

### Triple-verification record

The older tables below are retained as historical verification records. Current
runtime dependency and public-provenance failures remain blockers even though
C1 is green.

| Pass | What is verified | Result | Evidence | Timestamp ET |
|---|---|---|---|---|
| 1 — Coverage | Rules, all nine constraints, status ledger, proof/replay contract, defects, gates, schedule, risks, feedback ID, and next-session commands are saved | **PASS** | 926-line handover; nine numbered constraints; required-section scan found zero omissions | 2026-07-14 19:05 |
| 2 — Consistency | Handover agrees with live 2026 rules, README, DECISIONS, and actual repository state | **PASS** | Uncached rules/FAQ returned 200 and confirmed Build Week, Developer Tools, GPT-5.6, July 21, pre-existing-only evaluation, `/feedback`, no-rebuild, and under-three-minute requirements; no gpt-oss text | 2026-07-14 19:05 |
| 3 — Executable truth | Links resolve and current Python, dependencies, tests, lint, Git, and artifact state are recorded without hiding failures | **PASS** | Zero local-link failures; 71 tests passed; Ruff passed; expected blockers preserved: `pip check` exit 1, Git check exit 128, submission/run artifacts absent | 2026-07-14 19:05 |

Prompt 3 becomes documentation-ready only after all three rows are marked
`PASS`. Flagship-run readiness remains a separate gate.

### Corrected master-plan triple verification

| Pass | What is verified | Result | Evidence | Timestamp ET |
|---|---|---|---|---|
| 1 - Coverage | Product thesis, official rules, truthful architecture, scope matrices, current state, eight P0 gaps, experiment, DC01 contract, proof bundle, viewer, video, gates, prompts, compliance, ZeroFake rails, and go/no-go are saved | **PASS** | 1,084-line master plan with 18 numbered sections and copy-ready P0, proof, runtime, reviewer, and video prompts | 2026-07-14 19:38 |
| 2 - Consistency | Master plan agrees with the live 2026 rules, official GPT-5.6 guidance, actual allowlists/capabilities, handover evidence states, and durable decisions | **PASS** | Independent rules, code, and strategy audits; false Plaso/Docker/multi-OS/causal-ablation/answer-key claims replaced | 2026-07-14 19:38 |
| 3 - Executable truth | Cross-document links, formatting, tests, lint, dependency/Git blockers, and proof red states remain visible and accurate | **PASS** | Relative-link scan passed; heading blank-line scan passed; master-plan em-dash scan passed; 71 tests passed; Ruff passed; `pip check` still reports three missing dependencies; Git check still fails because no repository exists | 2026-07-14 19:38 |

| Gate | State |
|---|---|
| Rules ambiguity resolved | READY |
| Strategic handover saved and linked | READY |
| Prompt 3 constraints preserved | READY |
| P0 implementation prompt | **COMPLETE, 80 tests pass** |
| C2 proof-artifact prompt may begin | READY |
| Public experiment freeze | **NOT READY** |
| Flagship GPT-5.6 run may begin | **NOT READY** |
| Video recording may begin | **NOT READY** |
| Submission may be called complete | **NOT READY** |

C2 should implement durable outputs, provider-returned identity, manifest,
summary, environment record, verifier, bounded audited retries, and dependency
locks. No new product breadth and no GPT-5.6 DC01 call.

## Living update protocol

At the end of every substantial future session:

1. Update the document-control verification timestamp.
2. Update the implementation/proof ledger using the defined evidence states.
3. Record exact commands and outcomes for newly verified work.
4. Link every new retained artifact.
5. Update the applicable gate and daily checklist.
6. Add or resolve risks without deleting historical truth.
7. Record scope or product decisions and who owns them.
8. Recalculate the remaining clock when schedule decisions change.
9. State the single next highest-leverage action.

### Change log

| Date/time ET | Change | Evidence | Next action |
|---|---|---|---|
| 2026-07-14 18:58 | Created living handover; reconciled current rules, repository state, defects, positioning, Prompt 3 constraints, and delivery gates | Direct current rules/FAQ/overview; 71 tests; Ruff; wheel build; source inspection; focused reproductions | Fix the three reproduced defects, then implement durable full-output artifacts |
| 2026-07-14 19:05 | Completed all three pre-Prompt-3 documentation verification passes | Current uncached rules and FAQ; nine-constraint coverage scan; zero broken local links; 71 tests; Ruff; truthful dependency/Git/artifact red states | Begin the focused P0 correctness/proof implementation block |
| 2026-07-14 19:30 | Saved the deeply corrected winner master plan and synchronized README, AGENTS, decisions, and handover; added provider-returned-model and partition-aware TSK proof requirements | Independent rules, repository, and experiment audits; official GPT-5.6 guidance; current tests/Ruff/pip/Git checks; DC01 source and answer-page verification | Execute the focused P0 correctness prompt saved in the master plan |
| 2026-07-14 19:38 | Completed three verification passes over the corrected master-plan integration | 1,084-line/18-section coverage; link and heading scans; no em dash in master plan; 71 tests; Ruff; truthful dependency and Git failures retained | Execute the focused P0 correctness prompt saved in the master plan |
| 2026-07-14 20:50 | Deeply red-teamed and saved the Winner Roadmap; corrected the C0-C7 order, forbade GPT-5.6 DC01 rehearsal before a public freeze, split factual correctness from receipt sufficiency, retained the existing Volatility path, and made hosted plus offline viewing the no-rebuild contract | Current Official Rules; official GPT-5.6 and Responses guidance; Qwen adapter/source inspection; independent strategy audit; 881-line roadmap | Finish C1 verification and honest local provenance, then start C2 |
| 2026-07-14 20:50 | Implemented and root-verified all three reproduced C1 defects: rendered Markdown inertness, exact partition-offset propagation into sealed `fsstat`, and log-before-memory classification | 80 tests passed in 1.39s; six rendered report-safety tests; 34 focused evidence/tool tests; Ruff check and format check; wheel build | Commit the honest baseline, then implement C2 proof artifacts |
| 2026-07-14 20:50 | Initialized local Git on `main`, added evidence/secret exclusions, created `BUILD_PROVENANCE.md`, and passed high-confidence secret plus evidence scans | Local Git state; `.gitignore`; scans found no key/evidence candidate; public remote absent | Create baseline commit and publish only after final tracked-file review |

## Single next action

Commit the reviewed honest local baseline, then execute C2: durable
content-addressed full outputs, provider-returned model identity, manifest,
summary, environment record, `verify-run`, bounded audited retries, and locked
Python 3.11 dependencies. Do not run GPT-5.6 on DC01 until deterministic native
smoke and the public experiment freeze also pass.
