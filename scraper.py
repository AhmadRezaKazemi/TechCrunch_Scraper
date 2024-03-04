import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import validators

BASE_URL = "https://search.techcrunch.com/search;_ylt=A;_ylc=X?" \
           "p={keyword}&fr2=sb-top&fr=techcrunch&b={page_number}"


class AutoScrapper:
    def __init__(self, url):
        self.url = url


def get_webpage_data(url):
    try:
        url_response = requests.get(url, timeout=args.timeout)
        url_response.raise_for_status()
        return url_response
    except Exception as e:
        print(f'could not fetch {url}. error: {e}')
        return None


def urls_from_library_lol(url):
    response = get_webpage_data(url)

    if response is None:
        return None

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f'could not parse {response.url} with error: {e}')
        return None

    try:
        all_urls = [item.find('a')['href'] for item in soup.find_all('h2') if item.find('a')]

        all_urls.extend([item.find('a')['href'] for item in soup.find_all('li') if item.find('a')])

        return all_urls
    except Exception as e:
        print(f'could not get fetch urls from {url} with error {e}')
        return None


def urls_from_libgen_li(url):
    response = get_webpage_data(url)

    if response is None:
        return None

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f'could not parse {response.url} with error: {e}')
        return None

    try:
        return [soup.find('table').find_all('td')[1].find('a')['href'].strip()]
    except Exception as e:
        print(f'could not get fetch urls from {url} with error {e}')
        return None


def fetch_book_download_urls(urls):
    download_urls = []

    for url in urls:
        url_list = None
        domain = urlparse(url).netloc
        if domain == "library.lol":
            url_list = urls_from_library_lol(url)
        elif domain == 'libgen.li':
            url_list = urls_from_libgen_li(url)

        if url_list is not None:
            download_urls.extend(url_list)

    # remove duplicates
    download_urls = sorted(set(download_urls))

    for url in download_urls:
        if not validators.url(url):
            download_urls.remove(url)

    return download_urls


def book_title(element):
    all_names = element.find_all('a')

    if len(all_names) > 1:
        name = all_names[1]
    else:
        name = all_names[0]

    if hasattr(name, 'contents'):
        return name.contents[0].strip()
    else:
        return name.text.strip()


def parse_detailed_url(url):
    response = get_webpage_data(url)

    if response is None:
        print(f"could not load {url} for download links")
        return ""

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f'could not parse {response.url} with error: {e}')
        return ""

    all_urls = soup.find_all('table')[4].find_all('td')

    urls = [item.find('a')['href'] for item in all_urls[0:2]]

    return urls, fetch_book_download_urls(urls)


def parse_simple(soup):
    table_rows = soup.find_all('table')[2].find_all('tr')

    book_rows = table_rows[1:]

    if len(book_rows) == 0:
        return None

    all_books = [row.find_all('td') for row in book_rows]

    books = []

    for book in all_books:
        download_urls = [item.find('a')['href'] for item in book[9:-1]]
        books.append(
            {
                "ID": book[0].text.strip(),
                "Author": book[1].text.strip(),
                "Title": book_title(book[2]),
                "Publisher": book[3].text.strip(),
                "Year": book[4].text.strip(),
                "Pages": book[5].text.strip(),
                "Language": book[6].text.strip(),
                "Size": book[7].text.strip(),
                "Extension": book[8].text.strip(),
                "Download Webpages": download_urls,
                "Download Links": fetch_book_download_urls(download_urls),
            }
        )

    return books


def parse_detailed(soup):
    all_books_tables = soup.find_all('table')[3:-1:2]

    if len(all_books_tables) == 0:
        return None

    books = []

    for book in all_books_tables:
        all_rows = book.find('tbody').find_all('tr')[:-1]
        first_row = all_rows[1].find_all('td')
        second_row = all_rows[2].find_all('td')
        third_row = all_rows[3].find_all('td')
        forth_row = all_rows[4].find_all('td')
        fifth_row = all_rows[5].find_all('td')
        sixth_row = all_rows[6].find_all('td')
        seventh_row = all_rows[7].find_all('td')
        eighth_row = all_rows[8].find_all('td')
        ninth_row = all_rows[9].find_all('td')

        download_webpages, download_links = parse_detailed_url(WEBSITE_PREFIX + first_row[2].find('a')['href'])

        books.append({
            "ID": seventh_row[3].text.strip(),
            "Image URL": WEBSITE_PREFIX + first_row[0].find('img')['src'],
            "Title": first_row[2].text.strip(),
            "Volume": first_row[3].text.split(':', 1)[-1].strip(),
            "Author": second_row[1].text.strip(),
            "Series": third_row[1].text.split(':', 1)[-1].strip(),
            "Publisher": forth_row[1].text.strip(),
            "year": fifth_row[1].text.strip(),
            "Edition": fifth_row[3].text.strip(),
            "Language": sixth_row[1].text.strip(),
            "Pages": sixth_row[3].text.strip(),
            "ISBN": [item.strip() for item in seventh_row[1].text.strip().split(',')],
            "Time Added": eighth_row[1].text.strip(),
            "Time Modified": eighth_row[3].text.strip(),
            "Size": ninth_row[1].text.strip(),
            "Extension": ninth_row[3].text.strip(),
            "Download Webpages": download_webpages,
            "Download Links": download_links,
        })

    return books


def parse_url(response):
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f'could not parse {response.url} with error: {e}')
        return None

    if args.detailed:
        return parse_detailed(soup)
    else:
        return parse_simple(soup)


def scrap_url(cli_args):
    global args
    args = cli_args
    page_index = 1

    request_url = BASE_URL.format(
        keyword=args.keywords.replace(" ", "+"),
        view_style="detailed" if args.detailed else "simple",
        mask_option="0" if args.mask_option else "1",
        column=args.column,
        page_number=page_index,
    )

    response = get_webpage_data(request_url)

    if response is None:
        print(f"Error! could not load {request_url}")
        return

    books = []

    # Todo: make percentage progress per each book
    while response is not None:
        print(f'scraping page {page_index}')

        results = parse_url(response)

        # webpage would not raise 404, instead there is no content
        if results is None:
            break

        books.extend(results)

        page_index += 1

        request_url = BASE_URL.format(
            keyword=args.keywords.replace(" ", "+"),
            view_style="detailed" if args.detailed else "simple",
            mask_option="0" if args.mask_option else "1",
            column=args.column,
            page_number=page_index,
        )

        # try multiple times
        for i in range(3):
            response = get_webpage_data(request_url)

            if response is not None:
                break

    print(f'reached end of pages. last page was {page_index-1}')

    return books
