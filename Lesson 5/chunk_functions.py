import multiprocessing as mp
from multiprocessing import Lock, Value
import os


def get_file_chunks(file_name: str, max_cpu: int = 8) -> tuple[int, list[tuple[str, int, int]], int]:
    """Split file into chunks based on the number of available CPUs."""
    cpu_count = min(max_cpu, mp.cpu_count())

    file_size = os.path.getsize(file_name)
    chunk_size = file_size // cpu_count

    start_end = []
    with open(file_name, 'rb') as f:
        def is_new_line(position):
            """Check if the byte at position is a newline."""
            if position == 0:
                return True
            f.seek(position - 1)
            return f.read(1) == b'\n'

        chunk_start = 0
        while chunk_start < file_size:
            chunk_end = min(file_size, chunk_start + chunk_size)
            if chunk_end < file_size:
                while not is_new_line(chunk_end):
                    chunk_end += 1
                    if chunk_end >= file_size:
                        break
            start_end.append((file_name, chunk_start, chunk_end))
            chunk_start = chunk_end
    return cpu_count, start_end, file_size


def _process_file_chunk(file_name: str, chunk_start: int, chunk_end: int, counter: Value, lock: Lock) -> dict:
    """Process each file chunk separately, calculating min, max, sum, and count for measurements."""
    words_num = 0
    processed_bytes = 0
    words = {}
    with open(file_name, mode="rb") as f:
        f.seek(chunk_start)
        if chunk_start != 0:
            f.readline()  # Skip partial line at the start if not at the beginning of the file
        line = f.readline()
        while line and f.tell() <= chunk_end:
            processed_bytes += len(line)
            try:
                _word, _, match_count, _ = line.decode('utf-8').strip().split("\t")
                if _word in words:
                    words[_word] += int(match_count)
                else:
                    words[_word] = int(match_count)
                words_num += 1

                # Update the counter safely using lock
                if processed_bytes % 1000 == 0:  # Update counter every 1000 words for example
                    with lock:
                        counter.value += processed_bytes
                        processed_bytes = 0
            except ValueError:
                pass  # Handle decoding or splitting errors
            line = f.readline()

        # Update any remaining count not added in the loop
        with lock:
            counter.value += words_num % 1000

    return words


if __name__ == "__main__":
    # Example usage
    cpu_count, chunks, file_size = get_file_chunks("C:/Users/vlady/googlebooks-eng-all-1gram-20120701-a")
    print(f"File size: {file_size}")
    print(f"CPU Count: {cpu_count}")
    for chunk in chunks:
        print(f"Chunk from {chunk[1]} to {chunk[2]} in {chunk[0]}")
