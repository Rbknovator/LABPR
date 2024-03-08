import asyncio
import json
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='../Laboratorul-4/server.log', level=logging.INFO,
                    format='Сервер - %(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

connected_users = {}

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info(f"Новое соединение от {addr}")
    try:
        user = await register(reader, writer)
        if user:
            await manage_messages(user, reader, writer)
    finally:
        await unregister(user, writer)

async def register(reader, writer):
    try:
        logging.info("Ожидание регистрации клиента...")
        data = await reader.readline()
        registration_info = json.loads(data.decode())
        nickname = registration_info.get("nickname")

        if not nickname:
            logging.warning("Никнейм не предоставлен.")
            return None

        if nickname in connected_users:
            logging.warning(f"Никнейм {nickname} уже занят.")
            return None

        connected_users[nickname] = writer
        logging.info(f"Пользователь {nickname} успешно зарегистрирован.")
        await notify_users()
        return nickname
    except Exception as e:
        logging.error(f"Ошибка при регистрации: {e}")
        return None

async def unregister(user, writer):
    if user in connected_users:
        del connected_users[user]
        logging.info(f"Пользователь {user} отключен.")
        await notify_users()

async def manage_messages(user, reader, writer):
    while True:
        try:
            data = await reader.readline()
            if not data:
                break  # Соединение закрыто
            message_info = json.loads(data.decode())
            await process_message(user, message_info)
        except Exception as e:
            logging.error(f"Ошибка при обработке сообщения: {e}")
            break

async def process_message(user, data):
    to_user = data.get("to")
    message = data.get("message")
    timestamp = datetime.now().isoformat()

    if to_user in connected_users:
        target_writer = connected_users[to_user]
        forward_message = json.dumps({"from": user, "to": to_user, "message": message, "timestamp": timestamp})
        target_writer.write(forward_message.encode() + b'\n')
        await target_writer.drain()
        logging.info(f"Сообщение от {user} к {to_user}: {message}")
    else:
        logging.warning(f"Пользователь {to_user} не найден.")

async def notify_users():
    update_message = json.dumps({"action": "update", "users": list(connected_users.keys())})
    for writer in connected_users.values():
        writer.write(update_message.encode() + b'\n')
        await writer.drain()

async def main():
    server = await asyncio.start_server(handle_client, 'localhost', 6789)
    addr = server.sockets[0].getsockname()
    logging.info(f"Сервер запущен на {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
