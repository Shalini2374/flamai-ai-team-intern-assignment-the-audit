# AI_USAGE.md

## Where AI helped

- Explained concepts before I used them: KV-cache memory math, why GQA
  uses fewer KV heads than query heads, grapheme clusters vs. Python's
  code-point counting, and what "goodput" vs. "reported throughput"
  mean in a serving log.
- Drafted the A2 experiment scripts (double-space, averaging,
  lowercase, NFC, tokenizer-comparison) and the A3 multi-denominator
  comparison script. I ran all of these myself and checked the output
  before accepting any finding -- several toy-corpus conclusions
  changed once re-run on the full 200-sentence corpus.
- For Part C, I proposed combining SFT and the rewriter model in a few
  different ways. Discussing each version helped me see that putting
  SFT (riskiest, hardest to undo) on the 4 languages I couldn't verify
  was backwards risk allocation. I revised the recommendation to the
  final staged B+C approach based on that.
- Helped structure the final write-ups (A4 memo, Part B files, Part C
  memo) after the substance was already worked out through testing and
  discussion.

## Where AI could have misled me if I hadn't checked

- In an early B2 draft, a specific claim about preemption ("KV cache is
  evicted, and a re-admitted sequence's prompt is recomputed from
  scratch") was stated as fact by one AI tool. Nothing in
  `model_spec.md` or `bench_log.csv` actually establishes this -- it
  was a plausible technical detail not backed by the evidence I had.
  Cross-checking this claim with another AI tool flagged it as
  unevidenced, and I softened it to only what the log supports
  ("consistent with KV-cache preemption causing additional work and
  contention").
- Early in A2, NFC normalization looked harmless based only on the
  10-line toy corpus (0/10 lines changed). Re-testing on the full
  200-line A1 corpus showed it actually changed 13% of Hindi lines. I
  did not submit the small-sample conclusion without re-validating at
  scale.

## What I made sure I understood myself

- Every number in NOTEBOOK.md was checked against terminal output I
  actually ran, not accepted on AI's word alone.
- I can re-derive the KV-cache formula, explain each fertility bug's
  mechanism, and restate the tokenizer-dependence finding without
  referring back to this conversation.
- Final decisions -- which bugs to report, which denominator to
  recommend in A3, and which approach to recommend in Part C -- were
  made by me after weighing the options presented.