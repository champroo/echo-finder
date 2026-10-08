# Lead Finder

Finds local food businesses (restaurants, cafes, bakeries, food trucks, caterers),
scores how likely each one is to need marketing help, and outputs a ranked list
for the sales team.

```
Google Places API  ->  SQLite database  ->  scoring engine  ->  leads.csv
   (places.py)           (db.py)           (scoring.py)        (main.py)
```

## How scoring works

All weights live in `config.yaml` so they can be tuned with the sales team
without editing code.

| Signal | Points | Why it matters |
|---|---|---|
| Opening soon | +3 | Needs marketing now, hasn't hired anyone |
| ≤ 20 reviews | +2 | Probably new, building awareness |
| No website | +2 | Clear gap the agency can fill |
| 4.2+ stars, 21–100 reviews | +2 | Good product, low visibility |
| 2+ locations | +2 | Growing, has budget |
| Rating under 3.5 | −2 | Harder sell |
| National chain | −5 | Has in-house marketing |

## Project layout

```
leadfinder/
  places.py    API calls, with retry + backoff on rate limits
  db.py        SQLite storage; place_id primary key = automatic dedup
  scoring.py   Pure scoring logic (easy to test)
  main.py      Runs the pipeline end to end
tests/         pytest tests
config.yaml    Areas, categories, scoring weights, chain list
```
