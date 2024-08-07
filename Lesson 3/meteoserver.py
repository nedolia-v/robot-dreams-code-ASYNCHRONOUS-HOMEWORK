import asyncio
import random

clients = []

# Початкові випадкові значення
temperature = random.uniform(-10, 35)
humidity = random.uniform(0, 100)
wind_speed = random.uniform(0, 30)

async def generate_weather_data():
    # Генерація метеорологічних даних з поступовою зміною.
    global temperature, humidity, wind_speed

    # Зміна значень з обмеженням
    temperature += random.uniform(-1, 1)
    humidity += random.uniform(-0.3, 0.3)
    wind_speed += random.uniform(-3, 3)

    # Обмеження діапазону значень
    temperature = max(min(temperature, 35), -10)
    humidity = max(min(humidity, 100), 0)
    wind_speed = max(min(wind_speed, 30), 0)

    return f"Temperature: {temperature:.2f} C, Humidity: {humidity:.2f}%, Wind Speed: {wind_speed:.2f} m/s\n"

async def broadcast_data():
    # Відправка даних усім підключеним клієнтам.
    while True:
        data = await generate_weather_data()
        print(f"Broadcasting: {data.strip()}")
        for writer in clients:
            writer.write(data.encode())
            await writer.drain()
        await asyncio.sleep(2)  # Надсилати дані кожні 2 секунди

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"Connected by {addr}")
    clients.append(writer)

    try:
        await reader.read()  # Чекаємо поки клієнт закриє з'єднання
    finally:
        print(f"Connection with {addr} closed")
        clients.remove(writer)
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, "localhost", 8000)
    print("Serving on localhost:8000")
    async with server:
        await asyncio.gather(server.serve_forever(), broadcast_data())

asyncio.run(main())