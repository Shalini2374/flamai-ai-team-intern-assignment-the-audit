# Claim: analyze() in fertility.py averages each line's own tokens/words
# ratio ("average of ratios") instead of computing total_tokens/total_words
# across the corpus ("ratio of totals"). Measuring the size of this gap
# on the real 200-sentence corpus, across all 4 languages.

import tiktoken

enc = tiktoken.get_encoding("gpt2")

def compare_methods(path):
    print(f"--- {path} ---")
    words_list = []
    tokens_list = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = line.lower()
            words = line.split(" ")
            tokens = enc.encode(line)
            words_list.append(len(words))
            tokens_list.append(len(tokens))

    ratios = [t / w for t, w in zip(tokens_list, words_list)]
    method_a = sum(ratios) / len(ratios)
    method_b = sum(tokens_list) / sum(words_list)

    print(f"Method A (avg of ratios): {method_a:.4f}")
    print(f"Method B (total/total):   {method_b:.4f}")
    print(f"Difference: {abs(method_a - method_b):.4f} "
          f"({abs(method_a-method_b)/method_b*100:.1f}% relative)\n")

compare_methods("corpus_full/eng_sample.txt")
compare_methods("corpus_full/hin_sample.txt")
compare_methods("corpus_full/tam_sample.txt")
compare_methods("corpus_full/tel_sample.txt")