import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from local_settings import PATH
import re
import os


class HtmlDownloader:
    def __init__(self, url):
        self.url = url

    def download_page_component(self, url, media_path):
        absolute_url = urljoin(self.url, url)
        filename = os.path.basename(urlparse(absolute_url).path)
        resource_filepath = os.path.join(media_path, filename)
        if not os.path.exists(resource_filepath):
            resource_response = requests.get(absolute_url)
            with open(resource_filepath, 'wb') as f:
                f.write(resource_response.content)
        return filename

    def download_page(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            title = re.sub(r'[\\/:*?"<>|]', '_', soup.title.string)[:60].strip()

            html_filepath = f'{PATH}/{title}'
            media_path = f"{html_filepath}/media"
            os.makedirs(media_path, exist_ok=True)

            for tag in soup.find_all('img', src=True):
                url = tag.get('src')
                try:
                    if url:
                        filename = self.download_page_component(url, media_path)
                        tag['src'] = f"media/{filename}"
                except Exception as e:
                    continue

            for tag in soup.find_all(['link', 'script'], href=True):
                url = tag.get('href')
                if url:
                    try:
                        filename = self.download_page_component(url, media_path)
                        tag['href'] = f"media/{filename}"
                    except Exception as e:
                        continue

            with open(f'{html_filepath}/{title}.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())

            return html_filepath

        except Exception as e:
            print('Could not download webpage:', e)
            return None
