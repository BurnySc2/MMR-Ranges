from dataclasses import dataclass

import arrow
import httpx
from loguru import logger

from .constants import REGIONS
from .helper import fetch_multiple

"""
Functions to retrieve all necessary info that are displayed in the header of the website
"""


@dataclass
class SeasonInfo:
    season_start: arrow.Arrow
    season_end: arrow.Arrow
    season_number: int
    season_start_readable: str
    season_end_readable: str


async def get_current_season_info(client: httpx.AsyncClient, access_token: str) -> SeasonInfo:
    get_season_number_url = "https://{}.api.blizzard.com/sc2/ladder/season/{}"
    urls = []
    for index, region in enumerate(REGIONS, start=1):
        urls.append(get_season_number_url.format(region, index))
    responses = await fetch_multiple(client, access_token, urls, fetch_delay=0)

    season_numbers = {
        region: response["seasonId"] for region, response in zip(REGIONS, responses)
    }
    logger.info(f"Season numbers are: {season_numbers}")

    season_start = max(int(response["startDate"]) for response in responses)
    season_end = max(int(response["endDate"]) for response in responses)
    season_number = max(int(response["seasonId"]) for response in responses)
    return SeasonInfo(
        arrow.get(season_start),
        arrow.get(season_end),
        season_number,
        # Wednesday 2020-09-30
        arrow.get(season_start).strftime("%A %Y-%m-%d"),
        arrow.get(season_end).strftime("%A %Y-%m-%d"),
    )


def convert_header_data_to_json(header_data: SeasonInfo) -> dict[str, arrow.Arrow | int | str]:
    return {
        "time": arrow.now().strftime("%A %Y-%m-%d %H:%M"),
        "season": header_data.season_number,
        "season_start": header_data.season_start_readable,
        "season_end": header_data.season_end_readable,
    }
