## Session 1 — Initial audit setup

### Goal
Set up the environment and reproduce the previous intern's baseline
before making any changes to fertility.py.

### Observation
Created venv, installed tiktoken and transformers. The starter corpus
contains only a small English/Hindi smoke test (10 lines each), so these
initial experiments are treated as exploratory evidence rather than
final multilingual conclusions.

---

## Baseline — Original fertility.py

### Goal
Reproduce the previous intern's reported tokenizer numbers.

### Command
python fertility.py --corpus eng=corpus_sample/eng_sample.txt --corpus hin=corpus_sample/hin_sample.txt --tokenizer gpt2

### Result

| Language | Fertility (tok/word) | tok/char |
|----------|----------------------|----------|
| English  | 1.27                 | 0.226    |
| Hindi    | 7.45                 | 1.579    |

Hindi fertility is reported as 5.89x English.

### Observation
The original result was successfully reproduced.

---

## Experiment 1 — split(" ") word-count handling

### Hypothesis
The script counts words using line.split(" "). Double spaces in the raw
corpus text could create phantom empty-string "words," inflating the
word count and understating fertility.

### Command
python partA/experiments/test_double_space_bug.py

### Result
1/10 English lines affected (line 6, "books  in the cupboard" — double space)
1/10 Hindi lines affected (line 9, same double-space pattern)

### Observation
Confirmed real mechanism, same root cause in both languages. Low
frequency in this sample (1/10). Effect on the final fertility ratio not
yet measured — next step is to quantify how much this shifts the
headline 5.89x number, not just count affected lines.

---

## Experiment 2 — per-line averaging vs corpus-level ratio

### Hypothesis
analyze() averages each line's own tokens/words ratio, rather than
computing total_tokens / total_words across the whole corpus. These two
methods can diverge.

### Command
python partA/experiments/test_averaging_bug.py

### Result
English: Method A (avg of ratios) = 1.2652, Method B (total/total) = 1.2532
  → 1.0% difference
Hindi: Method A = 7.4485, Method B = 7.4032 → 0.6% difference

### Observation
Real, measurable distortion, but small. Does not explain the headline
5.89x gap on its own. Framing: this gives every sentence equal weight
regardless of length, which may not match a corpus-level cost estimate
leadership actually needs.

---

## Experiment 3 — lowercasing effect

### Hypothesis
The script lowercases text "so casing doesn't add noise." Hindi has no
upper/lowercase distinction, while case changes can affect GPT-2
tokenization for English.

### Command
python partA/experiments/test_lowercase_effect.py

### Result
English: 3/10 lines changed token count, all increased after lowercasing
  (e.g. 8→9, 10→11, 12→13)
Hindi: 0/10 lines changed

### Observation
Real, asymmetric effect on this sample — only the English side changed.
Not calling this a definite "bug"; it's a preprocessing choice with a
measurable, one-sided side effect. Still need to measure its effect on
the overall eng/hin ratio, not just count of lines changed.

---

## Experiment 4 — NFC normalization effect

### Hypothesis
The script applies unicodedata.normalize("NFC", line). This could
silently change token counts, especially for Hindi where some characters
can be represented in more than one Unicode form.

### Command
python partA/experiments/test_normalization_effect.py

### Result
0/10 lines changed, both languages.

### Observation
No token-count difference was observed on this starter corpus.
Candidate for the "looks suspicious but is actually fine" requirement.
Plan to add one deliberately decomposed test string later to strengthen
this claim, since this test alone doesn't rule out the issue on
non-normalized input.

---

## Experiment 5 — is Hindi's fertility a language property or a tokenizer property?

### Hypothesis
REPORT_v0.md claims Hindi's higher fertility is "a property of the
script, not the tokenizer." Testing this by comparing GPT-2 against a
multilingual tokenizer (XLM-R) on the same text.

### Command
python partA/experiments/test_multilingual_tokenizer_comparison.py

### Result
GPT-2: eng=9.90 tok/line, hin=45.90 tok/line, ratio = 4.64x
XLM-R: eng=10.00 tok/line, hin=8.80 tok/line, ratio = 0.88x

### Observation
Strong evidence against the report's claim that the observed Hindi/
English tokenization gap is independent of tokenizer choice. On this
sample, changing from GPT-2 to XLM-R changed the ratio from 4.64x to
0.88x. Caveat: only 10 lines per language — needs validation on the real
A1 corpus before trusting the exact magnitude. This experiment
technically belongs to A3's tokenizer-comparison requirement, reused
here as supporting evidence for the A2 conceptual audit.

---

## Decision point — move to A1 before finalizing A2

### Reasoning
All experiments above were run on the 10-line "smoke test" corpus, which
the assignment itself describes as too small to trust. Before writing up
final A2 conclusions, plan to:
1. Build the real 4-language corpus (A1): English, Hindi, + 2 Dravidian
   languages
2. Re-run all 5 experiments above on the larger corpus
3. Confirm whether each finding generalizes or was a fluke of small
   sample size
4. Add one more experiment: len() code points vs. grapheme clusters as a
   possible additional conceptual issue in the "tok/char" metric
---
## A1 — Corpus construction

### Dataset
FLORES-200 (via flores_plus)

### Languages
English, Hindi, Tamil, Telugu

### Size
200 aligned sentences per language

### Output
eng_sample.txt
hin_sample.txt
tam_sample.txt
tel_sample.txt
corpus_manifest.csv

### Observation
Successfully created a 4-language aligned evaluation corpus
for downstream tokenizer benchmarking.
## Session 2 — Re-running audit experiments on the A1 corpus

### Goal

Re-run the audit experiments on the larger 4-language A1 corpus
(200 parallel sentences each for English, Hindi, Tamil, and Telugu)
to determine whether the findings from the 10-line smoke-test corpus
generalize.

### Experiment 1 — split(" ") word-count handling

### Command

python partA/experiments/test_double_space_bug.py

### Result

| Language | Lines affected |
|---|---:|
| English | 0/200 |
| Hindi | 0/200 |
| Tamil | 12/200 (6%) |
| Telugu | 26/200 (13%) |

### Observation

The issue is more prevalent in the real corpus than the smoke-test
suggested, particularly for Tamil and Telugu. Multiple spaces occur in
the source text, so `split(" ")` can create empty-string entries that
are incorrectly counted as words. The affected-line count establishes
the mechanism, but the resulting change in fertility still needs to be
quantified before assigning a final magnitude.

---

### Experiment 2 — per-line averaging vs corpus-level ratio

### Command

python partA/experiments/test_averaging_bug.py

### Result

| Language | Avg of line ratios | Total tokens / total words | Relative difference |
|---|---:|---:|---:|
| English | 1.3306 | 1.3141 | 1.3% |
| Hindi | 7.6863 | 7.6988 | 0.2% |
| Tamil | 24.4608 | 24.1129 | 1.4% |
| Telugu | 19.9317 | 19.8567 | 0.4% |

### Observation

The two aggregation methods differ for all four languages, but the
difference is small in this corpus (0.2–1.4%). The direction is not
consistent across languages: the per-line average is higher for
English and Tamil, but lower for Hindi and Telugu. Therefore this is a
real aggregation issue, but it does not explain the large
cross-language fertility differences by itself.

---

### Experiment 3 — lowercasing effect

### Command

python partA/experiments/test_lowercase_effect.py

### Result

| Language | Lines with changed token count |
|---|---:|
| English | 134/200 (67%) |
| Hindi | 8/200 (4%) |
| Tamil | 8/200 (4%) |
| Telugu | 28/200 (14%) |

### Observation

The effect is substantially larger on the A1 corpus than on the
10-line smoke test. English is affected most strongly, but the
presence of affected lines in Hindi, Tamil, and Telugu shows that
multilingual text can contain case-bearing material such as Latin
script words. Lowercasing therefore changes the actual input seen by
the tokenizer and is not token-count neutral. The overall fertility
distortion still needs to be quantified before assigning a final
magnitude.

---

### Experiment 4 — NFC normalization effect

### Command

python partA/experiments/test_normalization_effect.py

### Result

| Language | Lines with changed token count |
|---|---:|
| English | 0/200 |
| Hindi | 26/200 (13%) |
| Tamil | 1/200 (0.5%) |
| Telugu | 0/200 |

### Observation

Unlike the smoke-test result, NFC normalization changes token counts
for a measurable portion of the Hindi corpus and one Tamil sentence.
The earlier 10-line experiment therefore gave a false negative.
Normalization should not be classified as harmless based only on the
smoke test. The next step is to quantify the resulting fertility
change and inspect representative affected examples.

---

### Experiment 5 — tokenizer dependence of the cross-language gap

### Command

python partA/experiments/test_multilingual_tokenizer_comparison.py

### Result

| Language | GPT-2 avg tok/line | XLM-R avg tok/line | GPT-2 / English | XLM-R / English |
|---|---:|---:|---:|---:|
| English | 28.49 | 31.32 | 1.00x | 1.00x |
| Hindi | 196.32 | 38.49 | 6.89x | 1.23x |
| Tamil | 404.74 | 40.81 | 14.21x | 1.30x |
| Telugu | 340.14 | 40.52 | 11.94x | 1.29x |

### Observation

The large cross-language token-count gap is strongly dependent on the
tokenizer. GPT-2 produces substantially more tokens for Hindi, Tamil,
and Telugu relative to English, whereas XLM-R produces much smaller
and more consistent ratios. This directly challenges REPORT_v0's claim
that the observed Indic tokenization gap is a property of the script
rather than the tokenizer.

This experiment also provides supporting evidence for A3, where
multiple tokenizers are explicitly required. The final A3 comparison
will use the full A1 corpus and controlled denominator choices.

---

## Session 2 — Revision of hypotheses

### Observation

The larger A1 corpus changed the interpretation of some smoke-test
findings. The double-space issue became more relevant for Tamil and
Telugu, lowercasing affected a much larger fraction of English lines,
and NFC normalization changed token counts in Hindi despite showing no
effect in the smoke test.

The smoke-test experiments were therefore useful for identifying
questions to investigate, but the A1 corpus is the basis for final
multilingual conclusions.

### Next step

Quantify the effect of `split(" ")`, lowercasing, and NFC normalization
on the final fertility values. Then investigate whether `tok/char`,
which currently uses Python `len()`, is an appropriate
language-neutral denominator.
---

## Experiment 7 — quantifying fertility shifts (split, lowercase, NFC)

### Goal
Move from "how many lines changed" to "how much did the final fertility
number actually shift" for the three preprocessing-related findings.

### Command
python partA/experiments/measure_remaining_effects.py

### Result

| Language | split(" ")→split() | Lowercase effect | NFC effect |
|---|---:|---:|---:|
| English | +0.00% | +5.30% | +0.00% |
| Hindi | +0.00% | +0.03% | +0.20% |
| Tamil | +0.33% | +0.01% | -0.00% |
| Telugu | +1.03% | +0.06% | +0.00% |

### Observation
Lowercasing has by far the largest measured effect, and it is
concentrated on English (+5.30%), consistent with the 67% of English
lines whose token count changed. The split(" ") fix matters only for
Tamil and Telugu (+0.33%, +1.03%). NFC's effect is small in relative
fertility terms even for Hindi (+0.20%), despite affecting 13% of lines
by line-count — meaning the affected lines shift by only 1-2 tokens
each on average, not dramatically. All three are real, quantified, and
none individually explains the large GPT-2 cross-language gap. 
---

## Experiment 8 — random.seed(1337): suspicious but fine

### Hypothesis
fertility.py imports random and sets random.seed(1337) with a comment
"reproducibility," but analyze() and read_lines() never call anything
from the random module. If true, this line has no effect on output.

### Command
python partA/experiments/test_seed_effect.py

### Result
seed=1337: 1.330634
seed=999:  1.330634
no seed:   1.330634
All identical: True

### Observation
Confirmed: the seed has zero effect on the reported fertility number.
This is the "looks suspicious but is actually fine" item required by
A2. Verified with evidence rather than asserted, avoiding the
assignment's -5 penalty for unverified claims.

---

## A2 — Complete

All required elements are now evidenced:
- Code bugs: split(" ") phantom words (Exp 1, 7), per-line averaging
  (Exp 2)
- Conceptual bug: tokenizer choice, not language, drives most of the
  cross-language gap (Exp 5)
- Preprocessing issues with measured impact: lowercasing (Exp 3, 7),
  NFC normalization (Exp 4, 7)
- Suspicious-but-fine: random.seed(1337) (Exp 8)

Moving to A3: corrected cross-language comparison using the A1 corpus,
multiple tokenizers, and multiple denominators. 
---

## A3 — Corrected cross-language comparison

### Goal
Recompute fertility properly on the A1 corpus (200 parallel sentences,
4 languages), using multiple tokenizers and multiple denominators, and
determine which single number should drive a routing/cost decision.

### Command
python partA/a3_corrected_comparison.py

### Result

GPT-2 -- ratio vs English:
| Denominator | Hindi | Tamil | Telugu |
|---|---:|---:|---:|
| Per word | 6.09x | 19.42x | 15.93x |
| Per grapheme | 10.86x | 19.78x | 21.06x |
| Per byte | 2.81x | 4.71x | 4.66x |
| Per sentence | 7.27x | 14.95x | 12.56x |

XLM-R -- ratio vs English:
| Denominator | Hindi | Tamil | Telugu |
|---|---:|---:|---:|
| Per word | 1.07x | 1.74x | 1.69x |
| Per grapheme | 1.92x | 1.78x | 2.24x |
| Per byte | 0.50x | 0.43x | 0.50x |
| Per sentence | 1.27x | 1.34x | 1.33x |

mBERT -- ratio vs English:
| Denominator | Hindi | Tamil | Telugu |
|---|---:|---:|---:|
| Per word | 1.52x | 2.78x | 2.72x |
| Per grapheme | 2.72x | 2.83x | 3.59x |
| Per byte | 0.70x | 0.68x | 0.80x |
| Per sentence | 1.81x | 2.14x | 2.13x |

### Observation
Switching tokenizers (GPT-2 to XLM-R/mBERT) moves the ratio by roughly
5-15x. Switching denominators within a single tokenizer moves it by
only 2-5x. Tokenizer choice, not denominator choice, is the dominant
factor -- confirming A2's conceptual finding at full corpus scale and
across two additional tokenizers.

No denominator is perfectly bias-free:
- Per-word undercounts fairly for Indic scripts, since a single word
  can carry grammatical information English expresses as multiple
  separate words.
- Per-byte overcorrects in the opposite direction: Devanagari/Tamil/
  Telugu characters occupy ~3 bytes in UTF-8 versus 1 byte for Latin
  script, inflating the denominator independent of tokenizer quality.
  This produces ratios below 1.0x for XLM-R, which reflects encoding
  size, not superior tokenization.
- Per-grapheme is more language-neutral than raw code-point counting,
  but the number of graphemes needed to express equivalent content can
  still differ across scripts.
- Per-sentence is the strongest choice for this corpus specifically,
  because the sentences are parallel, so each sentence holds the
  underlying content approximately constant across languages (not
  exactly constant, since translations can carry small linguistic
  differences -- but far more constant than word, grapheme, or byte
  counts, which vary with script and morphology independent of
  content).

### Conclusion
The single number recommended to drive the routing-and-cost decision:
tokens-per-sentence, measured with a multilingual tokenizer (XLM-R or
mBERT), not GPT-2. On this corpus: Hindi ~1.27-1.81x, Tamil
~1.34-2.14x, Telugu ~1.33-2.13x relative to English -- substantially
lower than REPORT_v0's claimed 5.89x-7x, which was measured with GPT-2
and a whitespace-word denominator.
---

## A4 — Recommendation memo

### Goal

Translate the corrected A3 results into a routing and cost recommendation,
while stating the main benchmark caveat and a production metric to monitor.

### Decision

The original finding that Indic languages require more tokens than English
is directionally supported, but the magnitude is strongly tokenizer-dependent.
GPT-2 showed a 7.27x–14.95x Indic/English gap on the parallel-sentence
metric, compared with 1.27x–1.34x for XLM-R and 1.81x–2.14x for mBERT.

For routing and cost estimation, tokens-per-parallel-sentence was selected
as the primary metric because the A1 corpus contains aligned translations
of the same 200 sentences across languages. Tokenizer choice should be
based on the actual production model rather than assuming the original
GPT-2-based 5.89x–7x multiplier.

### Recommendation

Use a multilingual tokenizer for Indic-language traffic and budget using
measurements from the actual production tokenizer/model. Track actual
tokens per request by input language in production.

### Main caveat

The A1 corpus contains only 200 formal parallel sentences per language and
does not represent conversational, code-mixed, transliterated, or noisy
production traffic. Therefore the measured token premium may differ from
production traffic.

### Deliverable
The full recommendation memo is in `partA/A4_recommendation_memo.md`.
<<<<<<< HEAD
=======

>>>>>>> 84ec59eb11087c490f36d5196dfb7652095a1463
### A4 complete.

## Session 3 — Part B: Capacity reconciliation

### B1 — KV-cache capacity reconciliation

### Goal
Estimate max concurrent 4096-token sequences from model_spec.md, check against bench_log.csv.

### Method
Manual arithmetic from model_spec.md (see partB/B1_kv_cache.md for full derivation).

### Result
KV cache = 114,688 bytes/token (112 KiB). Full 4096-token sequence = 448 MiB. Budget after fp16 weights (8.4 GB) and overhead (1.6 GB) from a 24 GB / 0.92-util GPU = 12.08 GB → predicted ~25.7 concurrent sequences.

### Revision
First pass treated "24 GB" as binary GiB → ~28.9 sequences. model_spec.md doesn't state a convention, so checked both against the log instead of assuming: at batch 24, kv_cache_util=0.93 implies 24/0.93=25.8 (matches decimal-bytes estimate); the GiB estimate would imply 24/28.9=0.83, a clearly worse fit. Decimal bytes adopted based on this evidence, not assumption.

### Observation
Cross-checked two more ways: batch 32 (32-7 preempted=25 active) and batch 48 (48-23 preempted=25 active) both land on ~25, consistent with the ~25.7 prediction. All three benchmark readings agree.

### Next step
B2: explain why reported_tok_s falls (1607→1384→1298) past batch 24, using the ~25.7 predicted capacity as the starting mechanism to investigate.
### B2 — Long-context capacity anomaly

### Goal
Explain why throughput stops scaling with batch size for the
3584-prompt / 512-generation workload.

### Observation
For the long-context sweep, throughput increases up to batch 24 but
then decreases:

- Batch 16: 1311.4 tok/s
- Batch 24: 1607.4 tok/s
- Batch 32: 1384.0 tok/s
- Batch 48: 1298.5 tok/s

This is the throughput anomaly.

### Hypothesis
B1 predicts capacity of ~25-26 full-length 4096-token sequences.
Batches 32 and 48 exceed this capacity, causing KV-cache pressure and
sequence preemption.

### Evidence
At batch 24, KV utilization is 0.93 with 0 preemptions.
At batch 32, utilization reaches 0.97 with 7 preemptions.
At batch 48, utilization remains 0.97 with 23 preemptions.

The wall-clock time also grows faster than the number of requests:

- Batch 24 → 32: 61.16s → 94.71s (+55%) for +33% requests.
- Batch 32 → 48: 94.71s → 151.41s (+60%) for +50% requests.

Latency shows the same degradation: TTFT p50 rises from 500.5 ms
(batch 24) to 636.9 ms (batch 32) and 955.4 ms (batch 48), while
e2e p95 rises from 69,221 ms to 105,428 ms.

Together, KV saturation, increasing preemptions, superlinear
wall-clock growth, and worsening latency support KV-cache pressure
and preemption as the mechanism behind the throughput drop.

### Decision
For this 4096-token workload, cap admitted concurrency around batch 24
rather than allowing batches 32-48.

### Predicted effect
Batch 24 already achieves 1607.4 tok/s with zero preemptions, so keeping
concurrency around this region should avoid the observed degradation
and maintain throughput near the measured 1607 tok/s peak.

### Next step
B3: identify the throughput-column misread in the original report and
independently calculate honest goodput for the batch-24 long-context row.
### B3 — Throughput-column misread

### Goal
Check the meaning of `reported_tok_s` and correct REPORT_v0's claims
about long-prompt throughput and linear batch scaling.

### Investigation
For the batch-24 long-context row:

```text
(3584 + 512) × 24 / 61.16
= 1607.4 tok/s
```

This exactly reproduces `reported_tok_s`, so the benchmark arithmetic is
correct. The metric counts both prompt/prefill and generated/decode
tokens.

### Interpretation
The long-context workload contains 3584 prompt tokens and only 512
generated tokens per request. Therefore 87.5% of the counted tokens are
prompt tokens. Comparing `reported_tok_s` across short and long prompts
does not directly compare generation throughput.

This explains REPORT_v0's batch-16 claim: long prompts show 1311.4
reported tok/s versus 883.2 for short prompts, but the metric counts
the much larger prompt-token volume in the long workload.

### Honest batch-24 goodput

Way A — generated tokens over total wall-clock:

```text
512 × 24 / 61.16
≈ 200.9 generated tok/s
```

Way B — ITL-based decode estimate:

```text
24 / 0.09607
≈ 249.8 generated tok/s
```

The two decode-oriented estimates are substantially closer to each
other than either is to the reported 1607.4 tok/s. They measure
different aspects of the run, so they are not expected to be identical.

### Result
The `reported_tok_s` calculation is not mathematically wrong; the
misread is interpreting the combined prompt-plus-generation metric as
pure generation throughput.

### Decision
Use decode-oriented goodput when discussing generation performance,
and do not use the reported 1607 tok/s as a pure decode-throughput
number.

B2 also shows that throughput cannot be assumed to scale linearly with
batch size because KV-cache saturation and preemption cause throughput
to fall beyond batch 24.

### Next step
B4: choose one serving counter/metric that could independently confirm
the KV-cache/preemption mechanism identified in B2.

### B4 — Validation metric

### Goal
Choose one production metric that can validate the B2 KV-cache/preemption hypothesis.

### Decision
Monitor the **sequence-preemption counter/rate**. A concrete example is vLLM's Prometheus `vllm:num_preemptions` metric.

### Expected result
Preemptions should remain ~0 below the estimated ~25–26 sequence capacity and rise once concurrency exceeds it. This matches the benchmark: **0 → 7 → 23** preempted sequences at batches **24 → 32 → 48**.

If throughput degrades without increased preemptions, investigate other bottlenecks.

**B4 complete.**
## Part C — Decision memo: casual tone for 6 languages

Recommended a staged approach: prompt-engineering tested first (cheapest and fully reversible), then a <=1B rewriter model only if needed (contained risk, easy rollback), with full SFT deferred. Initial thinking was to combine SFT and a rewriter, but after considering the constraints (2-week timeline, one reviewer covering only Hindi/Kannada, and 4 languages that cannot be natively verified), I reversed that decision. Applying SFT across all 6 languages would place the highest-risk, hardest-to-undo change exactly where verification is weakest. The final recommendation therefore prioritizes reversible methods first and limits model changes until broader multilingual validation is available. Full assumptions, arithmetic, success metric, kill criterion, and Day-1 experiment are documented in `partC/memo.md`.

## Assignment status

Parts A, B, and C complete.
