import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# Функция отправки письма
def send_email():
    try:
        server = smtplib.SMTP(smtp_server.get(), 587)
        server.starttls()
        server.login(email_login.get(), email_password.get())
        msg = MIMEMultipart()
        msg['From'] = email_login.get()
        msg['To'] = recipient_email.get()
        msg['Subject'] = subject.get()
        msg.attach(MIMEText(email_body.get("1.0", END), 'plain'))
        server.send_message(msg)
        server.quit()
        messagebox.showinfo("Успех", "Письмо успешно отправлено!")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Функция для чтения входящих писем
def read_emails():
    try:
        mail = imaplib.IMAP4_SSL(imap_server.get())
        mail.login(email_login.get(), email_password.get())
        mail.select('inbox')
        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()
        latest_email_id = email_ids[-1]  # Получаем последнее сообщение
        result, data = mail.fetch(latest_email_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        messagebox.showinfo("Последнее письмо", f"От: {msg['From']}\nТема: {msg['Subject']}\n{msg.get_payload(decode=True)}")
        mail.logout()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Создание графического интерфейса
root = Tk()
root.title("Email Client")

Label(root, text="Логин:").grid(row=0, column=0)
Label(root, text="Пароль:").grid(row=1, column=0)
Label(root, text="SMTP сервер:").grid(row=2, column=0)
Label(root, text="IMAP сервер:").grid(row=3, column=0)
Label(root, text="Получатель:").grid(row=4, column=0)
Label(root, text="Тема:").grid(row=5, column=0)
Label(root, text="Сообщение:").grid(row=6, column=0)

email_login = Entry(root)
email_password = Entry(root, show="*")
smtp_server = Entry(root)
imap_server = Entry(root)
recipient_email = Entry(root)
subject = Entry(root)
email_body = ScrolledText(root, height=10, width=50)

email_login.grid(row=0, column=1)
email_password.grid(row=1, column=1)
smtp_server.grid(row=2, column=1)
imap_server.grid(row=3, column=1)
recipient_email.grid(row=4, column=1)
subject.grid(row=5, column=1)
email_body.grid(row=6, column=1, columnspan=2)

Button(root, text="Отправить", command=send_email).grid(row=7, column=0)
Button(root, text="Получить последнее письмо", command=read_emails).grid(row=7, column=1)

root.mainloop()

