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


def get_avg_games_entry(wins: dict, losses: dict, profiles: dict, race: str) -> str:
    """ Calculate the average games per race. If race=='TOTAL', calculate the total average (not the sum of all 4 averages). """
    if race == "TOTAL":
        total_profiles = sum(profiles.values())
        if total_profiles == 0:
            return "-"
        total_wins = sum(wins.values())
        total_losses = sum(losses.values())
        total_games = total_wins + total_losses
        return str(round(total_games / total_profiles, AVG_GAMES_ROUNDING))

    if profiles.get(race, 0) == 0:
        return "-"
    total_games = wins.get(race, 0) + losses.get(race, 0)
    return str(round(total_games / profiles[race], AVG_GAMES_ROUNDING))


def get_avg_winrate_entry(wins: dict, losses: dict, race: str) -> str:
    """ Calculate the winrate per race. """
    total_games = wins.get(race, 0) + losses.get(race, 0)
    if total_games == 0:
        return "-"
    return str(round(wins.get(race) / total_games * 100, AVG_WINRATE_ROUNDING))


async def get_sc2_legacy_ladder_api_data(
    client: aiohttp.ClientSession, access_token: str, fetch_delay: float, prepared_data: dict, gm_data: dict
):
    url = "https://{}.api.blizzard.com/sc2/legacy/ladder/{}/{}"
    # url = f"https://{region}.api.blizzard.com/sc2/legacy/ladder/{region_id}/{ladder_id}"

    # Each table has keys: us, eu, kr
    avg_games_table = {}
    avg_winrate_table = {}

    for region_id, region_name in enumerate(REGIONS, start=1):
        new_table_avg_games = []
        new_table_avg_winrate = []
        for mode in MODES[:1]:
            row_number = 0
            for league_id, league in enumerate(LEAGUES[:6]):
                for tier_id in reversed(range(3)):
                    # Skip if it doesnt exist, e.g. for GM when GM is locked
                    if not get(prepared_data, f"{mode}/{league_id}/{tier_id}", default={}):
                        continue

                    new_row_avg_games = [ROW_DESCRIPTIONS[row_number]]
                    new_row_avg_winrate = [ROW_DESCRIPTIONS[row_number]]
                    row_number += 1

                    # Get normal non-ladder stats
                    urls = [
                        url.format(region_name, region_id, ladder_id)
                        for ladder_id in get(
                            prepared_data, f"{mode}/{league_id}/{tier_id}/{region_name}/ladder_ids", default=[]
                        )
                    ]
                    responses = await fetch_multiple(client, access_token, urls, fetch_delay)

                    # Collect games per race, keys are: P, T, Z, R
                    league_tier_wins = {}
                    league_tier_losses = {}
                    league_tier_profiles = {}

                    for response in responses:
                        if "ladderMembers" not in response:
                            logger.error(f"Error with response, no key found with 'ladderMembers")
                            continue
                        for profile in response["ladderMembers"]:
                            # Ignore profile if buggy (race not shown?)
                            if "favoriteRaceP1" not in profile:
                                logger.error(f"Error with profile")
                                continue
                            wins = profile["wins"]
                            losses = profile["losses"]
                            race = profile["favoriteRaceP1"][0]
                            # Load old data from dict
                            total_race_wins = get(league_tier_wins, f"{race}", default=0)
                            total_race_losses = get(league_tier_losses, f"{race}", default=0)
                            total_race_profiles = get(league_tier_profiles, f"{race}", default=0)

                            # Store new sum of data
                            new(league_tier_wins, f"{race}", total_race_wins + wins)
                            new(league_tier_losses, f"{race}", total_race_losses + losses)
                            new(league_tier_profiles, f"{race}", total_race_profiles + 1)

                    # Calculate average games per profile
                    new_row_avg_games += [
                        get_avg_games_entry(league_tier_wins, league_tier_losses, league_tier_profiles, race)
                        for race in RACES + ["TOTAL"]
                    ]

                    # Calculate average winrate per race
                    new_row_avg_winrate += [
                        get_avg_winrate_entry(league_tier_wins, league_tier_losses, race) for race in RACES
                    ]

                    new_table_avg_games.append(new_row_avg_games)
                    new_table_avg_winrate.append(new_row_avg_winrate)

        new_table_avg_games.append(STATISTICS_HEADER_WITH_TOTAL)
        new_table_avg_games.reverse()
        avg_games_table[f"{region_name}"] = new_table_avg_games

        new_table_avg_winrate.append(STATISTICS_HEADER)
        new_table_avg_winrate.reverse()
        avg_winrate_table[f"{region_name}"] = new_table_avg_winrate

    # Add GM stats
    await add_gm_stats(gm_data, avg_games_table, avg_winrate_table)

    logger.info(f"Outputting info to 'avg_games_table.json'")
    with open("avg_games_table.json", "w") as f:
        json.dump(avg_games_table, f, indent=4, sort_keys=True)

    logger.info(f"Outputting info to 'avg_winrate_table.json'")
    with open("avg_winrate_table.json", "w") as f:
        json.dump(avg_winrate_table, f, indent=4, sort_keys=True)
    return {
        "avg_games": avg_games_table,
        "avg_winrate": avg_winrate_table,
    }


async def add_gm_stats(gm_data, avg_games_table, avg_winrate_table):
    # Add GM stats
    for region_id, region_name in enumerate(REGIONS, start=1):
        new_row_avg_games = [ROW_DESCRIPTIONS[-1]]
        new_row_avg_winrate = [ROW_DESCRIPTIONS[-1]]

        # Parse GM data
        region_players = get(gm_data, [str(region_id - 1), "ladderTeams"], default=[])
        if not region_players:
            new_row_avg_games.append("-")
            new_row_avg_winrate.append("-")
        total_wins = 0
        total_losses = 0
        total_players = 0

        for race in RACES:
            # Count players, skip if equal to 0
            players_with_that_race = len(
                [
                    player
                    for player in region_players
                    if "favoriteRace" in player["teamMembers"][0]
                    and player["teamMembers"][0]["favoriteRace"][0].lower() == race.lower()
                ]
            )
            if players_with_that_race == 0:
                new_row_avg_games.append("-")
                new_row_avg_winrate.append("-")
                continue

            wins = sum(
                player["wins"]
                for player in region_players
                if "favoriteRace" in player["teamMembers"][0]
                and player["teamMembers"][0]["favoriteRace"][0].lower() == race.lower()
            )
            losses = sum(
                player["losses"]
                for player in region_players
                if "favoriteRace" in player["teamMembers"][0]
                and player["teamMembers"][0]["favoriteRace"][0].lower() == race.lower()
            )
            total_wins += wins
            total_losses += losses
            total_players += players_with_that_race
            new_row_avg_games.append(f"{round((wins + losses) / players_with_that_race, AVG_GAMES_ROUNDING)}")
            new_row_avg_winrate.append(f"{round(100 * wins / (wins + losses), AVG_WINRATE_ROUNDING)}")

        # Do not add any row if there are 0 players or no stats
        if total_players == 0:
            continue

        # Add total average to row
        new_row_avg_games.append(f"{round((total_wins + total_losses) / total_players, AVG_GAMES_ROUNDING)}")

        avg_games_table[f"{region_name}"].insert(1, new_row_avg_games)
        avg_winrate_table[f"{region_name}"].insert(1, new_row_avg_winrate)
