# Sentinel Unchained repository instructions

`docs/WINNER_ROADMAP.md` controls Build Week priority, sequence, positioning,
and go/no-go gates. `docs/HACKATHON_MASTER_PLAN.md` owns the detailed
experiment, proof, judge-experience, prompt, and submission contracts.
`HACKATHON_HANDOVER.md` is the living execution-status source of truth. Read all
three before substantial work.

For every material implementation, verification, artifact, scope, schedule, or
submission-status change:

1. Update `HACKATHON_HANDOVER.md` in the same work session.
2. Preserve the distinction between `IMPLEMENTED`, `VERIFIED`, and
   `DEMONSTRATED`; do not mark work complete without the required evidence.
3. Record exact commands/outcomes and link retained artifacts.
4. Update the applicable gate, daily checklist, risk, change log, and single
   next action.
5. Preserve the verified prior-work versus Build Week boundary. Never backdate
   provenance or reuse Qwen metrics/artifacts as Unchained proof.
6. Verify current event rules by opening the live 2026 Official Rules directly;
   cached search results may contain the unrelated 2025 gpt-oss event.
7. Update `docs/HACKATHON_MASTER_PLAN.md` whenever a verified rule, thesis,
   flagship scope, experiment, public claim, hard gate, judge path, prompt, or
   submission requirement changes. Keep status evidence in the handover rather
   than duplicating unsupported completion claims in the master plan.
8. Update `docs/WINNER_ROADMAP.md` when priority, execution order,
   preregistration, scope-cut, or go/no-go logic changes. Never run GPT-5.6 on
   the scored DC01 case before the public experiment freeze defined there.

Before handing off code changes, run the narrowest relevant tests and then:

```powershell
python -m pytest
python -m ruff check .
```

Never expose or commit API keys, private forensic evidence, provider secrets, or
unsanitized private-case tool output.
