#!/usr/bin/env python3

import argparse
import os
import sys
import time
from pathlib import Path

from astropy.io import fits


DEFAULT_DIRECTORY = Path(
    "/run/media/dokeeffe/WD/ObservatoryMain-ARCHIVE/CalibratedLight"
)
FITS_SUFFIXES = (
    ".fits",
    ".fit",
    ".fts",
    ".fits.fz",
    ".fit.fz",
    ".fts.fz",
    ".fits.gz",
    ".fit.gz",
    ".fts.gz",
)


def collect_targets(directory):
    targets = set()
    scanned = 0
    skipped = 0
    walk_errors = []
    progress_is_tty = sys.stderr.isatty()
    last_progress = time.monotonic()

    if progress_is_tty:
        print("Scanning FITS files... 0 processed", end="", file=sys.stderr, flush=True)

    def report_walk_error(error):
        walk_errors.append(error)
        if progress_is_tty:
            print(file=sys.stderr)
        print(f"Warning: cannot scan {error.filename}: {error}", file=sys.stderr)

    for root, _, filenames in os.walk(directory, onerror=report_walk_error):
        for filename in filenames:
            if not filename.lower().endswith(FITS_SUFFIXES):
                continue

            path = Path(root) / filename
            scanned += 1
            now = time.monotonic()
            if progress_is_tty and now - last_progress >= 0.5:
                print(
                    f"\rScanning FITS files... {scanned} processed",
                    end="",
                    file=sys.stderr,
                    flush=True,
                )
                last_progress = now
            elif not progress_is_tty and scanned % 1000 == 0:
                print(f"Scanned {scanned} FITS files...", file=sys.stderr)

            try:
                header = fits.getheader(path, 0)
            except (OSError, ValueError, IndexError, fits.verify.VerifyError) as error:
                skipped += 1
                if progress_is_tty:
                    print(file=sys.stderr)
                print(f"Warning: cannot read {path}: {error}", file=sys.stderr)
                continue

            target = header.get("OBJECT")
            if target is None or not str(target).strip():
                skipped += 1
                continue
            targets.add(str(target).strip())

    if progress_is_tty:
        print(f"\rScanning FITS files... done ({scanned} processed)", file=sys.stderr)

    return targets, scanned, skipped, len(walk_errors)


def main():
    parser = argparse.ArgumentParser(
        description="List unique TARGET values from FITS headers recursively."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=DEFAULT_DIRECTORY,
        help=f"directory to scan (default: {DEFAULT_DIRECTORY})",
    )
    args = parser.parse_args()

    if not args.directory.is_dir():
        parser.error(f"not a directory: {args.directory}")

    targets, scanned, skipped, walk_errors = collect_targets(args.directory)
    for target in sorted(targets, key=str.casefold):
        print(target)

    print(
        f"Scanned {scanned} FITS file(s); found {len(targets)} unique target(s); "
        f"skipped {skipped} file(s) without a readable TARGET; "
        f"encountered {walk_errors} directory error(s).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
