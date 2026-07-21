# Honest win assessment - OpenAI Build Week (Developer Tools)

**Date:** 2026-07-20 · **Deadline:** 2026-07-21 17:00 PT · **Judging:** 2026-07-22 → 08-05
**Rules source:** <https://openai.devpost.com/rules> (extracted 2026-07-20)
**Track:** Developer Tools · **Project:** Unchained

This is a brutally honest, no-hype read. Every optimistic claim is paired with
its caveat. Verification levels match the handover:
PROVEN / CODE-FIXED / STATIC-ONLY / PENDING.

> **The single most important correction to our own prior notes:** per the actual
> rules, a *valid, competitive* submission does **NOT** require an authentic
> COMPLETE Sol bundle. It requires a **demo video (< 3 min, with audio, showing
> Codex + GPT-5.6)**, a text description, a public repo + license, a README about
> the Codex collaboration, a **Codex Session ID**, **working test access a judge
> can run**, and install/test instructions. Our real blocker is the **video**,
> not the COMPLETE run.

## How the four criteria are actually scored

All four are **equally weighted**:

1. **Technological Implementation** - "How thoroughly and skillfully does the
   project use **Codex**?" (the *build* process, not the runtime AI).
2. **Design** - a **working/runnable** project with a complete, coherent product
   experience.
3. **Potential Impact** - a **credible, specific** case for a real problem.
4. **Quality of the Idea** - how **creative and novel** the concept is.

## Scorecard (honest, adversarially tempered)

| Criterion (equal weight) | Score | Honest rationale |
|---|---:|---|
| Technological Implementation (Codex usage) | **6.0 / 10** | We have a "Built with Codex" section and a Codex Session ID, but this criterion rewards *showing* skillful Codex collaboration. Until the video and README foreground the Codex workflow concretely (what Codex built, decisions, acceleration), this is middling. A strong, specific Codex-collaboration story could lift it to 7–8. |
| Design | **7.5 / 10** | Genuinely strong after this session: one-command self-driving `sentinel`, a `$0` no-key path a judge can run (profile a fixture, `verify`/`view` a supplied bundle, offline container), an offline byte-exact verifier, honest cards. Risk: a judge who tries a *full paid run* without a tiered OpenAI account stumbles (429/PARTIAL); the Linux/macOS/Docker paths are STATIC-ONLY (unproven on real hosts). |
| Potential Impact | **7.0 / 10** | Specific and credible: auditable, inspectable autonomy for high-consequence AI agents acting on evidence ("a transcript is not an answer; here is a sealed, offline-verifiable bundle of exactly what the AI did"). Caveat: DFIR is niche; the broader "any high-consequence agent" framing must land in the video, not just the docs. |
| Quality of the Idea | **8.0 / 10** | Our strongest dimension. The **authority split** (the model chooses strategy; deterministic code owns evidence, execution, citations, custody, and the report) plus an **offline, byte-exact proof bundle** is novel and defensible, and differentiates us from "agent that runs tools." |
| **Average** | **≈ 7.1 / 10** | Solid, idea-led, with a real execution/mandatory-item gap. |

> Adversarial reality check: **without the demo video the effective score is
> "incomplete," not 7.1.** The average above assumes a competent video ships and
> the no-key judge path works on first try.

## Win probability (honest)

- **If** a compelling < 3-min video ships **and** the no-key judge path is smooth:
  **~12–18%** chance of a **1st or 2nd** in Developer Tools.
- **Without** the video, or if the live demo stumbles: **~0%** (an incomplete or
  unrunnable submission does not place).

Why not higher: eight prize categories with 1st/2nd each means a strong field;
"skillful **Codex** usage" is a criterion many teams will target head-on, and it
is our weakest-evidenced dimension today; and our headline "autonomous DFIR with
verifiable proof" is impressive only if the judge sees it *work*, not just reads
claims. Why not lower: the idea is genuinely novel, the no-key verifiable
experience is a real, runnable differentiator, and the submission-mandatory items
are nearly all in place - the gap is executable in the time remaining.

## What must be true to WIN (separated honestly)

**Mandatory for a valid submission (the real gate):**

| Requirement | Status | Note |
|---|---|---|
| Demo video < 3 min, audio, shows Codex + GPT-5.6 | **PENDING** | The true blocker. Must show the Codex build story *and* a live GPT-5.6 run. |
| Text description of features | PARTIAL | README/DevPost draft covers it; needs a tight submission writeup. |
| Public repo + license | **PRESENT** | Public, MIT. |
| README describing Codex collaboration | **PRESENT** | "Built with Codex" section + workflow notes; strengthen with specifics. |
| Codex Session ID | **PRESENT** | `019f61e5-5755-7a02-adb4-618d32baab27` - re-confirm it is the final core thread. |
| Working test access a judge can run | **PRESENT** | No-key path: profile the fixture, `verify`/`view` a supplied bundle, offline container. This is a genuine strength. |
| Install/test instructions (required for dev tools) | **PRESENT** | One-command flow + START-HERE + JUDGE-QUICKSTART. |

**Optional but strengthening (NOT required by the rules):**

- An authentic **COMPLETE GPT-5.6 Sol bundle** verified with
  `--require-complete --require-live-gpt56`. It would elevate Design and Impact
  from "runnable + a capped live opening" to "full lifecycle proven," but it is
  **not** a rules prerequisite. Blockers remain real: OpenAI account **TPM tier**
  (serializer packet ~271k > new-account 200k limit → 429), **token headroom**
  (lifecycle can exceed the 400k HEAVY cap), and a **real memory image**.

## SWOT

- **Strengths:** novel authority-split idea; offline, byte-exact verifiable proof
  bundle; a real no-key experience a judge can run in minutes; honest,
  non-overstating UX; a live GPT-5.6 Sol capped opening on real memory already
  retained.
- **Weaknesses:** no demo video yet; Codex-usage evidence is thin for a criterion
  that weights it equally; no authentic COMPLETE run; Linux/macOS/Docker are
  STATIC-ONLY; niche (DFIR) headline.
- **Opportunities:** the no-key verifiable path is rare and demo-friendly; the
  "inspectable autonomy for any high-consequence agent" framing generalizes the
  impact; a crisp Codex-collaboration narrative can directly lift the weakest
  criterion.
- **Threats:** strong field across 8 categories; judges may read "no COMPLETE
  run" as incomplete despite the rules; a live demo that 429s/PARTIALs on camera
  would hurt more than help.

## Highest-leverage moves before the deadline (ranked)

1. **Record the < 3-min demo video** (mandatory; lifts Design + Technological
   Implementation). Show, in order: the one-command `sentinel` flow → the `$0`
   no-key card → an offline `verify` returning **VALID** → and the Codex build
   story on screen. Rehearse so nothing 429s live. *Effort: hours. Without this,
   nothing else matters.*
2. **Sharpen the Codex-collaboration story** in the README + video (lifts the
   weakest, equally-weighted criterion). Be specific: what Codex built, which
   decisions it drove, how it accelerated the work; cite the Session ID. *Effort:
   1–2 hours.*
3. **Guarantee the no-key judge path is flawless** on a clean machine (lifts
   Design). Re-run the two-command install → `sentinel` → `verify`/`view` from a
   fresh clone in a fresh terminal; fix any friction. *Effort: 1–2 hours; mostly
   done this session.*
4. **(Optional, high-value) Produce ONE authentic COMPLETE Sol bundle.** Tier up
   the OpenAI account, run HEAVY on a real memory image with deliberate token
   headroom, verify strictly to VALID, and show it in the video. *Effort: hours +
   real spend + a real image; a strong differentiator but not required.*
5. **Freeze the benchmark rubric, then run the comparison** and record
   numerator/denominator/source. *Effort: hours; strengthens Impact if time
   allows.*

## Honest disclosures (do not overstate to judges)

- The authentic **COMPLETE** Sol bundle, the frozen **benchmark**, and the
  **demo video** do **not exist yet**.
- All **Linux/macOS/Docker** claims are **STATIC-ONLY** - read and reasoned, not
  executed on a real host.
- Offline verification proves lifecycle, custody, citations, report, and viewer
  are internally consistent; it does **not** prove the model's forensic
  interpretation is true, and it does **not** authenticate OpenAI.
- The one live milestone that IS real: a GPT-5.6 Sol **capped opening** on a real
  2 GiB Windows memory image, retained and offline-verifiable, terminal state
  intentionally **PARTIAL**.

## Bottom line

**Can we win? Realistically: a modest but real chance in Developer Tools - 
conditional entirely on shipping a strong demo video and a crisp Codex story, on
top of the runnable, verifiable, no-key experience we now have.** The idea and
the proof mechanism are genuinely competitive; the execution gap is the video and
the Codex-usage narrative, both achievable before the deadline. The COMPLETE Sol
bundle would raise the ceiling but is not the gate the rules impose.
