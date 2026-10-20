#!/usr/bin/env python3

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

from astropy.io import fits


DEFAULT_DIRECTORY = Path(
    "/run/media/dokeeffe/WD/ObservatoryMain-ARCHIVE/CalibratedLight"
)
DEFAULT_DATABASE = Path(__file__).with_name("fits_headers.sqlite3")
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


def create_schema(connection):
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE,
            size INTEGER,
            mtime_ns INTEGER,
            error TEXT
        );
        CREATE TABLE IF NOT EXISTS cards (
            file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            hdu INTEGER NOT NULL,
            card_index INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            value TEXT,
            comment TEXT,
            PRIMARY KEY (file_id, hdu, card_index)
        );
        CREATE INDEX IF NOT EXISTS cards_keyword_value
            ON cards(keyword, value);
        CREATE INDEX IF NOT EXISTS cards_file_keyword
            ON cards(file_id, keyword);
        """
    )


def rebuild_index(directory, database):
    directory = directory.resolve()
    database = database.resolve()
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    scanned = 0
    indexed = 0
    failed = 0
    walk_errors = 0
    progress_is_tty = sys.stderr.isatty()
    last_progress = time.monotonic()

    def report_walk_error(error):
        nonlocal walk_errors
        walk_errors += 1
        if progress_is_tty:
            print(file=sys.stderr)
        print(f"Warning: cannot scan {error.filename}: {error}", file=sys.stderr)

    try:
        create_schema(connection)
        with connection:
            connection.execute("DELETE FROM files")

            for root, _, filenames in os.walk(directory, onerror=report_walk_error):
                for filename in filenames:
                    if not filename.lower().endswith(FITS_SUFFIXES):
                        continue

                    path = (Path(root) / filename).resolve()
                    scanned += 1
                    now = time.monotonic()
                    if progress_is_tty and now - last_progress >= 0.5:
                        print(
                            f"\rIndexed {indexed} of {scanned} FITS files "
                            f"({failed} failed)",
                            end="",
                            file=sys.stderr,
                            flush=True,
                        )
                        last_progress = now
                    elif not progress_is_tty and scanned % 1000 == 0:
                        print(
                            f"Processed {scanned} FITS files "
                            f"({indexed} indexed, {failed} failed)...",
                            file=sys.stderr,
                        )

                    try:
                        stat = path.stat()
                        hdus = fits.open(path, mode="readonly", memmap=False)
                        with hdus:
                            card_rows = [
                                (
                                    hdu_index,
                                    card_index,
                                    card.keyword,
                                    None if card.value is None else str(card.value),
                                    card.comment,
                                )
                                for hdu_index, hdu in enumerate(hdus)
                                for card_index, card in enumerate(hdu.header.cards)
                            ]
                        error_message = None
                        indexed += 1
                    except (
                        OSError,
                        ValueError,
                        EOFError,
                        fits.verify.VerifyError,
                    ) as error:
                        stat = None
                        card_rows = []
                        error_message = f"{type(error).__name__}: {error}"
                        failed += 1
                        print(
                            f"Warning: cannot index {path}: {error_message}",
                            file=sys.stderr,
                        )

                    cursor = connection.execute(
                        """
                        INSERT INTO files (path, size, mtime_ns, error)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            str(path),
                            stat.st_size if stat else None,
                            stat.st_mtime_ns if stat else None,
                            error_message,
                        ),
                    )
                    if card_rows:
                        connection.executemany(
                            """
                            INSERT INTO cards
                                (file_id, hdu, card_index, keyword, value, comment)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            ((cursor.lastrowid, *row) for row in card_rows),
                        )

        if progress_is_tty:
            print(
                f"\rIndex rebuild complete: {indexed} indexed, {failed} failed "
                f"out of {scanned} FITS files.",
                file=sys.stderr,
            )
        else:
            print(
                f"Index rebuild complete: {indexed} indexed, {failed} failed "
                f"out of {scanned} FITS files; {walk_errors} directory error(s).",
                file=sys.stderr,
            )
    finally:
        connection.close()

    return failed == 0 and walk_errors == 0


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild a SQLite index of FITS headers in a directory tree."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=DEFAULT_DIRECTORY,
        help=f"directory to scan (default: {DEFAULT_DIRECTORY})",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )
    args = parser.parse_args()

    if not args.directory.is_dir():
        parser.error(f"not a directory: {args.directory}")
    if args.database.resolve().is_relative_to(args.directory.resolve()):
        parser.error("database must be outside the directory being scanned")

    return 0 if rebuild_index(args.directory, args.database) else 1


if __name__ == "__main__":
    raise SystemExit(main())
