import unicodedata
import tiktoken

TOKENIZER = tiktoken.get_encoding("gpt2")

CORPORA = {
    "English": "corpus_full/eng_sample.txt",
    "Hindi": "corpus_full/hin_sample.txt",
    "Tamil": "corpus_full/tam_sample.txt",
    "Telugu": "corpus_full/tel_sample.txt",
}


def read_raw_lines(path):
    lines = []

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            if line:
                lines.append(line)

    return lines


def fertility(lines, transform, split_method):
    ratios = []

    for line in lines:
        line = transform(line)

        tokens = TOKENIZER.encode(line)

        if split_method == "literal":
            words = line.split(" ")
        else:
            words = line.split()

        ratios.append(len(tokens) / len(words))

    return sum(ratios) / len(ratios)


def token_count(line):
    return len(TOKENIZER.encode(line))


for language, path in CORPORA.items():

    raw_lines = read_raw_lines(path)

    # ---------------------------------------------------------
    # 1. split(" ") vs split()
    # ---------------------------------------------------------

    original_split = fertility(
        raw_lines,
        lambda x: unicodedata.normalize("NFC", x).lower(),
        "literal",
    )

    corrected_split = fertility(
        raw_lines,
        lambda x: unicodedata.normalize("NFC", x).lower(),
        "normal",
    )

    split_change = (
        (corrected_split - original_split) / original_split
    ) * 100

    # ---------------------------------------------------------
    # 2. Lowercase vs original case
    # ---------------------------------------------------------

    original_case = fertility(
        raw_lines,
        lambda x: unicodedata.normalize("NFC", x),
        "normal",
    )

    lower_case = fertility(
        raw_lines,
        lambda x: unicodedata.normalize("NFC", x).lower(),
        "normal",
    )

    lowercase_change = (
        (lower_case - original_case) / original_case
    ) * 100

    # ---------------------------------------------------------
    # 3. NFC normalization vs raw Unicode
    # ---------------------------------------------------------

    raw_nfc = fertility(
        raw_lines,
        lambda x: x,
        "normal",
    )

    normalized_nfc = fertility(
        raw_lines,
        lambda x: unicodedata.normalize("NFC", x),
        "normal",
    )

    nfc_change = (
        (normalized_nfc - raw_nfc) / raw_nfc
    ) * 100

    # Count affected lines
    lowercase_affected = sum(
        token_count(line) != token_count(line.lower())
        for line in raw_lines
    )

    nfc_affected = sum(
        token_count(line) != token_count(unicodedata.normalize("NFC", line))
        for line in raw_lines
    )

    print(f"\n{'=' * 55}")
    print(language)
    print(f"{'=' * 55}")

    print("\n1. split(' ') vs split()")
    print(f"Original split(' ') : {original_split:.4f}")
    print(f"Corrected split()   : {corrected_split:.4f}")
    print(f"Relative change     : {split_change:+.2f}%")

    print("\n2. Lowercase")
    print(f"Original case       : {original_case:.4f}")
    print(f"Lowercased          : {lower_case:.4f}")
    print(f"Relative change     : {lowercase_change:+.2f}%")
    print(
        f"Lines with changed token count: "
        f"{lowercase_affected}/{len(raw_lines)}"
    )

    print("\n3. NFC normalization")
    print(f"Without NFC         : {raw_nfc:.4f}")
    print(f"With NFC            : {normalized_nfc:.4f}")
    print(f"Relative change     : {nfc_change:+.2f}%")
    print(
        f"Lines with changed token count: "
        f"{nfc_affected}/{len(raw_lines)}"
    )