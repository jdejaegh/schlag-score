import json
import matplotlib.pyplot as plt

with open("data_colruyt.json", "r", encoding="utf-8") as f:
    items = json.load(f)

def compute_score(item):
    try:
        alcohol = float(item.get("AlcoholVolume", 0))
        amount = item.get("amount", 0)
        if isinstance(amount, dict):
            amount = amount.get("source", 0)
        amount = float(amount)
        price = float(item.get("price", {}).get("basicPrice", 0))
        if price > 0:
            return (alcohol * amount * 100) / price
    except:
        pass
    return 0

scored_items = [(compute_score(item), item) for item in items]
scored_items = [x for x in scored_items if x[0] > 0]
scored_items.sort(reverse=True, key=lambda x: x[0])

rank = 1
for score, item in scored_items:
    print(f"#{rank} | {score:.2f} | {item.get('LongName', '')} (https://www.colruyt.be/fr/produits/{item.get('commercialArticleNumber')})")
    rank += 1

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
