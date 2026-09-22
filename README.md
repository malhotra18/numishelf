# Numishelf

**A local-first coin shelf for serious collectors.**

Numishelf is a local-first coin catalogue and collection tracker for collectors who want to stop flipping through albums just to answer: "Do I already have this one?"

It ships with a seeded U.S. coin catalogue, lets you search and filter the catalogue, and stores your personal holdings permanently in SQLite. You can track multiple copies of the same catalogue coin with different years, mint marks, grades, album locations, acquisition dates, and notes.

Numishelf is built for numismatists who care about the practical details: mint marks, albums, duplicates, upgrades, proofs, notes, and fast lookup at the moment a coin is in hand.

## Why Numishelf?

Physical albums are great for display, but they are slow for discovery. Numishelf gives collectors a searchable working shelf:

- answer "Do I already own this design?" without opening every page
- track where a coin physically lives in your albums, flips, trays, or boxes
- keep notes for provenance, condition, duplicates, upgrades, and finds
- browse a catalogue visually with local coin images where available
- export your collection so your records are not trapped in one app

## Current Status

Numishelf is intentionally simple: Python backend, SQLite database, and a browser UI. No account, cloud sync, or external service is required to maintain your collection.

Current seeded catalogue in this checkout:

```text
896 catalogue records
583 Wikipedia-imported U.S. commemorative records
722 local catalogue image files
426 catalogue records with at least one local image
```

## Features

- Searchable U.S. coin catalogue
- My Collection view for owned coins only
- Persistent SQLite storage
- Multiple holdings per catalogue coin
- Issue year, mint mark, quantity, grade, album location, acquired date, and notes
- Local image cache for catalogue images
- Add custom catalogue coins from the UI
- Import additional catalogue rows from CSV
- Export/import JSON backups
- Source URLs stored on imported catalogue records

## Built For Collectors

Numishelf treats the catalogue and the collection as different things.

The catalogue is the reference shelf: coin types, designs, programmes, years, sources, descriptions, and images.

Your collection is the personal shelf: the exact coins you own, with mint marks, quantities, grades, notes, and physical locations.

That means one catalogue entry can support multiple real holdings:

```text
Delaware State Quarter
- 1999 P, circulated, Book 1 page 2
- 1999 D, uncirculated, Book 1 page 2
- 1999 S proof, proof album
```

This is the workflow a collector actually uses when sorting change, checking travel coins, filling quarter books, or managing duplicates.

## Quick Start

Run the app:

```bash
python3 app.py
```

Open:

```text
http://127.0.0.1:8001/
```

The app stores data in:

```text
data/numismatics.sqlite
```

## How Collection Tracking Works

The catalogue record represents the coin type or issue, for example "Delaware State Quarter" or "Morgan Dollar".

A collection holding represents your actual owned coin:

```text
coin: Delaware State Quarter
issue year: 1999
mint mark: P
quantity: 1
grade: Circulated
album location: Book 1, page 2, slot A
notes: Found in change
```

You can save multiple holdings against the same catalogue record, which is useful for P/D/S mint marks, duplicates, proofs, upgrades, or coins stored in different albums.

## Catalogue Scope

The built-in seed includes:

- Regular U.S. type coins across cents, nickels, dimes, quarters, half dollars, dollars, gold types, and bullion programs
- 50 State Quarters
- DC and U.S. Territories Quarters
- America the Beautiful Quarters
- American Women Quarters
- 2026 Semiquincentennial quarter designs
- Presidential $1 Coins
- Native American $1 Coins
- American Innovation $1 Coins
- U.S. commemorative coin tables imported from Wikipedia decade pages

This is a collector catalogue, not an auction database. It does not attempt to store every slab certification, price, sale, error, die variety, or marketplace listing.

## Project Layout

```text
app.py                              # Python HTTP server, API, SQLite schema
catalog_seed.py                     # Built-in catalogue seed data
import_wikipedia_commemoratives.py  # Wikipedia commemorative table importer
download_catalog_images.py          # Downloads remote image URLs into static/
index.html                          # Browser UI
app.js                              # Browser interactions and API calls
styles.css                          # UI styles
data/numismatics.sqlite             # Local database
static/images/catalog/              # Local catalogue image cache
```

## Database

The database has two main tables:

- `coins`: catalogue records
- `collection_items`: personal holdings

Important `coins` fields:

- `name`
- `denomination`
- `years`
- `program`
- `category`
- `description`
- `source`
- `obverse_image`
- `reverse_image`
- `tags`

Important `collection_items` fields:

- `coin_id`
- `issue_year`
- `mint_mark`
- `quantity`
- `grade`
- `album_location`
- `acquired_at`
- `notes`

## Importing More Catalogue Data

You can add individual catalogue records in the UI, or bulk import a CSV:

```bash
python3 app.py --import-catalog-csv path/to/catalog.csv
```

CSV columns:

```text
id,name,denomination,years,program,category,description,source,obverse_image,reverse_image,tags
```

Use `|` between multiple tags.

## Wikipedia Commemorative Import

Import U.S. commemorative coin decade tables:

```bash
python3 import_wikipedia_commemoratives.py
```

The importer currently reads pre-1900, 1900s, 1910s, 1920s, 1930s, 1940s, 1950s, 1970s, 1980s, 1990s, 2000s, 2010s, and 2020s pages.

When a Wikipedia table includes obverse/reverse image columns, the importer stores those image URLs in SQLite.

## Local Image Cache

Download remote catalogue images into the project:

```bash
python3 download_catalog_images.py
```

Images are stored in:

```text
static/images/catalog/
```

The downloader updates SQLite so catalogue records point at local `/static/images/catalog/...` URLs instead of remote Wikimedia URLs.

## Backups

Use **Export backup** in the app to download a JSON backup containing catalogue records and collection holdings.

Use **Import backup** to restore that JSON later.

## Open Source License

Numishelf's application code is released under the MIT License. See [LICENSE](LICENSE).

Imported catalogue data and downloaded media may come from third-party sources and remain under their original terms. See [NOTICE](NOTICE) and [ATTRIBUTION.md](ATTRIBUTION.md).

Important practical note: this repo's `.gitignore` excludes the local SQLite database and generated image cache by default. That keeps your personal collection and third-party media cache out of public commits. Users can rebuild generated data locally with:

```bash
python3 import_wikipedia_commemoratives.py
python3 download_catalog_images.py
```

## Notes For Contributors

Numishelf currently uses only the Python standard library for the app server and SQLite persistence. The import/download scripts use `requests` and `beautifulsoup4`.

Good next improvements:

- More image coverage for regular U.S. type coins
- Better source-specific importers for U.S. Mint pages
- Date/mint/variety-level catalogue expansion
- Coin photos for personal holdings
- Tests around importer normalization and database migration
- Optional desktop packaging
