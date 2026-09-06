# test_seed_effect.py
# Claim: fertility.py sets random.seed(1337), but analyze() never calls
# anything from the random module. Confirming the seed has zero effect
# on output by running analyze() twice with different/no seeds.

import unicodedata
import tiktoken
import random

enc = tiktoken.get_encoding("gpt2")

def analyze(lines):
    per_line_fertility = []
    for line in lines:
        line = line.lower()
        tokens = enc.encode(line)
        words = line.split(" ")
        per_line_fertility.append(len(tokens) / len(words))
    return sum(per_line_fertility) / len(per_line_fertility)

with open("corpus_full/eng_sample.txt", encoding="utf-8") as f:
    lines = [unicodedata.normalize("NFC", l.strip()) for l in f if l.strip()]

random.seed(1337)
result_a = analyze(lines)

random.seed(999)  # different seed
result_b = analyze(lines)

random.seed(None)  # no seed at all
result_c = analyze(lines)

print(f"seed=1337: {result_a:.6f}")
print(f"seed=999:  {result_b:.6f}")
print(f"no seed:   {result_c:.6f}")
print(f"All identical: {result_a == result_b == result_c}")