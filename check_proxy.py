import threading
import random
import queue
import requests
import re
from bs4 import BeautifulSoup
import requests


proxy_link = 'https://free-proxy-list.net/'

response = requests.get(proxy_link)

# print('Response the status code:', response.status_code)
# print('=========================================================================\n')

if response.status_code == 200:
  soup = BeautifulSoup(response.content, 'html.parser')

# print(soup)
# soup
# print('\n=========================================================================\n')


# =================================      SCRAPING PROXY LIST   =========================== 

def scrape_proxies(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')

  # Temukan elemen textarea dengan class 'form-control' (sesuaikan selector jika perlu)
  textarea = soup.find('textarea', class_='form-control')

  # Ambil teks dari textarea dan bagi menjadi list berdasarkan baris
  proxy_list = textarea.text.strip().split('\n')

  # Filter list untuk menghapus baris kosong
  proxy_list = [proxy for proxy in proxy_list if proxy]

  return proxy_list

# Ganti dengan URL target
url = proxy_link
proxies = scrape_proxies(url)
proxies.pop(0)
proxies.pop(0)

list_prox = []
# Cetak hasil
for proxy in proxies:
#   print(proxy)
  list_prox.append(proxy)


# print('Hasil proxy list sementara (mix Valid & non-Valid):\n',list_prox)
# print('\n=========================================================================\n')


# =================================      TEST VALID PROXY LIST / TESTING PROXY YG VALID  =========================== 
def check_proxies(proxies, limit=30):
    """Fungsi untuk mengecek validitas proxy secara multi-threading.
    Args:
        proxies: List of proxies.
    """
    q = queue.Queue()
    valid_proxies = []

    for p in proxies:
        q.put(p)

    def worker():
        while not q.empty() and len(valid_proxies) <= limit:
            proxy = q.get()
            try:
                res = requests.get('http://ipinfo.io/json',
                                   proxies={'http': proxy, 'https': proxy})
                if res.status_code == 200:
                    # print(proxy, "is valid")
                    valid_proxies.append(proxy)
            # except requests.exceptions.RequestException as e:
            except:
                # print(f"Error checking proxy {proxy}: {e}")
                continue

    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return valid_proxies

limits = 50
valid_proxies = check_proxies(proxies)
print("Data type valid_proxies:", type(valid_proxies),'\n')
print("banyak data valid_proxies:", len(valid_proxies),'\n')
print("Valid proxies:", valid_proxies)
print('\n=========================================================================\n')


sites_to_check = ['https://irecommend.ru/content/polet-aeroflotom-moskva-kolombo-noyabr-2024',
                  'https://irecommend.ru/content/ochen-nravitsya-vyruchaet-paru-khitrostei-dlya-novichkov',
                  'https://irecommend.ru/content/utair']

# counter = 0
# valid_proxies = ['50.169.37.50:80', '50.217.226.47:80' , '50.168.72.119:80']
for site in sites_to_check:
    try:
        # proxies = random.choice(proxies)
        proxy = random.choice(valid_proxies)
        print(f'Using the proxy: {proxy}')
        res = requests.get(site, proxies={"http": proxy,
                                          'https': proxy},
                                          timeout=5
                                          )
        print(f'Status code: {res.status_code}')
    except:
        print('Failed !')
