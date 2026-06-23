import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse


def download_pdfs(base_url, download_dir='ford_manuals'):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if re.search(r'\.pdf$', href, re.IGNORECASE):
                full_url = urljoin(base_url, href)
                pdf_links.append(full_url)

        print(f'Найдено {len(pdf_links)} PDF:')
        for i, pdf_url in enumerate(pdf_links, 1):
            print(f'{i}. {pdf_url}')

            filename = os.path.join(download_dir, f'manual_{i}_{os.path.basename(urlparse(pdf_url).path)}')
            pdf_response = requests.get(pdf_url, headers=headers)
            pdf_response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            print(f'Скачано: {filename}')

    except requests.exceptions.RequestException as e:
        print(f'Ошибка: {e}')


# Для Ford
download_pdfs('https://www.major-ford.ru/owners/manual/carsarch/')

if __name__ == "__main__":
    download_pdfs(download_pdfs)