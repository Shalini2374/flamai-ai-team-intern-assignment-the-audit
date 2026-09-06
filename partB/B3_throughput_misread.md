# B3 — Throughput-column misread

## 1. What does `reported_tok_s` count?

For the batch-24 long-context row:

```text
prompt_len   = 3584
gen_len      = 512
num_requests = 24
wall_clock_s = 61.16
reported_tok_s = 1607.4
```

Reconstructing the reported value:

```text
(3584 + 512) × 24
= 4096 × 24
= 98,304 tokens

98,304 / 61.16
= 1607.4 tok/s
```

Therefore:

```text
reported_tok_s
= (prompt_len + gen_len) × num_requests
  / wall_clock_s
```

The arithmetic is correct. The issue is how this metric is interpreted.

## 2. Why is this misleading as generation throughput?

`reported_tok_s` combines prompt/prefill tokens and generated/decode
tokens into one numerator.

For the long-context workload:

```text
3584 prompt tokens
+ 512 generated tokens
= 4096 counted tokens/request
```

Thus 87.5% of the counted tokens are prompt tokens:

```text
3584 / 4096 = 87.5%
```

Prefill and decode are different phases with different performance
characteristics. Therefore, the combined token rate should not be
interpreted as pure generation/decode throughput.

## 3. Why does the long prompt appear better at batch 16?

For the short-prompt workload:

```text
512 prompt + 256 generated
= 768 tokens/request
```

For the long-prompt workload:

```text
3584 prompt + 512 generated
= 4096 tokens/request
```

Because `reported_tok_s` counts both types of tokens, the long-prompt
row puts many more prompt tokens into the numerator.

At batch 16:

- Short prompt: **883.2 reported tok/s**
- Long prompt: **1311.4 reported tok/s**

This does not demonstrate that long prompts have better generation
throughput. It reflects the fact that the metric counts the much larger
prefill token volume in the long-prompt workload.

## 4. Honest batch-24 goodput

### Way A — generated tokens over total wall-clock time

Only count tokens actually generated for users:

```text
512 × 24
= 12,288 generated tokens
```

Then:

```text
12,288 / 61.16
≈ 200.9 generated tok/s
```

### Way B — ITL-based decode estimate

For batch 24:

```text
itl_ms_p50 = 96.07 ms
batch_size = 24
```

Assuming one decode step produces approximately one token per active
sequence:

```text
24 tokens / 0.09607 seconds
≈ 249.8 generated tok/s
```

The two estimates are not identical because Way A includes the entire
run, including prefill and other serving overhead, while Way B uses the
median inter-token latency to estimate decode-step throughput.

However, both are far below the reported 1607.4 tok/s and are much more
representative of decode-oriented throughput.

### Comparison

| Metric | Approx. rate |
|---|---:|
| Reported combined prompt + generation rate | 1607.4 tok/s |
| Way A: generated tokens / wall-clock | 200.9 tok/s |
| Way B: ITL-based decode estimate | 249.8 tok/s |

The reported 1607.4 tok/s should therefore not be described as pure
generation throughput.

## 5. Corrected interpretation and capacity-planning conclusion

The report should have said:

> `reported_tok_s` is a combined prompt-plus-generation token rate, so it should not be interpreted as pure decode/generation throughput; for batch 24, decode-oriented goodput is approximately 201 tok/s by wall-clock accounting, with an independent ITL-based estimate of approximately 250 tok/s.

> Throughput should not be assumed to scale linearly with batch size: as shown in B2, the long-context workload peaks around batch 24 and then degrades when KV-cache capacity is exceeded and sequence preemptions increase.

## Conclusion

The benchmark arithmetic is internally consistent: 1607.4 tok/s is the
correct value for the reported combined-token metric. The misread is
treating that metric as generation throughput.

For generation-focused analysis, the batch-24 workload produces
approximately 200.9 generated tok/s by wall-clock accounting, with an
independent ITL-based estimate of approximately 249.8 tok/s.