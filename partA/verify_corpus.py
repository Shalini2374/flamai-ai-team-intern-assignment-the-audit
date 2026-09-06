for lang in ["eng", "hin", "tam", "tel"]:
    path = f"corpus_full/{lang}_sample.txt"
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    print(f"{lang}: {len(lines)} lines")