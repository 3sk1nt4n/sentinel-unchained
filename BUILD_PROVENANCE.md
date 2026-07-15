# Sentinel Unchained Build Provenance

> **Created:** 2026-07-14 during the OpenAI Build Week submission period
> **Purpose:** distinguish prior work, new Build Week work, Codex work, and
> current proof limits
> **Current status:** honest local baseline; public remote timestamp pending

This document records provenance without backdating or overstating what Git can
prove. It must be updated whenever a material dependency, source boundary,
Codex thread, freeze version, or submission artifact changes.

## 1. Important timing limitation

The project directory acquired its first Git repository after a substantial
amount of the initial Unchained scaffold, controller, tests, and documentation
had already been created in Codex on July 14, 2026.

The initial commit therefore proves the exact state captured at that baseline.
It does not, by itself, prove the creation time of every line in that state.
Local filesystem timestamps and local Git dates are not independent time
anchors. The retained Codex thread and successful `/feedback` upload provide
additional Build Week evidence, while later public commits and server-side CI
timestamps will provide stronger independent anchors.

No commit will be backdated. Public Build Week history must not be force-pushed,
rebased, or deleted after publication.

## 2. Codex thread evidence

Current successful `/feedback` Codex Session ID:

```text
019f61e5-5755-7a02-adb4-618d32baab27
```

This is the current majority-core implementation thread. Re-evaluate that fact
near submission after material later work. Use the final successful `/feedback`
ID from the thread where the majority of core functionality was actually built.

The screenshot of the successful upload is retained outside the repository. It
must not be used as a substitute for source history, working code, or an
authentic GPT-5.6 runtime proof.

## 3. Prior work boundary

The prior project is the author's MIT-licensed repository:

```text
https://github.com/3sk1nt4n/Sentinel-Ensemble-Qwen
commit 9f309c6134e857f7b86f3e6b9c6709ce954944a5
```

Prior work used by this project:

- selected typed forensic tool functions;
- selected evidence-mounting substrate;
- fixed forensic plugin metadata used by the reviewed allowlist.

The dependency is declared at the exact commit in `pyproject.toml`. It is not
copied into this repository as a pretense of new Build Week code.

Prior work not claimed as new Unchained implementation:

- the Sentinel Ensemble pipeline;
- the prior deterministic semantic validator;
- prior prompts;
- prior reporting code;
- prior metrics, findings, runs, screenshots, or videos.

## 4. New Build Week work

The following project-owned areas were built for Sentinel Unchained during this
Build Week effort and are the work intended for evaluation:

- `src/unchained/evidence.py`: bounded discovery, content classification,
  capability routing, read-only mount control, symbol readiness, and custody;
- `src/unchained/tools.py` and `src/unchained/_tool_worker.py`: reviewed typed
  authority boundary, private worker execution, containment, output limits, and
  profile-dependent catalog;
- `src/unchained/model.py`: OpenAI Responses API integration and normalized
  provider responses;
- `src/unchained/agent.py`: opening selection, adaptive loop, forced structured
  finalization, fresh downgrade-only review, reporting, and report safety;
- `src/unchained/audit.py`, `caps.py`, `models.py`, `prompts.py`, `cli.py`, and
  `__main__.py`: audit chain, budgets, domain types, runtime instruction,
  lifecycle, terminal states, and CLI;
- all project-owned tests under `tests/`;
- the Unchained README, decision record, master plan, winner roadmap, handover,
  and later proof/viewer/submission artifacts.

This boundary must remain visible in the README and Devpost description because
the Official Rules evaluate a pre-existing project's submission-period
additions only.

## 5. Human and Codex roles

Human-owned product and research decisions include:

- choosing the controlled-autonomy versus deterministic-trust comparison;
- choosing Developer Tools and the trust-measurement framing;
- selecting DFIR as the demonstration domain;
- choosing DC01 as the known-answer public benchmark;
- accepting the single-case and possible training-contamination limitations;
- requiring truthful scope labels and a no-fake evidence policy;
- approving scope cuts, public claims, the frozen rubric, and final submission.

Codex has accelerated:

- repository inspection and architecture implementation;
- typed controller, evidence, tool, audit, cap, and report-safety code;
- adversarial tests and defect reproduction;
- live-rules and official-API verification;
- code, security, experiment, judge-experience, and strategy review;
- documentation, handover, and prompt construction;
- future proof-bundle, verifier, viewer, and submission QA work recorded by
  later commits.

These role descriptions must be updated from actual retained work. They are not
permission to claim a future artifact as complete.

## 6. Baseline state captured on July 14

At the local baseline:

- the offline controller and safety boundaries are substantial;
- the three reproduced C1 defects have code fixes and adversarial regressions;
- the current suite contains 80 passing tests in the active environment;
- Ruff source checks pass;
- the active Python environment is 3.14.3, not the required clean Python 3.11
  proof environment;
- live runtime dependencies remain incomplete in the active environment;
- no authentic GPT-5.6 DC01 investigation exists;
- no public proof bundle, hosted viewer, public video, or Devpost confirmation
  exists;
- no public Git remote or independent server timestamp exists yet.

These statements describe the baseline only. The living
`HACKATHON_HANDOVER.md` controls current status after later work.

## 7. Planned independent experiment anchor

Before the first GPT-5.6 investigation of DC01, the project must publicly bind:

- exact source commit;
- prompt hashes;
- tool-catalog digest;
- dependency lock and runtime versions;
- evidence hashes;
- rubric and scoring-code hashes;
- model alias;
- caps, retry policy, and price-table digest;
- metric definitions;
- infrastructure-fault definition;
- primary-run selection rule.

The freeze commit will be pushed publicly, tagged, and checked by a
server-timestamped CI run that recomputes every digest. A local commit alone is
not described as immutable or unimpeachable.

## 8. Artifact provenance rules

- Every public runtime number must derive from a verified authentic-run bundle.
- Requested and provider-returned model identities must be stored separately.
- Fake-model fixtures and synthetic receipts must remain labeled as offline
  controller tests.
- Every valid post-freeze run and every invalid attempt required by the frozen
  protocol must remain disclosed.
- Evidence archives, recovered malware, credentials, secrets, private-case
  output, and answer keys must never be committed.
- A resolving citation proves traceability, not semantic support.
- Project-authored evaluation must not be described as independent human
  evaluation.
- Final proof links, freeze links, tags, release links, workflow links, and the
  submission commit must be appended here when they exist.

## 9. Provenance ledger

| Date | Event | Independent anchor | Notes |
|---|---|---|---|
| 2026-07-14 | Majority-core Codex thread and successful feedback upload retained | Codex Session ID above | Supports Build Week development history; not runtime proof |
| 2026-07-14 | Honest local Git baseline created | Local commit, to be recorded after creation | Exact content binding; no independent timestamp yet |
| Pending | Public baseline push | Public remote commit | Do not backdate or rewrite |
| Pending | Experiment freeze | Public tag plus server-timestamped digest CI | Must precede first GPT-5.6 DC01 investigation |
| Pending | Authentic primary run | Verified proof bundle | First valid post-freeze run controls |
| Pending | Submission freeze | Public tag and Devpost confirmation | Exact submitted state |
