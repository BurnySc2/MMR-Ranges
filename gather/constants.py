from pydantic import BaseModel




MODES = ["201", "202", "203", "204", "206"]
TABLE_HEADER = ["Server", "Americas", "Europe", "Korea"]
STATISTICS_HEADER = ["Race", "P", "T", "Z", "R"]
STATISTICS_HEADER_WITH_TOTAL = STATISTICS_HEADER + ["Total"]
LEAGUES = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "GrandMaster"]
REGIONS = ["us", "eu", "kr"]
TIERS = list(reversed(range(1, 4)))
ROW_DESCRIPTIONS = [
    f"{league} {tier}"
    for league in LEAGUES
    for tier in TIERS
    if league != "GrandMaster"
] + ["GrandMaster"]
RACES = ["P", "T", "Z", "R"]

AVG_GAMES_ROUNDING = 1
AVG_WINRATE_ROUNDING = 1
