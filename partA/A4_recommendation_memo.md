# A4 — Recommendation Memo

## Corrected headline numbers
The direction of the original finding is correct: Indic languages
require more tokens than English. However, the reported magnitude is
strongly tokenizer-dependent. On the parallel-sentence metric, GPT-2
shows a 7.27x-14.95x Indic/English gap, while XLM-R shows 1.27x-1.34x
and mBERT shows 1.81x-2.14x.

The corrected conclusion is therefore not a single universal
multiplier: the Indic token premium depends heavily on the tokenizer.
For XLM-R, the measured premium is approximately 1.3x; for mBERT,
approximately 1.8x-2.1x. REPORT_v0's 5.89x-7x figure is specific to
its GPT-2 tokenizer and should not be treated as an inherent property
of Hindi, Tamil, or Telugu.

## Routing recommendation
Use tokens-per-parallel-sentence as the primary cross-language cost
metric, not tokens-per-word or tokens-per-byte -- the corpus (200
FLORES-200 sentences per language) is parallel, so this denominator
holds content approximately constant across languages, unlike word
count (varies with morphology) or byte count (varies with script
encoding size). Recommend switching the serving tokenizer to a
multilingual one for Indic-language traffic; do not claim that all
multilingual tokenizers converge on the same multiplier -- XLM-R and
mBERT differ meaningfully from each other (1.3x vs. 1.8-2.1x), so the
choice of multilingual tokenizer still matters.

## Biggest caveat
This corpus is 200 formal, professionally-translated parallel
sentences per language (FLORES-200 devtest). It does not cover
conversational, code-mixed, transliterated, or noisy production
traffic, which may show a different premium than measured here.
Separately, two preprocessing issues in fertility.py (lowercasing and
double-space handling in split()) were found to measurably distort
reported numbers -- lowercasing shifted English fertility by +5.3%,
and the double-space issue was present in 6-13% of Tamil/Telugu lines.
Both should be fixed regardless of tokenizer choice.

## Metric to monitor in production
Budget using measurements from the actual production tokenizer/model,
not a fixed assumed multiplier. The A3 results show why a single
GPT-2-based 6-7x multiplier is unsafe; the tested multilingual
tokenizers substantially reduce the observed premium, but still show a
real Indic token premium. Track actual tokens-per-request in
production, segmented by detected input language, and compare against
whichever tokenizer/model is actually deployed -- if the real-traffic
ratio diverges materially from this benchmark's range, that signals
either informal/code-mixed traffic behaving differently, or an
incomplete tokenizer migration.