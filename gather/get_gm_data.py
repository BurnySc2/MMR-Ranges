import json
from copy import deepcopy

import httpx
from dpath.util import new
from loguru import logger

from .constants import REGIONS
from .helper import fetch_multiple


async def get_sc2_gm_api_data(client: httpx.AsyncClient, access_token: str, fetch_delay: float):
    url = "https://{}.api.blizzard.com/sc2/ladder/grandmaster/{}"

    urls = [url.format(region, index) for index, region in enumerate(REGIONS, start=1)]

    logger.info("Fetching GM data")
    responses = await fetch_multiple(client, access_token, urls, fetch_delay)
    logger.info("Fetched GM data")

    logger.info("Outputting info to 'data_gm_api.json'")
    with open("data_gm_api.json", "w") as f:
        json.dump(responses, f, indent=4, sort_keys=True)
    return responses


async def mix_gm_data(prepared_data, gm_borders):
    prepared_data["201"]["6"] = {}
    # Empty when GM isn't open
    if len(gm_borders) == 0:
        return prepared_data
    prepared_data["201"]["6"]["2"] = gm_borders["201"][6][0]
    with open("data_ladder_api_with_gm.json", "w") as f:
        json.dump(prepared_data, f, indent=4, sort_keys=True)
    return prepared_data


async def get_gm_borders(gm_data: dict):
    gm_table_info = {}
    for index, region in enumerate(REGIONS):
        # No GM data could be retrieved
        if not gm_data[index]:
            continue
        ladder_teams = gm_data[index]["ladderTeams"]
        rank190: list = deepcopy(ladder_teams)
        # Sometimes, some players don't seem to have mmr
        rank190 = [i for i in rank190 if "mmr" in i]
        # Sort descending
        rank190.sort(key=lambda x: x["mmr"], reverse=True)
        rank190 = rank190[:190]
        # GM somehow doesnt have at least one member
        if not rank190:
            continue
        max_mmr = rank190[0]["mmr"]
        min_mmr = rank190[-1]["mmr"]

        new(gm_table_info, ["201", "6", "0", region, "min_rating"], min_mmr)
        new(gm_table_info, ["201", "6", "0", region, "max_rating"], max_mmr)

    return gm_table_info
