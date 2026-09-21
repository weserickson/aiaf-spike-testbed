"""RES-000-boot-smoke: noop arm.

Exercises the pod boot path end to end: CUDA availability, a real kernel
launch, a checkpoint write, and a log write. No hypothesis, no metrics beyond
pass/fail.
"""
import argparse
import json
import time
from pathlib import Path

import torch

EXP_DIR = Path(__file__).resolve().parent
SEED = 0


def main(seed: int) -> None:
    assert torch.cuda.is_available(), "CUDA not available"
    device = torch.device("cuda")

    torch.manual_seed(seed)
    a = torch.randn(1024, 1024, device=device)
    b = torch.randn(1024, 1024, device=device)
    start = time.time()
    c = a @ b
    torch.cuda.synchronize()
    elapsed = time.time() - start
    checksum = c.sum().item()

    (EXP_DIR / "logs").mkdir(exist_ok=True)
    (EXP_DIR / "checkpoints").mkdir(exist_ok=True)

    log_line = (
        f"noop: device={torch.cuda.get_device_name(0)} "
        f"matmul_1024x1024_s={elapsed:.4f} checksum={checksum:.4f} seed={seed}\n"
    )
    with open(EXP_DIR / "logs" / "noop.log", "a") as f:
        f.write(log_line)

    torch.save({"checksum": checksum, "seed": seed}, EXP_DIR / "checkpoints" / "noop.pt")

    result = {"device": torch.cuda.get_device_name(0), "matmul_seconds": elapsed, "checksum": checksum}
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    main(args.seed)
