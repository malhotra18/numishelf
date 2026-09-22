from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

from app import DB_PATH, init_db
from catalog_seed import slug


SOURCES = [
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_before_1900",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1900s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1910s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1920s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1930s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1940s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1950s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1970s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1980s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1990s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(2000s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(2010s)",
    "https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(2020s)",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_text(value: str) -> str:
    value = re.sub(r"\[\s*(?:\d+|Note\s+\d+)\s*\]", "", value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def image_url(cell) -> str:
    image = cell.find("img")
    if not image:
        return ""
    src = image.get("src") or image.get("data-src") or ""
    if src.startswith("//"):
        return f"https:{src}".split("?", 1)[0]
    if src.startswith("/"):
        return f"https://en.wikipedia.org{src}".split("?", 1)[0]
    return src.split("?", 1)[0]


def fetch(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=30, headers={"User-Agent": "NumismaticsLocalApp/1.0"})
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def page_title(url: str) -> str:
    return urlparse(url).path.rsplit("/", 1)[-1].replace("_", " ")


def nearest_year(table) -> str:
    node = table
    while node:
        node = node.find_previous(["h2", "h3"])
        if not node:
            break
        text = clean_text(node.get_text(" ", strip=True))
        match = re.search(r"(18|19|20)\d{2}(?:\s*[-\u2013]\s*(?:18|19|20)?\d{2})?", text)
        if match:
            return match.group(0).replace(" ", "").replace("\u2013", "-")
    return ""


def expanded_table_rows(table) -> list[dict[str, str]]:
    grid: list[list[str]] = []
    image_grid: list[list[str]] = []
    spans: dict[tuple[int, int], tuple[str, str, int]] = {}

    for row_index, tr in enumerate(table.find_all("tr")):
        output: list[str] = []
        images: list[str] = []
        col = 0
        for cell in tr.find_all(["th", "td"]):
            while (row_index, col) in spans:
                text, img, remaining = spans.pop((row_index, col))
                output.append(text)
                images.append(img)
                if remaining > 1:
                    spans[(row_index + 1, col)] = (text, img, remaining - 1)
                col += 1

            text = clean_text(cell.get_text(" ", strip=True))
            img = image_url(cell)
            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))
            for _ in range(colspan):
                output.append(text)
                images.append(img)
                if rowspan > 1:
                    spans[(row_index + 1, col)] = (text, img, rowspan - 1)
                col += 1

        while (row_index, col) in spans:
            text, img, remaining = spans.pop((row_index, col))
            output.append(text)
            images.append(img)
            if remaining > 1:
                spans[(row_index + 1, col)] = (text, img, remaining - 1)
            col += 1
        grid.append(output)
        image_grid.append(images)

    if not grid:
        return []
    headers = [clean_text(header) for header in grid[0]]
    rows = []
    for row_index, values in enumerate(grid[1:], start=1):
        if not any(values):
            continue
        row = {headers[index]: values[index] if index < len(values) else "" for index in range(len(headers))}
        images = image_grid[row_index]
        for index, header in enumerate(headers):
            if header == "Obverse" and index < len(images):
                row["__obverse_image"] = images[index]
            if header == "Reverse" and index < len(images):
                row["__reverse_image"] = images[index]
        rows.append(row)
    return rows


def face_to_denomination(face_value: str, coin_name: str) -> str:
    text = f"{face_value} {coin_name}".lower()
    if "$50" in text:
        return "Gold $50"
    if "$25" in text:
        return "Gold $25"
    if "$10" in text:
        return "Gold $10"
    if "$5" in text:
        return "Gold $5"
    if "$3" in text:
        return "Gold $3"
    if "$2.50" in text or "$2 1/2" in text or "quarter eagle" in text:
        return "Gold $2.50"
    if "$1" in text or "dollar" in text:
        return "Dollar"
    if "50" in face_value or "half dollar" in text:
        return "Half dollar"
    if "25" in face_value or "quarter" in text:
        return "Quarter"
    if "10" in face_value or "dime" in text:
        return "Dime"
    if "5" in face_value or "nickel" in text:
        return "Nickel"
    if "cent" in text:
        return "Cent"
    return clean_text(face_value) or "Commemorative"


def source_id(url: str) -> str:
    return slug(page_title(url).replace("List of United States commemorative coins and medals", "commemorative"))


def extract_rows(url: str) -> list[dict]:
    soup = fetch(url)
    extracted = []
    for table in soup.select("table.wikitable"):
        year = nearest_year(table)
        rows = expanded_table_rows(table)
        for row in rows:
            face = row.get("Face value", "")
            name = row.get("Coin", "")
            if not face or not name or name.lower() == "coin":
                continue
            name = clean_text(name)
            if not name or "vetoed" in name.lower():
                continue
            available = clean_text(row.get("Available", "")) or year
            obverse = clean_text(row.get("Obverse design", ""))
            reverse = clean_text(row.get("Reverse design", ""))
            composition = clean_text(row.get("Composition", ""))
            mintage = clean_text(row.get("Mintage", ""))
            coin_id = f"wiki-{source_id(url)}-{slug(year or available)}-{slug(face)}-{slug(name)}"
            extracted.append(
                {
                    "id": coin_id[:220],
                    "name": name,
                    "denomination": face_to_denomination(face, name),
                    "years": available,
                    "program": "U.S. commemorative coins",
                    "category": "Commemorative coin",
                    "description": "; ".join(
                        part
                        for part in [
                            f"Face value: {face}",
                            f"Obverse: {obverse}" if obverse else "",
                            f"Reverse: {reverse}" if reverse else "",
                            f"Composition: {composition}" if composition else "",
                            f"Mintage: {mintage}" if mintage else "",
                        ]
                        if part
                    ),
                    "source": url,
                    "obverse_image": row.get("__obverse_image", ""),
                    "reverse_image": row.get("__reverse_image", ""),
                    "tags": ["commemorative", page_title(url), year],
                }
            )
    return extracted


def upsert_rows(rows: list[dict]) -> int:
    timestamp = now_iso()
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        for url in SOURCES:
            db.execute(
                """
                DELETE FROM coins
                WHERE source = ?
                  AND custom = 0
                  AND id NOT IN (SELECT DISTINCT coin_id FROM collection_items)
                """,
                (url,),
            )
        for row in rows:
            db.execute(
                """
                INSERT INTO coins (
                  id, name, denomination, years, program, category, description,
                  source, obverse_image, reverse_image, tags, custom, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
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
                  updated_at = excluded.updated_at
                WHERE coins.custom = 0
                """,
                (
                    row["id"],
                    row["name"],
                    row["denomination"],
                    row["years"],
                    row["program"],
                    row["category"],
                    row["description"],
                    row["source"],
                    row["obverse_image"],
                    row["reverse_image"],
                    json.dumps(row["tags"]),
                    timestamp,
                    timestamp,
                ),
            )
    return len(rows)


def main() -> None:
    init_db()
    rows: list[dict] = []
    for url in SOURCES:
        page_rows = extract_rows(url)
        print(f"{len(page_rows):>3} rows - {url}")
        rows.extend(page_rows)
    print(f"Imported {upsert_rows(rows)} commemorative catalogue rows")


if __name__ == "__main__":
    main()
