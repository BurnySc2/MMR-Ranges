# Other
import time
import os
import sys
import re
import time
import json
import sys
import collections
from pathlib import Path

# Coroutines and multiprocessing
import asyncio
import aiohttp
import arrow


# Simple logging https://github.com/Delgan/loguru
from loguru import logger

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

# Type annotation / hints
from typing import List, Iterable, Union


class MMRranges:
    def __init__(self, client):
        self.client = client

        directory = Path(__file__).parent

        auth_json_path = directory / "auth.json"
        if auth_json_path.exists():
            with open(auth_json_path) as f:
                data = json.load(f)
                self.MY_CLIENT_ID = data["CLIENT_ID"]
                self.MY_CLIENT_SECRET = data["CLIENT_SECRET"]
        else:
            _, self.MY_CLIENT_ID, self.MY_CLIENT_SECRET = sys.argv

        self.data_json_path = directory / "data.json"
        self.index_html_path = directory / "website" / "index.html"

        # API rate limit
        self.rate_limit = 50  # x calls per second, can be up to 100 per second
        self.delay_per_fetch = 1 / self.rate_limit

        # Will be populated later
        self.token: str = ""
        self.season_min = 0
        self.season_numbers = {}
        self.season_start: int = 0
        self.season_end: int = 0
        self.season_max: int = 0

        self.regions = ["us", "eu", "kr"]
        self.queue_ids = ["201", "202", "203", "204", "206"]  # 1 on 1 etc
        self.team_types = ["0"]  # arranged or random
        self.league_ids = [x for x in range(6, -1, -1)]  # bronze to master league, 5 = master
        self.hregions = {"eu": "Europe", "us": "Americas", "kr": "Korea"}
        self.hqueue_ids = {"201": "1v1", "202": "2v2", "203": "3v3", "204": "4v4", "206": "Archon"}
        leagues = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "GrandMaster"][::-1]
        self.hleague_ids = {str(league_id): leagueName for league_id, leagueName in zip(self.league_ids, leagues)}
        self.htier = {str(i): str(i + 1) for i in range(3)}

        self.data = {}  # populated in prepare_response_data
        """
        self.data = {
            "season": {
                "queue_id" {
                    "region": {
                        "league": {
                            "tierID": {
                                "min_rating": 3000,
                                "max_rating": 3500
                            }
                        }                        
                    }    
                }
            }
        }
        """

    async def get_access_token(self):
        logger.info(f"Grabbing access token...")
        response = await self.client.get(
            "https://us.battle.net/oauth/token",
            params={"grant_type": "client_credentials"},
            auth=aiohttp.BasicAuth(self.MY_CLIENT_ID, self.MY_CLIENT_SECRET),
        )
        assert response.status == 200
        token_json = await response.json()
        logger.info(f"Got access token")
        self.token = token_json["access_token"]

    async def get_min_season(self):
        for i in range(500):
            response = await self.get_api_data("eu", f"{i}", "101", "0", "5")
            status = response.get("code", 200)
            if status == 200:
                self.season_min = i
                logger.info(f"Grabbed minimum season: {i}")
                return

    async def fetch(self, url, fetch_delay=0):
        if fetch_delay > 0:
            await asyncio.sleep(fetch_delay)
        logger.info(f"Fetching url {url}")
        access_token = f"access_token={self.token}"
        correct_url = url + access_token if url.endswith("?") or url.endswith("&") else url + f"?{access_token}"
        async with self.client.get(correct_url) as response:
            # assert response.status == 200, f"Response status: {response.status}, error: {response.reason}"
            logger.info(f"Done fetching url {url}")
            return await response.json()

    async def get_season_number(self):
        tasks = []
        get_season_number_url = "https://{}.api.blizzard.com/sc2/ladder/season/{}"
        for index, region in enumerate(self.regions):
            region_url = get_season_number_url.format(region, index + 1)
            task = asyncio.ensure_future(self.fetch(region_url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)

        self.season_numbers = {region: response["seasonId"] for region, response in zip(self.regions, responses)}
        self.season_start = max(int(response["startDate"]) for response in responses)
        self.season_end = max(int(response["endDate"]) for response in responses)
        self.season_max = max(self.season_numbers.values())

        return self.season_max

    async def get_api_data(self, region, season_number, queue_id, teamtype, league_id, fetch_delay: float = 0):
        # url = "https://{}.api.battle.net/data/sc2/league/{}/{}/{}/{}?access_token={}".format(region, season_number, queue_id, teamtype, league_id, self.token)
        url = "https://{}.api.blizzard.com/data/sc2/league/{}/{}/{}/{}?locale=en_US&".format(
            region, season_number, queue_id, teamtype, league_id,
        )

        logger.info(f"Fetching api data {url}")
        response = await self.fetch(url, fetch_delay)
        return response

    async def get_all_data(self):
        tasks = []
        total_responses = []
        function_call_count = 0
        for region, season_max in self.season_numbers.items():
            # Only show the last 8 seasons
            season_min = max(season_max - 8, self.season_min)
            for season_number in range(season_min, season_max + 1):
                for queue_id in self.queue_ids:
                    for team_type in self.team_types:
                        # Skip GM
                        for league_id in self.league_ids[1:]:
                            task = asyncio.ensure_future(
                                self.get_api_data(
                                    region,
                                    season_number,
                                    queue_id,
                                    team_type,
                                    league_id,
                                    fetch_delay=self.delay_per_fetch * function_call_count,
                                )
                            )
                            tasks.append(task)
                            function_call_count += 1

            total_responses = await asyncio.gather(*tasks)
        logger.info(f"Api data pulled, total number of calls: {function_call_count}")
        self.responses = total_responses
        return total_responses

    async def get_gm_data(self):
        for index, region in enumerate(self.regions, start=1):
            response = await self.client.get(
                f"https://us.api.blizzard.com/sc2/ladder/grandmaster/{index}?access_token={self.token}"
            )
            json_data = await response.json()
            if json_data.get("code", 200) == 200:
                # "mmr" entry might be missing
                min_mmr = min(member["mmr"] for member in json_data["ladderTeams"] if "mmr" in member)
                max_mmr = max(member["mmr"] for member in json_data["ladderTeams"] if "mmr" in member)
                # fmt: off
                response_data = {
                    # Season
                    str(self.season_max - 1): {
                        # Queue id, 201 for 1v1
                        "201": {
                            # League id, 6 for GM
                            "6": {
                                # Tier id
                                "": {
                                    # Region
                                    region: {
                                        "min_rating": min_mmr,
                                        "max_rating": max_mmr,
                                    }
                                }
                            }
                        }
                    }
                }
                # fmt: on
                self.data = self.update_nested_dict(self.data, response_data)

    def update_nested_dict(self, my_dict, new_dict):
        for k, v in new_dict.items():
            if isinstance(my_dict, collections.Mapping):
                if isinstance(v, collections.Mapping):
                    r = self.update_nested_dict(my_dict.get(k, {}), v)
                    my_dict[k] = r
                else:
                    my_dict[k] = new_dict[k]
            else:
                my_dict = {k: new_dict[k]}
        return my_dict

    def prepare_response_data(self):
        for response in self.responses:
            if response.get("code", 200) == 200:
                # total season id, in general each year has 4-6 seasons
                season_id: int = str(response["key"]["season_id"])
                # the game type, e.g. 1v1 2v2 for [201, 202, 203, 204, 206] 206 being archon
                queue_id: int = str(response["key"]["queue_id"])
                region: str = response["_links"]["self"]["href"].lstrip("https:").lstrip("/")[:2]
                # league id 0 is bronze, league id 5 is master
                league_id: int = str(response["key"]["league_id"])
                team_type: int = str(response["key"]["team_type"])  # arranged team or random
                # tier 0 in api is tier 1 on ladder, tier 2 in api is tier 3 on ladder
                tiers = {
                    tier["id"]: {"min_rating": tier["min_rating"], "max_rating": tier["max_rating"]}
                    for tier in response["tier"]
                }

                response_data = {
                    season_id: {
                        queue_id: {league_id: {str(tierid): {region: tierData} for tierid, tierData in tiers.items()}}
                    }
                }

                self.data = self.update_nested_dict(self.data, response_data)
        logger.info("Data prepared")
        return self.data

    def verify_response_data(self):
        assert (
            self.season_numbers["us"] == self.season_numbers["eu"] == self.season_numbers["kr"]
        ), f"Season change going on. Current season numbers: {self.season_numbers}"

        expected_amount = self.season_numbers["us"] - self.season_min + 1
        assert (
            len(self.data) == expected_amount
        ), f"Amount of fetched seasons {len(self.data)} does not match the expected amount of {expected_amount}"

        for season_id, queue_data in self.data.items():
            assert (
                len(queue_data) == 5
            ), f"Something wrong with the amount of received queue data for season {season_id}, only received {len(queue_data)} values instead of expected 5"
            for queue_id, league_data in queue_data.items():
                assert len(league_data) in {
                    6,
                    7,
                }, f"Something wrong with the amount of received league data for season {season_id}, only received {len(league_data)} values instead of expected 6 or 7"
                for league_id, server_data in league_data.items():
                    assert len(server_data) in {
                        1,
                        3,
                    }, f"Something wrong with the amount of received server data for season {season_id}, only received {len(server_data)} values instead of expected 1 (for GM) or 3"
        return True

    def verify_new_data_different_from_old_data(self):
        logger.info("Comparing new data with old data...")
        if self.data_json_path.exists():
            with open(self.data_json_path) as f:
                old_data = json.load(f)
        else:
            return True

        # logger.info(f"Until now, everything took {time.perf_counter() - self.t0:.2f} seconds")

        # Dictionary comparison
        if self.data != old_data:
            logger.info("New data is different!")
            return True
        logger.info("New data is the same as old data.")
        return False

    def write_json_data(self):
        logger.info(f"Writing json data to: {self.data_json_path}")
        with open(self.data_json_path, "w") as f:
            json.dump(self.data, f, indent=2)

    @property
    def fileStart(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->

    <title>
        MMR Ranges in StarCraft 2
    </title>

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

</head>

<body>


<div class="container">
    <div class="row justify-content-center">
        <h1 class="text-center btn-light">MMR Ranges - Last update: {0}</h1>
    </div>
    <div class="row justify-content-center">
        <div class="col-auto">
            <table class="table table-hover text-center">
                <tbody >
                    <tr>
                        <th class="btn-secondary btn-md" scope="row">Season number:</th>
                        <td class="btn-light btn-md">{1}</td>
                    </tr>
                    <tr>
                        <th class="btn-secondary btn-md" scope="row">Season start:</th>
                        <td class="btn-light btn-md">{2}</td>
                    </tr>
                    <tr>
                        <th class="btn-secondary btn-md" scope="row">Season end:</th>
                        <td class="btn-light btn-md">{3}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="col justify-content-center">
"""

    @property
    def fileEnd(self):
        return """  
</div>

<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

</body>

<footer>

</footer>
</html>
"""

    @property
    def get_dropdown_navbar(self):

        start = """
    <div class="row justify-content-center">
        <div class="col-auto">
            <ul class="nav nav-tabs">
"""
        end = """
            </ul>
        </div>
    </div>
"""
        dropdown_template = """
                <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle{0}" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">{1}</a>
                    <div class="dropdown-menu">
                        <a class="dropdown-item{0}" href="#{2}" data-toggle="tab">{7}</a>
                        <a class="dropdown-item" href="#{3}" data-toggle="tab">{8}</a>
                        <a class="dropdown-item" href="#{4}" data-toggle="tab">{9}</a>
                        <a class="dropdown-item" href="#{5}" data-toggle="tab">{10}</a>
                        <a class="dropdown-item" href="#{6}" data-toggle="tab">{11}</a>
                    </div>
                </li>
"""

        # Last and previous season are identical for some reason, so skip first season
        seasons = sorted(list(self.data.keys()), key=lambda x: int(x))[1:]
        hqueue_ids = [self.hqueue_ids[queue_id] for queue_id in self.queue_ids]
        navbarContent = start
        for season in seasons:
            season_queue_ids = [season + self.hqueue_ids[queue_id] for queue_id in self.queue_ids]
            # logger.info(len(hqueue_ids), len(season_queue_ids), self.queue_ids, season, type(self.queue_ids[0]), type(season))
            if season == seasons[-1]:
                navbarContent += dropdown_template.format(
                    " active", "Season {}".format(season), *season_queue_ids, *hqueue_ids
                )
            else:
                navbarContent += dropdown_template.format(
                    "", "Season {}".format(season), *season_queue_ids, *hqueue_ids
                )
        navbarContent += end
        # logger.info("navbarcontent\n", navbarContent)
        return navbarContent

    def create_season_gametype_table(self, season, queue_id, data2, active=False, indention=0):
        tableStart = """    
    <div class="tab-pane{1}" id="{0}" role="tabpanel" aria-labelledby="{0}">
        <div class="row justify-content-center">
            <div class="col-auto">
                <table class="table table-hover text-center">
                    <thead>
                        <th scope="col">Server</th>
                        <th scope="col">Americas</th>
                        <th scope="col">Europe</th>
                        <th scope="col">Korea</th>
                    </thead>
                    <tbody>
"""
        if active:
            tableStart = tableStart.format(season + self.hqueue_ids[queue_id], " in active")
        else:
            tableStart = tableStart.format(season + self.hqueue_ids[queue_id], "")

        tableEnd = """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
"""
        rowStart = "<tr>\n"
        rowEnd = "</tr>\n"
        columnEntryTemplate = '<th scope="row">{}</th>\n'

        tableContent = tableStart
        for league_id, data3 in data2.items():
            for tierid, data4 in data3.items():
                tableContent += "\t" * indention + rowStart
                # Exception for GM which has no tiers
                # if len(data2) == 1:
                if tierid == "":
                    firstColumn = "{}".format(self.hleague_ids[league_id])
                else:
                    firstColumn = "{} {}".format(self.hleague_ids[league_id], self.htier[tierid])
                tableContent += "\t" * (indention + 1) + columnEntryTemplate.format(firstColumn)
                for region, rating in data4.items():
                    cellEntry = "{} - {}".format(rating["min_rating"], rating["max_rating"])
                    tableContent += "\t" * (indention + 1) + columnEntryTemplate.format(cellEntry)
                tableContent += "\t" * indention + rowEnd
        tableContent += tableEnd

        return tableContent

    def get_title_data(self):
        t = arrow.now("UTC")
        time_for_title = t.format("dddd YYYY-MM-DD HH:mm")
        # time_for_title = t.format("dddd YYYY-MM-DD HH:mm ZZ")

        season_number = self.season_max

        t = arrow.Arrow.fromtimestamp(self.season_start)
        season_start_date = t.format("dddd YYYY-MM-DD")

        t = arrow.Arrow.fromtimestamp(self.season_end)
        season_end_date = t.format("dddd YYYY-MM-DD")

        return time_for_title, season_number, season_start_date, season_end_date

    def build_html_file(self, title_data):
        """ Returns content of HTML file """
        content = ""

        # file start
        # title with last update time stamp
        content += self.fileStart.format(*title_data)

        # build season+gametype dropdown navbar
        content += self.get_dropdown_navbar

        # build content for each season number + game type combo
        content += """<div class="tab-content">"""
        for season, data1 in self.data.items():
            # Last and previous season are identical for some reason, so everything is offset by 1, and skip most recent season
            season_plus_one: int = int(season) + 1
            if season_plus_one > self.season_max:
                logger.info(f"Continueing at most recent season: {season_plus_one}")
                continue
            logger.info(f"Building HTML, season: {season_plus_one}")
            for queue_id, data2 in data1.items():
                boolean = season_plus_one == self.season_max and queue_id == self.queue_ids[0]
                content += self.create_season_gametype_table(
                    str(season_plus_one), queue_id, data2, active=boolean, indention=6
                )
        content += """</div>"""

        # write info about donation, contact, and pythonanywhere website alternative
        # file end
        content += self.fileEnd

        return content

    def write_to_html(self, content):
        logger.info("Writing html file...")
        folder_path = os.path.dirname(self.index_html_path)
        if not self.index_html_path.parent.exists():
            logger.info(f"Creating folder for html file: {folder_path}")
            os.makedirs(folder_path)
        logger.info(f"Writing html file to {self.index_html_path}")
        with open(self.index_html_path, "w+") as f:
            f.write(content)


async def main():
    async with aiohttp.ClientSession() as client:
        mmrranges = MMRranges(client)
        await mmrranges.get_access_token()
        await mmrranges.get_min_season()
        await mmrranges.get_season_number()
        title_data = mmrranges.get_title_data()
        await mmrranges.get_all_data()
        await mmrranges.get_gm_data()
        mmrranges.prepare_response_data()
        mmrranges.verify_response_data()
        if mmrranges.verify_new_data_different_from_old_data():
            mmrranges.write_json_data()
            content = mmrranges.build_html_file(title_data)
            mmrranges.write_to_html(content)
            exit(0)
        # Error, don't continue next step in github actions
        exit(1)


if __name__ == "__main__":
    loop: asyncio.BaseEventLoop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

    # In Python 3.7 it is just::
    # asyncio.run(main())
