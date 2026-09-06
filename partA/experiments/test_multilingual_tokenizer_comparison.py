# Claim under test: REPORT_v0.md says Hindi's high fertility is "a
# property of the script, not the tokenizer." Testing this across all
# 4 languages on the real corpus by comparing GPT-2 vs XLM-R.

import tiktoken
from transformers import AutoTokenizer

gpt2_enc = tiktoken.get_encoding("gpt2")
xlmr_tok = AutoTokenizer.from_pretrained("xlm-roberta-base")

def avg_tokens_per_line(path, encode_fn):
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    counts = [len(encode_fn(line.lower())) for line in lines]
    return sum(counts) / len(counts)

langs = {
    "eng": "corpus_full/eng_sample.txt",
    "hin": "corpus_full/hin_sample.txt",
    "tam": "corpus_full/tam_sample.txt",
    "tel": "corpus_full/tel_sample.txt",
}

gpt2_avg = {}
xlmr_avg = {}

for lang, path in langs.items():
    gpt2_avg[lang] = avg_tokens_per_line(path, gpt2_enc.encode)
    xlmr_avg[lang] = avg_tokens_per_line(
        path, lambda s: xlmr_tok.encode(s, add_special_tokens=False)
    )

print("lang   GPT-2 avg   XLM-R avg   GPT-2/eng ratio   XLM-R/eng ratio")
for lang in langs:
    print(f"{lang:<6} {gpt2_avg[lang]:>9.2f}   {xlmr_avg[lang]:>9.2f}   "
          f"{gpt2_avg[lang]/gpt2_avg['eng']:>15.2f}x   "
          f"{xlmr_avg[lang]/xlmr_avg['eng']:>15.2f}x")