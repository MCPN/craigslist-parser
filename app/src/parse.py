from typing import List, Optional
from datetime import datetime

from lxml import html
from requests import Session


XPATH_COUNT = "(//span[contains(concat(' ', @class, ' '), ' totalcount ')]/text())"
XPATH_TIMESTAMPS = "(//time[contains(concat(' ', @class, ' '), ' result-date ')]/@datetime)"
XPATH_URL = "(//a[contains(concat(' ', @class, ' '), ' result-title hdrlnk ')]/@href)"
ADVERTS_PER_PAGE = 120


class DatetimeParseError(ValueError):
    """Throws if passed timestamps are ill-formed"""
    pass


class CraigslistSession:
    """Wrapper for requests.Session"""
    def __init__(self, query: str, region: str, sort: Optional[str] = None) -> None:
        self.session = Session()
        self.session.params.update({'query': query, 'sort': sort if sort is not None else 'date'})
        self.url = f'https://{region}.craigslist.org/search/jjj'

    def parse(self, offset: Optional[int] = None) -> str:
        params = {}
        if offset is not None:
            params['s'] = str(offset)
        return self.session.get(self.url, params=params, timeout=5).text


def get_total_count(content: str) -> int:
    """Returns the total amount of adverts of request"""
    tree = html.fromstring(content)
    count = tree.xpath(XPATH_COUNT)
    if not count:
        return -1
    else:
        return int(count[0])


def get_timestamps(content: str, first: bool = False) -> List[str]:
    """Returns timestamps from page (if first is True, returns only the first one)"""
    tree = html.fromstring(content)
    if first:
        return tree.xpath(XPATH_TIMESTAMPS + '[1]')
    else:
        return tree.xpath(XPATH_TIMESTAMPS)


def get_adverts_from_page(content: str, start: datetime, finish: datetime) -> List[str]:
    """Returns filtered by timestamps adverts"""
    return [ad for ad in get_timestamps(content) if start <= datetime.fromisoformat(ad) <= finish]


def get_adverts(query: str, region: str, start: str, finish: str) -> List[str]:
    """Main function for the /stat request"""
    try:
        start = datetime.fromisoformat(start)
        finish = datetime.fromisoformat(finish)
    except ValueError:
        raise DatetimeParseError

    session = CraigslistSession(query, region)
    page = session.parse()
    total_count = get_total_count(page)
    if total_count == -1:
        return []

    adverts = []
    for offset in range(0, total_count, ADVERTS_PER_PAGE):
        page = session.parse(offset=offset)
        adverts += get_adverts_from_page(page, start, finish)
    return adverts


def get_top_adverts_from_page(content: str, amount: int) -> List[str]:
    """Gets the top amount of adverts from page"""
    tree = html.fromstring(content)
    return tree.xpath(XPATH_URL)[:amount]


def get_top_adverts(query: str, region: str, amount: int, sort: str) -> List[str]:
    """Main function for the /top request"""
    session = CraigslistSession(query, region, sort)
    page = session.parse()
    return get_top_adverts_from_page(page, amount)
