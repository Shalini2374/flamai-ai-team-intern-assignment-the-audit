def check_file(path):
    print(f"--- {path} ---")
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    affected = 0
    for i, line in enumerate(lines):
        line = line.lower()
        naive = len(line.split(" "))
        fixed = len(line.split())
        if naive != fixed:
            affected += 1

    print(f"Total lines affected: {affected}/{len(lines)}\n")

check_file("corpus_full/eng_sample.txt")
check_file("corpus_full/hin_sample.txt")
check_file("corpus_full/tam_sample.txt")
check_file("corpus_full/tel_sample.txt")
def check_file(path):
    print(f"--- {path} ---")
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    affected = 0
    for i, line in enumerate(lines):
        line = line.lower()
        naive = len(line.split(" "))
        fixed = len(line.split())
        if naive != fixed:
            affected += 1

    print(f"Total lines affected: {affected}/{len(lines)}\n")

check_file("corpus_full/eng_sample.txt")
check_file("corpus_full/hin_sample.txt")
check_file("corpus_full/tam_sample.txt")
check_file("corpus_full/tel_sample.txt")