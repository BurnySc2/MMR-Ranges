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


async def get_sc2_gm_api_data(client: aiohttp.ClientSession, access_token: str, fetch_delay: float):
    url = "https://{}.api.blizzard.com/sc2/ladder/grandmaster/{}"

    urls = [url.format(region, index) for index, region in enumerate(REGIONS, start=1)]

    logger.info(f"Fetching GM data")
    responses = await fetch_multiple(client, access_token, urls, fetch_delay)
    logger.info(f"Fetched GM data")

    logger.info(f"Outputting info to 'data_gm_api.json'")
    with open("data_gm_api.json", "w") as f:
        json.dump(responses, f, indent=4, sort_keys=True)
    return responses
