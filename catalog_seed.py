from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CoinSeed:
    id: str
    name: str
    denomination: str
    years: str
    program: str
    category: str
    description: str
    source: str
    tags: tuple[str, ...] = field(default_factory=tuple)


def slug(value: str) -> str:
    cleaned = []
    last_dash = False
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
            last_dash = False
        elif not last_dash:
            cleaned.append("-")
            last_dash = True
    return "".join(cleaned).strip("-")


US_MINT_CIRCULATING = "https://www.usmint.gov/learn/coins-and-medals/circulating-coins"
US_MINT_DOLLARS = "https://www.usmint.gov/learn/coins-and-medals/circulating-coins/dollar-coins"
US_MINT_ATB = "https://www.usmint.gov/learn/coins-and-medals/circulating-coins/quarter/america-the-beautiful-quarters"
US_MINT_CCCRA = "https://www.usmint.gov/news/inside-the-mint/coin-programs-in-the-circulating-collectible-coin-redesign-act"
US_MINT_NATIVE_DOLLAR = "https://www.usmint.gov/learn/coins-and-medals/collectible-coins/native-american-dollar-coins"
US_MINT_INNOVATION = "https://www.usmint.gov/learn/coins-and-medals/collectible-coins/american-innovation-dollar-coins"


REGULAR_TYPES = [
    ("cent-flowing-hair-chain", "Flowing Hair Chain Cent", "Cent", "1793", "Large cents", "Early federal copper cent with chain reverse"),
    ("cent-flowing-hair-wreath", "Flowing Hair Wreath Cent", "Cent", "1793", "Large cents", "Early federal copper cent with wreath reverse"),
    ("cent-liberty-cap", "Liberty Cap Cent", "Cent", "1793-1796", "Large cents", "Liberty Cap copper cent"),
    ("cent-draped-bust", "Draped Bust Cent", "Cent", "1796-1807", "Large cents", "Draped Bust copper cent"),
    ("cent-classic-head", "Classic Head Cent", "Cent", "1808-1814", "Large cents", "Classic Head copper cent"),
    ("cent-coronet", "Coronet Head Cent", "Cent", "1816-1857", "Large cents", "Coronet or Matron Head copper cent"),
    ("cent-flying-eagle", "Flying Eagle Cent", "Cent", "1856-1858", "Small cents", "First small-size U.S. cent"),
    ("cent-indian-head", "Indian Head Cent", "Cent", "1859-1909", "Small cents", "Liberty wearing feathered headdress"),
    ("cent-lincoln-wheat", "Lincoln Wheat Cent", "Cent", "1909-1958", "Lincoln cents", "Wheat ears reverse"),
    ("cent-lincoln-memorial", "Lincoln Memorial Cent", "Cent", "1959-2008", "Lincoln cents", "Lincoln Memorial reverse"),
    ("cent-lincoln-bicentennial", "Lincoln Bicentennial Cents", "Cent", "2009", "Lincoln cents", "Four one-year reverses for Lincoln's bicentennial"),
    ("cent-lincoln-shield", "Lincoln Shield Cent", "Cent", "2010-present", "Lincoln cents", "Union shield reverse"),
    ("two-cent-shield", "Shield Two-Cent Piece", "Two cent", "1864-1873", "Two-cent pieces", "First U.S. coin bearing IN GOD WE TRUST"),
    ("three-cent-silver", "Silver Three-Cent Piece", "Three cent", "1851-1873", "Three-cent pieces", "Small silver three-cent coin"),
    ("three-cent-nickel", "Nickel Three-Cent Piece", "Three cent", "1865-1889", "Three-cent pieces", "Copper-nickel three-cent coin"),
    ("half-dime-flowing-hair", "Flowing Hair Half Dime", "Half dime", "1794-1795", "Half dimes", "Early silver half dime"),
    ("half-dime-draped-bust", "Draped Bust Half Dime", "Half dime", "1796-1805", "Half dimes", "Draped Bust silver half dime"),
    ("half-dime-capped-bust", "Capped Bust Half Dime", "Half dime", "1829-1837", "Half dimes", "Capped Bust silver half dime"),
    ("half-dime-seated-liberty", "Seated Liberty Half Dime", "Half dime", "1837-1873", "Half dimes", "Seated Liberty silver half dime"),
    ("nickel-shield", "Shield Nickel", "Nickel", "1866-1883", "Nickels", "First five-cent nickel"),
    ("nickel-liberty-head", "Liberty Head Nickel", "Nickel", "1883-1913", "Nickels", "Liberty Head or V nickel"),
    ("nickel-buffalo", "Buffalo Nickel", "Nickel", "1913-1938", "Nickels", "Indian Head obverse and bison reverse"),
    ("nickel-jefferson-monticello", "Jefferson Nickel", "Nickel", "1938-2003", "Nickels", "Monticello reverse"),
    ("nickel-westward-journey", "Westward Journey Nickels", "Nickel", "2004-2005", "Nickels", "Peace Medal, Keelboat, Bison, and Ocean in View reverses"),
    ("nickel-jefferson-return", "Jefferson Return to Monticello Nickel", "Nickel", "2006-present", "Nickels", "Forward-facing Jefferson obverse"),
    ("dime-draped-bust", "Draped Bust Dime", "Dime", "1796-1807", "Dimes", "Early federal silver dime"),
    ("dime-capped-bust", "Capped Bust Dime", "Dime", "1809-1837", "Dimes", "Capped Bust silver dime"),
    ("dime-seated-liberty", "Seated Liberty Dime", "Dime", "1837-1891", "Dimes", "Seated Liberty silver dime"),
    ("dime-barber", "Barber Dime", "Dime", "1892-1916", "Dimes", "Charles Barber Liberty head design"),
    ("dime-mercury", "Mercury Dime", "Dime", "1916-1945", "Dimes", "Winged Liberty Head dime"),
    ("dime-roosevelt", "Roosevelt Dime", "Dime", "1946-2025", "Dimes", "Torch, olive branch, and oak branch reverse"),
    ("dime-semiq", "Semiquincentennial Dime", "Dime", "2026", "Semiquincentennial", "One-year Liberty over Tyranny design"),
    ("twenty-cent-seated-liberty", "Seated Liberty Twenty-Cent Piece", "Twenty cent", "1875-1878", "Twenty-cent pieces", "Short-lived silver twenty-cent denomination"),
    ("quarter-draped-bust", "Draped Bust Quarter", "Quarter", "1796-1807", "Quarters", "Early federal silver quarter"),
    ("quarter-capped-bust", "Capped Bust Quarter", "Quarter", "1815-1838", "Quarters", "Capped Bust silver quarter"),
    ("quarter-seated-liberty", "Seated Liberty Quarter", "Quarter", "1838-1891", "Quarters", "Seated Liberty silver quarter"),
    ("quarter-barber", "Barber Quarter", "Quarter", "1892-1916", "Quarters", "Charles Barber Liberty head design"),
    ("quarter-standing-liberty", "Standing Liberty Quarter", "Quarter", "1916-1930", "Quarters", "Standing Liberty silver quarter"),
    ("quarter-washington-standard", "Washington Quarter", "Quarter", "1932-1998", "Quarters", "Eagle reverse"),
    ("quarter-bicentennial", "Bicentennial Washington Quarter", "Quarter", "1975-1976", "Commemorative circulating", "Drummer boy reverse"),
    ("half-dollar-flowing-hair", "Flowing Hair Half Dollar", "Half dollar", "1794-1795", "Half dollars", "Early federal silver half dollar"),
    ("half-dollar-draped-bust", "Draped Bust Half Dollar", "Half dollar", "1796-1807", "Half dollars", "Draped Bust silver half dollar"),
    ("half-dollar-capped-bust", "Capped Bust Half Dollar", "Half dollar", "1807-1839", "Half dollars", "Capped Bust silver half dollar"),
    ("half-dollar-seated-liberty", "Seated Liberty Half Dollar", "Half dollar", "1839-1891", "Half dollars", "Seated Liberty silver half dollar"),
    ("half-dollar-barber", "Barber Half Dollar", "Half dollar", "1892-1915", "Half dollars", "Charles Barber Liberty head design"),
    ("half-dollar-walking-liberty", "Walking Liberty Half Dollar", "Half dollar", "1916-1947", "Half dollars", "Walking Liberty obverse"),
    ("half-dollar-franklin", "Franklin Half Dollar", "Half dollar", "1948-1963", "Half dollars", "Benjamin Franklin and Liberty Bell"),
    ("half-dollar-kennedy", "Kennedy Half Dollar", "Half dollar", "1964-2025", "Half dollars", "Presidential seal reverse"),
    ("half-dollar-bicentennial", "Bicentennial Kennedy Half Dollar", "Half dollar", "1975-1976", "Commemorative circulating", "Independence Hall reverse"),
    ("half-dollar-enduring-liberty", "Enduring Liberty Half Dollar", "Half dollar", "2026", "Semiquincentennial", "One-year 250th anniversary design"),
    ("dollar-flowing-hair", "Flowing Hair Dollar", "Dollar", "1794-1795", "Dollar coins", "First U.S. silver dollar type"),
    ("dollar-draped-bust", "Draped Bust Dollar", "Dollar", "1795-1804", "Dollar coins", "Early federal silver dollar"),
    ("dollar-gobrecht", "Gobrecht Dollar", "Dollar", "1836-1839", "Dollar coins", "Seated Liberty pattern and regular issue dollar"),
    ("dollar-seated-liberty", "Seated Liberty Dollar", "Dollar", "1840-1873", "Dollar coins", "Seated Liberty silver dollar"),
    ("dollar-trade", "Trade Dollar", "Dollar", "1873-1885", "Dollar coins", "Trade dollar for Asian commerce"),
    ("dollar-morgan", "Morgan Dollar", "Dollar", "1878-1904, 1921", "Dollar coins", "Classic Morgan silver dollar"),
    ("dollar-peace", "Peace Dollar", "Dollar", "1921-1935", "Dollar coins", "Peace silver dollar"),
    ("dollar-eisenhower", "Eisenhower Dollar", "Dollar", "1971-1978", "Dollar coins", "Apollo 11 mission patch reverse"),
    ("dollar-susan-b-anthony", "Susan B. Anthony Dollar", "Dollar", "1979-1981, 1999", "Dollar coins", "First circulating U.S. coin honoring a non-mythical woman"),
    ("dollar-sacagawea", "Sacagawea Golden Dollar", "Dollar", "2000-2008", "Dollar coins", "Soaring eagle reverse"),
    ("gold-dollar-liberty-head", "Liberty Head Gold Dollar", "Gold $1", "1849-1854", "Gold coins", "Small gold dollar, Type I"),
    ("gold-dollar-indian-princess-small-head", "Indian Princess Gold Dollar - Small Head", "Gold $1", "1854-1856", "Gold coins", "Gold dollar, Type II"),
    ("gold-dollar-indian-princess-large-head", "Indian Princess Gold Dollar - Large Head", "Gold $1", "1856-1889", "Gold coins", "Gold dollar, Type III"),
    ("gold-quarter-eagle-turban-head", "Turban Head Quarter Eagle", "Gold $2.50", "1796-1807", "Gold coins", "Early quarter eagle gold coin"),
    ("gold-quarter-eagle-capped-bust", "Capped Bust Quarter Eagle", "Gold $2.50", "1808-1834", "Gold coins", "Capped Bust quarter eagle"),
    ("gold-quarter-eagle-classic-head", "Classic Head Quarter Eagle", "Gold $2.50", "1834-1839", "Gold coins", "Classic Head quarter eagle"),
    ("gold-quarter-eagle-liberty-head", "Liberty Head Quarter Eagle", "Gold $2.50", "1840-1907", "Gold coins", "Liberty Head quarter eagle"),
    ("gold-quarter-eagle-indian-head", "Indian Head Quarter Eagle", "Gold $2.50", "1908-1929", "Gold coins", "Incuse Indian Head quarter eagle"),
    ("gold-three-dollar-indian-princess", "Indian Princess Three-Dollar Gold Piece", "Gold $3", "1854-1889", "Gold coins", "Three-dollar gold denomination"),
    ("gold-four-dollar-stella", "Stella Four-Dollar Gold Piece", "Gold $4", "1879-1880", "Gold coins", "Pattern four-dollar gold coin"),
    ("gold-half-eagle-turban-head", "Turban Head Half Eagle", "Gold $5", "1795-1807", "Gold coins", "Early half eagle gold coin"),
    ("gold-half-eagle-capped-bust", "Capped Bust Half Eagle", "Gold $5", "1807-1834", "Gold coins", "Capped Bust half eagle"),
    ("gold-half-eagle-classic-head", "Classic Head Half Eagle", "Gold $5", "1834-1838", "Gold coins", "Classic Head half eagle"),
    ("gold-half-eagle-liberty-head", "Liberty Head Half Eagle", "Gold $5", "1839-1908", "Gold coins", "Liberty Head half eagle"),
    ("gold-half-eagle-indian-head", "Indian Head Half Eagle", "Gold $5", "1908-1929", "Gold coins", "Incuse Indian Head half eagle"),
    ("gold-eagle-turban-head", "Turban Head Eagle", "Gold $10", "1795-1804", "Gold coins", "Early ten-dollar gold eagle"),
    ("gold-eagle-liberty-head", "Liberty Head Eagle", "Gold $10", "1838-1907", "Gold coins", "Liberty Head ten-dollar eagle"),
    ("gold-eagle-indian-head", "Indian Head Eagle", "Gold $10", "1907-1933", "Gold coins", "Saint-Gaudens Indian Head eagle"),
    ("gold-double-eagle-liberty-head", "Liberty Head Double Eagle", "Gold $20", "1849-1907", "Gold coins", "Liberty Head twenty-dollar gold coin"),
    ("gold-double-eagle-saint-gaudens", "Saint-Gaudens Double Eagle", "Gold $20", "1907-1933", "Gold coins", "Saint-Gaudens twenty-dollar gold coin"),
    ("bullion-american-eagle-gold", "American Gold Eagle", "Gold bullion", "1986-present", "Bullion coins", "Modern U.S. gold bullion coin program"),
    ("bullion-american-eagle-silver", "American Silver Eagle", "Silver bullion", "1986-present", "Bullion coins", "Modern U.S. silver bullion coin program"),
    ("bullion-american-eagle-platinum", "American Platinum Eagle", "Platinum bullion", "1997-present", "Bullion coins", "Modern U.S. platinum bullion coin program"),
    ("bullion-american-eagle-palladium", "American Palladium Eagle", "Palladium bullion", "2017-present", "Bullion coins", "Modern U.S. palladium bullion coin program"),
    ("bullion-american-buffalo-gold", "American Buffalo Gold Coin", "Gold bullion", "2006-present", "Bullion coins", "24-karat gold bullion coin using Buffalo nickel designs"),
]


STATE_QUARTERS = [
    (1999, "Delaware", "The First State"), (1999, "Pennsylvania", "Commonwealth statue"), (1999, "New Jersey", "Washington Crossing the Delaware"), (1999, "Georgia", "Peach and state outline"), (1999, "Connecticut", "Charter Oak"),
    (2000, "Massachusetts", "The Minuteman"), (2000, "Maryland", "State House"), (2000, "South Carolina", "Carolina wren and palmetto"), (2000, "New Hampshire", "Old Man of the Mountain"), (2000, "Virginia", "Jamestown ships"),
    (2001, "New York", "Statue of Liberty and state outline"), (2001, "North Carolina", "First Flight"), (2001, "Rhode Island", "Sailboat and bridge"), (2001, "Vermont", "Camel's Hump and maple trees"), (2001, "Kentucky", "Federal Hill and racehorse"),
    (2002, "Tennessee", "Musical heritage"), (2002, "Ohio", "Birthplace of Aviation Pioneers"), (2002, "Louisiana", "Louisiana Purchase"), (2002, "Indiana", "Indy race car"), (2002, "Mississippi", "Magnolia blossoms"),
    (2003, "Illinois", "Land of Lincoln"), (2003, "Alabama", "Helen Keller"), (2003, "Maine", "Pemaquid Point Light"), (2003, "Missouri", "Corps of Discovery"), (2003, "Arkansas", "Rice, diamond, and mallard"),
    (2004, "Michigan", "Great Lakes State"), (2004, "Florida", "Gateway to Discovery"), (2004, "Texas", "Lone Star State"), (2004, "Iowa", "Foundation in Education"), (2004, "Wisconsin", "Agriculture"),
    (2005, "California", "John Muir and Yosemite"), (2005, "Minnesota", "Land of 10,000 Lakes"), (2005, "Oregon", "Crater Lake"), (2005, "Kansas", "Buffalo and sunflower"), (2005, "West Virginia", "New River Gorge"),
    (2006, "Nevada", "Wild horses"), (2006, "Nebraska", "Chimney Rock"), (2006, "Colorado", "Colorful Colorado"), (2006, "North Dakota", "Badlands and bison"), (2006, "South Dakota", "Mount Rushmore and pheasant"),
    (2007, "Montana", "Big Sky Country"), (2007, "Washington", "Salmon and Mount Rainier"), (2007, "Idaho", "Peregrine falcon"), (2007, "Wyoming", "Buckaroo"), (2007, "Utah", "Golden Spike"),
    (2008, "Oklahoma", "Scissor-tailed flycatcher"), (2008, "New Mexico", "Zia sun symbol"), (2008, "Arizona", "Grand Canyon and saguaro"), (2008, "Alaska", "Grizzly bear"), (2008, "Hawaii", "King Kamehameha I"),
]

TERRITORY_QUARTERS = [
    (2009, "District of Columbia", "Duke Ellington"), (2009, "Puerto Rico", "Isla del Encanto"), (2009, "Guam", "Guahan I Tano ManChamorro"), (2009, "American Samoa", "Ava bowl and whisk"), (2009, "U.S. Virgin Islands", "Bananaquit and yellow cedar"), (2009, "Northern Mariana Islands", "Limestone latte stone"),
]

BEAUTIFUL_QUARTERS = [
    (2010, "Hot Springs", "Arkansas"), (2010, "Yellowstone", "Wyoming"), (2010, "Yosemite", "California"), (2010, "Grand Canyon", "Arizona"), (2010, "Mount Hood", "Oregon"),
    (2011, "Gettysburg", "Pennsylvania"), (2011, "Glacier", "Montana"), (2011, "Olympic", "Washington"), (2011, "Vicksburg", "Mississippi"), (2011, "Chickasaw", "Oklahoma"),
    (2012, "El Yunque", "Puerto Rico"), (2012, "Chaco Culture", "New Mexico"), (2012, "Acadia", "Maine"), (2012, "Hawaii Volcanoes", "Hawaii"), (2012, "Denali", "Alaska"),
    (2013, "White Mountain", "New Hampshire"), (2013, "Perry's Victory", "Ohio"), (2013, "Great Basin", "Nevada"), (2013, "Fort McHenry", "Maryland"), (2013, "Mount Rushmore", "South Dakota"),
    (2014, "Great Smoky Mountains", "Tennessee"), (2014, "Shenandoah", "Virginia"), (2014, "Arches", "Utah"), (2014, "Great Sand Dunes", "Colorado"), (2014, "Everglades", "Florida"),
    (2015, "Homestead", "Nebraska"), (2015, "Kisatchie", "Louisiana"), (2015, "Blue Ridge Parkway", "North Carolina"), (2015, "Bombay Hook", "Delaware"), (2015, "Saratoga", "New York"),
    (2016, "Shawnee", "Illinois"), (2016, "Cumberland Gap", "Kentucky"), (2016, "Harpers Ferry", "West Virginia"), (2016, "Theodore Roosevelt", "North Dakota"), (2016, "Fort Moultrie", "South Carolina"),
    (2017, "Effigy Mounds", "Iowa"), (2017, "Frederick Douglass", "District of Columbia"), (2017, "Ozark Riverways", "Missouri"), (2017, "Ellis Island", "New Jersey"), (2017, "George Rogers Clark", "Indiana"),
    (2018, "Pictured Rocks", "Michigan"), (2018, "Apostle Islands", "Wisconsin"), (2018, "Voyageurs", "Minnesota"), (2018, "Cumberland Island", "Georgia"), (2018, "Block Island", "Rhode Island"),
    (2019, "Lowell", "Massachusetts"), (2019, "American Memorial Park", "Northern Mariana Islands"), (2019, "War in the Pacific", "Guam"), (2019, "San Antonio Missions", "Texas"), (2019, "Frank Church River of No Return", "Idaho"),
    (2020, "National Park of American Samoa", "American Samoa"), (2020, "Weir Farm", "Connecticut"), (2020, "Salt River Bay", "U.S. Virgin Islands"), (2020, "Marsh-Billings-Rockefeller", "Vermont"), (2020, "Tallgrass Prairie", "Kansas"),
    (2021, "Tuskegee Airmen", "Alabama"),
]

AMERICAN_WOMEN_QUARTERS = [
    (2022, "Maya Angelou"), (2022, "Dr. Sally Ride"), (2022, "Wilma Mankiller"), (2022, "Nina Otero-Warren"), (2022, "Anna May Wong"),
    (2023, "Bessie Coleman"), (2023, "Edith Kanakaole"), (2023, "Eleanor Roosevelt"), (2023, "Jovita Idar"), (2023, "Maria Tallchief"),
    (2024, "Rev. Dr. Pauli Murray"), (2024, "Patsy Takemoto Mink"), (2024, "Dr. Mary Edwards Walker"), (2024, "Celia Cruz"), (2024, "Zitkala-Sa"),
    (2025, "Ida B. Wells"), (2025, "Juliette Gordon Low"), (2025, "Dr. Vera Rubin"), (2025, "Stacey Park Milbern"), (2025, "Althea Gibson"),
]

SEMIQUINCENTENNIAL_QUARTERS = [
    (2026, "Mayflower Compact"), (2026, "Revolutionary War"), (2026, "Declaration of Independence"), (2026, "U.S. Constitution"), (2026, "Gettysburg Address"),
]

PRESIDENTIAL_DOLLARS = [
    (2007, "George Washington"), (2007, "John Adams"), (2007, "Thomas Jefferson"), (2007, "James Madison"),
    (2008, "James Monroe"), (2008, "John Quincy Adams"), (2008, "Andrew Jackson"), (2008, "Martin Van Buren"),
    (2009, "William Henry Harrison"), (2009, "John Tyler"), (2009, "James K. Polk"), (2009, "Zachary Taylor"),
    (2010, "Millard Fillmore"), (2010, "Franklin Pierce"), (2010, "James Buchanan"), (2010, "Abraham Lincoln"),
    (2011, "Andrew Johnson"), (2011, "Ulysses S. Grant"), (2011, "Rutherford B. Hayes"), (2011, "James Garfield"),
    (2012, "Chester A. Arthur"), (2012, "Grover Cleveland - first term"), (2012, "Benjamin Harrison"), (2012, "Grover Cleveland - second term"),
    (2013, "William McKinley"), (2013, "Theodore Roosevelt"), (2013, "William Howard Taft"), (2013, "Woodrow Wilson"),
    (2014, "Warren G. Harding"), (2014, "Calvin Coolidge"), (2014, "Herbert Hoover"), (2014, "Franklin D. Roosevelt"),
    (2015, "Harry S. Truman"), (2015, "Dwight D. Eisenhower"), (2015, "John F. Kennedy"), (2015, "Lyndon B. Johnson"),
    (2016, "Richard Nixon"), (2016, "Gerald Ford"), (2016, "Ronald Reagan"), (2020, "George H. W. Bush"),
]

NATIVE_AMERICAN_DOLLARS = [
    (2009, "Agriculture and the Three Sisters"), (2010, "Great Law of Peace"), (2011, "Wampanoag Treaty"), (2012, "Trade Routes in the 17th Century"),
    (2013, "Treaty with the Delawares"), (2014, "Native Hospitality"), (2015, "Mohawk Ironworkers"), (2016, "Code Talkers"),
    (2017, "Sequoyah"), (2018, "Jim Thorpe"), (2019, "Mary Golda Ross and the Space Program"), (2020, "Elizabeth Peratrovich"),
    (2021, "American Indians in the U.S. Military"), (2022, "Ely S. Parker"), (2023, "Maria Tallchief"), (2024, "Indian Citizenship Act of 1924"),
    (2025, "Mary Kawena Pukui"), (2026, "Polly Cooper and the Oneida at Valley Forge"),
]

INNOVATION_DOLLARS = [
    (2018, "Introductory coin", "First U.S. patent"),
    (2019, "Delaware", "Classifying the stars"), (2019, "Pennsylvania", "Polio vaccine"), (2019, "New Jersey", "Light bulb"), (2019, "Georgia", "Trustees' Garden"),
    (2020, "Connecticut", "Gerber Variable Scale"), (2020, "Massachusetts", "Telephone"), (2020, "Maryland", "Hubble Space Telescope"), (2020, "South Carolina", "Septima Clark"),
    (2021, "New Hampshire", "Home video game system"), (2021, "Virginia", "Chesapeake Bay Bridge-Tunnel"), (2021, "New York", "Erie Canal"), (2021, "North Carolina", "First public university"),
    (2022, "Rhode Island", "Naval War College"), (2022, "Vermont", "Snowboarding"), (2022, "Kentucky", "Bluegrass music"), (2022, "Tennessee", "Tennessee Valley Authority"),
    (2023, "Ohio", "Underground Railroad"), (2023, "Louisiana", "Higgins Boat"), (2023, "Indiana", "Automobile racing"), (2023, "Mississippi", "Delta blues"),
    (2024, "Illinois", "Steel plow"), (2024, "Alabama", "Saturn V rocket"), (2024, "Maine", "Dr. Bernard Lown"), (2024, "Missouri", "George Washington Carver"),
    (2025, "Arkansas", "Raye Montague"), (2025, "Michigan", "Automobile assembly line"), (2025, "Florida", "Space Shuttle Program"), (2025, "Texas", "Mission Control at the Johnson Space Center"),
    (2026, "Iowa", "Dr. Norman Borlaug"), (2026, "Wisconsin", "Cray-1 Supercomputer"), (2026, "California", "Steve Jobs"), (2026, "Minnesota", "Mobile refrigeration"),
]


def build_seed_catalog() -> list[CoinSeed]:
    coins: list[CoinSeed] = [
        CoinSeed(
            id=coin_id,
            name=name,
            denomination=denomination,
            years=years,
            program=program,
            category="Type coin",
            description=description,
            source=US_MINT_CIRCULATING if denomination != "Dollar" else US_MINT_DOLLARS,
            tags=(denomination, program),
        )
        for coin_id, name, denomination, years, program, description in REGULAR_TYPES
    ]

    coins.extend(
        CoinSeed(
            id=f"quarter-state-{slug(state)}",
            name=f"{state} State Quarter",
            denomination="Quarter",
            years=str(year),
            program="50 State Quarters",
            category="Circulating commemorative",
            description=design,
            source=US_MINT_CIRCULATING,
            tags=("quarter", state, "state quarter"),
        )
        for year, state, design in STATE_QUARTERS
    )

    coins.extend(
        CoinSeed(
            id=f"quarter-territory-{slug(place)}",
            name=f"{place} Quarter",
            denomination="Quarter",
            years=str(year),
            program="DC and U.S. Territories Quarters",
            category="Circulating commemorative",
            description=design,
            source=US_MINT_CIRCULATING,
            tags=("quarter", place, "territory quarter"),
        )
        for year, place, design in TERRITORY_QUARTERS
    )

    coins.extend(
        CoinSeed(
            id=f"quarter-atb-{slug(site)}",
            name=f"{site} Quarter",
            denomination="Quarter",
            years=str(year),
            program="America the Beautiful Quarters",
            category="Circulating commemorative",
            description=f"{place} national park or national site design",
            source=US_MINT_ATB,
            tags=("quarter", site, place, "America the Beautiful"),
        )
        for year, site, place in BEAUTIFUL_QUARTERS
    )

    coins.extend(
        CoinSeed(
            id=f"quarter-awq-{slug(honoree)}",
            name=f"{honoree} Quarter",
            denomination="Quarter",
            years=str(year),
            program="American Women Quarters",
            category="Circulating commemorative",
            description=f"Honors {honoree}",
            source=US_MINT_CCCRA,
            tags=("quarter", honoree, "American Women"),
        )
        for year, honoree in AMERICAN_WOMEN_QUARTERS
    )

    coins.extend(
        CoinSeed(
            id=f"quarter-semiq-{slug(theme)}",
            name=f"{theme} Quarter",
            denomination="Quarter",
            years=str(year),
            program="Semiquincentennial",
            category="Circulating commemorative",
            description="1776-2026 one-year circulating quarter design",
            source=US_MINT_CCCRA,
            tags=("quarter", theme, "250th"),
        )
        for year, theme in SEMIQUINCENTENNIAL_QUARTERS
    )

    coins.extend(
        CoinSeed(
            id=f"dollar-president-{slug(president)}",
            name=f"{president} Presidential Dollar",
            denomination="Dollar",
            years=str(year),
            program="Presidential $1 Coins",
            category="Collectible/circulating dollar",
            description=f"Honors President {president}",
            source=US_MINT_DOLLARS,
            tags=("dollar", president, "presidential"),
        )
        for year, president in PRESIDENTIAL_DOLLARS
    )

    coins.extend(
        CoinSeed(
            id=f"dollar-native-{year}",
            name=f"{year} Native American $1 Coin",
            denomination="Dollar",
            years=str(year),
            program="Native American $1 Coins",
            category="Collectible dollar",
            description=theme,
            source=US_MINT_NATIVE_DOLLAR,
            tags=("dollar", theme, "Sacagawea"),
        )
        for year, theme in NATIVE_AMERICAN_DOLLARS
    )

    coins.extend(
        CoinSeed(
            id=f"dollar-innovation-{year}-{slug(state_name)}",
            name=f"{state_name} American Innovation Dollar",
            denomination="Dollar",
            years=str(year),
            program="American Innovation $1 Coins",
            category="Collectible dollar",
            description=theme,
            source=US_MINT_INNOVATION,
            tags=("dollar", state_name, theme, "American Innovation"),
        )
        for year, state_name, theme in INNOVATION_DOLLARS
    )

    return coins
