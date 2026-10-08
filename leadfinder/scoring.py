import re


def normalize_name(name):
    name = name.lower()
    name = re.sub(r"#\s*\d+", "", name)       # drop store numbers like "#2"
    name = re.sub(r"[^a-z0-9 ]", "", name)    # drop punctuation
    return " ".join(name.split())


def is_chain(name, chains):
    lower = name.lower()
    return any(chain in lower for chain in chains)


def count_locations(places):
    counts = {}
    for p in places:
        key = normalize_name(p["name"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def score_place(place, rules, chains, location_count=1):
    score = 0
    reasons = []
    rating = place.get("rating")
    reviews = place.get("review_count") or 0

    if is_chain(place["name"], chains):
        return rules["chain_penalty"], ["national chain"]

    if place.get("status") == "FUTURE_OPENING":
        score += rules["future_opening"]
        reasons.append("opening soon")
    elif reviews <= rules["likely_new_max_reviews"]:
        score += rules["likely_new"]
        reasons.append(f"only {reviews} reviews, likely new")

    if not place.get("website"):
        score += rules["no_website"]
        reasons.append("no website")

    if (rating is not None
            and rating >= rules["hidden_gem_min_rating"]
            and rules["likely_new_max_reviews"] < reviews <= rules["hidden_gem_max_reviews"]):
        score += rules["hidden_gem"]
        reasons.append(f"{rating} stars but only {reviews} reviews")

    if location_count >= 2:
        score += rules["multiple_locations"]
        reasons.append(f"{location_count} locations")

    if rating is not None and rating < rules["low_rating_threshold"]:
        score += rules["low_rating_penalty"]
        reasons.append(f"low rating ({rating})")

    return score, reasons


def score_all(places, rules, chains):
    counts = count_locations(places)
    scored = []
    for p in places:
        s, reasons = score_place(p, rules, chains, counts[normalize_name(p["name"])])
        scored.append({**p, "score": s, "reasons": "; ".join(reasons)})
    scored.sort(key=lambda p: p["score"], reverse=True)
    return scored
