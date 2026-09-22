# Attribution and Data Sources

Numishelf separates the app license from imported catalogue content and media.

## Application Code

The application code is licensed under the MIT License. See [LICENSE](LICENSE).

## U.S. Mint Sources

The seed catalogue references public U.S. Mint programme pages, including:

- https://www.usmint.gov/learn/coins-and-medals/circulating-coins
- https://www.usmint.gov/learn/coins-and-medals/commemorative-coins
- https://www.usmint.gov/learn/coins-and-medals/circulating-coins/dollar-coins
- https://www.usmint.gov/learn/coins-and-medals/collectible-coins/native-american-dollar-coins
- https://www.usmint.gov/learn/coins-and-medals/collectible-coins/american-innovation-dollar-coins

U.S. Mint site terms say some government-created works are not covered by U.S.
copyright, but they also warn users not to assume everything on the site is in
the public domain. Review current U.S. Mint terms before redistributing data or
media from the site.

## Wikipedia Tables

`import_wikipedia_commemoratives.py` imports table data from Wikipedia U.S.
commemorative coin decade pages. Wikipedia text is generally available under
Creative Commons Attribution-ShareAlike 4.0 International and the GNU Free
Documentation License.

Source pages currently used:

- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_before_1900
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1900s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1910s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1920s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1930s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1940s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1950s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1970s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1980s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(1990s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(2000s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(2010s)
- https://en.wikipedia.org/wiki/List_of_United_States_commemorative_coins_and_medals_(2020s)

## Wikimedia Images

`download_catalog_images.py` downloads image URLs already stored in SQLite,
primarily Wikimedia thumbnail URLs discovered from Wikipedia tables.

Wikimedia Commons media files have individual licenses and attribution
requirements. Some files are public domain; others are Creative Commons
licensed and require attribution. The generated local cache is not covered by
Numishelf's MIT License.

For public redistribution, either:

- exclude `static/images/catalog/` and let users rebuild the cache locally, or
- generate and maintain file-level attributions and licenses for every bundled
  media file.
