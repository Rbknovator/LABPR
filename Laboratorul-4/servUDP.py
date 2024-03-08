import socket
import threading
import json
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='Сервер - %(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

connected_users = {}


def handle_client_message(data, client_address):
    message_data = json.loads(data.decode())
    action = message_data.get('action')

    if action == 'register':
        # Регистрация нового пользователя
        user = message_data.get('nickname')
        if user and user not in connected_users:
            connected_users[user] = client_address
            logging.info(f"Пользователь {user} успешно зарегистрирован.")
            broadcast_users_list()  # Обновляем список пользователей после регистрации нового пользователя
        else:
            logging.warning(f"Никнейм {user} уже используется.")

    elif action == 'message':
        # Отправка сообщения от одного пользователя другому
        to_user = message_data.get('to')
        from_user = message_data.get('from')
        if to_user in connected_users:
            # Формирование и отправка сообщения
            forward_message = json.dumps(message_data)
            server_socket.sendto(forward_message.encode(), connected_users[to_user])
            logging.info(f"Сообщение от {from_user} успешно отправлено к {to_user}")
        else:
            logging.warning(f"Попытка отправить сообщение несуществующему пользователю {to_user}")


def broadcast_users_list():
    # Рассылка списка всех пользователей
    users_list = list(connected_users.keys())
    message = json.dumps({"action": "update_users", "users": users_list})
    for address in connected_users.values():
        server_socket.sendto(message.encode(), address)


def server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 6789))
    logging.info("Сервер запущен и ожидает подключения...")

    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            threading.Thread(target=handle_client_message, args=(data, client_address)).start()
        except Exception as e:
            logging.error(f"Ошибка: {e}")


if __name__ == "__main__":
    server()
