# Other
import os
import json
import sys
from pathlib import Path

# Coroutines and multiprocessing
import asyncio
import aiohttp

# Simple logging https://github.com/Delgan/loguru
from loguru import logger

from gather.get_legacy_ladders_data import get_sc2_legacy_ladder_api_data

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

from gather.helper import get_access_token
from gather.create_header import get_current_season_info, convert_header_data_to_json
from gather.get_api_data import get_sc2_league_api_data

from gather.create_tables import prepare_mmr_table_data, create_mmr_tables
from gather.get_gm_data import get_sc2_gm_api_data, get_gm_borders, mix_gm_data

"""
ladder API:
/sc2/ladder/season/:regionId: 
{
  "seasonId": 45,
  "number": 3,
  "year": 2020,
  "startDate": "1601487375",
  "endDate": "1611640800"
}

/sc2/ladder/grandmaster/:regionId: 

/data/sc2/league/{seasonId}/{queueId}/{teamType}/{leagueId}
{
  "_links": {
    "self": {
      "href": "https://us.api.blizzard.com/data/sc2/league/45/201/0/5?namespace=prod"
    }
  },
  "key": {
    "league_id": 5,
    "season_id": 45,
    "queue_id": 201,
    "team_type": 0
  },
  "tier": [
    {
      "id": 0,
      "min_rating": 4781,
      "max_rating": 5012,
      "division": [
        {
          "id": 5,
          "ladder_id": 292909,
          "member_count": 100
        },
...

/sc2/legacy/ladder/:regionId/:ladderId
{
  "ladderMembers": [
    {
      "character": {
        "id": "XXXX",
        "realm": 1,
        "region": 1,
        "displayName": "XXXX",
        "clanName": "",
        "clanTag": "",
        "profilePath": "/profile/1/1/11293431"
      },
      "joinTimestamp": 1601501502,
      "points": 623,
      "wins": 29,
      "losses": 16,
      "highestRank": 2,
      "previousRank": 0,
      "favoriteRaceP1": "PROTOSS"
    },

/sc2/profile/:regionId/:realmId/:profileId/ladder/:ladderId
{
  "ladderTeams": [
    {
      "teamMembers": [
        {
          "id": "XXXX",
          "realm": 1,
          "region": 1,
          "displayName": "XXXX",
          "favoriteRace": "protoss"
        }
      ],
      "previousRank": 0,
      "points": 623,
      "wins": 29,
      "losses": 16,
      "mmr": 5728,
      "joinTimestamp": 1601501502
    },
"""


class MMRranges:
    def __init__(self, client):
        self.client: aiohttp.ClientSession = client
        self.token: str = None

        directory = Path(__file__).parent

        auth_json_path = directory / "auth.json"
        if auth_json_path.exists():
            with open(auth_json_path) as f:
                data = json.load(f)
                self.MY_CLIENT_ID = data["CLIENT_ID"]
                self.MY_CLIENT_SECRET = data["CLIENT_SECRET"]
        else:
            _, self.MY_CLIENT_ID, self.MY_CLIENT_SECRET = sys.argv

        # API rate limit
        self.rate_limit = 50  # x calls per second, can be up to 100 per second
        self.delay_per_fetch = 1 / self.rate_limit

    async def async_init(self):
        self.token: str = await get_access_token(self.client, self.MY_CLIENT_ID, self.MY_CLIENT_SECRET)

    async def run(self):
        # Grab raw API data
        season_info = await get_current_season_info(self.client, self.token)
        ladders_api_info = await get_sc2_league_api_data(
            self.client, self.token, season_info.season_number, self.delay_per_fetch
        )
        gm_data = await get_sc2_gm_api_data(self.client, self.token, self.delay_per_fetch)
        gm_borders = await get_gm_borders(gm_data)

        # Format the received data into a readable shape
        prepared_data = await prepare_mmr_table_data(ladders_api_info)
        prepared_data = await mix_gm_data(prepared_data, gm_borders)

        # Grab statistics from individual player profiles
        race_league_statistics = await get_sc2_legacy_ladder_api_data(
            self.client, self.token, self.delay_per_fetch, prepared_data, gm_data
        )

        # Generate the tables
        mmr_tables = await create_mmr_tables(prepared_data)

        # Write data to files
        data_folder = Path(__file__).parent / "src" / "data"

        os.makedirs(data_folder, exist_ok=True)
        with open(data_folder / "data_header.json", "w") as f:
            json.dump(convert_header_data_to_json(season_info), f, indent=4)
        with open(data_folder / "data_mmr_table.json", "w") as f:
            json.dump(mmr_tables, f, indent=4)
        with open(data_folder / "data_avg_games_table.json", "w") as f:
            json.dump(race_league_statistics["avg_games"], f, indent=4)
        with open(data_folder / "data_avg_winrate_table.json", "w") as f:
            json.dump(race_league_statistics["avg_winrate"], f, indent=4)
        with open(data_folder / "data_total_games_table.json", "w") as f:
            json.dump(race_league_statistics["total_games"], f, indent=4)


async def main():
    async with aiohttp.ClientSession() as client:
        mmrranges = MMRranges(client)
        await mmrranges.async_init()
        await mmrranges.run()


if __name__ == "__main__":
    asyncio.run(main())
