import asyncio
import json
import os
import re
from typing import List, Optional

import httpx
from dpath.util import get, merge, new
from loguru import logger


async def get_access_token(client: httpx.AsyncClient) -> str:
    client_id: str = os.getenv("CLIENT_ID")  # pyre-fixme[9]
    client_secret: str = os.getenv("CLIENT_SECRET")  # pyre-fixme[9]
    logger.info("Grabbing access token...")
    response = await client.post(
        "https://us.battle.net/oauth/token",
        params={"grant_type": "client_credentials"},
        auth=httpx.BasicAuth(client_id, client_secret),
    )
    assert response.is_success, response.status_code
    token_json = response.json()
    logger.info("Got access token")
    return token_json["access_token"]


async def fetch(
    client: httpx.AsyncClient, access_token: str, url: str, fetch_delay: float = 0
) -> dict:
    if fetch_delay > 0:
        await asyncio.sleep(fetch_delay)
    logger.info(f"Fetching url {url}")
    try:
        response = await client.get(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )
        return response.json()
    except (httpx.ReadTimeout, httpx.ReadError, json.JSONDecodeError):
        return {}


async def fetch_multiple(
    client: httpx.AsyncClient,
    access_token: str,
    urls: List[str],
    fetch_delay: float = 0,
) -> List[dict]:
    """
    Usage:
    async for i in fetch_multiple():
        print(i)
    """
    tasks = [
        asyncio.create_task(fetch(client, access_token, url, fetch_delay * i))
        for i, url in enumerate(urls)
    ]
    responses = await asyncio.gather(*tasks)
    return responses


def get_region_from_href(url) -> Optional[str]:
    """Returns one of: us, eu, kr"""
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
