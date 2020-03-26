import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import do_math, download_site, download_all_sites, find_sums, cpu_bound_summing, download_image
import pytest
import aiohttp
import time
from hypothesis import given
import hypothesis.strategies as st


@pytest.mark.asyncio
async def test_download_image():
    # With this download throttle, it should take at least 9 seconds to download the 1mb image at 100kb/s
    download_path = "test/image.png"

    # Cleanup from last time
    if os.path.isfile(download_path):
        os.remove(download_path)

    t0 = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        result: bool = await download_image(
            session,
            url="https://file-examples.com/wp-content/uploads/2017/10/file_example_PNG_1MB.png",
            file_path=download_path,
            temp_file_path="test/image_download_not_complete",
            download_speed=100 * 2 ** 10,
        )
    t1 = time.perf_counter()
    assert result
    assert t1 - t0 > 9
    assert os.path.isfile(download_path)

    # Cleanup
    os.remove(download_path)

    # Without throttle, it should take less than 3 seconds
    t0 = time.perf_counter()
    assert not os.path.isfile(download_path)
    async with aiohttp.ClientSession() as session:
        result: bool = await download_image(
            session,
            url="https://file-examples.com/wp-content/uploads/2017/10/file_example_PNG_1MB.png",
            file_path=download_path,
            temp_file_path="test/image_download_not_complete",
        )
    t1 = time.perf_counter()
    assert result
    assert t1 - t0 < 9
    assert os.path.isfile(download_path)

    # Cleanup
    os.remove(download_path)


@pytest.mark.asyncio
async def test_download_site():
    async with aiohttp.ClientSession() as session:
        res = await download_site(session, "http://www.jython.org")
    assert res.content_length > 0


@pytest.mark.asyncio
async def test_download_all_sites():
    urls = ["http://www.jython.org"] * 2
    results = await download_all_sites(urls)
    assert sum(result.content_length for result in results) > 0


@pytest.mark.asyncio
async def test_do_math():
    res = await do_math(7)
    assert 10 == res


@pytest.mark.asyncio
@given(st.integers())
async def test_do_math_integers(value):
    assert 3 + value == await do_math(value)


@pytest.mark.asyncio
@given(st.floats(allow_infinity=False, allow_nan=False))
async def test_do_math_floats(value):
    assert 3 + value == await do_math(value)


@given(st.integers(min_value=0, max_value=10000))
def test_cpu_bound_summing(number):
    assert sum(i * i for i in range(number)) == cpu_bound_summing(number)
