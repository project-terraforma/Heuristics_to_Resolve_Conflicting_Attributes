#!/usr/bin/env python3
"""
compare_sfbiz_overture.py — clean restart (v1.0)
================================================
Flags business‑name mismatches between **DataSF Active Business Locations** and
**Overture Maps – Places**, with as few moving parts as possible.

Why this version should “just work”
----------------------------------
1. **Explicit SoQL query** — we ask DataSF to return exactly four columns:
   `location_id`, `trade_name`, `lat`, `lon`.  No guessing field names.
2. **Requests‑only download** — we fetch the CSV with Python, save to a temp
   file, then load it with DuckDB.  Avoids `httpfs` HEAD woes entirely.
3. **No auto‑detection logic** — fewer edge‑cases.
4. **Single dependency** besides the standard library: **duckdb ≥0.9**.

Install & run
-------------
```bash
pip install --upgrade duckdb  # requests is stdlib in Py≥3.12 else pip install requests
python compare_sfbiz_overture.py                 # default settings
# Custom clip & output
python compare_sfbiz_overture.py \
       --bbox "-122.52,37.70,-122.35,37.83" \
       --distance 10  --outfile sf_mismatch.parquet
```

Outputs: Parquet file with columns
`location_id | sf_name | ovt_id | ovt_name | dist_m | edit_dist`
"""

from __future__ import annotations

import argparse
import csv
import sys
import tempfile
from pathlib import Path
from typing import Tuple

import duckdb
import requests

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
DATASF_SOQL = (
    "https://data.sfgov.org/resource/kvj8-g7jh.csv"
    "?$select=location_id,trade_name,latitude(location)%20as%20lat,longitude(location)%20as%20lon"
    "&$limit=200000"
)
OVERTURE_S3 = "s3://overturemaps-us-west-2/release/{rel}/theme=places/type=place/*"
DEFAULT_RELEASE = "2025-05-21.0"

# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Find SF business name mismatches vs Overture Maps.")
    p.add_argument("--release", default=DEFAULT_RELEASE, help="Overture release tag (YYYY-MM-DD.X)")
    p.add_argument("--bbox", default="-123.2,37.0,-121.7,38.2", help="xmin,ymin,xmax,ymax (WGS84)")
    p.add_argument("--distance", type=float, default=15.0, help="Max metres between points for join")
    p.add_argument("--outfile", default="sf_name_mismatch.parquet", help="Parquet output path")
    p.add_argument("--levenshtein", type=int, default=0, help="≥ this edit-distance ⇒ mismatch")
    return p.parse_args()

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def fetch_datasf_csv(dest: Path):
    print("[1/4] Downloading DataSF extract …")
    with requests.get(DATASF_SOQL, timeout=60) as r:
        r.raise_for_status()
        dest.write_bytes(r.content)
    print(f"      Saved {dest.stat().st_size/1e6:.1f} MB → {dest}")


def load_into_duckdb(csv_path: Path, release: str, bbox: Tuple[float, float, float, float]):
    print("[2/4] Loading into DuckDB …")
    con = duckdb.connect(":memory:")
    con.execute("INSTALL spatial; LOAD spatial;")

    # Businesses table
    con.execute(
        """
        CREATE TABLE sf_business AS
        SELECT location_id,
               lower(trim(trade_name)) AS name,
               ST_Point(lon, lat, 4326) AS geom
        FROM read_csv_auto(?);
        """,
        [str(csv_path)],
    )

    # Overture table (clip to bbox for speed)
    xmin, ymin, xmax, ymax = bbox
    parquet_glob = OVERTURE_S3.format(rel=release)
    con.execute("SET s3_region='us-west-2';")
    con.execute(
        f"""
        CREATE TABLE overture_places AS
        SELECT id,
               lower(trim(names['primary']['name'])) AS name,
               geometry AS geom
        FROM read_parquet('{parquet_glob}')
        WHERE bbox.xmin BETWEEN {xmin} AND {xmax}
          AND bbox.ymin BETWEEN {ymin} AND {ymax};
        """
    )
    return con


def compare(con: duckdb.DuckDBPyConnection, max_dist: float, min_edit: int, out_path: str):
    print("[3/4] Comparing …")
    lev = "edit_distance"  # DuckDB stdlib; levenshtein requires extension.
    con.execute(
        f"""
        CREATE TABLE joined AS
        SELECT b.location_id, b.name AS sf_name,
               o.id AS ovt_id,   o.name AS ovt_name,
               ST_Distance(b.geom, o.geom) AS dist_m,
               {lev}(b.name, o.name) AS edit_dist
        FROM sf_business b
        JOIN overture_places o
          ON ST_DWithin(b.geom, o.geom, {max_dist});
        """
    )
    con.execute(
        f"CREATE TABLE mism AS SELECT * FROM joined WHERE edit_dist > {min_edit};"
    )
    con.execute("COPY mism TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [out_path])
    n = con.execute("SELECT COUNT(*) FROM mism").fetchone()[0]
    print(f"[4/4] Wrote {n} mismatches → {out_path}")

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main():
    args = parse_args()
    try:
        bbox = tuple(map(float, args.bbox.split(",")))
        assert len(bbox) == 4
    except Exception:
        sys.exit("--bbox must be xmin,ymin,xmax,ymax")

    with tempfile.TemporaryDirectory() as tmpd:
        csv_path = Path(tmpd) / "datasf_extract.csv"
        fetch_datasf_csv(csv_path)
        con = load_into_duckdb(csv_path, args.release, bbox)
        compare(con, args.distance, args.levenshtein, args.outfile)
        print("✓ Done.")

if __name__ == "__main__":
    main()
