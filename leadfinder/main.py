import argparse
import csv
import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from leadfinder import db, places, scoring

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_COLUMNS = ["score", "name", "reasons", "category", "address",
                  "rating", "review_count", "website", "maps_url", "first_seen"]


def load_config():
    with open(ROOT / "config.yaml") as f:
        return yaml.safe_load(f)


def fetch_live(config):
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise SystemExit("No API key found. Copy .env.example to .env and add your key.")

    found = []
    for area in config["areas"]:
        for category in config["categories"]:
            query = f"{category} in {area}"
            print(f"Searching: {query}")
            try:
                results = places.search(query, api_key, config["max_pages_per_search"])
            except places.PlacesAPIError as e:
                # One failed search shouldn't kill the whole run.
                print(f"  Skipped, error: {e}")
                continue
            print(f"  {len(results)} results")
            found.extend(results)
    return found


def fetch_sample():
    with open(ROOT / "sample_data" / "sample_places.json") as f:
        return [places.simplify(p) for p in json.load(f)["places"]]


def export_csv(leads, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)


def main():
    parser = argparse.ArgumentParser(description="Find and score local food business leads.")
    parser.add_argument("--sample", action="store_true", help="use fake sample data instead of the API")
    args = parser.parse_args()

    config = load_config()
    found = fetch_sample() if args.sample else fetch_live(config)

    db_path = ROOT / ("sample.db" if args.sample else "leads.db")
    conn = db.connect(db_path)
    new_count = db.upsert(conn, found)
    print(f"\nFound {len(found)} results, {new_count} new businesses added to the database.")

    leads = scoring.score_all(db.all_places(conn), config["scoring"], config["chains"])
    leads = [l for l in leads if l["status"] != "CLOSED_PERMANENTLY"]

    out = ROOT / "leads.csv"
    export_csv(leads, out)
    print(f"Wrote {len(leads)} scored leads to {out.name}\n")
    print("Top 5 leads:")
    for l in leads[:5]:
        print(f"  [{l['score']:>2}] {l['name']} - {l['reasons']}")


if __name__ == "__main__":
    main()
