from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

import requests

from app import DB_PATH, init_db


IMAGE_DIR = Path(__file__).resolve().parent / "static" / "images" / "catalog"
IMAGE_COLUMNS = ("obverse_image", "reverse_image")
CONTENT_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}


def is_remote(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def local_url(path: Path) -> str:
    return "/" + path.relative_to(Path(__file__).resolve().parent).as_posix()


def extension_from_response(response: requests.Response, fallback_url: str) -> str:
    content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if content_type in CONTENT_EXTENSIONS:
        return CONTENT_EXTENSIONS[content_type]

    suffix = Path(urlparse(fallback_url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
        return ".jpg" if suffix == ".jpeg" else suffix

    return ".img"


def download_image(session: requests.Session, url: str, base_path: Path, force: bool) -> Path | None:
    for existing in base_path.parent.glob(f"{base_path.name}.*"):
        if existing.is_file() and not force:
            return existing

    response = session.get(url, timeout=30)
    response.raise_for_status()
    if not response.content:
        return None

    extension = extension_from_response(response, url)
    path = base_path.with_suffix(extension)
    path.write_bytes(response.content)
    return path


def cache_images(limit: int | None = None, force: bool = False) -> dict[str, int]:
    init_db()
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    stats = {"remote": 0, "downloaded": 0, "skipped": 0, "failed": 0}

    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """
            SELECT id, name, obverse_image, reverse_image
            FROM coins
            WHERE obverse_image LIKE 'http%'
               OR reverse_image LIKE 'http%'
            ORDER BY id
            """
        ).fetchall()

        session = requests.Session()
        session.headers.update({"User-Agent": "NumismaticsLocalApp/1.0"})

        processed = 0
        for row in rows:
            updates: dict[str, str] = {}
            for column in IMAGE_COLUMNS:
                url = row[column] or ""
                if not is_remote(url):
                    continue
                if limit is not None and processed >= limit:
                    break

                stats["remote"] += 1
                base_path = IMAGE_DIR / f"{row['id']}-{column.replace('_image', '')}"
                try:
                    before = set(base_path.parent.glob(f"{base_path.name}.*"))
                    path = download_image(session, url, base_path, force)
                    if not path:
                        stats["failed"] += 1
                        continue
                    after = set(base_path.parent.glob(f"{base_path.name}.*"))
                    stats["downloaded" if force or after != before else "skipped"] += 1
                    updates[column] = local_url(path)
                    processed += 1
                    print(f"{updates[column]} <- {row['name']}")
                except Exception as exc:  # noqa: BLE001 - keep bulk downloader moving.
                    stats["failed"] += 1
                    print(f"FAILED {row['id']} {column}: {exc}")

            if updates:
                assignments = ", ".join(f"{column} = ?" for column in updates)
                db.execute(
                    f"UPDATE coins SET {assignments}, updated_at = datetime('now') WHERE id = ?",
                    [*updates.values(), row["id"]],
                )

            if limit is not None and processed >= limit:
                break

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Download remote catalogue images into the local package.")
    parser.add_argument("--limit", type=int, help="Download at most this many image files.")
    parser.add_argument("--force", action="store_true", help="Re-download images even when local files exist.")
    args = parser.parse_args()
    stats = cache_images(limit=args.limit, force=args.force)
    print(stats)


if __name__ == "__main__":
    main()
