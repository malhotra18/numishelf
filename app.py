from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from catalog_seed import build_seed_catalog, slug


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "numismatics.sqlite"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS coins (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  denomination TEXT NOT NULL,
  years TEXT NOT NULL,
  program TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  source TEXT NOT NULL DEFAULT '',
  obverse_image TEXT NOT NULL DEFAULT '',
  reverse_image TEXT NOT NULL DEFAULT '',
  tags TEXT NOT NULL DEFAULT '[]',
  custom INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS collection_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  coin_id TEXT NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
  issue_year TEXT NOT NULL DEFAULT '',
  mint_mark TEXT NOT NULL DEFAULT '',
  quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0),
  grade TEXT NOT NULL DEFAULT '',
  album_location TEXT NOT NULL DEFAULT '',
  notes TEXT NOT NULL DEFAULT '',
  acquired_at TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_collection_coin_id ON collection_items(coin_id);
CREATE INDEX IF NOT EXISTS idx_coins_denomination ON coins(denomination);
CREATE INDEX IF NOT EXISTS idx_coins_program ON coins(program);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def dict_from_row(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with connect() as db:
        db.executescript(SCHEMA)
        ensure_schema(db)
        seed_catalog(db)


def ensure_schema(db: sqlite3.Connection) -> None:
    coin_columns = {row["name"] for row in db.execute("PRAGMA table_info(coins)")}
    if "obverse_image" not in coin_columns:
        db.execute("ALTER TABLE coins ADD COLUMN obverse_image TEXT NOT NULL DEFAULT ''")
    if "reverse_image" not in coin_columns:
        db.execute("ALTER TABLE coins ADD COLUMN reverse_image TEXT NOT NULL DEFAULT ''")


def seed_catalog(db: sqlite3.Connection) -> None:
    timestamp = now_iso()
    for coin in build_seed_catalog():
        db.execute(
            """
            INSERT INTO coins (
              id, name, denomination, years, program, category, description,
              source, obverse_image, reverse_image, tags, custom, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', '', ?, 0, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name = excluded.name,
              denomination = excluded.denomination,
              years = excluded.years,
              program = excluded.program,
              category = excluded.category,
              description = excluded.description,
              source = excluded.source,
              tags = excluded.tags,
              updated_at = excluded.updated_at
            WHERE coins.custom = 0
            """,
            (
                coin.id,
                coin.name,
                coin.denomination,
                coin.years,
                coin.program,
                coin.category,
                coin.description,
                coin.source,
                json.dumps(list(coin.tags)),
                timestamp,
                timestamp,
            ),
        )


def list_state() -> dict:
    with connect() as db:
        coins = [
            normalize_coin(row)
            for row in db.execute(
                """
                SELECT
                  c.*,
                  COALESCE(SUM(ci.quantity), 0) AS owned_quantity,
                  COUNT(ci.id) AS holding_count
                FROM coins c
                LEFT JOIN collection_items ci ON ci.coin_id = c.id
                GROUP BY c.id
                ORDER BY c.denomination, c.program, c.years, c.name
                """
            )
        ]
        holdings = [dict_from_row(row) for row in db.execute("SELECT * FROM collection_items ORDER BY coin_id, id")]

    owned_coins = sum(1 for coin in coins if coin["owned_quantity"] > 0)
    total_quantity = sum(item["quantity"] for item in holdings)
    denominations = sorted({coin["denomination"] for coin in coins})
    programs = sorted({coin["program"] for coin in coins})

    return {
        "coins": coins,
        "holdings": holdings,
        "facets": {"denominations": denominations, "programs": programs},
        "stats": {
            "catalog_count": len(coins),
            "owned_coin_count": owned_coins,
            "total_quantity": total_quantity,
            "completion_rate": round((owned_coins / len(coins)) * 100) if coins else 0,
        },
    }


def normalize_coin(row: sqlite3.Row) -> dict:
    coin = dict_from_row(row)
    coin["tags"] = json.loads(coin["tags"] or "[]")
    coin["custom"] = bool(coin["custom"])
    coin["owned_quantity"] = int(coin["owned_quantity"] or 0)
    coin["holding_count"] = int(coin["holding_count"] or 0)
    return coin


def add_catalog_coin(payload: dict) -> dict:
    name = str(payload.get("name", "")).strip()
    denomination = str(payload.get("denomination", "")).strip()
    if not name or not denomination:
        raise ValueError("name and denomination are required")

    timestamp = now_iso()
    base_id = f"custom-{slug(name)}"
    coin_id = payload.get("id") or base_id

    with connect() as db:
        existing = db.execute("SELECT 1 FROM coins WHERE id = ?", (coin_id,)).fetchone()
        if existing:
            coin_id = f"{base_id}-{int(datetime.now().timestamp())}"
        db.execute(
            """
            INSERT INTO coins (
              id, name, denomination, years, program, category, description,
              source, obverse_image, reverse_image, tags, custom, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                coin_id,
                name,
                denomination,
                str(payload.get("years", "")).strip() or "Unknown",
                str(payload.get("program", "")).strip() or "Custom",
                str(payload.get("category", "")).strip() or "Custom",
                str(payload.get("description", "")).strip(),
                str(payload.get("source", "")).strip(),
                str(payload.get("obverse_image", "")).strip(),
                str(payload.get("reverse_image", "")).strip(),
                json.dumps(payload.get("tags", ["custom"])),
                timestamp,
                timestamp,
            ),
        )
    return {"ok": True, "id": coin_id}


def add_holding(payload: dict) -> dict:
    coin_id = str(payload.get("coin_id", "")).strip()
    if not coin_id:
        raise ValueError("coin_id is required")
    quantity = int(payload.get("quantity") or 1)
    if quantity < 1:
        raise ValueError("quantity must be at least 1")

    timestamp = now_iso()
    with connect() as db:
        coin = db.execute("SELECT id FROM coins WHERE id = ?", (coin_id,)).fetchone()
        if not coin:
            raise ValueError("coin does not exist")
        cursor = db.execute(
            """
            INSERT INTO collection_items (
              coin_id, issue_year, mint_mark, quantity, grade, album_location,
              notes, acquired_at, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                coin_id,
                str(payload.get("issue_year", "")).strip(),
                str(payload.get("mint_mark", "")).strip().upper(),
                quantity,
                str(payload.get("grade", "")).strip(),
                str(payload.get("album_location", "")).strip(),
                str(payload.get("notes", "")).strip(),
                str(payload.get("acquired_at", "")).strip(),
                timestamp,
                timestamp,
            ),
        )
        return {"ok": True, "id": cursor.lastrowid}


def delete_holding(item_id: int) -> dict:
    with connect() as db:
        db.execute("DELETE FROM collection_items WHERE id = ?", (item_id,))
    return {"ok": True}


def export_data() -> dict:
    with connect() as db:
        coins = [normalize_plain_coin(row) for row in db.execute("SELECT * FROM coins ORDER BY denomination, program, years, name")]
        holdings = [dict_from_row(row) for row in db.execute("SELECT * FROM collection_items ORDER BY coin_id, id")]
    return {"exported_at": now_iso(), "coins": coins, "collection_items": holdings}


def normalize_plain_coin(row: sqlite3.Row) -> dict:
    coin = dict_from_row(row)
    coin["tags"] = json.loads(coin["tags"] or "[]")
    coin["custom"] = bool(coin["custom"])
    return coin


def import_data(payload: dict) -> dict:
    timestamp = now_iso()
    coins = payload.get("coins", [])
    holdings = payload.get("collection_items", payload.get("holdings", []))
    imported_coins = 0
    imported_holdings = 0

    with connect() as db:
        for coin in coins:
            if not coin.get("id") or not coin.get("name"):
                continue
            db.execute(
                """
                INSERT INTO coins (
                  id, name, denomination, years, program, category, description,
                  source, obverse_image, reverse_image, tags, custom, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  name = excluded.name,
                  denomination = excluded.denomination,
                  years = excluded.years,
                  program = excluded.program,
                  category = excluded.category,
                  description = excluded.description,
                  source = excluded.source,
                  obverse_image = excluded.obverse_image,
                  reverse_image = excluded.reverse_image,
                  tags = excluded.tags,
                  custom = MAX(coins.custom, excluded.custom),
                  updated_at = excluded.updated_at
                """,
                (
                    str(coin["id"]),
                    str(coin["name"]),
                    str(coin.get("denomination", "")),
                    str(coin.get("years", "")),
                    str(coin.get("program", "")),
                    str(coin.get("category", "")),
                    str(coin.get("description", "")),
                    str(coin.get("source", "")),
                    str(coin.get("obverse_image", "")),
                    str(coin.get("reverse_image", "")),
                    json.dumps(coin.get("tags", [])),
                    1 if coin.get("custom") else 0,
                    str(coin.get("created_at") or timestamp),
                    timestamp,
                ),
            )
            imported_coins += 1

        for item in holdings:
            coin_id = str(item.get("coin_id", "")).strip()
            if not coin_id:
                continue
            if not db.execute("SELECT 1 FROM coins WHERE id = ?", (coin_id,)).fetchone():
                continue
            db.execute(
                """
                INSERT INTO collection_items (
                  coin_id, issue_year, mint_mark, quantity, grade, album_location,
                  notes, acquired_at, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    coin_id,
                    str(item.get("issue_year", "")).strip(),
                    str(item.get("mint_mark", "")).strip().upper(),
                    int(item.get("quantity") or 1),
                    str(item.get("grade", "")).strip(),
                    str(item.get("album_location", "")).strip(),
                    str(item.get("notes", "")).strip(),
                    str(item.get("acquired_at", "")).strip(),
                    timestamp,
                    timestamp,
                ),
            )
            imported_holdings += 1

    return {"ok": True, "coins": imported_coins, "collection_items": imported_holdings}


def import_catalog_csv(path: Path) -> int:
    timestamp = now_iso()
    imported = 0
    with path.open(newline="", encoding="utf-8") as handle, connect() as db:
        reader = csv.DictReader(handle)
        for row in reader:
            name = (row.get("name") or "").strip()
            denomination = (row.get("denomination") or "").strip()
            if not name or not denomination:
                continue
            coin_id = (row.get("id") or f"custom-{slug(name)}").strip()
            db.execute(
                """
                INSERT INTO coins (
                  id, name, denomination, years, program, category, description,
                  source, obverse_image, reverse_image, tags, custom, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  name = excluded.name,
                  denomination = excluded.denomination,
                  years = excluded.years,
                  program = excluded.program,
                  category = excluded.category,
                  description = excluded.description,
                  source = excluded.source,
                  obverse_image = excluded.obverse_image,
                  reverse_image = excluded.reverse_image,
                  tags = excluded.tags,
                  custom = 1,
                  updated_at = excluded.updated_at
                """,
                (
                    coin_id,
                    name,
                    denomination,
                    (row.get("years") or "Unknown").strip(),
                    (row.get("program") or "Custom import").strip(),
                    (row.get("category") or "Custom").strip(),
                    (row.get("description") or "").strip(),
                    (row.get("source") or "").strip(),
                    (row.get("obverse_image") or "").strip(),
                    (row.get("reverse_image") or "").strip(),
                    json.dumps([tag.strip() for tag in (row.get("tags") or "").split("|") if tag.strip()]),
                    timestamp,
                    timestamp,
                ),
            )
            imported += 1
    return imported


class NumismaticsHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        route = "/index.html" if parsed.path == "/" else parsed.path
        path = (BASE_DIR / unquote(route.lstrip("/"))).resolve()
        if BASE_DIR not in path.parents and path != BASE_DIR:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(path.stat().st_size))
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self.send_json(list_state())
            return
        if parsed.path == "/api/export":
            self.send_json(
                export_data(),
                headers={"Content-Disposition": f'attachment; filename="numismatics-{datetime.now().date()}.json"'},
            )
            return

        route = "/index.html" if parsed.path == "/" else parsed.path
        self.send_file(route.lstrip("/"))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
            if parsed.path == "/api/catalog":
                self.send_json(add_catalog_coin(payload), status=HTTPStatus.CREATED)
            elif parsed.path == "/api/collection":
                self.send_json(add_holding(payload), status=HTTPStatus.CREATED)
            elif parsed.path == "/api/import":
                self.send_json(import_data(payload), status=HTTPStatus.CREATED)
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/collection/"):
            item_id = int(parsed.path.rsplit("/", 1)[-1])
            self.send_json(delete_holding(item_id))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK, headers: dict | None = None) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, relative_path: str) -> None:
        path = (BASE_DIR / unquote(relative_path)).resolve()
        if BASE_DIR not in path.parents and path != BASE_DIR:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local U.S. coin catalogue and collection app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--import-catalog-csv", type=Path)
    args = parser.parse_args()

    init_db()
    if args.import_catalog_csv:
        imported = import_catalog_csv(args.import_catalog_csv)
        print(f"Imported {imported} catalogue rows from {args.import_catalog_csv}")

    server = ThreadingHTTPServer((args.host, args.port), NumismaticsHandler)
    print(f"Serving Numismatics at http://{args.host}:{args.port}/")
    print(f"SQLite database: {DB_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    main()
