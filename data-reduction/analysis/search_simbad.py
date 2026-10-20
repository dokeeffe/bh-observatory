#!/usr/bin/env python3

import argparse
import csv
import io
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from astropy import units as u
from astropy.coordinates import SkyCoord


SIMBAD_TAP_URL = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
DEFAULT_RA = "02h52m19.37s"
DEFAULT_DEC = "+24d44m04.72s"
DEFAULT_RADIUS_ARCMIN = 15.0


def search_simbad(coordinate, radius):
    adql = (
        "SELECT main_id, ra, dec FROM basic "
        "WHERE 1=CONTAINS("
        "POINT('ICRS', ra, dec), "
        f"CIRCLE('ICRS', {coordinate.ra.deg:.12f}, "
        f"{coordinate.dec.deg:.12f}, {radius.to_value(u.deg):.12f})"
        ")"
    )
    parameters = urlencode(
        {
            "request": "doQuery",
            "lang": "adql",
            "format": "csv",
            "query": adql,
        }
    )
    request = Request(
        f"{SIMBAD_TAP_URL}?{parameters}",
        headers={"User-Agent": "bh-observatory SIMBAD coordinate search"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            content = response.read().decode("utf-8-sig")
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"SIMBAD query failed: {error}") from error

    rows = csv.DictReader(io.StringIO(content))
    if not rows.fieldnames or not {"main_id", "ra", "dec"}.issubset(rows.fieldnames):
        raise RuntimeError(f"Unexpected response from SIMBAD: {content[:500]}")

    results = []
    for row in rows:
        if not row.get("main_id"):
            continue
        object_coordinate = SkyCoord(
            ra=float(row["ra"]) * u.deg,
            dec=float(row["dec"]) * u.deg,
            frame="icrs",
        )
        results.append(
            (
                coordinate.separation(object_coordinate).to_value(u.arcmin),
                row["main_id"],
                object_coordinate.ra.deg,
                object_coordinate.dec.deg,
            )
        )
    return sorted(results)


def main():
    parser = argparse.ArgumentParser(
        description="Find SIMBAD objects within a radius of sky coordinates."
    )
    parser.add_argument("--ra", default=DEFAULT_RA, help="right ascension (default: %(default)s)")
    parser.add_argument(
        "--dec", default=DEFAULT_DEC, help="declination (default: %(default)s)"
    )
    parser.add_argument(
        "--radius-arcmin",
        type=float,
        default=DEFAULT_RADIUS_ARCMIN,
        help="search radius in arcminutes (default: %(default)s)",
    )
    args = parser.parse_args()

    if args.radius_arcmin <= 0:
        parser.error("--radius-arcmin must be greater than zero")
    try:
        coordinate = SkyCoord(args.ra, args.dec, unit=(u.hourangle, u.deg), frame="icrs")
    except ValueError as error:
        parser.error(f"invalid coordinates: {error}")

    try:
        results = search_simbad(coordinate, args.radius_arcmin * u.arcmin)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    if not results:
        print("No SIMBAD objects found within the search radius.")
        return 0

    print("Separation (arcmin)\tSIMBAD ID\tRA (deg)\tDec (deg)")
    for separation, main_id, ra, dec in results:
        print(f"{separation:.4f}\t{main_id}\t{ra:.8f}\t{dec:+.8f}")
    print(f"\nFound {len(results)} object(s) within {args.radius_arcmin:g} arcmin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
