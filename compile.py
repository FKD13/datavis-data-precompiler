import csv
import json
import os
from functools import lru_cache

import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s\t%(message)s'))

logger = colorlog.getLogger('example')
logger.addHandler(handler)
logger.setLevel('DEBUG')

COMPILE_SERIES = (
    "SH.H2O.BASW.ZS",     # People using at least basic drinking water services (% of population)
    "SH.HIV.INCD.TL.P3",  # Incidence of HIV, all (per 1,000 uninfected population)
    "SE.PRM.ENRR",        # School enrollment, primary (% gross)
    "SE.PRM.NENR",        # School enrollment, primary (% net)
    "SE.SEC.ENRR",        # School enrollment, secondary (% gross)
    "SE.SEC.NENR",        # School enrollment, secondary (% net)
    "SE.TER.ENRR",        # School enrollment, tertiary (% gross)
    "SH.TBS.INCD",        # Incidence of tuberculosis (per 100,000 people)
    "SH.IMM.IBCG",        # Immunization, BCG (% of one-year-old children)
    "SH.XPD.CHEX.PC.CD",  # Current health expenditure per capita (current US$)
)


@lru_cache
def open_file(path: str) -> list:
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)


for series in COMPILE_SERIES:
    stats_series = open_file('raw_data/HNP_StatsSeries.csv')
    if series not in [s['Series Code'] for s in stats_series]:
        logger.warning(f"Series {series} not found")
        continue

    logger.debug(f'{series} >>> Loading data')
    stats_data = open_file('raw_data/HNP_StatsData.csv')
    series_data = sorted([row for row in stats_data if row['Indicator Code'] == series], key=lambda x: x['Country Name'])

    logger.debug(f'{series} >>> Setting up directory structure')
    os.makedirs(f'compiled_data/{series}/year', exist_ok=True)

    year_data = {year: [] for year in range(1960, 2022)}
    year_data[0] = []

    logger.debug(f'{series} >>> Processing data')
    for row in series_data:
        country = {
            'Country Name': row['Country Name'],
            'Country Code': row['Country Code']
        }

        for year in range(1960, 2022):
            country_year = dict(country)
            year_value: str = row[f'{year}']
            country_year['years'] = [{year: float(year_value) if year_value != '' else None}]
            year_data[year] += [country_year]

        country['years'] = []
        for year in range(1960, 2022):
            year_value: str = row[f'{year}']
            country['years'] += [{year: float(year_value) if year_value != '' else None}]
        year_data[0] += [country]

    logger.debug(f'{series} >>> Saving compiled_data/{series}/all.json')
    with open(f'compiled_data/{series}/all.json', 'w') as file:
        json.dump(year_data[0], file)

    for year in range(1960, 2022):
        logger.debug(f'{series} >>> Saving compiled_data/{series}/year/{year}.json')
        with open(f'compiled_data/{series}/year/{year}.json', 'w') as file:
            json.dump(year_data[year], file)

    logger.info(f'{series} >>> Compiled {series}')
