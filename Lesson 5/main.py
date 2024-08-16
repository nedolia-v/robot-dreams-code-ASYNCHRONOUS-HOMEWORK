import asyncio
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from functools import partial
from itertools import batched
from functions import count_words, mp_count_words

FILE_PATH = "C:/Users/vlady/googlebooks-eng-all-1gram-20120701-a"
WORD = "ära"


@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg} took {time.perf_counter() - start:.2f} second")


def reduce_words(target: dict, source: dict) -> dict:
    for key, value in source.items():
        if key in target:
            target[key] += value
        else:
            target[key] = value
    return target


async def monitoring(counter, counter_lock, total):
    while True:
        with counter_lock:
            print(f"Progress: {counter.value}/{total}")
            if counter.value == total:
                break
        await asyncio.sleep(1)


async def main():
    loop = asyncio.get_event_loop()
    words = {}

    with timer("Reading file"):
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = file.readlines()

    batch_size = 60_000
    with mp.Manager() as manager:
        counter = manager.Value("i", 0)
        counter_lock = manager.Lock()

        monitoring_task = asyncio.create_task(
            monitoring(counter, counter_lock, len(data))
        )

        with ProcessPoolExecutor() as executor:
            with timer("Processing data"):
                results = []
                for batch in batched(data, batch_size):
                    results.append(
                        loop.run_in_executor(executor, mp_count_words, batch, counter, counter_lock)
                    )
                done, _ = await asyncio.wait(results)
        try:
            monitoring_task.cancel()
            await monitoring_task
        except asyncio.CancelledError:
            print("Monitoring task cancelled ")
            pass

    with timer("Reducing results"):
        for result in done:
            words = reduce_words(words, result.result())

    with timer("Printing results"):
        print("Total words: ", len(words))
        print("Total count for word : ", words[WORD])


if __name__ == '__main__':
    with timer("Total time"):
        asyncio.run(main())
