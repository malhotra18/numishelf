from __future__ import annotations

import re
import sqlite3
import unicodedata


def first_year(value: str) -> str:
    match = re.search(r"(18|19|20)\d{2}", value or "")
    return match.group(0) if match else ""


def squash(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.lower()).strip()


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", squash(value))


STOPWORDS = {
    "american",
    "and",
    "dr",
    "national",
    "of",
    "park",
    "quarter",
    "rev",
    "site",
    "state",
    "the",
    "women",
}


def tokens(value: str) -> list[str]:
    return [token for token in squash(value).split() if token not in STOPWORDS and len(token) > 1]


def contains_name(haystack: str, needle: str) -> bool:
    return squash(needle) in squash(haystack)


def token_match(haystack: str, needle: str) -> bool:
    haystack_tokens = set(tokens(haystack))
    needle_tokens = tokens(needle)
    if not needle_tokens:
        return False
    if set(needle_tokens).issubset(haystack_tokens):
        return True
    if compact(needle) and compact(needle) in compact(haystack):
        return True
    if len(needle_tokens) >= 2 and {needle_tokens[0], needle_tokens[-1]}.issubset(haystack_tokens):
        return True
    return False


def presidential_subject(name: str) -> str:
    value = name.replace(" Presidential Dollar", "")
    value = value.replace(" - first term", " first term")
    value = value.replace(" - second term", " second term")
    return value


def quarter_subject(name: str) -> str:
    value = name
    for suffix in (" State Quarter", " Quarter"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
    return value


def innovation_subject(name: str) -> str:
    return name.replace(" American Innovation Dollar", "")


def find_canonical_coin(db: sqlite3.Connection, wiki_row: sqlite3.Row) -> str | None:
    year = first_year(wiki_row["years"])
    name = wiki_row["name"]
    denomination = wiki_row["denomination"]
    if not year:
        return None

    candidates = db.execute(
        """
        SELECT id, name, years, denomination, program
        FROM coins
        WHERE program != 'U.S. commemorative coins'
          AND denomination = ?
          AND years LIKE ?
        """,
        (denomination, f"%{year}%"),
    ).fetchall()

    for candidate in candidates:
        program = candidate["program"]
        candidate_name = candidate["name"]

        if program == "Presidential $1 Coins" and contains_name(name, presidential_subject(candidate_name)):
            return candidate["id"]

        if program in {
            "50 State Quarters",
            "DC and U.S. Territories Quarters",
            "America the Beautiful Quarters",
            "American Women Quarters",
            "Semiquincentennial",
            "Commemorative circulating",
        }:
            subject = quarter_subject(candidate_name)
            if (
                contains_name(name, subject)
                or contains_name(candidate_name, name.replace(" quarter", ""))
                or token_match(name, subject)
                or ("bicentennial" in squash(name) and candidate["id"] == "quarter-bicentennial")
            ):
                return candidate["id"]

        if program == "Native American $1 Coins" and "native american" in squash(name):
            return candidate["id"]

        if program == "American Innovation $1 Coins" and contains_name(name, innovation_subject(candidate_name)):
            return candidate["id"]

    return None


def merge_coin(db: sqlite3.Connection, source_id: str, target_id: str) -> bool:
    if source_id == target_id:
        return False

    source = db.execute("SELECT * FROM coins WHERE id = ?", (source_id,)).fetchone()
    target = db.execute("SELECT * FROM coins WHERE id = ?", (target_id,)).fetchone()
    if not source or not target:
        return False

    obverse = target["obverse_image"] or source["obverse_image"]
    reverse = target["reverse_image"] or source["reverse_image"]
    source_url = target["source"] or source["source"]
    db.execute(
        """
        UPDATE coins
        SET obverse_image = ?, reverse_image = ?, source = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (obverse, reverse, source_url, target_id),
    )
    db.execute("UPDATE collection_items SET coin_id = ? WHERE coin_id = ?", (target_id, source_id))
    db.execute("DELETE FROM coins WHERE id = ?", (source_id,))
    return True


def reconcile_imported_overlaps(db: sqlite3.Connection) -> int:
    rows = db.execute(
        """
        SELECT *
        FROM coins
        WHERE program = 'U.S. commemorative coins'
        ORDER BY years, name
        """
    ).fetchall()

    merged = 0
    for row in rows:
        target_id = find_canonical_coin(db, row)
        if target_id and merge_coin(db, row["id"], target_id):
            merged += 1
    return merged
