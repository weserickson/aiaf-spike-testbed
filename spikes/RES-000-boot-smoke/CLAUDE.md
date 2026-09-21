# CLAUDE.md

Standing instructions for agents running experiments on a pod. These override your defaults.

This file lives in your spike folder, next to `SPEC.md`, copied there when the spike was
created. That location is deliberate: Claude Code reads `CLAUDE.md` from the working
directory and every directory above it, most specific last — so if the repo root also
carries one, written for a human iterating interactively, this file is the later and more
specific of the two. Nothing enforces that; it is simply where the file sits.

It is also frozen here alongside the spike it governs. Rebuild the image, change the
template, and this spike still runs under the contract it was created with.

Where a rule has a reason attached, the reason matters as much as the rule — if you find yourself
looking for a way to satisfy the letter of a rule while defeating its purpose, stop and ask instead.

---

## Where you are

You are running on a disposable RunPod pod, working on one spike. Your identity and context:

| Variable | Meaning |
| --- | --- |
| `$EXP_ID` | e.g. `RES-142-warmup-length-7b` — Linear key plus slug |
| `$EXP_KEY` | e.g. `RES-142` — the Linear key alone, derived from `$EXP_ID` |
| `$EXP_DIR` | `spikes/$EXP_ID/` — your folder, and the whole of your PR |
| `$S3_PREFIX` | `s3://aiaf-cg-fellowship/p2-selfie/$EXP_KEY/` — heavy artifacts |
| `$SLACK_THREAD` | the thread where you talk to the researcher |
| `$BRANCH` | `exp/$EXP_ID` — already checked out |

**Read these before doing anything else:** `$EXP_DIR/SPEC.md` (your orders) and
`$S3_PREFIX/NOTES.md` (what a previous instance of you already tried, if any).

The pod is cattle. Anything that exists only on this pod is already lost. Commit and sync
continuously.

---

## The spec is binding

`SPEC.md` is the contract. You may read it. **You may not edit it.** Changes to the hypothesis,
arms, success criteria or interpretation thresholds come from the researcher, through the thread.

Run the arms listed in section 2. Do not add arms, ablations, seeds, sweeps or "while I'm here"
variants.

**Extra arms are a proposal, not a decision.** When you think of something worth testing — and you
will, constantly — write it in the Parking Lot section of `SPEC.md`. That is the one edit to
`SPEC.md` you may make. The researcher promotes items from the parking lot; you never do.

Why: every extra arm costs the researcher a decision, and decisions are the scarce resource here,
not compute. A parked idea is not a lost idea.

---

## Repo layout and code discipline

```
spikes/$EXP_ID/
├── SPEC.md           your orders (read-only to you, except the Parking Lot)
├── report.ipynb      the product
├── run_experiment.py the code
├── manifest.json     how to reproduce this run
└── logs/             gitignored, synced to S3
```

**Copy, do not factor.** Copying whole files from another spike folder is correct and expected. Do
not extract shared helpers across folders. Do not create, modify or delete anything in `src/`.

Why: the moment a spike depends on shared code, a later change to that code makes this spike hard to
reproduce. That cost lands on the researcher weeks from now, when the context is gone. Duplication
is the cheaper problem. This will feel wrong. Do it anyway.

If you believe something genuinely belongs in `src/`, put it in the Parking Lot. The test for
promotion is *stability*, not reuse — "we use this twice" is the wrong reason — and you are not in
a position to judge whether something has stopped changing.

**Scripts do the work; the notebook reports it.** Write `.py` files, run them from the command
line, collect logs. Never paste scripts into the notebook. The notebook is the report, not your
workspace.

---

## Talking to the researcher

Everything goes in `$SLACK_THREAD`. One mechanism covers every case: **notify, block, default.**

1. Post your question **with the default you will take**.
2. State the deadline as a clock time.
3. Wait the window. Keep any compute already in flight running while you wait.
4. No reply → take the default, and record it in the report.

### Message format

Every post opens with a header line and closes with a footer:

```
❓ ASK · RES-142-warmup-length-7b · pod a3f9
Cosine or linear decay for the warmup tail?
Defaulting to cosine at 14:32 unless you say otherwise.
— 22m elapsed · $4.10 spent
```

Types: `📊 STATUS` · `❓ ASK` · `🔑 AUTH` · `✅ DONE` · `💀 FAILED`.

### Rules

- Never `@channel` or `@here`. Never mention anyone but the researcher.
- Never post outside your own thread.
- One question per post. If you have three, you have one post with three numbered questions and
  three defaults.
- `STATUS` at checkpoints only, not on a timer. Silence is fine; nobody wants a heartbeat.
- Re-read the thread at every checkpoint and every natural stopping point. The researcher may give
  you unprompted feedback at any time, and it takes precedence over your current plan.
- Write anything you learn from the thread into `NOTES.md`. Your context will not survive a
  restart; that file will.

### Timeouts

| Situation | Window | Default if no reply |
| --- | --- | --- |
| Decision during a run | 10 min | your stated proposal |
| Smoke gate still failing after one retry | 10 min | your stated proposal |
| Spend projected over ceiling | 10 min | do not run |
| Max runtime reached | 30 min | terminate |

---

## Cost

GPU time is the only cost that matters. Your own token usage is noise; do not mention it.

| Projected cost | What you do |
| --- | --- |
| Under $25 | Proceed. Log it. Say nothing. |
| $25–50 | Proceed. Flag it in the report. |
| Over $50 | Stop and ask. Default is do not run. |

Project the cost from the smoke run's measured throughput **before** launching the real run, and
write it into the Budget section of `SPEC.md`. A cap that only fires after the money is gone is not
a cap.

Check the running total continuously. Crossing $50 mid-run is an `ASK` with terminate as the
default.

Max runtime is 12 hours unless `SPEC.md` says otherwise.

Do not ask about small amounts. A $10 experiment is not a problem and never needs approval.

---

## Smoke gate

Before any real run, execute a two-minute toy version: smallest model, one or two steps, a handful
of samples, every code path exercised including checkpoint writes and S3 sync.

On failure you get **one** auto-fix and **one** retry. If the retry also fails, post the failure,
your diagnosis and your proposed fix, and follow the standard loop.

The auto-fix may touch code and config only. **Never `SPEC.md`.** Dropping an arm or relaxing a
threshold to make the smoke test pass is the exact failure this rule exists to prevent.

Commit the fix separately with a message starting `smoke-fix:` and name it in the report.

---

## Artifacts

Code and report go in git. Everything heavy goes to S3.

| Goes to S3 | Never in git |
| --- | --- |
| `logs/`, `metrics/`, `plots/`, `checkpoints/` | checkpoints, datasets, raw logs |

Sync with `aws s3 sync` (or `s5cmd`) every 30–60 seconds and once more on exit. S3 has no append;
do not upload per line.

The RunPod network volume is a cache for datasets and weights. It is not storage. Nothing lives
only there.

**`manifest.json`** lives in the repo folder and records: git SHA, container image **digest** (not
tag), the exact `run_experiment.py` invocation, resolved config, dataset version, seeds, pod type,
S3 prefix. Someone must be able to reproduce this run from the manifest alone.

The S3 prefix is keyed by `$EXP_KEY`, not `$EXP_ID`. Slugs get rewritten when a spike
is renamed; the issue key does not. A prefix built from the slug would strand every
artifact written under the old name. You do not construct this path yourself — the pod
derives it and refuses to boot if it disagrees with anything passed in.

**`NOTES.md`** is your running log: what you tried, what happened, what you concluded, what you
decided and why. Append as you go, sync to S3. It is the memory that survives your context window,
and it is what you write the report from.

---

## The report notebook

`report.ipynb` is the product. The bar: understandable by someone with an ML background and no
context on this project.

**Header** — Title matching the issue · Date · Goal (1–3 sentences) · Context (a paragraph on what
came before and why it matters). Goal and Context come from `SPEC.md`.

**Body** — labelled sections that read in order. After every figure or table, interpret it: what it
shows, what it means for the research question, how it connects to the goal. Keep cells modular.

**Figures** — label every axis, include legends, make each one interpretable without reading the
surrounding code. **A figure with no value gets deleted, not captioned.** Do not produce nine plots
because you can.

**Fixed closing sections**, in this order, every time:

1. Headline result against the pre-registered interpretation in `SPEC.md`
2. What was surprising
3. What would make this wrong
4. Decisions defaulted without the researcher
5. Cost
6. Parking lot
7. Recommended next step

Section 3 is not optional and not a formality. You are systematically overconfident about your own
results; state the concrete thing that would overturn them.

---

## Git and finishing

- Commit as you work. Push continuously. The branch should be followable in real time.
- Never merge. Never touch `main`. Never force-push.
- Never commit secrets, checkpoints, datasets or logs.

**When the experiment ends**, do not open the PR yet. Post `DONE` with the headline result and wait
for a consultation session: you and the researcher talk through what the results mean. Write the
notebook after that conversation, not before.

Then, and only then: open a **draft** PR titled `$EXP_ID`, labelled `experiment`, with a description
carrying the research question, what changed, and the key findings. Post one line to Linear with the
result and the PR link. Then terminate the pod.

Any other ending is a `FAILED` post with your last logs. Never exit silently.

---

## Never

- Edit `SPEC.md` outside the Parking Lot
- Add experimental arms without approval
- Create or modify anything in `src/`
- Extract shared code across spike folders
- Merge, or push to `main`
- Edit Linear issue titles, descriptions or fields — comment only
- Paste scripts into the notebook
- Ask about amounts under $25
- Sit idle waiting for a human with no timeout running
