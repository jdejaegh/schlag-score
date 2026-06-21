import json
import matplotlib.pyplot as plt

with open("data_colruyt.json", "r", encoding="utf-8") as f:
    items = json.load(f)

try:
    with open('ranks.json', "r", encoding="utf-8") as f:
        saved_scores = json.load(f)
except:
    saved_scores = None

def compute_score(item):
    try:
        alcohol = float(item.get("AlcoholVolume", 0))
        price_1 = float(item.get("price", {}).get("measurementUnitPrice"))
        price_2 = float(item.get("price", {}).get("pricePerUOM"))
        assert price_1 == price_2

        unit = item.get("price", {}).get("measurementUnit")
        assert unit == "L"

        if price_1 is not None and price_1 > 0:
            return (alcohol / price_1) * 100

    except:
        pass
    return 0

scored_items = [(compute_score(item), item) for item in items]
scored_items = [x for x in scored_items if x[0] > 0]
scored_items.sort(reverse=True, key=lambda x: x[0])

print("| Rank | Score | Product |")
print("|------|-------|---------|")

rank = 1
scores = dict()
for score, item in scored_items:

    product_id = item.get("commercialArticleNumber")

    evol = ""
    if saved_scores is not None:
        if product_id not in saved_scores:
            evol = '🌟 '
        elif rank < saved_scores[product_id]:
            evol = '🔺 '
        elif rank > saved_scores[product_id]:
            evol = '🔻 '
        elif rank == saved_scores[product_id]:
            evol = '🟰 '

    print(f"| {evol}#{rank} | {score:.1f} | {item.get('LongName', '')} (https://www.colruyt.be/fr/produits/{product_id}) |")
    scores[product_id] = rank
    rank += 1

with open('new_ranks.json', "w", encoding="utf-8") as f:
    json.dump(scores, f)

# Distribution plot
scores = [score for score, _ in scored_items]

plt.figure(figsize=(10, 6))
counts, bins, patches = plt.hist(scores, bins=20, edgecolor='black', alpha=0.7)

for count, bin_edge, patch in zip(counts, bins, patches):
    if count > 0:
        plt.text(patch.get_x() + patch.get_width() / 2, count, str(int(count)),
                 ha='center', va='bottom', fontsize=8)

plt.xlabel('Schlag Score', fontsize=14)
plt.ylabel('Count of drinks', fontsize=14)
plt.title('Schlag Score Distribution', fontsize=16)
plt.xticks(bins, [f"{b:.0f}" for b in bins])
plt.xlim(left=0)
plt.ylim(bottom=0)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig("score_distribution.png", dpi=300)
