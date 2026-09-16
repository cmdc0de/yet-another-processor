---
name: implement-m
description: >
  Implement the current sequence's unfinished milestone from its spec
  docs, write a test walkthrough, commit and push, then sync the user's
  checkout so they can run tests without a manual git pull. Use when
  implementing a milestone, "implement m1", after a spec plan is agreed,
  or when the user runs /implement-m.
user-invocable: true
argument-hint: "[sequence] [mN|close]"
---

# implement-m

Implement one spec milestone. Counterpart to the `spec` skill. Read that skill’s layout; do not invent paths.

Read `docs/project-goals.md`, then the sequence’s `docs/<slug>/features.md`.

This skill implements. It does not spec. If `features.md` or `milestones/m<N>-plan.md` is missing, stop and tell the user to run `/spec`.

## Choose sequence and milestone

Sequence (`<slug>`) from the user argument, else the sequence that has `claimed` features and an unimplemented milestone. If more than one qualifies, ask. Vocabulary is **sequence**, not “principal”. The catalog file is `features.md`, not `feature.md`.

Milestone is the user argument (`m1`, `m2`, …) else: for implement, the **smallest N** still `claimed`; for close, the **smallest N** that is `implemented`. Never skip an unfinished earlier milestone. Never pick the largest N just because it is latest. Do not re-implement a milestone whose features are already `implemented` or `done`.

Required files (must already exist from `/spec`):

- `docs/<slug>/features.md`
- `docs/<slug>/milestones/m<N>-plan.md`
- `docs/<slug>/milestones/m<N>-testplan.md`
- `docs/<slug>/design.md` when the plan depends on a frozen contract

If those files exist only as uncommitted drafts, stop. Spec docs must be committed first.

## Implement

Read the plan, the testplan, and `design.md` if present. Implement **only** the feature IDs listed on that plan. Leave `open` features and later milestones alone.

Code goes at the repo-root paths in project-goals (`compiler/`, `emu/rust/`, `os/`, `lt-spice/`, …), not under `docs/`.

Satisfy every check in `m<N>-testplan.md`. Do not rewrite that file; it is the agreed acceptance contract.

## Walkthrough (`m<N>-walkthrough.md`)

After the code exists, write `docs/<slug>/milestones/m<N>-walkthrough.md`. Do **not** name it `m<N>-test-plan.md` or overwrite `m<N>-testplan.md`.

```markdown
# <Sequence> m<N> walkthrough

Checkout: the tree after this commit. Commands assume repo root.

## <feature ID> — <short name>
1. Command (cwd, exact invocation)
2. Expected output / pass condition (from m<N>-testplan.md)
```

One section per testplan check, in the same order. Commands must be runnable by the user in their checkout with no extra setup beyond what the walkthrough states.

## Update `features.md` after implementation

In the same turn as the walkthrough, before commit, update every feature ID from this milestone:

1. Wrap the Feature cell in `~~...~~` (strikethrough). If it is already struck, leave it.
2. Set Status to `implemented`.
3. Set Milestone to `m<N>` (spec usually already filled this when the plan was claimed; write it if it is empty). Do not put “implemented in mN” in the Feature text — the Milestone column is that note.

Do not delete rows. Do not strikethrough `open` features. Do not mark `done` yet.

`/implement-m close` (or the user says “mN passed”) after they run the walkthrough: set those IDs to `done`, keep the strikethrough and Milestone, commit `features.md`, push, sync checkout.

## Commit, push, sync checkout

After implementation + walkthrough (or after close):

1. Stage only files from this milestone (code, tests, `m<N>-walkthrough.md`, and `features.md`). On close, stage `features.md` only if nothing else changed. Do not stage unrelated dirty files (including leftover deletions).
2. Commit. Message: `Implement <slug> m<N>: <one line>` or `Mark <slug> m<N> features done`.
3. `git push` to the tracked remote.
4. Sync the **user checkout** so they do not have to `git pull` by hand.

User checkout, first match:

- `$YAP_CHECKOUT` if set
- `/home/cmdc0de/dev/yet-another-processor` if it exists and `origin` URL matches this repo
- otherwise ask

Sync:

```bash
git -C <checkout> status --porcelain
git -C <checkout> rev-parse --abbrev-ref HEAD
```

- Same branch as we pushed, porcelain empty → `git -C <checkout> pull --ff-only`.
- Dirty or pull would not fast-forward → **do not overwrite**. Tell them what blocked it and the commit hash. Do not `reset --hard`. Do not rsync over a dirty tree.
- If this process is already in the user checkout, skip the second-tree pull.

Tell them the commit hash, the walkthrough path in **their** tree, and to run those commands. Stop. Do not declare the milestone done.

## Chat shape

- Start: sequence, mN, feature IDs being implemented.
- End: files changed, commit, push, whether the user checkout was pulled, walkthrough path, “run this then say if it passed”.
