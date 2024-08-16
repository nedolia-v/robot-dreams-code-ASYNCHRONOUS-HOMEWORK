import os
import multiprocessing as mp
from gc import disable as gc_disable, enable as gc_enable


def get_file_chunks(file_name: str, max_cpu: int = 8) -> tuple[int, list[tuple[str, int, int]]]:
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
    return cpu_count, start_end


def _process_file_chunk(file_name: str, chunk_start: int, chunk_end: int) -> dict:
    """Process each file chunk separately, calculating min, max, sum, and count for measurements."""
    result = {}
    with open(file_name, mode="rb") as f:
        f.seek(chunk_start)
        gc_disable()  # Optimize performance by disabling garbage collection
        # Skip partial line at the start if not at the beginning of the file
        if chunk_start != 0:
            f.readline()
        line = f.readline()
        while line and f.tell() <= chunk_end:
            try:
                location, measurement = line.decode('utf-8').strip().split(";")
                measurement = float(measurement)
                if location in result:
                    result[location]['min'] = min(result[location]['min'], measurement)
                    result[location]['max'] = max(result[location]['max'], measurement)
                    result[location]['sum'] += measurement
                    result[location]['count'] += 1
                else:
                    result[location] = {'min': measurement, 'max': measurement, 'sum': measurement, 'count': 1}
            except ValueError:
                # Ignore lines that do not conform to expected format
                pass
            line = f.readline()
        gc_enable()  # Re-enable garbage collection after processing
    return result


if __name__ == "__main__":
    # Example usage
    cpu_count, chunks = get_file_chunks("C:/Users/vlady/googlebooks-eng-all-1gram-20120701-a")
    print(f"CPU Count: {cpu_count}")
    for chunk in chunks:
        print(f"Chunk from {chunk[1]} to {chunk[2]} in {chunk[0]}")
