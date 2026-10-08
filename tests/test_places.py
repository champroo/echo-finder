"""Tests for turning Google's JSON into our flat format. No network needed."""

from leadfinder.places import simplify


def test_simplify_full_record():
    raw = {"id": "abc", "displayName": {"text": "Rosa's"}, "formattedAddress": "1 Main St",
           "primaryType": "bakery", "businessStatus": "OPERATIONAL", "rating": 4.5,
           "userRatingCount": 12, "websiteUri": "https://rosa.example"}
    p = simplify(raw)
    assert p["name"] == "Rosa's"
    assert p["review_count"] == 12
    assert p["website"] == "https://rosa.example"


def test_simplify_missing_fields_get_defaults():
    p = simplify({"id": "xyz"})
    assert p["name"] == ""
    assert p["rating"] is None
    assert p["review_count"] == 0
    assert p["website"] == ""
