import asyncio
import json
import tkinter as tk
from tkinter import simpledialog
import threading
import logging

# Настройка логирования
logging.basicConfig(filename='../Laboratorul-4/app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s', encoding='utf-8')

class ChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.reader = None
        self.writer = None

    def init_ui(self):
        self.title("Чат Клиент")
        self.geometry("800x600")

        self.container = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(self.container)
        self.text_area.config(state=tk.DISABLED)  # Сделать область текста только для чтения
        self.container.add(self.text_area)

        self.users_list = tk.Listbox(self.container)
        self.container.add(self.users_list)

        self.info_label = tk.Label(self, text="Выберите пользователя из списка для отправки сообщения")
        self.info_label.pack()

        self.message_entry = tk.Entry(self)
        self.message_entry.pack(fill=tk.X, padx=10, pady=10)

        self.send_button = tk.Button(self, text="Отправить", command=self.on_send_button_clicked)
        self.send_button.pack(pady=10)

    async def connect_to_server(self, address, nickname):
        try:
            self.reader, self.writer = await asyncio.open_connection(*address)
            logging.info("Отправка запроса на регистрацию...")
            await self.send_message({"type": "HELLO-REQUEST", "nickname": nickname})

            # Ожидание подтверждения регистрации
            await self.listen_to_server()
        except Exception as e:
            logging.error(f"Ошибка подключения к серверу: {e}")

    async def listen_to_server(self):
        try:
            while True:
                message = await self.reader.readline()
                if not message:
                    break
                message_data = json.loads(message.decode())
                if message_data.get("action") == "update":
                    self.update_users_list(message_data["users"])
                elif message_data.get("action") == "message":
                    self.display_message(message_data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Ошибка при получении данных: {e}")

    async def send_message(self, message_data):
        message = json.dumps(message_data).encode() + b'\n'
        self.writer.write(message)
        await self.writer.drain()

    def on_send_button_clicked(self):
        selected = self.users_list.curselection()
        if not selected:
            logging.warning("Получатель не выбран.")
            return

        recipient = self.users_list.get(selected[0])
        message = self.message_entry.get()
        if not message:
            logging.warning("Сообщение пустое.")
            return

        asyncio.run_coroutine_threadsafe(self.send_message({"action": "message", "to": recipient, "message": message}), asyncio.get_event_loop())

    def display_message(self, data):
        message = f"{data['from']} to {data['to']} ({data.get('timestamp')}): {data['message']}"
        self.after(0, lambda: self.append_message_to_chat(message))

    def append_message_to_chat(self, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def update_users_list(self, users):
        self.after(0, lambda: [self.users_list.delete(0, tk.END)] + [self.users_list.insert(tk.END, user) for user in users])

def start_client():
    client = ChatClient()
    server_address = ('localhost', 6789)
    nickname = simpledialog.askstring("Никнейм", "Введите ваш никнейм:", parent=client)
    if nickname:
        logging.info(f"Запуск клиента с никнеймом {nickname}")
        threading.Thread(target=lambda: asyncio.run(client.connect_to_server(server_address, nickname)), daemon=True).start()
    client.mainloop()

if __name__ == "__main__":
    start_client()
