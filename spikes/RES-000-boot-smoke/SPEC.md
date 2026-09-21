# RES-000-boot-smoke

Throwaway spike. It exists to exercise the pod boot path end to end, nothing else.
Delete the repo once the automation is trusted.

## 1. Hypothesis

None. This is not an experiment. The question it answers is operational: does a pod
boot, authenticate, clone, read this file, run something on the GPU, sync to S3 and
terminate cleanly, without a human touching it?

## 2. Arms

One, called `noop`:

- import torch, assert `torch.cuda.is_available()`
- run a small matmul so a real CUDA kernel executes
- write one line to `logs/noop.log` and one small file to `checkpoints/`
- write `manifest.json`
- write DONE to `.supervisor-status`

Do not add arms. There is nothing here to sweep.

## 3. Success criteria

The gate is operational, not empirical:

- the smoke gate passes
- `manifest.json` records a non-null image digest and a GPU
- artifacts appear under `s3://aiaf-cg-fellowship/p2-selfie/RES-000/`
- the supervisor posts DONE and the pod terminates on its own

## 4. Interpretation

Pre-registered, so there is nothing to argue about afterwards:

- all four criteria met -> the boot path works; write the report and stop
- any criterion missed -> FAILED, with the logs. Do not retry more than the one
  auto-fix the smoke gate allows

## 5. Budget

Ceiling $5. This should cost cents. Anything approaching the ceiling means something
is wrong and terminating is the right answer.

Max runtime 30 minutes.

## 6. Parking Lot

_Ideas go here. The researcher promotes them; you never do._
