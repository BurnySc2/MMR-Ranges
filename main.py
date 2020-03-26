# Other
import time
import os
import sys
import re
import time
from contextlib import contextmanager

# Coroutines and multiprocessing
import asyncio
import aiohttp
from multiprocessing import Process, Lock, Pool

# Simple logging https://github.com/Delgan/loguru
from loguru import logger

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

# Type annotation / hints
from typing import List, Iterable, Union


async def main():
    logger.info("Simple {} logger output", "loguru")

    regex_match_test()

    measure_time()

    sites: List[str] = ["http://www.jython.org", "http://olympus.realpython.org/dice"] * 80
    start_time = time.perf_counter()
    await download_all_sites(sites)

    # Download an image with download speed throttle
    async with aiohttp.ClientSession() as session:
        result: bool = await download_image(
            session,
            url="https://file-examples.com/wp-content/uploads/2017/10/file_example_PNG_1MB.png",
            file_path="test/image.png",
            temp_file_path="test/image_download_not_complete",
            # Download at speed of 100kb/s
            download_speed=100 * 2 ** 10,
        )

    end_time = time.perf_counter()
    print(f"Time for sites download taken: {end_time - start_time}")

    math_result = await do_math(6)

    start_time = time.perf_counter()
    do_multiprocessing()
    end_time = time.perf_counter()
    print(f"Time for multiprocessing taken: {end_time - start_time}")

    print(f"Creating hello world file...")
    create_file()


def measure_time():
    @contextmanager
    def time_this(label: str):
        start = time.perf_counter_ns()
        try:
            yield
        finally:
            end = time.perf_counter_ns()
            print(f"TIME {label}: {(end-start)/1e9} sec")

    # Use like this
    if __name__ == "__main__":
        with time_this("square rooting"):
            for n in range(10 ** 7):
                x = n ** 0.5


def regex_match_test():
    """
    Match pattern:
    HH:MM:SS
    """
    assert re.fullmatch(r"(\d{2}):(\d{2}):(\d{2})", "00:00:00")
    assert not re.fullmatch(r"(\d{2}):(\d{2}):(\d{2})", "0:00:00")
    assert not re.fullmatch(r"(\d{2}):(\d{2}):(\d{2})", "00:0:00")
    assert not re.fullmatch(r"(\d{2}):(\d{2}):(\d{2})", "00:00:0")
    assert not re.fullmatch(r"(\d{2}):(\d{2}):(\d{2})", "00:0000")


def generate_roman_number(n: int) -> str:
    """
    Allowed roman numbers:
    IV, VI, IX, XI, XC, LC, XXXIX, XLI
    Disallowed:
    IIV, VIIII, XXXX, IXL, XIL
    """
    if 4000 < n:
        raise ValueError(f"Input too big: {n}")
    number_list = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    string_as_list = []
    for divisor, character in number_list:
        if n >= divisor:
            count, n = divmod(n, divisor)
            string_as_list.extend(count * [character])
    return "".join(string_as_list)


def regex_match_roman_number(roman_number: str) -> bool:
    """ Returns True if input string is a roman number
    First row: Look ahead -> dont match empty string
    Second row: 1000-3000
    Third row: 3400 or 3900, connected with 100, 200, 300, or 500, 600, 700 or 800
    Same pattern for 4th and 5th row
    """
    numbers_1_to_3889 = r"""
    (?=[MDCLXVI])
        M{0,3}
            ( C[MD] | D?C{0,3} )
                ( X[CL] | L?X{0,3} )
                    ( I[XV] | V?I{0,3} )
    """.replace(
        " ", ""
    ).replace(
        "\n", ""
    )
    return bool(re.fullmatch(numbers_1_to_3889, roman_number))

# TODO write as test
# for i in range(1, 3500):
#     assert regex_match_roman_number(generate_roman_number(i)), f"{i}"

async def download_image(
    session: aiohttp.ClientSession,
    url: str,
    file_path: str,
    temp_file_path: str,
    download_speed: int = -1,
    chunk_size: int = 1024,
) -> bool:
    """
    Downloads an image (or a file even) from "url" and saves it to "temp_file_path". When the download is complete, it renames the file at "temp_file_path" to "file_path".
    It respects "download_speed" in bytes per second. If no parameter was given, it will ignore the download limit.

    Returns boolean if download was successful.
    """
    downloaded: int = 0
    # Download start time
    time_last_subtracted = time.perf_counter()
    # Affects sleep time and check size for download speed, should be between 0.1 and 1
    accuracy: float = 0.1

    # Check if file exists
    if not os.path.isfile(file_path):
        try:
            async with session.get(url) as response:
                # Assume everything went well with the response, no connection or server errors
                assert response.status == 200
                # Open file in binary write mode
                with open(temp_file_path, "wb") as f:
                    # Download file in chunks
                    async for data in response.content.iter_chunked(chunk_size):
                        # Write data to file in asyncio-mode using aiofiles
                        f.write(data)
                        # Keep track of how much was downloaded
                        downloaded += chunk_size
                        # Wait if downloaded size has reached its download throttle limit
                        while 0 < download_speed and download_speed * accuracy < downloaded:
                            time_temp = time.perf_counter()
                            # This size should be the estimated downloaded size in the passed time
                            estimated_download_size = download_speed * (time_temp - time_last_subtracted)
                            downloaded -= estimated_download_size
                            time_last_subtracted = time_temp
                            await asyncio.sleep(accuracy)
            await asyncio.sleep(0.1)
            try:
                os.rename(temp_file_path, file_path)
                return True
            except PermissionError:
                # The file might be open by another process
                print(f"Permissionerror: Unable to rename file from ({temp_file_path}) to ({file_path})")
        except asyncio.TimeoutError:
            # The The server might suddenly not respond
            print(f"Received timeout error in url ({url}) in file path ({file_path})!")
    else:
        # The file already exists!
        print(f"File for url ({url}) in file path ({file_path}) already exists!")
    return False


async def download_site(session: aiohttp.ClientSession, url: str) -> aiohttp.ClientResponse:
    async with session.get(url) as response:
        return response


async def download_all_sites(sites: Iterable[str]) -> List[aiohttp.ClientResponse]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in sites:
            # In python 3.7: asyncio.create_task instead of asyncio.ensure_future
            task = asyncio.ensure_future(download_site(session, url))
            tasks.append(task)

        # Run all tasks in "parallel" and wait until all of them are completed
        # responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Or to iterate over tasks as they complete (random order)
        responses = []
        for future in asyncio.as_completed(tasks):
            response = await future
            response_url = str(response.url)
            responses.append(response)

    return responses


async def do_math(number: Union[int, float]) -> Union[int, float]:
    return number + 3


def cpu_bound_summing(number: int) -> int:
    return sum(i * i for i in range(number))


def find_sums(numbers: Iterable[int]) -> List[int]:
    with Pool() as pool:
        result = pool.map(cpu_bound_summing, numbers)
    return result


def do_multiprocessing():
    numbers: List[int] = [5_000_000 + x for x in range(20)]
    sums: List[int] = find_sums(numbers)


def create_file():
    path = os.path.dirname(__file__)
    example_file_path = os.path.join(path, "hello_world.txt")
    with open(example_file_path, "w") as f:
        f.write("Hello world!\n")
    print(f"Hello world file created in path {example_file_path}")


if __name__ == "__main__":
    loop: asyncio.BaseEventLoop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

    # In Python 3.7 it is just::
    # asyncio.run(main())
