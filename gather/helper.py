from loguru import logger
from dpath.util import new, merge, get

from typing import Optional, List, Dict, Any, Generator
import aiohttp
import asyncio
import re
import json


async def get_access_token(client: aiohttp.ClientSession, client_id: str, client_secret: str) -> str:
    logger.info(f"Grabbing access token...")
    response = await client.get(
        "https://us.battle.net/oauth/token",
        params={"grant_type": "client_credentials"},
        auth=aiohttp.BasicAuth(client_id, client_secret),
    )
    assert response.status == 200, response.status
    token_json = await response.json()
    logger.info(f"Got access token")
    return token_json["access_token"]


async def fetch(client: aiohttp.ClientSession, access_token: str, url: str, fetch_delay: float = 0) -> dict:
    if fetch_delay > 0:
        await asyncio.sleep(fetch_delay)
    logger.info(f"Fetching url {url}")
    access_token = f"access_token={access_token}"
    if "?" in url:
        end = "&"
    else:
        end = "?"
    ending = "" if url.endswith(end) else end
    correct_url = f"{url}{ending}{access_token}"
    async with client.get(correct_url) as response:
        logger.info(f"Done fetching url {url}")
        if response.status == 200:
            try:
                json_response = await response.json()
            except aiohttp.ContentTypeError:
                return {}
            return json_response
        logger.error(
            f"Unable to decode url '{url}', receiving response status '{response.status}' and error '{response.reason}'"
        )
        return {}


async def fetch_multiple(
    client: aiohttp.ClientSession, access_token: str, urls: List[str], fetch_delay: float = 0
) -> List[dict]:
    """
    Usage:
    async for i in fetch_multiple():
        print(i)
    """
    tasks = [asyncio.create_task(fetch(client, access_token, url, fetch_delay * i)) for i, url in enumerate(urls)]
    responses = await asyncio.gather(*tasks)
    return responses


def get_region_from_href(url) -> Optional[str]:
    """ Returns one of: us, eu, kr"""
    result = re.findall(r".+((?:us)|(?:eu)|(?:kr))\.api.+", url)
    if result:
        return result[0]
    return None


if __name__ == "__main__":
    a = {}
    new(a, "b/c/d", 5)
    print(a)
    assert get(a, "b/c/d", default=7) == 5

    b = {}
    new(b, "e/f/g", 6)
    print(b)
    print(get(a, "e/f/g", default=7))
    print(get(a, "e/f/h", default=8))
    assert get(a, "e/f/h", default=8) == 8

    merge(a, b)
    print(a)
    print(json.dumps(a, indent=4, sort_keys=True))
