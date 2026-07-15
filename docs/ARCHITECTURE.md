# Sentinel Unchained Architecture

Sentinel Unchained is a trust-measurement harness for model-directed digital-forensics investigations. The forensic case is the testbed. The product is the auditable boundary around an autonomous investigator.

## Pipeline and trust boundary

```text
evidence folder
      |
      v
PROFILE + ROUTE [deterministic]
  classify content, detect evidence OS/shape, hash custody, capability label
      |
      v
OPENING BOOK [GPT-5.6] -- chooses up to six available typed tools
      |
      v
parallel typed execution [deterministic authority]
      |
      v
PLAN -> ACT -> OBSERVE -> UPDATE loop [GPT-5.6]
      |             one typed tool per turn, hard caps enforced by code
      v
literal DONE -> forced serialization [deterministic protocol]
      |
      v
FRESH JUDGE [GPT-5.6] -- preserve or downgrade only
      |
      v
REPORT [GPT-5.6] -> content-addressed proof bundle
      |
      v
post-run SHA-256 custody verification [deterministic]
```

The model may choose tools, arguments, hypotheses, stopping point, labels, and report prose. It cannot access a shell, open an arbitrary path, change evidence, bypass the typed tool registry, change audit records, or raise a cap. Code owns custody, tool authority, append-only audit recording, protocol validation, and resource limits.

## Deterministic safety floor

| Domain | Guarantee | Limit, stated plainly |
|---|---|---|
| Evidence | Inputs are profiled and SHA-256 hashed before and after execution. | The application detects a mismatch; it is not an externally immutable evidence vault. |
| Tools | Only registered typed forensic functions execute. Arguments are validated and no model-generated shell command runs. | A registered tool can still return incomplete or tool-specific output. |
| Audit | Model messages, calls, output excerpts, hashes, usage, timestamps, and cost estimates are recorded in JSONL. | App-level append-only behavior is not a tamper-proof external ledger. |
| Caps | Tool calls, tokens, wall time, and estimated spend have hard limits; a fired cap produces a PARTIAL result. | Provider billing and network failures remain outside local enforcement. |

## Observed behavior and current status

The pre-freeze DC01 rehearsal is retained as non-primary evidence. The opening book selected `vol_pstree`, `vol_psscan`, `vol_netscan`, `vol_malfind`, `vol_cmdline`, and `vol_svcscan`. These executed through typed functions, retained content-addressed outputs, and passed final custody matching. The large `vol_netscan` result exercised the bounded 65,536-byte model-view receipt path. The run stopped before judge and report because the Responses replay contained a provider-only `status` field. Commit `57e6124` removes that field during replay and adds a regression test. The judge and report legs are implemented and their first complete live exercise is intentionally reserved for the post-freeze primary run.

## Data boundary

The provider receives the neutral evidence profile, model messages, typed tool arguments, and retained tool output needed for the investigation. The evidence file itself is read locally by the native tools. Requests use `store=false`; prompt caching is disabled where the provider surface supports that option. Operators must still review sensitive output before sending a case to an external provider.

## Budget and model policy

The repository currently supports GPT-5.6 and GPT-5.6 Sol identifiers only. There is no alternate-provider smoke mode and no cheaper model that can produce a scored result.

| Mode | Tool calls | Tokens | Wall time | Estimated cap |
|---|---:|---:|---:|---:|
| `strict` rehearsal | 20 | 100,000 | 600 s | $2.50 |
| `default` / scored | 60 | 400,000 | 1,800 s | $10.00 |

`run.ps1 -Caps strict` now applies the strict values to the child process. Runtime cost is billed to the operator's API project, not Codex credits. The estimator is deliberately conservative and must not be presented as a provider invoice.

## Provenance receipts and verification

Each accepted provider response records the provider-returned model identity, response ID, request correlation where available, validated usage, and the exact retained tool-output artifacts cited by findings. `verify-run` checks the manifest, artifact hashes, citation resolution, response metadata, and custody result. `--require-live-gpt56` additionally rejects fake or replay-only evidence for a scored run.

Relevant implementation modules are `unchained.evidence`, `unchained.tools`, `unchained.audit`, `unchained.caps`, `unchained.artifacts`, `unchained.model`, and `unchained.verify`.
