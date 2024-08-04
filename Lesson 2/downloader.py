import asyncio
import aiohttp
import argparse
from aiofiles import open as aio_open
import re
import os
import shutil
import time

async def fetch(url, session):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                data = await response.text()
                safe_filename = re.sub(r'[<>:"/\\|?*]+', '', url)
                file_path = os.path.join('output', f"{safe_filename}.txt")
                async with aio_open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(data)
                print(f"Збережено: {file_path}")
            else:
                print(f"Помилка: Не вдалося завантажити {url}, статус: {response.status}")
    except Exception as e:
        print(f"Помилка при завантаженні {url}: {e}")

async def main(urlsfile):
    if not os.path.exists('output'):
        os.makedirs('output')
    else:
        shutil.rmtree('output')
        os.makedirs('output')

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(url, session) for url in urlsfile]
        await asyncio.gather(*tasks)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Час завантаження та запису: {elapsed_time:.2f} секунд")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='Файл з URL-адресами')
    args = parser.parse_args()

    with open(args.file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    asyncio.run(main(urls))