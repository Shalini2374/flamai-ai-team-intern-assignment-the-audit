# A3 -- corrected cross-language comparison.
# Computes tokens per: whitespace word, grapheme cluster, UTF-8 byte,
# and per parallel sentence -- using GPT-2, XLM-R, and mBERT -- on the
# real A1 corpus (200 aligned sentences per language).

import unicodedata
import tiktoken
from transformers import AutoTokenizer
import regex

gpt2_enc = tiktoken.get_encoding("gpt2")
xlmr_tok = AutoTokenizer.from_pretrained("xlm-roberta-base")
mbert_tok = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")

TOKENIZERS = {
    "gpt2":  lambda s: gpt2_enc.encode(s),
    "xlmr":  lambda s: xlmr_tok.encode(s, add_special_tokens=False),
    "mbert": lambda s: mbert_tok.encode(s, add_special_tokens=False),
}

LANGS = {
    "eng": "corpus_full/eng_sample.txt",
    "hin": "corpus_full/hin_sample.txt",
    "tam": "corpus_full/tam_sample.txt",
    "tel": "corpus_full/tel_sample.txt",
}

def load_lines(path):
    with open(path, encoding="utf-8") as f:
        return [unicodedata.normalize("NFC", l.strip()) for l in f if l.strip()]

def count_words(line):
    return len(line.split())

def count_graphemes(line):
    return len(regex.findall(r"\X", line))

def count_bytes(line):
    return len(line.encode("utf-8"))

DENOMINATORS = {
    "per_word":     count_words,
    "per_grapheme": count_graphemes,
    "per_byte":     count_bytes,
    "per_sentence": lambda line: 1,
}

results = {}

for lang, path in LANGS.items():
    lines = load_lines(path)
    results[lang] = {}
    for tok_name, tok_fn in TOKENIZERS.items():
        results[lang][tok_name] = {}
        for denom_name, denom_fn in DENOMINATORS.items():
            ratios = []
            for line in lines:
                tokens = tok_fn(line)
                denom = denom_fn(line)
                ratios.append(len(tokens) / denom)
            results[lang][tok_name][denom_name] = sum(ratios) / len(ratios)

for tok_name in TOKENIZERS:
    print(f"\n{'='*75}")
    print(f"Tokenizer: {tok_name}")
    print(f"{'='*75}")
    header = f"{'lang':<6}" + "".join(f"{d:>16}" for d in DENOMINATORS)
    print(header)
    for lang in LANGS:
        row = f"{lang:<6}"
        for denom_name in DENOMINATORS:
            row += f"{results[lang][tok_name][denom_name]:>16.3f}"
        print(row)

    print(f"\n  -- ratio vs English --")
    print(header)
    for lang in LANGS:
        row = f"{lang:<6}"
        for denom_name in DENOMINATORS:
            val = results[lang][tok_name][denom_name]
            eng_val = results["eng"][tok_name][denom_name]
            row += f"{val/eng_val:>16.2f}"
        print(row)