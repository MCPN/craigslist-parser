import pytest
from datetime import datetime

from storage import Storage, StorageError
from parse import (
    get_total_count,
    get_timestamps,
    get_adverts_from_page,
    get_top_adverts_from_page,
)


def test_db():
    s = Storage()
    uuid = s.add('dogs', 'moscow')
    response = s.get(uuid)
    assert len(response) == 2
    assert response[0] == 'dogs'
    assert response[1] == 'moscow'

    with pytest.raises(StorageError):
        s.get('1')


files = [
    'tests/big.html',
    'tests/small.html',
    'tests/empty.html',
]
counts = [925, 3, -1]
timestamps = [
    [
        '2020-11-28 06:53',
    ],
    [
        '2020-11-11 05:16',
        '2020-10-29 02:52',
        '2020-10-16 23:25',
    ],
    [],
]
is_first = [True, False, False]


@pytest.mark.parametrize('page, count', zip(files, counts))
def test_total_count(page, count):
    f = open(page, 'r')
    assert get_total_count(f.read()) == count
    f.close()


@pytest.mark.parametrize('page, ads, first', zip(files, timestamps, is_first))
def test_adverts(page, ads, first):
    f = open(page, 'r')
    assert get_timestamps(f.read(), first=first) == ads
    f.close()


starts = [
    '2020-11-28 06:53',
    '2020-11-27 13:31',
    '2020-11-23 08:22',
    '2019-01-01',
]
finishes = [
    '2020-11-28 06:53',
    '2020-11-28 06:53',
    '2020-11-23 09:05',
    '2020-01-01',
]
expected = [
    [
        '2020-11-28 06:53',
    ],
    [
        '2020-11-28 06:53',
        '2020-11-27 15:17',
        '2020-11-27 13:31',
    ],
    [
        '2020-11-23 09:05',
        '2020-11-23 09:05',
        '2020-11-23 08:31',
        '2020-11-23 08:22',
    ],
    [],
]


@pytest.mark.parametrize('start, finish, exp', zip(starts, finishes, expected))
def test_get_timestamps_from_page(start, finish, exp):
    f = open('tests/big.html', 'r')
    assert get_adverts_from_page(f.read(), datetime.fromisoformat(start), datetime.fromisoformat(finish)) == exp
    f.close()


urls = [
    [
        'https://seattle.craigslist.org/see/trp/d/la-grange-cdl-otr-only-teams-over-4k/7238164754.html',
        'https://seattle.craigslist.org/skc/csr/d/auburn-customer-service-representative/7237944125.html',
    ],
    [
        'https://moscow.craigslist.org/edu/d/teach-english-in-china/7228904806.html',
        'https://moscow.craigslist.org/edu/d/teach-english-in-china/7221946324.html',
        'https://moscow.craigslist.org/edu/d/teach-english-in-china/7215207837.html',
    ],
]
amounts = [2, 100000000]


@pytest.mark.parametrize('file, amount, exp', zip(files[:2], amounts, urls))
def test_get_top_adverts_from_page(file, amount, exp):
    f = open(file, 'r')
    assert get_top_adverts_from_page(f.read(), amount) == exp
    f.close()
