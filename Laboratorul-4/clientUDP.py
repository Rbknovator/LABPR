import tkinter as tk
from tkinter import simpledialog
import threading
import socket
import json
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='client.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    encoding='utf-8')

class ChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', 6789)
        self.running = True
        self.init_ui()
        # Инициализация пользователя и запуск потока для приема сообщений перенесены сюда
        self.ask_nickname_and_register()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def ask_nickname_and_register(self):
        self.nickname = simpledialog.askstring("Никнейм", "Введите ваш никнейм:", parent=self)
        if self.nickname:
            self.register_to_server()
        else:
            self.running = False
            self.destroy()

    def init_ui(self):
        self.title("Чат Клиент UDP")
        self.geometry("800x600")

        self.container = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(self.container)
        self.text_area.config(state=tk.DISABLED)
        self.container.add(self.text_area)

        self.users_list = tk.Listbox(self.container)
        self.container.add(self.users_list)

        self.info_label = tk.Label(self, text="Выберите пользователя из списка для отправки сообщения")
        self.info_label.pack()

        self.message_entry = tk.Entry(self)
        self.message_entry.pack(fill=tk.X, padx=10, pady=10)

        self.send_button = tk.Button(self, text="Отправить", command=self.on_send_button_clicked)
        self.send_button.pack(pady=10)

    def register_to_server(self):
        message = json.dumps({"action": "register", "nickname": self.nickname})
        self.client_socket.sendto(message.encode(), self.server_address)

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

        self.send_message(recipient, message)

    def send_message(self, recipient, message):
        message_data = {
            "action": "message",
            "from": self.nickname,
            "to": recipient,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.client_socket.sendto(json.dumps(message_data).encode(), self.server_address)
        logging.info(f"Сообщение отправлено к {recipient}: {message}")
        self.message_entry.delete(0, tk.END)
        self.append_message_to_chat(f"You to {recipient}: {message}")

    def receive_messages(self):
        while self.running:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                message_data = json.loads(data.decode())
                if 'action' in message_data and message_data['action'] == 'update_users':
                    self.update_users_list(message_data['users'])
                elif 'message' in message_data:
                    message = f"{message_data['from']} to {message_data['to']} ({message_data.get('timestamp')}): {message_data['message']}"
                    self.append_message_to_chat(message)
            except Exception as e:
                logging.error(f"Ошибка при приеме сообщения: {e}")
                break

    def update_users_list(self, users):
        self.after(0, lambda: [self.users_list.delete(0, tk.END)] + [self.users_list.insert(tk.END, user) for user in users])

    def append_message_to_chat(self, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def on_closing(self):
        self.running = False
        self.client_socket.close()
        self.destroy()

if __name__ == "__main__":
    client = ChatClient()
    client.protocol("WM_DELETE_WINDOW", client.on_closing)  # Handle window closing
    client.mainloop()
