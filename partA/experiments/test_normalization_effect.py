# Claim: fertility.py applies unicodedata.normalize("NFC", line). Testing
# whether this changes token counts on the real corpus, across all 4
# languages -- especially Tamil/Telugu, which use combining/joining
# Unicode characters more than English/Hindi.

import tiktoken
import unicodedata

enc = tiktoken.get_encoding("gpt2")

def check_normalization_effect(path):
    print(f"--- {path} ---")
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    affected = 0
    for line in lines:
        normalized = unicodedata.normalize("NFC", line)
        tokens_raw = enc.encode(line)
        tokens_nfc = enc.encode(normalized)
        if len(tokens_raw) != len(tokens_nfc):
            affected += 1

    print(f"Total lines affected: {affected}/{len(lines)}\n")

check_normalization_effect("corpus_full/eng_sample.txt")
check_normalization_effect("corpus_full/hin_sample.txt")
check_normalization_effect("corpus_full/tam_sample.txt")
check_normalization_effect("corpus_full/tel_sample.txt")