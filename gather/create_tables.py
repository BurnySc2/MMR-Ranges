from loguru import logger
from dpath.util import get, new, merge

from typing import Optional, List, Dict, Any, Generator
import aiohttp
import asyncio
import re
import json
import arrow

from .helper import fetch_multiple, get_region_from_href
from .constants import *
from dpath.util import get, new, merge


async def prepare_mmr_table_data(responses: List[dict]):
    data = {}
    for response in responses:
        # There was an error in the response, empty dict is returned
        if response == {}:
            continue

        if response.get("code", 200) == 200:
            # total season id, in general each year has 4-6 seasons
            season_id: str = str(response["key"]["season_id"])
            # the game type, e.g. 1v1 2v2 for [201, 202, 203, 204, 206] 206 being archon
            queue_id: str = str(response["key"]["queue_id"])
            region: str = get_region_from_href(response["_links"]["self"]["href"])
            # league id 0 is bronze, league id 5 is master
            league_id: str = str(response["key"]["league_id"])
            # tier 0 in api is tier 1 on ladder, tier 2 in api is tier 3 on ladder
            tiers = {
                tier["id"]: {"min_rating": tier["min_rating"], "max_rating": tier["max_rating"],}
                for tier in response["tier"]
            }

            # Only interested in ladderids for 1v1 queue
            if queue_id == "201":
                for tier in response["tier"]:
                    # Entry "division" may be missing instead of having empty array...
                    tiers[tier["id"]]["ladder_ids"] = (
                        [division["ladder_id"] for division in tier["division"]] if "division" in tier else []
                    )

            response_data = {
                queue_id: {league_id: {str(tierid): {region: tierData} for tierid, tierData in tiers.items()}}
            }
            merge(data, response_data)
    logger.info("Data prepared")

    logger.info(f"Outputting info to 'data_table_raw.json'")
    with open("data_table_raw.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

    return data


async def create_mmr_tables(prepared_data: dict):
    formatted_table = {}
    for mode in MODES:
        new_table = []
        row_number = 0
        for league_id, league in enumerate(LEAGUES):
            for tier_id in reversed(range(3)):

                # Skip if it doesnt exist, e.g. for GM when GM is locked
                if not get(prepared_data, f"{mode}/{league_id}/{tier_id}", default={}):
                    continue

                new_row = [ROW_DESCRIPTIONS[row_number]]
                row_number += 1
                for region_id, region_name in enumerate(REGIONS, start=1):
                    min_rating = str(
                        get(prepared_data, f"{mode}/{league_id}/{tier_id}/{region_name}/min_rating", default="")
                    )
                    max_rating = str(
                        get(prepared_data, f"{mode}/{league_id}/{tier_id}/{region_name}/max_rating", default="")
                    )

                    if not min_rating or not max_rating:
                        field = "-"
                    else:
                        field = f"{min_rating} - {max_rating}"
                    new_row.append(field)
                new_table.append(new_row)
        new_table.append(TABLE_HEADER)
        new_table.reverse()
        formatted_table[mode] = new_table

    logger.info(f"Outputting info to 'formatted_table.json'")
    with open("formatted_table.json", "w") as f:
        json.dump(formatted_table, f, indent=4, sort_keys=True)
    return formatted_table
