import argparse
import asyncio
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from chunk_functions import _process_file_chunk, get_file_chunks

# FILE_PATH = "C:/Users/vlady/googlebooks-eng-all-1gram-20120701-a"
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
            print(f"Progress: {counter.value}/{total} ({(counter.value/total)*100:.2f}%)")
            if counter.value == total:
                break
        await asyncio.sleep(1)


async def main(file_path):
    loop = asyncio.get_event_loop()
    words = {}
    cpu_count, chunks, file_size = get_file_chunks(file_path)

    with mp.Manager() as manager:
        counter = manager.Value("i", 0)
        counter_lock = manager.Lock()

        monitoring_task = asyncio.create_task(
            monitoring(counter, counter_lock, file_size)
        )

        with ProcessPoolExecutor() as executor:
            with timer("Processing data"):
                results = []
                for file_name, chunk_start, chunk_end in chunks:
                    results.append(
                        loop.run_in_executor(executor, _process_file_chunk,
                                             file_name, chunk_start, chunk_end, counter, counter_lock)
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
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('file_path', type=str, help='File path to process')
    args = parser.parse_args()

    with timer("Total time"):
        asyncio.run(main(args.file_path))
