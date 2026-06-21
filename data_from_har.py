import json
import fire
from pathlib import Path

OUT_PATH = "products.json"

TARGET_URL = "https://apip.colruyt.be/gateway/emec.colruyt.protected.bffsvc/cg/fr/api/product-search-prs"


def extract_products(har_path: str):
    har = json.loads(Path(har_path).read_text(encoding="utf-8"))
    products = []

    for entry in har.get("log", {}).get("entries", []):
        request = entry.get("request", {})
        url = request.get("url", "").split("?")[0]
        method = request.get("method", "")

        if url != TARGET_URL or method != "GET":
            continue

        response = entry.get("response", {})
        content = response.get("content", {})

        try:
            payload = json.loads(content.get("text"))
        except Exception as exc:
            print(f"Skipping entry in {har_path}: {exc}")
            continue

        for product in payload.get("products", []):
            if isinstance(product, dict):
                products.append(product)

    return products


def main(*har_paths: str):
    seen = {}
    duplicates = 0

    for har_path in har_paths:
        for product in extract_products(har_path):
            key = product.get("technicalArticleNumber")
            if key is None:
                continue
            if key in seen:
                duplicates += 1
                continue
            seen[key] = product

    unique_products = list(seen.values())

    Path(OUT_PATH).write_text(
        json.dumps(unique_products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"Extracted {len(unique_products)} unique products "
        f"({duplicates} duplicates skipped) to {OUT_PATH}"
    )


if __name__ == "__main__":
    fire.Fire(main)
