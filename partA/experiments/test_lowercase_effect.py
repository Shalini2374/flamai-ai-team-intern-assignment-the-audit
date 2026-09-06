# Claim: fertility.py calls line.lower() before tokenizing. Hindi/Tamil/
# Telugu have no letter case, so lowercasing should only affect English.
# Measuring how many lines change token count, per language, on the real
# corpus.

import tiktoken
enc = tiktoken.get_encoding("gpt2")

def check_lowercase_effect(path):
    print(f"--- {path} ---")
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    affected = 0
    for line in lines:
        tokens_original = enc.encode(line)
        tokens_lower = enc.encode(line.lower())
        if len(tokens_original) != len(tokens_lower):
            affected += 1

    print(f"Total lines affected: {affected}/{len(lines)}\n")

check_lowercase_effect("corpus_full/eng_sample.txt")
check_lowercase_effect("corpus_full/hin_sample.txt")
check_lowercase_effect("corpus_full/tam_sample.txt")
check_lowercase_effect("corpus_full/tel_sample.txt")