import asyncio

async def read_weather_data(reader: asyncio.StreamReader):
    # Читання даних з сервера.
    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            print(f"Received: {data.decode().strip()}")
    except asyncio.CancelledError:
        print("Connection closed")

async def main():
    reader, writer = await asyncio.open_connection('localhost', 8000)
    try:
        await read_weather_data(reader)
    finally:
        print("Closing the connection")
        writer.close()
        await writer.wait_closed()

asyncio.run(main())