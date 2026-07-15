# Sentinel Unchained: Winner Roadmap

> **Role:** priority, sequencing, positioning, and go/no-go overlay
> **Status:** active execution contract
> **Last deep review:** 2026-07-14
> **Track:** Developer Tools
> **Internal submission deadline:** 2026-07-20
> **Hard deadline:** 2026-07-21 17:00 PT / 20:00 ET

This roadmap sits on top of
[HACKATHON_MASTER_PLAN.md](HACKATHON_MASTER_PLAN.md). It does not authorize a
re-scaffold. The master plan owns the detailed architecture, experiment, proof
bundle, judge experience, and submission contracts. This roadmap controls the
order in which the remaining work is attempted and the claims that may be made
about that work. [HACKATHON_HANDOVER.md](../HACKATHON_HANDOVER.md) remains the
live evidence-backed status ledger. [DECISIONS.md](../DECISIONS.md) remains the
durable architecture record.

If these files conflict, apply this precedence:

1. current OpenAI Build Week Official Rules and logged-in submission form;
2. this roadmap for priority, sequence, and gate order;
3. the master plan for detailed product and proof contracts;
4. the living handover for current execution state;
5. DECISIONS for accepted architecture history.

## 1. Winner verdict

Proceed with Sentinel Unchained. Do not pivot and do not re-scaffold.

The strongest product is not another autonomous DFIR analyst. It is a
developer-facing trust-measurement harness for model-directed investigators,
demonstrated on a forensic benchmark.

Use this public one-line framing:

> Sentinel Unchained is a trust-measurement harness that quantifies
> receipt-grounded reliability for a GPT-5.6-directed investigator on a frozen
> forensic benchmark, then publishes a proof bundle every judge can inspect.

Use this memorable supporting line:

> Unchained reasoning. Chained evidence.

Do not say the experiment measures exactly how far autonomous investigators in
general can be believed. One public case cannot support that generalization.
Do not call the investigator unsupervised. It operates inside deterministic
authority, custody, protocol, audit, and budget boundaries.

### Why this framing is stronger

- The agent itself is not the only product. The experiment protocol, receipt
  store, verifier, adjudication, metrics, and viewer form a reusable developer
  tool for evaluating agents.
- DFIR is an unusually demanding testbed because unsupported claims can look
  convincing and evidence provenance matters.
- The entry has a concrete audience: security-agent developers, DFIR platform
  teams, SOC automation engineers, and agent-evaluation researchers.
- The external benchmark and proof bundle turn a model demo into an inspectable
  measurement product.
- The framing stays consistent with Sentinel Ensemble. Ensemble is the
  production-oriented trust architecture; Unchained is the controlled-autonomy
  measurement instrument.

## 2. The keystone artifact

The keystone is:

> One authentic, complete, post-freeze GPT-5.6 run against real DC01 evidence,
> producing a content-addressed proof bundle, a frozen-reference evaluation,
> and a no-rebuild viewer that a judge can inspect.

That artifact is necessary. It is not sufficient by itself. The current rules
score Technical Implementation, Design, Potential Impact, and Quality of the
Idea equally. The authentic bundle proves the implementation; the viewer and
quickstart prove the product experience; the audience and evaluation prove
impact; the trust-measurement design proves novelty.

No fake model, replay, screenshot, synthetic receipt, or recorded verifier can
substitute for the authentic run. Those artifacts can prove controller behavior
or accessibility only when labeled accurately.

## 3. Critical scientific correction

### Freeze before GPT-5.6 sees DC01

The original overlay placed authentic GPT-5.6 dress rehearsals on DC01 before
the rubric and protocol freeze. That order is rejected.

A fresh API request may be stateless, but the development process is not. Once
the developer sees which DC01 tools GPT-5.6 chose, which facts it missed, which
claims it overreached on, and what the reviewer caught, later prompt, catalog,
rubric, threshold, and metric changes can overfit to the benchmark.

Therefore:

> The complete protocol, code, prompts, eligible tool catalog, caps, retry
> policy, rubric, scoring rules, metric definitions, fault rules, and primary-run
> selection rule must be publicly frozen before the first GPT-5.6 investigation
> of DC01.

### Allowed before the freeze

- download, hash, extract, and inventory DC01;
- confirm read-only access and custody behavior;
- run deterministic native tools directly, without GPT-5.6;
- confirm Windows symbols, output parsing, timeouts, containment, retention,
  hashing, cleanup, and exact partition handling;
- inspect the supplied evidence to determine which reference facts are actually
  observable through the frozen tool surface;
- rehearse GPT-5.6 function calling against fake typed tools, synthetic
  receipts, generic non-case data, or a different explicitly unscored case.

### Forbidden before the freeze

- a GPT-5.6 investigation of DC01;
- prompt tuning based on a DC01 model run;
- changing tool eligibility because GPT-5.6 missed a DC01 fact;
- building the rubric around facts the model happened to find;
- changing metric definitions or pass thresholds after seeing DC01 proposals;
- hiding or relabeling a semantically weak technically valid run.

If GPT-5.6 has already investigated DC01 before a public freeze, disclose it.
The later run can remain an authentic product demonstration, but it must not be
described as an untouched preregistered evaluation.

## 4. Correct critical path

```text
C0 HONEST PROVENANCE BASELINE
        |
        v
C1 THREE CORRECTNESS FIXES + WINDOWS PROMPT CONSISTENCY
        |
        v
C2 DURABLE PROOF CONTRACT + VERIFIER + LOCKED ENVIRONMENT
        |
        v
C3 CLEAN PYTHON 3.11 + DETERMINISTIC REAL-TOOL SMOKE
        |
        v
C4 PUBLIC PROTOCOL AND RUBRIC FREEZE
        |
        v
C5 FIRST GPT-5.6 DC01 RUN IS THE PRIMARY RESULT
        |
        v
C6 ADJUDICATION + HOSTED/OFFLINE VIEWER + VERIFY-RUN
        |
        v
C7 README + VIDEO + FEEDBACK + TAG + DEVPOST SUBMISSION
```

If time slips, cut breadth and presentation iterations. Never cut the authentic
run, retained receipts, public freeze, no-rebuild test path, or truthful
disclosure.

## 5. C0: immediate provenance baseline

Do this before further material feature work:

1. Initialize Git without backdating.
2. Create an honest baseline commit containing the current implemented state.
3. Add `BUILD_PROVENANCE.md` distinguishing prior work from Build Week work.
4. Preserve the current successful `/feedback` ID and screenshot.
5. Push to a public remote when the repository has passed a secret and evidence
   scan.
6. Do not force-push, rewrite, or delete the public Build Week history.
7. Request Codex credits and retain the confirmation if not already complete.
8. Start or verify the DC01 acquisition outside the repository.
9. Open a Devpost draft early so every live form requirement is visible.
10. Identify the intended adjudicator before the scored run.

Local Git gives exact content binding but not an independently trustworthy
timestamp. Git author and committer dates can be edited, and local history can
be rewritten. Never call a local commit unimpeachable preregistration proof.

The strong future-tense claim is:

> The protocol and rubric will be committed publicly and independently
> server-timestamped before the primary run.

The past-tense claim is allowed only after a public remote commit and
server-side timestamp exist.

### C0 acceptance evidence

- local repository initialized;
- secret/evidence exclusion and scan pass;
- honest baseline commit and provenance map;
- public remote URL and remote commit, or an explicit blocker if remote access
  requires a human login;
- retained credit request result;
- acquisition manifest in progress or complete;
- Devpost draft state recorded.

## 6. C1: focused correctness gate

Fix exactly the reproduced defects before adding proof features:

1. Markdown sanitizer bypass, including malformed link/image syntax,
   protocol-relative targets, dangerous schemes, reference definitions, and raw
   HTML. Test rendered inertness, not only source-text replacement.
2. Exact partition-offset propagation from successful filesystem detection
   through mounting and partition-aware `fsstat` or equivalent tool exposure.
3. Text-log versus memory classification so a small text log containing a
   kernel banner cannot become a memory image.
4. Runtime prompt and public scope consistency: the flagship prompt is one
   Windows route until another evidence OS is genuinely demonstrated.

The phrase "five reproduced defects" is retired. There are three reproduced
defects, plus regression testing and documentation/handover duties.

### C1 acceptance evidence

- adversarial sanitizer fixtures are inert after rendering;
- the exact detected partition offset is retained and used;
- ordinary text logs remain logs;
- focused tests pass;
- full tests pass;
- Ruff passes;
- handover and any changed durable decisions are updated.

## 7. C2: proof and reliability contract

C2 may be split into small commits, but all required pieces must be working and
frozen before the primary run:

- full accepted tool outputs stored content-addressably;
- call ID, tool, typed arguments, status, duration, encoding, media type, byte
  count, truncation state, relative path, and SHA-256 retained;
- requested model alias and provider-returned `response.model` stored
  separately;
- response IDs, request IDs when available, status, usage, and timestamps
  retained for every request attempt;
- `manifest.json`, `summary.json`, and `environment.json` generated;
- prompt, catalog, dependency, cap, retry, rubric, scoring, and price-table
  digests bound into the manifest;
- audit chain and terminal state bound into the manifest;
- a no-network `verify-run` command;
- deterministic validation of artifact hashes, citation identity, successful
  receipt status, exact quoted-span presence, and summary consistency;
- a small bounded transient provider retry policy that cannot duplicate a
  forensic tool execution;
- exact Python 3.11 dependency lock or constraints;
- every request attempt audited, including ambiguous dispatch failures;
- conservative local estimated-cost enforcement and explicit unknown billing
  exposure when a dispatched failure returns no usage.

`MAX_COST_USD` is not a provider invoice guarantee. The safe claim is:

> The controller applies a conservative code-owned estimated inference budget
> before each request, bounds maximum output, audits every attempt, and stops
> when reported usage reaches the configured limit.

Use a dedicated funded OpenAI project, a low project-level budget or alert, and
the local cap. Provider billing remains authoritative when available.

### C2 acceptance evidence

- fake-model dry run creates a complete bundle;
- every accepted output is present and hash-valid;
- provider-returned-model fixtures verify requested-versus-returned capture;
- retries are bounded, audited, and tool-idempotent;
- `verify-run` passes the untouched fixture and fails every tampered fixture;
- dependency lock exists;
- tests, Ruff, build, and applicable `pip check` pass.

## 8. C3: clean environment and deterministic native proof

Do not build a new cross-platform Volatility Python API adapter unless the
existing reviewed path is reproduced as incapable of running the Windows
flagship.

The current prior dependency already maps fixed tool names to fixed Volatility
plugins and invokes the cross-platform `vol` console entry point through trusted
code. Unchained already wraps that path in a reviewed allowlist, a private
worker, code-owned evidence paths, bounded responses, credential scrubbing,
timeouts, and containment. Replacing it now risks bypassing those guarantees
and expanding scope.

C3 sequence:

1. Create a clean Python 3.11 environment.
2. Install the pinned project and locked dependencies.
3. Require `pip check`, tests, Ruff, wheel build, and installed-package smoke.
4. Load the existing real catalog.
5. Run actual catalog functions such as `vol_pstree` and `vol_netscan` or
   another eligible second memory function directly, without GPT-5.6.
6. Confirm real rows, symbol readiness, retained outputs, timeouts, cleanup, and
   custody.
7. Run paired-disk mount/probes only while that route remains within Gate A.
8. If the disk route misses Gate A, freeze the flagship to Windows memory-only.

Do not require `windows.pslist` if that function is not in the project-visible
catalog. Use the actual exposed typed functions. Do not claim symbol download
or resolution succeeded until the live output proves it.

If a new adapter becomes unavoidable, limit it to the demonstrated Windows
memory route and preserve fixed plugins, code-owned paths, process containment,
wall timeout, output limits, credential-free execution, complete receipts, and
adversarial boundary tests.

### C3 acceptance evidence

- Python 3.11 version transcript;
- clean install and `pip check`;
- full tests, Ruff, wheel, and installed smoke pass;
- existing real catalog loads;
- at least one existing native Windows-memory function returns real rows;
- exact output persists and verifies;
- cleanup and recorded custody pass;
- disk route either passes or is explicitly cut.

No full GPT-5.6 DC01 investigation is allowed yet.

## 9. C4: public experiment freeze

Before any GPT-5.6 DC01 investigator call, create and freeze:

```text
experiment/protocol-v1.md
experiment/reference-rubric-v1.json
experiment/scoring-spec-v1.md
experiment/run-selection-v1.md
experiment/freeze-manifest-v1.json
```

### Frozen rubric fields

Each reference fact needs:

- stable fact ID;
- one atomic factual proposition;
- observability from the supplied evidence route;
- required artifact/tool family;
- status: stable, approximate, ambiguous, or unobservable;
- inclusion or exclusion rationale;
- normalized objective values where applicable;
- match mode;
- receipt-sufficiency guidance;
- source and independent-evidence-check notes;
- ambiguity and timestamp-basis notes.

Exclude PCAP-only, desktop-only, disk-only when memory-only is frozen,
approximate without an accepted tolerance, ambiguous, unobservable, and broad
narrative facts from scored denominators.

### Two evaluation dimensions

Do not collapse truth and receipt support.

Dimension A, factual correctness:

```text
CORRECT | INCORRECT | AMBIGUOUS | OUT_OF_RUBRIC
```

Dimension B, receipt sufficiency:

```text
SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | CONTRADICTED
```

A fact may be true but unsupported by its cited receipt. A real citation may be
irrelevant. A claim may fall outside the answer rubric yet still have strong
receipt support. Preserve both dimensions.

Exact substring validation proves only that a quote occurs in a retained
receipt. It does not prove that the quote entails the claim. Deterministic code
may score normalized objective fields such as exact hashes, IP addresses, PIDs,
paths, event IDs, and timestamps with a frozen time basis. Relational,
interpretive, maliciousness, causality, absence, and cross-artifact claims need
blinded human or explicitly project-authored reference adjudication.

Preferred adjudication:

- a named human reviewer who did not build the result;
- randomized atomic findings;
- investigator and model-reviewer labels hidden during adjudication;
- factual correctness and receipt sufficiency labeled separately;
- raw labels, rationale, and dispute resolution retained;
- a second reviewer for disputes if time permits.

If no independent reviewer is available, use the honest phrase:

> Project-authored, preregistered reference-rubric evaluation.

Do not call a project-authored rubric independent external adjudication.

### Frozen metrics

Publish numerator and denominator for every rate. Report `not applicable` when
a denominator is zero.

| Metric | Frozen definition |
|---|---|
| Investigator proposal support rate | receipt-supported investigator proposals / all investigator proposals |
| Final-confirmed precision | receipt-supported final `CONFIRMED` findings / all final `CONFIRMED` findings |
| Discovered-fact recall | scored reference facts correctly surfaced at any status / all scored observable facts |
| Confirmed-fact recall | scored reference facts correctly surfaced and finally `CONFIRMED` / all scored observable facts |
| Reviewer catch rate | receipt-unsupported proposals downgraded / all receipt-unsupported proposals |
| Reviewer escape rate | receipt-unsupported proposals still `CONFIRMED` / all receipt-unsupported proposals |
| Reviewer over-downgrade rate | receipt-supported proposals unjustifiably downgraded / all receipt-supported proposals |
| Supported-claim retention | receipt-supported proposals preserved / all receipt-supported proposals |
| Citation integrity rate | findings whose cited artifacts, hashes, and quoted spans verify / all findings with citations |
| Opening contribution | final supported facts first supported by opening receipts / all final supported facts |
| Tool efficiency | supported facts / successful tool calls |

Also freeze definitions for tool statuses, opening time, time to first supported
fact, total runtime, provider usage fields, local estimated cost, provider-billed
cost if available, artifact size, and recorded custody result.

### Primary-run selection and infrastructure faults

Freeze objective infrastructure-fault criteria before the run. Examples may
include provider unavailability before a usable response, corrupt evidence
read, failed required symbol resolution, a verifier defect that invalidates all
receipts, or a custody failure. A weak finding set, missed fact, unsupported
claim, reviewer escape, high cost within cap, or unattractive score is not an
infrastructure fault.

Use:

> The first post-freeze run that completes without a predeclared infrastructure
> fault is the primary result. A semantically disappointing valid run remains
> primary. Every later valid run is a disclosed replicate.

### Independent time anchor

1. Commit the freeze files and all bound code.
2. Push the commit to the public remote.
3. Create `experiment-freeze-v1`.
4. Run server-timestamped CI that checks out the commit, recomputes every
   digest, prints the freeze table, and retains the manifest artifact.
5. Optionally publish a release containing the freeze manifest and hashes.
6. Retain the public commit, tag, workflow, and release URLs.
7. Never force-push or delete a freeze version.

If a real predeclared infrastructure bug requires change, retain the invalid
run and `v1`, document the reason, create `v2`, push it, and establish a new
server timestamp before the next candidate. Never relabel semantic failure as
infrastructure failure.

### C4 acceptance evidence

- complete rubric and scoring spec;
- all metrics, denominators, thresholds, fault rules, and selection rules
  frozen;
- code, prompts, catalog, caps, retries, dependencies, price table, evidence
  hashes, rubric, and scorer bound by digest;
- public commit and freeze tag;
- server-timestamped CI/release verification;
- no prior GPT-5.6 DC01 investigation, or an explicit disclosure if this claim
  can no longer be made.

## 10. C5: authentic primary run

Only after C4 passes:

1. Use a funded OpenAI project key without logging it.
2. Request `gpt-5.6` through the Responses API.
3. Record the provider-returned model, response IDs, request IDs when available,
   statuses, usage, and every attempt.
4. Give the model only a neutral case ID, generic filenames where safe,
   evidence profile, and frozen eligible typed functions.
5. Let it select 1 to 6 opening functions, execute them concurrently, and
   continue with one function per later turn.
6. Retain concise decision summaries, not hidden chain-of-thought.
7. Preserve every exact accepted output and all failures.
8. Enforce evidence pre/post hashing, cleanup, caps, and terminal status.
9. Do not discard the primary because its semantic result is weak.
10. Run deterministic verification before any public metric is computed.
11. Apply the frozen two-axis adjudication.
12. Run one or two identical replicates only after the primary, if stable and
    affordable, and publish every valid replicate.

The model alias in an environment variable proves only what was requested. The
provider-returned response object is required to show what was returned.

### C5 acceptance evidence

- authentic provider response and returned identity;
- real model-selected typed functions;
- real native execution on DC01;
- `COMPLETE` primary status;
- full retained proof bundle;
- every deterministic bundle and citation check passes;
- recorded pre/post custody values agree;
- frozen two-axis evaluation complete;
- every valid run and invalid attempt disclosed according to the protocol.

## 11. C6: judge product

The no-rebuild path is a hard Developer Tools requirement, not visual polish.
A Dockerfile still requires a build. A screencast lets a judge watch but does
not let a judge test.

Ship three layers:

1. a hosted HTTPS static viewer, preferably on a stable static host;
2. a downloadable offline viewer or release bundle;
3. a no-network `verify-run` command or prebuilt verification artifact.

The viewer must render only the completed proof bundle. It must not call the
model, rerun forensic tools, or imply that replay is live execution.

Required banner:

```text
Inspection of a retained genuine GPT-5.6 run.
No model or forensic tool is executed by this viewer.
```

### Viewer security and portability

- inline or local CSS and JavaScript only;
- no external dependencies or telemetry;
- no module imports for the offline file;
- no `fetch` of sibling JSON under `file://`;
- bundle data embedded at generation time or selected with an explicit file
  picker;
- evidence-derived and model-derived text inserted inertly with `textContent`,
  never trusted as `innerHTML`;
- restrictive Content Security Policy where compatible;
- no active images, external links, embedded SVG, or executable Markdown from
  receipts;
- current Chrome and Edge test required; Firefox and Safari tested where
  available;
- large full outputs kept as inert downloadable text or JSON with escaped
  previews.

The user experience target is:

```text
20 seconds to understand the result
1 click from a claim to its receipt
under 5 minutes to verify the core value
```

The viewer should show the case card, opening selections, turn sequence,
findings, model-reviewer changes, two-axis adjudication, metric numerators and
denominators, provider proof, audit state, output hashes, and recorded custody.

A resolving citation makes a claim inspectable. It does not prove the claim is
supported. The evaluator must expose irrelevant or insufficient receipts.

### Verifier wording

Without the original multi-gigabyte evidence, the judge can verify bundle
integrity and that the retained pre-hash and post-hash records agree. The judge
cannot independently rehash evidence bytes they do not possess.

Say:

> The verifier validates the retained custody record, audit chain, bundle
> integrity, output hashes, citation identity, quoted spans, and summary
> consistency.

Do not say the lightweight viewer independently re-verifies the original
evidence.

### C6 acceptance evidence

- hosted viewer works anonymously over HTTPS;
- offline viewer works from a clean download without a server;
- one click resolves each finding to the exact retained receipt context;
- replay banner is always visible;
- tampered bundles fail verification;
- browser security and portability checks are retained;
- verifier recording exists only as supplemental evidence.

## 12. C7: judge-facing submission

Finish:

- README first screen with the trust-measurement framing;
- explicit prior-work versus Build Week bright line;
- installation and supported-platform instructions;
- no-rebuild viewer and verifier path;
- optional funded-key live-run path;
- `JUDGE-QUICKSTART.md` with copy-paste instructions;
- truthful evidence-OS and host-OS matrices;
- Codex collaboration narrative and human decisions;
- GPT-5.6 integration details;
- DC01 credit and no-redistribution instructions;
- single-case and possible training-contamination limitations;
- Devpost description;
- authentic time-compressed video under 3:00, public on YouTube;
- audio that explicitly names both Codex and GPT-5.6;
- final `/feedback` from the true majority-core thread;
- exact submission tag;
- anonymous repository, viewer, video, release, and link QA;
- Devpost submission and retained confirmation.

Do not freeze truthful factual corrections to the result narrative after the
run. Freeze the protocol, metrics, and run-selection rule. Post-run result
documentation may be corrected with a visible history, but the valid primary
run may not be replaced or tuned away.

## 13. Hard gates

### Gate A: 2026-07-15 20:00 ET

- C1 green;
- proof structure substantially working;
- Python 3.11 clean environment;
- real catalog load;
- deterministic native memory-tool smoke;
- honest Git and provenance.

If disk is the blocker, cut to memory-only immediately.

### Gate B: before the first GPT-5.6 DC01 call

- rubric and scoring spec complete;
- factual correctness and receipt sufficiency separated;
- all metrics and denominators frozen;
- infrastructure faults and run-selection rule frozen;
- code, prompts, catalog, dependencies, caps, retry policy, and price table
  frozen;
- public remote freeze commit and tag;
- server-timestamped digest verification.

No DC01 GPT-5.6 rehearsal may cross this gate.

### Gate C: 2026-07-17 18:00 ET

- authentic primary run is `COMPLETE`;
- verified proof bundle;
- recorded custody agreement;
- frozen evaluation complete;
- no concealed citation, adjudication, or run-selection failure.

If this gate fails, stop viewer polish and diagnose only the live route.

### Gate D: 2026-07-18 20:00 ET

- hosted viewer;
- offline viewer;
- `verify-run`;
- judge quickstart draft;
- metric and claim table frozen to verified artifacts.

A screencast alone does not pass.

### Gate E: 2026-07-20

- public video;
- public or properly shared repository;
- anonymous viewer/test path;
- correct feedback ID;
- submission tag;
- all links tested;
- Devpost confirmation retained.

## 14. Scope-cut ladder

Apply cuts in this order:

1. If disk mounting misses Gate A, flagship becomes Windows memory-only.
2. Remove Linux, macOS, Plaso, Docker, Qwen reruns, and extra tool families.
3. Keep one authentic primary run and label it a single-run, single-case study.
4. Cut replicates before cutting primary proof.
5. Simplify viewer styling, but never remove the functioning hosted and offline
   no-rebuild paths.
6. Cut video retakes before cutting truthful authentication footage.
7. Cut prose length before cutting provenance, limitations, or metric
   denominators.

Never let a schedule slip justify fake output, hidden invalid runs, benchmark
tuning, unsupported claims, or replay presented as live execution.

## 15. Red-to-green scoreboard

```text
LOCAL GIT + PROVENANCE
        -> PUBLIC REMOTE
        -> C1 CORRECTNESS
        -> C2 PROOF CONTRACT
        -> PYTHON 3.11 + PIP CHECK
        -> REAL DETERMINISTIC TOOL OUTPUT
        -> PUBLIC EXPERIMENT FREEZE
        -> AUTHENTIC GPT-5.6 PRIMARY
        -> VERIFIED EVALUATION BUNDLE
        -> HOSTED + OFFLINE VIEWER
        -> PUBLIC VIDEO
        -> DEVPOST CONFIRMATION
```

Turn these green in order. A later green state never excuses an earlier red
state.

## 16. Paste-ready Codex sequence

The saved C1 and C2 prompts in the master plan remain the detailed
implementation prompts. The following prompts correct the later sequence.

### C3 prompt: real environment and deterministic native proof

```text
Continue the existing sentinel-unchained repository after C1 and C2. Do not add
product features and do not run GPT-5.6 against DC01 yet.

1. Create and prove a clean Python 3.11 environment. Install the project and
   locked dependencies. Run pip check, full pytest, Ruff, wheel build, and an
   installed-package CLI/import smoke.
2. Load the existing reviewed real tool catalog and worker boundary. Use the
   existing fixed Volatility tool path before considering any new adapter.
3. Against the real DC01 Windows memory image, directly execute at least one
   actually exposed native memory function such as vol_pstree, plus one second
   eligible memory function if time permits. Do not require windows.pslist when
   it is not in the model-visible catalog.
4. Prove real returned rows, symbol readiness, complete content-addressed output,
   timeout behavior, credential-free child environment, cleanup, and matching
   recorded custody.
5. Exercise paired-disk mounting/probes only if it remains inside Gate A. If it
   fails the gate, freeze the flagship to Windows memory-only and update every
   scope matrix.
6. Add a regression fixture based on a sanitized captured real output shape.

Do not create a direct cross-platform Volatility Python API adapter unless the
existing reviewed path is first reproduced as incapable of the Windows-memory
flagship. If a minimal replacement becomes necessary, preserve the fixed plugin
allowlist, code-owned evidence path, private process containment, wall timeout,
output bound, credential scrubbing, complete receipts, and adversarial tests.

Update the handover with exact commands, environment, outputs, hashes, gate
state, risks, and the single next action. No fake model or replay may be called
an authentic run.
```

### C4 prompt: preregister and publicly freeze

```text
Prepare the experiment freeze before the first GPT-5.6 investigation of DC01.
Do not call the model on DC01 in this task.

1. Create experiment/protocol-v1.md, reference-rubric-v1.json,
   scoring-spec-v1.md, run-selection-v1.md, and freeze-manifest-v1.json.
2. Build the rubric from atomic facts observable through the frozen evidence
   route and tool catalog. Exclude PCAP-only, desktop-only, unavailable-route,
   ambiguous, approximate-without-tolerance, and unobservable facts.
3. Separate factual correctness labels from receipt-sufficiency labels. Exact
   quote matching is citation integrity only. Use deterministic normalized
   matching only for objective fields with frozen normalization. Require blinded
   human or honestly project-authored adjudication for semantic claims.
4. Freeze every metric, numerator, denominator, zero-denominator rule,
   infrastructure-fault definition, success threshold, and first-valid-run
   selection rule before seeing model proposals.
5. Bind the exact Git commit, prompts, catalog, dependency lock, Python/native
   versions, evidence hashes, rubric, scorer, caps, retry policy, model alias,
   price table, and selection rule by digest.
6. Commit and push without rewriting history. Tag experiment-freeze-v1. Add a
   server-timestamped CI job that recomputes and publishes the digest table.
7. Save the public commit, tag, workflow, and release URLs in the handover.

Acceptance: every freeze artifact verifies, an independent server timestamp
exists, and no GPT-5.6 DC01 investigation occurred before the freeze. If that
last statement is no longer true, disclose the run and remove the untouched
preregistration claim.
```

### C5 prompt: authentic primary run and frozen evaluation

```text
Run the first authentic post-freeze GPT-5.6 investigation of DC01. The first
run without a predeclared infrastructure fault is the primary result, even if
its forensic performance is disappointing. No fake model or replay may satisfy
this task.

1. Use the OpenAI Responses API with requested alias gpt-5.6 and a funded
   project key. Never log the key.
2. Give the model only a neutral case ID, generic filenames where safe, the
   frozen profile, and the frozen eligible typed functions. Never provide the
   case name, source, answer key, or rubric.
3. Capture requested and provider-returned model identities, response/request
   IDs when available, status, usage, timestamps, and every request attempt.
4. Execute the 1-to-6 model-selected opening concurrently, then one typed
   function per later turn. Preserve concise decision summaries, not hidden
   chain-of-thought.
5. Retain all exact outputs, failures, audit events, manifests, summaries,
   environment records, prompt/catalog/rubric digests, and pre/post evidence
   hashes. Enforce cleanup and caps.
6. Run verify-run. Then apply the frozen two-axis evaluation and publish counts
   with every rate.
7. Never replace a valid primary for a nicer result. Later identical runs are
   disclosed replicates. A protocol change requires a retained new freeze
   version.

Acceptance: COMPLETE authentic primary, provider-returned identity, real typed
tool execution, complete hash-valid bundle, resolving citations, recorded
custody agreement, and frozen factual-correctness plus receipt-sufficiency
evaluation. Citation resolution is traceability, not proof of entailment.
```

### C6 prompt: no-rebuild judge product

```text
Build the judge product from the verified authentic bundle. It must not call a
model or forensic tool.

1. Generate a hosted HTTPS static viewer and a downloadable offline viewer or
   release bundle. The offline viewer must not fetch sibling files under
   file://; embed sanitized data or use an explicit file picker.
2. Render the case card, opening, turn sequence, findings, model-review changes,
   factual and receipt-sufficiency labels, metric numerators/denominators,
   provider proof, hashes, audit state, and retained custody record.
3. Make every finding one click from its exact receipt context and artifact
   hash. Explain that a resolving citation is inspectable, not automatically
   sufficient.
4. Insert all evidence/model text inertly. No trusted innerHTML, active images,
   executable Markdown, external dependencies, or telemetry. Add a restrictive
   CSP where compatible.
5. Keep the replay banner permanently visible. Test anonymous hosted access and
   the offline download on clean current browsers.
6. Ship verify-run and a retained PASS transcript. A screencast may supplement
   the path but may not replace it.

Acceptance: 20 seconds to understand, one click to the receipt, under five
minutes to verify the core value, anonymous hosted access, clean offline access,
and tamper tests that fail closed.
```

### C7 prompt: final docs, video, and submission freeze

```text
Prepare the final judge-facing submission from verified artifacts only.

1. Rewrite the README first screen around the trust-measurement harness. Add an
   unambiguous bright line: prior MIT typed forensic substrate versus Build Week
   agent loop, reviewer, proof contract, frozen evaluation, verifier, and
   viewer. Every number must link to a bundle artifact.
2. Create JUDGE-QUICKSTART.md with three copy-paste paths: hosted viewer,
   offline viewer plus verify-run, and optional funded-key pipeline run.
3. Publish truthful host-platform and evidence-OS matrices with TESTED,
   EXPERIMENTAL, LIMITED, or UNDEMONSTRATED labels.
4. Draft the Devpost description and a 2:45-to-2:50 narration. Show authentic
   time-compressed footage and the viewer. Audio must name Codex and GPT-5.6 and
   state the single-case scope and possible public-case training contamination.
5. Run a final claims-to-artifacts audit, tests, Ruff, build, verifier, secret
   scan, license check, anonymous link check, and video-duration/audio check.
6. Run /feedback in the true majority-core Codex thread, tag the exact
   submission commit, submit by July 20, and save confirmation.

Do not invent numbers, hide valid runs, claim an independent evaluator when the
evaluation is project-authored, call local Git immutable, call a local estimate
an invoice guarantee, or present replay as authentic execution.
```

## 17. Make-no-mistake rails

1. Authenticity starts with provider-returned metadata, not an environment
   variable or screenshot.
2. DC01 model inference starts only after the public experiment freeze.
3. Public Git plus server-side timestamp strengthens preregistration; it is not
   mathematical immutability.
4. Exact quote occurrence proves citation integrity, not semantic support.
5. Truth and receipt sufficiency are separate axes.
6. A same-model fresh reviewer is a downgrade-only check, not ground truth.
7. Resolving citations make claims inspectable, not automatically correct.
8. The local cost cap is conservative estimated control, not an invoice
   guarantee.
9. The existing reviewed Volatility path is preferred over a rushed new
   adapter.
10. A hosted viewer plus offline bundle is the no-rebuild path. A recording is
    supplemental evidence only.
11. The lightweight verifier validates retained custody records and bundle
    integrity, not absent original evidence bytes.
12. Every valid post-freeze run stays disclosed.
13. A protocol change creates a retained new freeze version.
14. No evidence archive, recovered malware, credential, secret, or answer key
    enters the repository, viewer, model context, or public bundle.
15. Every public metric includes its numerator, denominator, source artifact,
    and zero-denominator behavior.

## 18. Single next action

Complete C0 and C1, then execute the proof-artifact prompt already saved in the
master plan. Do not start a GPT-5.6 DC01 run until C2, C3, and the public C4
freeze are green.
