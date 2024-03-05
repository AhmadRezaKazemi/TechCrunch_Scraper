import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import validators


SEARCH_URL = "https://search.techcrunch.com/search;_ylt=A;_ylc=X?" \
             "p={keyword}&fr2=sb-top&fr=techcrunch&b={page_number}"
CATEGORY_URL = "https://techcrunch.com/wp-json/tc/v1/magazine?page={page_number}" \
               "&_embed=true&_envelope=true&categories={category_code}&cachePrevention=0"
CATEGORY_CODE = {
    'Startups': 20429,
    'Venture': 577030455,
    'Security': 21587494,
    'AI': 577047203,
    'Crypto': 576601119,
    'Apps': 577051039,
    'Fintech': 577030453,
    'Hardware': 449223024,
    'Transportation': 2401,
    'Media & Entertainment': 577030456,
    'Enterprise': 449557044,
    'Biotech & Health': 577030454,
    'Robotics': 577123751,
    'Gadgets': 577052803,
    'Privacy': 426637499,
    'TC': 17396
}


class Scrapper:
    def __init__(self, url, args):
        self.url = url
        self.args = args

    def get_webpage_data(self, url):
        try:
            url_response = requests.get(url, timeout=self.args.timeout)
            url_response.raise_for_status()
            return url_response
        except Exception as e:
            print(f'could not fetch {url}. error: {e}')
            return None

    def parse_url(self, response):
        return None

    @staticmethod
    def increase_page_number(index):
        return index + 1

    def create_url(self, page_index):
        return self.url.format(
            page_number=page_index,
        )

    def scrap_web_page(self):
        page_index = 1

        request_url = self.create_url(page_index)

        response = self.get_webpage_data(request_url)

        if response is None:
            print(f"Error! could not load {request_url}")
            return

        items = []

        # Todo: make percentage progress per each result
        while response is not None:
            results = self.parse_url(response)

            # webpage would not raise 404, instead there is no content
            if results is None:
                break

            items.extend(results)

            page_index = self.increase_page_number(page_index)

            request_url = self.create_url(page_index)

            # try multiple times
            for i in range(3):
                response = self.get_webpage_data(request_url)

                if response is not None:
                    break

        print(f'reached end of pages. last page was {page_index - 1}')

        return items


class AutoScrapper(Scrapper):
    def __init__(self, url, args):
        super().__init__(url, args)

    def create_url(self, page_index, category_code):
        return self.url.format(
            page_number=page_index,
            category_code=category_code
        )


class SearchScrapper(Scrapper):
    def __init__(self, url, args,  kewords, result_count):
        super().__init__(url, args)
        self.keywords = kewords
        self.result_count = result_count

    @staticmethod
    def increase_page_number(index):
        return index + 10
