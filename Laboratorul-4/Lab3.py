import requests
from threading import Thread
from queue import Queue

# Функция для чтения прокси из файла
def read_proxies(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

# Функция для проверки прокси
def check_proxy(proxy):
    try:
        response = requests.get('http://httpbin.org/ip', proxies={"http": f"http://{proxy}", "https": f"https://{proxy}"}, timeout=5)
        if response.status_code == 200:
            return True
    except:
        return False

# Функция для нахождения двух работающих прокси
def find_working_proxies(proxy_list):
    working_proxies = []
    for proxy in proxy_list:
        if check_proxy(proxy):
            working_proxies.append(proxy)
            if len(working_proxies) == 2:
                break
    return working_proxies

# Функция для выполнения запросов с использованием рабочих прокси
def make_request(method, proxies, q):
    proxy = {'http': f'http://{proxies[0]}', 'https': f'http://{proxies[1]}'}
    try:
        response = requests.request(method, URLS[method], proxies=proxy)
        q.put((method, response.text))
    except requests.RequestException as e:
        q.put((method, f"Ошибка запроса: {e}"))

# URL для тестовых запросов
URLS = {
    'GET': 'https://httpbin.org/get',
    'POST': 'https://httpbin.org/post',
    'HEAD': 'https://httpbin.org/get',
    'OPTIONS': 'https://httpbin.org/get',
}

# Путь к файлу с прокси
proxy_filename = 'proxy.txt'
proxy_list = read_proxies(proxy_filename)
working_proxies = find_working_proxies(proxy_list)

if len(working_proxies) < 2:
    print("Найдено менее двух рабочих прокси.")
else:
    # Инициализация очереди
    q = Queue()

    # Создание и запуск потоков для разных типов запросов
    methods = ['GET', 'POST', 'HEAD', 'OPTIONS']
    threads = [Thread(target=make_request, args=(method, working_proxies, q)) for method in methods]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Получение и вывод результатов из очереди
    while not q.empty():
        method, result = q.get()
        print(f"Method: {method}, Result: {result}\n")
