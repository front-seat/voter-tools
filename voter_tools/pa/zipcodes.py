"""Module for looking up zip codes, states, and counties."""

import csv
import pathlib
from enum import Enum

_ZIP_TO_STATE: dict[str, str] = {}
_ZIP_TO_COUNTY: dict[str, str] = {}

_ZIP_PATH = pathlib.Path(__file__).parent / "zipcodes.pa.csv"

_ZIPCODE_COLUMN = 1
_STATE_COLUMN = 4
_COUNTY_COLUMN = 5


def _load_zipcodes():
    global _ZIP_TO_STATE, _ZIP_TO_COUNTY
    if not _ZIP_TO_STATE or not _ZIP_TO_COUNTY:
        with open(_ZIP_PATH, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                _ZIP_TO_STATE[row[_ZIPCODE_COLUMN]] = row[_STATE_COLUMN]
                _ZIP_TO_COUNTY[row[_ZIPCODE_COLUMN]] = row[_COUNTY_COLUMN]


def _get_zip_to_state() -> dict[str, str]:
    """Return a dictionary mapping zip codes to state abbreviations."""
    _load_zipcodes()
    return _ZIP_TO_STATE


def _get_zip_to_county() -> dict[str, str]:
    """Return a dictionary mapping zip codes to county names."""
    _load_zipcodes()
    return _ZIP_TO_COUNTY


def get_state(zipcode: str) -> str | None:
    """Return the state abbreviation for a given zip code."""
    zip5 = zipcode[:5]
    return _get_zip_to_state().get(zip5)


def get_county(zipcode: str) -> str | None:
    """Return the county name for a given zip code."""
    zip5 = zipcode[:5]
    return _get_zip_to_county().get(zip5)


class CountyChoice(str, Enum):
    """
    Enum for the counties in Pennsylvania and their county codes.

    CONSIDER: This list is also returned by the API *SETUP calls, but it is
    used elsewhere (on PA's voter-facing websites, too) and it seems stable
    enough to hard-code here.
    """

    ADAMS = "ADAMS"  # 2290
    ALLEGHENY = "ALLEGHENY"  # 2291
    ARMSTRONG = "ARMSTRONG"  # 2292
    BEDFORD = "BEDFORD"  # 2294
    BERKS = "BERKS"  # 2295
    BLAIR = "BLAIR"  # 2296
    BRADFORD = "BRADFORD"  # 2297
    BUCKS = "BUCKS"  # 2298
    BUTLER = "BUTLER"  # 2299
    CAMBRIA = "CAMBRIA"  # 2300
    CAMERON = "CAMERON"  # 2301
    CARBON = "CARBON"  # 2302
    CENTRE = "CENTRE"  # 2303
    CHESTER = "CHESTER"  # 2304
    CLARION = "CLARION"  # 2305
    CLEARFIELD = "CLEARFIELD"  # 2306
    CLINTON = "CLINTON"  # 2307
    COLUMBIA = "COLUMBIA"  # 2308
    CRAWFORD = "CRAWFORD"  # 2309
    CUMBERLAND = "CUMBERLAND"  # 2310
    DAUPHIN = "DAUPHIN"  # 2311
    DELAWARE = "DELAWARE"  # 2312
    ELK = "ELK"  # 2313
    ERIE = "ERIE"  # 2314
    FAYETTE = "FAYETTE"  # 2315
    FOREST = "FOREST"  # 2316
    FRANKLIN = "FRANKLIN"  # 2317
    FULTON = "FULTON"  # 2318
    GREENE = "GREENE"  # 2319
    HUNTINGDON = "HUNTINGDON"  # 2320
    INDIANA = "INDIANA"  # 2321
    JEFFERSON = "JEFFERSON"  # 2322
    JUNIATA = "JUNIATA"  # 2323
    LACKAWANNA = "LACKAWANNA"  # 2324
    LANCASTER = "LANCASTER"  # 2325
    LAWRENCE = "LAWRENCE"  # 2326
    LEBANON = "LEBANON"  # 2327
    LEHIGH = "LEHIGH"  # 2328
    LUZERNE = "LUZERNE"  # 2329
    LYCOMING = "LYCOMING"  # 2330
    McKEAN = "McKEAN"  # 2331
    MERCER = "MERCER"  # 2332
    MIFFLIN = "MIFFLIN"  # 2333
    MONROE = "MONROE"  # 2334
    MONTGOMERY = "MONTGOMERY"  # 2335
    MONTOUR = "MONTOUR"  # 2336
    NORTHAMPTON = "NORTHAMPTON"  # 2337
    NORTHUMBERLAND = "NORTHUMBERLAND"  # 2338
    PERRY = "PERRY"  # 2339
    PHILADELPHIA = "PHILADELPHIA"  # 2340
    PIKE = "PIKE"  # 2341
    POTTER = "POTTER"  # 2342
    SCHUYLKILL = "SCHUYLKILL"  # 2343
    SNYDER = "SNYDER"  # 2344
    SOMERSET = "SOMERSET"  # 2345
    SULLIVAN = "SULLIVAN"  # 2346
    SUSQUEHANNA = "SUSQUEHANNA"  # 2347
    TIOGA = "TIOGA"  # 2348
    UNION = "UNION"  # 2349
    VENANGO = "VENANGO"  # 2350
    WARREN = "WARREN"  # 2351
    WASHINGTON = "WASHINGTON"  # 2352
    WAYNE = "WAYNE"  # 2353
    WESTMORELAND = "WESTMORELAND"  # 2354
    WYOMING = "WYOMING"  # 2355
    YORK = "YORK"  # 2356


def get_county_choice(zipcode: str) -> CountyChoice | None:
    """Get the county code for a Pennsylvania ZIP code."""
    county = get_county(zipcode)
    if county is None:
        return None
    try:
        return CountyChoice[county.upper()]
    except KeyError:
        return None
