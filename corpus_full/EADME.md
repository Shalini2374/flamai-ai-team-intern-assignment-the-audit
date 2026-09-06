# A1 — Multilingual Evaluation Corpus

## Source

FLORES-200 devtest sentences, accessed via the
`openlanguagedata/flores_plus` dataset on HuggingFace.

## Languages

| Language | Code (FLORES) | Script |
|---|---|---|
| English | eng_Latn | Latin |
| Hindi | hin_Deva | Devanagari |
| Tamil | tam_Taml | Tamil |
| Telugu | tel_Telu | Telugu |

Tamil and Telugu were selected as the two Dravidian languages.

## Size

200 parallel sentences per language (800 sentences total).
Sentences are aligned by `sentence_id` (0–199), so the same
underlying sentence is represented across all four language files.

## Domain

The source text comes from Wikinews articles and covers multiple
topics such as health, science, politics, and sports. The
`corpus_manifest.csv` records the domain and topic for each sentence.

## Files

- `eng_sample.txt`, `hin_sample.txt`, `tam_sample.txt`,
  `tel_sample.txt` — one sentence per line, UTF-8 text
- `corpus_manifest.csv` — combined manifest containing sentence ID,
  language, text, domain, and topic

## Preprocessing applied

- Extracted the `text` field from each source record
- Stripped leading/trailing whitespace per line
- No lowercasing or Unicode normalization was applied during corpus
  construction

Lowercasing and Unicode normalization are left to the tokenizer
audit experiments so their effects can be measured separately.

## What this corpus can and cannot tell you

This corpus is useful for comparing tokenizer behaviour on clean,
formal written text and for controlled cross-language comparison
because the sentences are parallel.

It cannot establish how tokenizers behave on informal or
conversational text, code-mixed or transliterated Indian-language
text, spelling errors and other non-standard writing, or
domain-specific vocabulary outside news writing.

Therefore, the measured fertility values should be treated as a
controlled benchmark rather than a direct prediction of production
token costs.