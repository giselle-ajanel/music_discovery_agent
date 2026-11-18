"""
Expand music_connections.csv to a target number of REAL artist profiles using Wikidata (CC0 data).

Keeps every original row, then adds real band memberships (Wikidata property P463 "member of"),
favoring artists who play in more than one band so the graph has supergroups and side projects
for the agent to discover.

Run from the repo folder (needs normal internet access):
    python3 expand_music_connections.py
Output: music_connections_expanded.csv  (same columns as music_connections.csv)
Then re-import into Neo4j and re-run your test queries.
Wikidata is rate-limited (about 1 request per minute), so a full run takes about 5 to 10 minutes.
Results are saved in wikidata_cache/, so if it stops, just run it again.
"""
import csv, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from collections import defaultdict

TARGET_ARTISTS = 1028
SRC, OUT = "music_connections.csv", "music_connections_expanded.csv"
ENDPOINT = "https://query.wikidata.org/sparql"
CACHE_DIR = "wikidata_cache"
UA = "MusicDiscoveryAssistant/1.0 (portfolio project; contact via GitHub giselle-ajanel)"
# rock band, musical group, girl group, boy band, musical duo
BAND_TYPES = ["Q5741069", "Q215380", "Q641066", "Q216337", "Q9212979"]

QUERY = """
SELECT ?artist ?artistLabel ?band ?bandLabel ?genreLabel ?inception ?instrumentLabel WHERE {{
  ?band wdt:P31 wd:{t} .
  ?artist wdt:P463 ?band ; wdt:P31 wd:Q5 .
  OPTIONAL {{ ?band wdt:P136 ?genre }}
  OPTIONAL {{ ?band wdt:P571 ?inception }}
  OPTIONAL {{ ?artist wdt:P1303 ?instrument }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} LIMIT 25000
"""

def run(query, cache_name, tries=6):
    """Query Wikidata, waiting out rate limits, and cache the result so re-runs skip finished queries."""
    cache = os.path.join(CACHE_DIR, cache_name + ".json")
    if os.path.exists(cache):
        print(f"  using saved result {cache}")
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                rows = json.load(r)["results"]["bindings"]
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(rows, f)
            print(f"  got {len(rows)} rows")
            return rows
        except urllib.error.HTTPError as e:
            wait = 75 if e.code == 429 else 20
            print(f"  HTTP {e.code}; waiting {wait}s (try {i + 1}/{tries})", file=sys.stderr); time.sleep(wait)
        except Exception as e:
            print(f"  query failed ({e}); waiting 20s (try {i + 1}/{tries})", file=sys.stderr); time.sleep(20)
    print("  giving up on this band type; continuing with what we have", file=sys.stderr)
    return []

def val(b, k): return b.get(k, {}).get("value", "")
def is_qid(s): return bool(re.fullmatch(r"Q\d+", s))

# ---- original rows ----
with open(SRC, newline="", encoding="utf-8") as f:
    original = list(csv.DictReader(f))
fields = list(original[0].keys())
artists = {r["ArtistName"] for r in original}
pairs = {(r["ArtistName"], r["BandName"]) for r in original}
print(f"original: {len(original)} rows, {len(artists)} artists")

# ---- pull Wikidata memberships ----
band_info, members, instruments = {}, defaultdict(set), defaultdict(list)
for n, t in enumerate(BAND_TYPES):
    if n and not os.path.exists(os.path.join(CACHE_DIR, t + ".json")):
        print("  waiting 65s (Wikidata allows about 1 request per minute right now)"); time.sleep(65)
    print(f"querying band type {t} ...")
    for b in run(QUERY.format(t=t), t):
        a, band = val(b, "artistLabel"), val(b, "bandLabel")
        if not a or not band or is_qid(a) or is_qid(band): continue
        members[band].add(a)
        info = band_info.setdefault(band, {"genre": "", "year": ""})
        g, inc = val(b, "genreLabel"), val(b, "inception")
        if g and not is_qid(g) and not info["genre"]: info["genre"] = g.title()
        if inc and not info["year"]: info["year"] = inc[:4]
        ins = val(b, "instrumentLabel")
        if ins and not is_qid(ins) and ins not in instruments[a] and len(instruments[a]) < 2: instruments[a].append(ins)

artist_bands = defaultdict(set)
for band, ms in members.items():
    for a in ms: artist_bands[a].add(band)

# bands ranked by how connected their members are (multi-band members first), then size
def score(band):
    ms = members[band]
    return (sum(len(artist_bands[a]) > 1 for a in ms), len(ms))
ranked = sorted((b for b in members if len(members[b]) >= 2), key=score, reverse=True)

new_rows = []
for band in ranked:
    if len(artists) >= TARGET_ARTISTS: break
    for a in sorted(members[band], key=lambda x: -len(artist_bands[x])):
        if (a, band) in pairs: continue
        if a not in artists and len(artists) >= TARGET_ARTISTS: continue
        artists.add(a); pairs.add((a, band))
        role = " / ".join(i.title() for i in instruments[a]) or "Member"
        new_rows.append({"ArtistName": a, "Role": role, "BandName": band,
                         "Genre": band_info[band]["genre"] or "Unknown",
                         "FormedYear": band_info[band]["year"] or "", "ConnectionType": "Member"})

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(original + new_rows)

multi = sum(1 for a in artists if len({b for (x, b) in pairs if x == a}) > 1)
print(f"wrote {OUT}: {len(original) + len(new_rows)} rows, {len(artists)} distinct artists, "
      f"{len({b for _, b in pairs})} bands, {multi} artists in 2+ bands")
if len(artists) < TARGET_ARTISTS:
    print(f"WARNING: only {len(artists)} artists found; the resume number should match this file.")
