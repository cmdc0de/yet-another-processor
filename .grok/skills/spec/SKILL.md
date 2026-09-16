---
name: spec
description: >
  Spec a sequence: write its feature catalog, slice a milestone off that
  list, agree the plan, write the milestone docs, then commit and push.
  Use when starting a sequence, planning a milestone, writing features.md,
  mN-plan.md, or mN-testplan.md, "spec the ISA", or when the user runs /spec.
user-invocable: true
argument-hint: "[sequence] [catalog|milestone|agree]"
---

# spec

Docs-first workflow for one sequence. This skill writes catalogs and milestone plans. It does not implement.

Read `docs/project-goals.md` before doing anything. Sequences are the **Subprojects** table. Order is **Sequencing principles**. Do not invent a parallel taxonomy.

## Layout

```
docs/<slug>/
  features.md
  design.md              # only if the sequence needs a frozen contract
  milestones/
    m<N>-plan.md
    m<N>-testplan.md
```

`<slug>` is the subproject name, lowercase, hyphenated (`ISA + ABI` → `isa`, `Rust OS emulator` → `emu-rust`). Code still lives at the repo-root paths in project-goals. Spec files always live under `docs/<slug>/`.

## Gates

1. **Draft in chat. Write to disk only after the user agrees.**
2. **Commit and push those docs in the same turn as the write.** Do not stage unrelated dirty files.
3. **Stop.** Do not implement the milestone unless the user explicitly asks after the push.
4. **One sequence at a time**, except sequences project-goals already marks as parallel (MOSFET cell library vs ISA).
5. **Do not write feature catalogs for sequences that are not next** (or parallel).

If the user asks to implement and the milestone docs are not committed, write/commit the docs first or refuse.

## Phase

Pick one from the user prompt and the tree:

| Phase | When | Action |
|---|---|---|
| Catalog | no `features.md`, or user says catalog / start sequence | Draft the full feature list |
| Design | catalog agreed, sequence needs a contract (ISA encodings, ABI, bus protocol), no `design.md` | Draft `design.md` |
| Milestone | `features.md` exists, user wants a milestone | Pull N open features, draft plan + test plan |
| Agree | user says agree / write it / looks good | Write the drafted files, update feature statuses, commit, push |

If the sequence is ambiguous, ask which subproject. Default next sequence is the first unfinished item in Sequencing principles.

## Catalog (`features.md`)

The catalog is the whole sequence’s backlog. It is not a design and not a schedule.

A feature must be:

- Independently completable (can be in a milestone by itself)
- Testable (the test plan can prove it)
- One concern (`ADD with flags`, not `design the ISA`)

Reject or split anything that is a phase, a subproject, or a design decision.

```markdown
# <Sequence> features

Prefix: `<PREFIX>`   <!-- slug, uppercased: ISA, EMU-RUST, OS -->

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| ISA-001 | 32 GPRs, one architectural file | open | |
```

Status is `open`, `claimed`, or `done`. Only a committed milestone plan may set `claimed` and fill Milestone (`m1`, `m2`, …). IDs are `<PREFIX>-NNN`, monotonic, never reused.

Draft the full list for this sequence. Do not leave “TBD later” holes that block the first milestone. Features that belong to a later generation (v1 non-goals in project-goals) stay out, or sit at the end marked as later-generation so they cannot be pulled into m1.

## Design (`design.md`)

Use only when software or hardware cannot proceed without a frozen representation (encodings, privilege bits, calling convention, bus cycles). Features name capabilities; `design.md` specifies representation.

Draft `design.md` after the catalog is agreed and before milestone 1. Do not stuff encodings into `features.md`. Do not start the bundled design-doc write/review loop unless the user asks.

## Milestone (`m<N>-plan.md` + `m<N>-testplan.md`)

N is the next unused milestone number in that folder. Propose a coherent slice; the user sets N (count of features), not a global constant.

Pull only `open` rows. Do not pull later-generation features into an early milestone. In the draft, list the IDs.

`m<N>-plan.md`:

```markdown
# <Sequence> m<N>

Features: ISA-001, ISA-004, ISA-005

## Intent
One paragraph.

## Work
- ...

## Done
Testable bullets, one per feature ID.

## Out of scope
Features explicitly not in this slice.
```

`m<N>-testplan.md`: one acceptance check per claimed feature ID. If a feature cannot be tested, it is not a feature — go back to the catalog.

On agree: write both files, set those rows to `claimed` / `m<N>` in `features.md`.

## Commit

After a successful write:

```bash
git add docs/<slug>/features.md docs/<slug>/design.md docs/<slug>/milestones/m<N>-plan.md docs/<slug>/milestones/m<N>-testplan.md
```

Add only files that exist and were part of this agree step. Commit, then `git push` to the tracked remote. Commit message: what sequence and phase (`Add isa feature catalog`, `Add isa m1 plan`).

Tell the user the commit hash and that implementation is a separate turn.

## Chat shape

- Catalog/milestone drafts: the tables and plans in the reply, then stop for agreement.
- After agree: paths written, commit hash, push result, what not to do next (do not implement unless asked).
