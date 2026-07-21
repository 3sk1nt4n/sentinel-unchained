## Inspiration

Agentic AI produces a transcript: a self-reported story of what the model says it did. In DFIR nobody can act on that - not an incident-response consultancy facing a regulator or opposing counsel, not an expert witness. The gap is structural: the model's narrative and the evidentiary record are the same object, so nothing checks the narrative. Unchained separates them. The thesis in one sentence: agentic AI in high-consequence domains is only sellable when every action it took can be checked by someone who trusts neither the agent, the vendor, nor the transcript.

## What it does

GPT-5.6 chooses where to look; deterministic code controls what may run and verifies exactly what was executed and cited.

Try it in 60 seconds, $0, no API key:

    git clone https://github.com/3sk1nt4n/Unchained.git; cd Unchained
    .\setup.ps1
    sentinel verify examples/public-run-complete --require-complete --require-live-gpt56

That prints VALID - 37 artifacts, 194 hash-chained audit entries: byte-exact offline re-verification of a real GPT-5.6 Sol COMPLETE investigation that ships in the repo (run 20260721T001718Z-f0cd5641): 31/31 typed Volatility tools across 20 adaptive turns on the public 2 GiB DC01 domain-controller memory image, 4 adjudicated findings (1 CONFIRMED / 2 NEEDS-REVIEW / 1 UNSUPPORTED) after a fresh-context downgrade-only review - $2.92, 9m39s, custody match. Two more retained runs ship beside it (an honest PARTIAL bundle and a sanitized Sol opening receipt); we keep PARTIAL and INVALID states rather than cherry-pick.

How: code profiles evidence with zero model calls and seals SHA-256 custody; GPT-5.6 opens with up to twelve typed tools that code validates all-or-none and runs in parallel; later turns allow one typed action each; a typed finish_investigation(status="DONE") forces structured findings; deterministic code resolves exact byte spans, renders the authoritative report and inert no-JS viewer, seals a content-addressed bundle, and verifies the whole lifecycle offline. Exactly 4 fixed GPT-5.6 requests plus one per adaptive action - never an unbounded loop. The Linux lanes were executed live on 2026-07-21; the Windows-sealed bundle strict-verifies VALID inside the no-network Linux container, byte-exact across operating systems.

Honest limits, kept on purpose: one public case on one flagship OS route; no measured competitive benchmark (deliberately cut - no unmeasured claims); receipts prove execution and citation support, not forensic truth; bundles are locally sealed (signed external anchoring is future work).

## How we built it

Codex Session ID: 019f61e5-5755-7a02-adb4-618d32baab27 (core build; /feedback uploaded). Codex was the primary implementation and adversarial-review collaborator: evidence lifecycle, Responses API adapter, typed execution boundary, caps, typed-DONE-v2 protocol, forced serializer, exact evidence spans, downgrade-only review, renderers, independent offline verifier, CLI, Docker isolation, and the 378-test offline gate (ruff clean). A second Codex thread (019f76f3-a19f-71d1-81b2-eed6305857f6) carried the Docker/README/release work. The human owned the product thesis, the authority split, the DFIR testbed and DC01 case, the hard caps, the scope cuts, and every public claim. At runtime, GPT-5.6 Sol is both the investigator and the reviewer; GPT-5.6 Terra is the cheap rehearsal lane behind an explicit launch card and key step.

Unchained is not an LLM pretending to be evidence. It is GPT-5.6 directing a bounded investigation whose actions, citations, custody, and final report can be checked independently.

Full detail - challenges, accomplishments, what we learned, what's next - ships in the repo: submission/DEVPOST-DESCRIPTION-FINAL.md.
