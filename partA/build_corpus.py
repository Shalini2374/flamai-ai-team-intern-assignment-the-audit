import os
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "120"

from huggingface_hub import hf_hub_download
import json
import csv

LANGS = {
    "eng": "eng_Latn",
    "hin": "hin_Deva",
    "tam": "tam_Taml",
    "tel": "tel_Telu",
}

REPO = "openlanguagedata/flores_plus"
OUT_DIR = "corpus_full"
os.makedirs(OUT_DIR, exist_ok=True)

N_SENTENCES = 200

all_rows = []  # for the combined CSV

for short_code, flores_code in LANGS.items():
    print(f"Downloading {flores_code}...")
    path = hf_hub_download(
        repo_id=REPO,
        repo_type="dataset",
        filename=f"dev/{flores_code}.jsonl",
    )

    lines_written = 0
    txt_path = os.path.join(OUT_DIR, f"{short_code}_sample.txt")
    with open(path, encoding="utf-8") as f, open(txt_path, "w", encoding="utf-8") as out:
        for line in f:
            obj = json.loads(line)
            out.write(obj["text"].strip() + "\n")

            all_rows.append({
                "sentence_id": obj["id"],
                "lang": short_code,
                "flores_code": flores_code,
                "text": obj["text"].strip(),
                "domain": obj.get("domain", ""),
                "topic": obj.get("topic", ""),
            })

            lines_written += 1
            if lines_written >= N_SENTENCES:
                break

    print(f"  wrote {lines_written} lines to {txt_path}")

# write the combined manifest CSV
csv_path = os.path.join(OUT_DIR, "corpus_manifest.csv")
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["sentence_id", "lang", "flores_code", "text", "domain", "topic"])
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nWrote combined manifest: {csv_path} ({len(all_rows)} rows)")
print("Done. All 4 .txt files use the same sentence IDs (0..N-1), so they stay parallel/aligned.")