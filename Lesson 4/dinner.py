import asyncio
table_capacity = 5
forks = [asyncio.Lock() for _ in range(table_capacity)]
places = range(table_capacity)

async def philosopher(place):
    while True:
        print(f"Philosopher {place} is thinking...")
        await asyncio.sleep(1)  # Thinking
        print(f"Philosopher {place} wants to eat.")

        left_fork = forks[place]
        right_fork = forks[(place + 1) % table_capacity]

        async with left_fork:
            print(f"Philosopher {place} picked up left fork.")
            async with right_fork:
                print(f"Philosopher {place} picked up right fork.")
                print(f"Philosopher {place} is eating.")
                await asyncio.sleep(1)  # Eating
                print(f"Philosopher {place} put down right fork.")
        print(f"Philosopher {place} put down forks.")

async def main():
    tasks = [philosopher(place) for place in places]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())