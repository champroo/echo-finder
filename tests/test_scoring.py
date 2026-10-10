"""Tests for the scoring logic. Run with: pytest"""

from leadfinder.scoring import is_chain, normalize_name, score_all, score_place

RULES = {
    "future_opening": 3, "likely_new": 2, "likely_new_max_reviews": 20,
    "no_website": 2, "hidden_gem": 2, "hidden_gem_min_rating": 4.2,
    "hidden_gem_max_reviews": 100, "multiple_locations": 2,
    "low_rating_penalty": -2, "low_rating_threshold": 3.5, "chain_penalty": -5,
    "bakery_bonus": 1,
}
CHAINS = ["starbucks", "subway"]


def make_place(**overrides):
    """A 'boring' baseline business that scores 0. Tests change one thing at a time."""
    place = {"name": "Test Cafe", "status": "OPERATIONAL", "rating": 4.0,
             "review_count": 500, "website": "https://example.com"}
    place.update(overrides)
    return place


def test_baseline_scores_zero():
    assert score_place(make_place(), RULES, CHAINS) == (0, [])


def test_no_website_adds_points():
    score, reasons = score_place(make_place(website=""), RULES, CHAINS)
    assert score == 2
    assert "no website" in reasons


def test_future_opening():
    score, _ = score_place(make_place(status="FUTURE_OPENING", review_count=0), RULES, CHAINS)
    assert score == 3  # future opening shouldn't also count as "likely new"


def test_hidden_gem():
    score, _ = score_place(make_place(rating=4.6, review_count=60), RULES, CHAINS)
    assert score == 2


def test_hidden_gem_boundaries():
    # Exactly at the thresholds still counts...
    assert score_place(make_place(rating=4.2, review_count=100), RULES, CHAINS)[0] == 2
    # ...just past them doesn't.
    assert score_place(make_place(rating=4.1, review_count=60), RULES, CHAINS)[0] == 0
    assert score_place(make_place(rating=4.6, review_count=101), RULES, CHAINS)[0] == 0


def test_low_rating_penalty():
    score, _ = score_place(make_place(rating=3.0), RULES, CHAINS)
    assert score == -2


def test_missing_rating_does_not_crash():
    score, _ = score_place(make_place(rating=None, review_count=0, website=""), RULES, CHAINS)
    assert score == 4  # likely new + no website


def test_chain_overrides_everything():
    score, reasons = score_place(make_place(name="Starbucks Reserve", website=""), RULES, CHAINS)
    assert score == -5
    assert reasons == ["national chain"]


def test_chain_match_is_case_insensitive():
    assert is_chain("SUBWAY", CHAINS)
    assert not is_chain("Rosa's Panaderia", CHAINS)


def test_normalize_name_strips_store_numbers():
    assert normalize_name("Joe's Tacos #2") == normalize_name("Joes Tacos # 1")


def test_score_all_detects_multiple_locations_and_sorts():
    places = [
        make_place(name="Pho King #1"),
        make_place(name="Pho King #2"),
        make_place(name="Plain Cafe"),
    ]
    leads = score_all(places, RULES, CHAINS)
    assert leads[0]["score"] == 2 and "2 locations" in leads[0]["reasons"]
    assert leads[-1]["name"] == "Plain Cafe"

def test_bakery_bonus():
    score, _ = score_place(make_place(category="bakery"), RULES, CHAINS)
    assert score == 1

def test_non_bakery_gets_no_bonus():
    score, _ = score_place(make_place(category="cafe"), RULES, CHAINS)
    assert score == 0