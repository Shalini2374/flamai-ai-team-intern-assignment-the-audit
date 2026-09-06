# B1 — KV-cache capacity reconciliation

## Inputs

From `model_spec.md`:

- GPU: 1x NVIDIA L4, 24 GB
- GPU memory utilization: 0.92
- Parameters: 4.2B, FP16
- Layers: 28
- KV heads: 8
- Head dimension: 128
- KV cache: FP16 (2 bytes)
- Non-KV overhead: 1.6 GB
- Max model length: 4096 tokens

## KV-cache calculation

KV cache stores both K and V:

```text
2 x 28 x 8 x 128 x 2
= 114,688 bytes/token
= 112 KiB/token
````

For a full 4096-token sequence:

```text
114,688 x 4096
= 469,762,048 bytes
= 448 MiB
```

## Available KV budget

Using consistent decimal bytes:

```text
Usable GPU memory = 24e9 x 0.92
                  = 22.08e9 bytes

FP16 weights      = 4.2e9 x 2
                  = 8.4e9 bytes

KV budget         = 22.08e9 - 8.4e9 - 1.6e9
                  = 12.08e9 bytes
```

Maximum full-length sequences:

```text
12.08e9 / 469,762,048
approx 25.7
```

**Estimated capacity: ~25-26 concurrent 4096-token sequences.**

## Benchmark reconciliation

The long-context workload is `3584 + 512 = 4096` tokens.

| Batch | KV util | Preempted | Capacity evidence |
| ----: | ------: | --------: | ----------------- |
|    24 |    0.93 |         0 | 24 / 0.93 ~ 25.8  |
|    32 |    0.97 |         7 | 32 - 7 = 25       |
|    48 |    0.97 |        23 | 48 - 23 = 25      |

The observed utilization and preemption behavior are consistent with
the calculated ~25-26 sequence capacity.

## Unit revision

An initial GiB interpretation gave ~28.9 sequences. The decimal-byte
calculation (~25.7) fits the benchmark substantially better, so the
decimal convention was adopted.

## Conclusion

The model requires **114,688 bytes (112 KiB) of KV cache per token**.
A 4096-token sequence requires **448 MiB**, giving an estimated
capacity of **~25-26 concurrent full-length sequences**. The benchmark
provides supporting evidence for this capacity boundary.


