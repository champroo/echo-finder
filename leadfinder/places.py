import time

import requests

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.primaryType",
    "places.businessStatus",
    "places.rating",
    "places.userRatingCount",
    "places.websiteUri",
    "places.googleMapsUri",
    "nextPageToken",
])


class PlacesAPIError(Exception):
    """Raised when Google returns an error we can't recover from."""

def _post_with_retry(body, api_key, max_retries=3):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    wait = 1
    for attempt in range(max_retries + 1):
        resp = requests.post(SEARCH_URL, json=body, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        retryable = resp.status_code == 429 or resp.status_code >= 500
        if retryable and attempt < max_retries:
            print(f"  Google returned {resp.status_code}, retrying in {wait}s...")
            time.sleep(wait)
            wait *= 2
            continue
        raise PlacesAPIError(f"{resp.status_code}: {resp.text[:300]}")


def search(query, api_key, max_pages=1):
    body = {"textQuery": query, "includeFutureOpeningBusinesses": True}
    results = []
    for _ in range(max_pages):
        data = _post_with_retry(body, api_key)
        results.extend(simplify(p) for p in data.get("places", []))
        token = data.get("nextPageToken")
        if not token:
            break
        body["pageToken"] = token
    return results


def simplify(raw):
    return {
        "place_id": raw["id"],
        "name": raw.get("displayName", {}).get("text", ""),
        "address": raw.get("formattedAddress", ""),
        "category": raw.get("primaryType", ""),
        "status": raw.get("businessStatus", ""),
        "rating": raw.get("rating"),
        "review_count": raw.get("userRatingCount", 0),
        "website": raw.get("websiteUri", ""),
        "maps_url": raw.get("googleMapsUri", ""),
    }
