import re

# blacklist words (VERY IMPORTANT)
STOP_ENTITIES = {
    "Key", "Insights", "Analysis", "Detailed", "Conclusion",
    "Sources", "Used", "Risks", "Challenges", "Strategic",
    "Recommendations", "This", "That", "These", "Those",
    "While", "However", "Additionally", "Overall", "Based",
    "Data", "Information", "Model"
}
KNOWN_COMPANIES = {
    "Zomato", "Swiggy", "Tesla", "BYD", "Ford", "GM",
    "Apple", "Samsung", "Xiaomi", "OnePlus",
    "Amazon", "Flipkart", "Meesho",
    "Netflix", "Disney", "Uber", "Ola",
    "TCS", "Infosys", "Wipro", "Paytm", "PhonePe", "Razorpay"
}

def extract_entities(text):
    candidates = re.findall(r'\b[A-Z][a-zA-Z0-9&]+\b', text)

    entities = []

    for word in candidates:
        if word in STOP_ENTITIES:
            continue

        if len(word) < 3:
            continue

        # 🔥 BOOST: keep known companies
        if word in KNOWN_COMPANIES:
            entities.append(word)
        else:
            # allow some unknown but limit noise
            if word.lower() not in {"analysis", "data", "model"}:
                entities.append(word)

    return list(set(entities))
# ------------------ METRICS ------------------

def precision_at_k(retrieved, ground_truth):
    retrieved_set = set(retrieved)
    gt_set = set(ground_truth)

    if len(retrieved_set) == 0:
        return 0

    return len(retrieved_set & gt_set) / len(retrieved_set)


def recall_at_k(retrieved, ground_truth):
    retrieved_set = set(retrieved)
    gt_set = set(ground_truth)

    if len(gt_set) == 0:
        return 0

    return len(retrieved_set & gt_set) / len(gt_set)


def f1_score(p, r):
    if p + r == 0:
        return 0
    return 2 * (p * r) / (p + r)