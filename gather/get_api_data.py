from loguru import logger
from dpath.util import get, new, merge

from typing import Optional, List, Dict, Any, Generator
import aiohttp
import asyncio
import re
import json
import arrow

from .helper import fetch_multiple
from .constants import *


async def get_sc2_league_api_data(
    client: aiohttp.ClientSession, access_token: str, season_number: int, fetch_delay: float
):
    url = "https://{}.api.blizzard.com/data/sc2/league/{}/{}/{}/{}?locale=en_US&"

    urls = []
    for region in ["us", "eu", "kr"]:
        for season in [season_number]:
            # 1v1, 2v2, 3v3, 4v4, archon
            for queue_id in MODES:
                for team_type in ["0"]:
                    for league_id in map(str, range(6)):
                        urls.append(url.format(region, season, queue_id, team_type, league_id))

    logger.info(f"Fetching {len(url)} urls")
    responses = await fetch_multiple(client, access_token, urls, fetch_delay)
    logger.info(f"Fetched {len(url)} urls")

    logger.info(f"Outputting info to 'data_ladder_api.json'")
    with open("data_ladder_api.json", "w") as f:
        json.dump(responses, f, indent=4, sort_keys=True)
    return responses
