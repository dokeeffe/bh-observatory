#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from pathlib import Path


DEFAULT_DATABASE = Path(__file__).with_name("fits_headers.sqlite3")


def connect(database, parser):
    if not database.is_file():
        parser.error(f"database not found: {database}; run rebuild_fits_header_index.py first")
    return sqlite3.connect(f"{database.resolve().as_uri()}?mode=ro", uri=True)


def command_keys(connection, _args):
    rows = connection.execute(
        """
        SELECT c.keyword, COUNT(DISTINCT c.file_id)
        FROM cards AS c
        GROUP BY c.keyword
        ORDER BY c.keyword COLLATE NOCASE
        """
    )
    for keyword, count in rows:
        print(f"{keyword}\t{count}")


def command_values(connection, args):
    rows = connection.execute(
        """
        SELECT c.value, COUNT(DISTINCT c.file_id)
        FROM cards AS c
        WHERE c.keyword = ?
        GROUP BY c.value
        ORDER BY COUNT(DISTINCT c.file_id) DESC, c.value COLLATE NOCASE
        """,
        (args.keyword.upper(),),
    )
    for value, count in rows:
        print(f"{value if value is not None else '<blank>'}\t{count}")


def command_find(connection, args):
    parameters = [args.keyword.upper()]
    if args.missing:
        sql = """
            SELECT f.path, f.error
            FROM files AS f
            WHERE NOT EXISTS (
                SELECT 1 FROM cards AS c
                WHERE c.file_id = f.id AND c.keyword = ?
        """
        parameters = [args.keyword.upper()]
        if args.hdu is not None:
            sql += " AND c.hdu = ?"
            parameters.append(args.hdu)
        sql += ") ORDER BY f.path"
    else:
        sql = """
            SELECT DISTINCT f.path, c.hdu, c.value
            FROM files AS f
            JOIN cards AS c ON c.file_id = f.id
            WHERE c.keyword = ?
        """
        if args.equals is not None:
            sql += " AND c.value = ?"
            parameters.append(args.equals)
        elif args.contains is not None:
            sql += " AND c.value LIKE ? ESCAPE '\\'"
            escaped = args.contains.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            parameters.append(f"%{escaped}%")
        if args.hdu is not None:
            sql += " AND c.hdu = ?"
            parameters.append(args.hdu)
        sql += " ORDER BY f.path"
    if args.limit:
        sql += " LIMIT ?"
        parameters.append(args.limit)

    for row in connection.execute(sql, parameters):
        print("\t".join("" if value is None else str(value) for value in row))


def command_show(connection, args):
    path = str(args.path.resolve())
    rows = connection.execute(
        """
        SELECT c.hdu, c.keyword, c.value, c.comment
        FROM files AS f
        JOIN cards AS c ON c.file_id = f.id
        WHERE f.path = ?
        ORDER BY c.hdu, c.card_index
        """,
        (path,),
    )
    found = False
    for hdu, keyword, value, comment in rows:
        found = True
        output = f"HDU {hdu}\t{keyword} = {value if value is not None else ''}"
        if comment:
            output += f" / {comment}"
        print(output)
    if not found:
        print(f"No indexed headers found for {path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Query the SQLite index created by rebuild_fits_header_index.py."
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("keys", help="list header keywords and file counts")

    values_parser = commands.add_parser(
        "values", help="list distinct values and file counts for a keyword"
    )
    values_parser.add_argument("keyword")

    find_parser = commands.add_parser(
        "find", help="find files by keyword, exact value, substring, or missing key"
    )
    find_parser.add_argument("keyword")
    find_mode = find_parser.add_mutually_exclusive_group()
    find_mode.add_argument("--equals", help="match this exact header value")
    find_mode.add_argument(
        "--contains", help="match this substring (ASCII case-insensitive)"
    )
    find_mode.add_argument(
        "--missing", action="store_true", help="find files without this keyword"
    )
    find_parser.add_argument(
        "--hdu", type=int, help="restrict the search to one HDU number"
    )
    find_parser.add_argument(
        "--limit", type=int, default=100, help="maximum output rows (0 for unlimited)"
    )

    show_parser = commands.add_parser("show", help="print all indexed cards for a file")
    show_parser.add_argument("path", type=Path)

    args = parser.parse_args()
    if args.command == "find" and args.limit < 0:
        parser.error("--limit must be zero or greater")
    if args.command == "find" and args.hdu is not None and args.hdu < 0:
        parser.error("--hdu must be zero or greater")

    connection = connect(args.database, parser)
    try:
        {
            "keys": command_keys,
            "values": command_values,
            "find": command_find,
            "show": command_show,
        }[args.command](connection, args)
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
