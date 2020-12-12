from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from requests.exceptions import Timeout

from storage import Storage, StorageError
from parse import get_adverts, get_top_adverts, DatetimeParseError

app = FastAPI()
storage = Storage(host='db', password='password')


@app.get("/")
def read_root() -> Dict[str, str]:
    """Landing page"""
    return {
        '/add': 'add region and query',
        '/stat': 'get stat by id and time interval',
        '/top': 'get top n adverts by time or relevance',
    }


@app.get("/add")
def add(query: str, region: str) -> Dict[str, str]:
    """Adds (query, region) to DB

    :param query: query to be made
    :param region: region for the query (request would be made on region.craigslist.org)
    :return: json with uuid for requests
    """
    return {'uuid': storage.add(query, region)}


@app.get("/get")
def get(uuid: str) -> Dict[str, str]:
    """Gets query and region by uuid

    :param uuid: registered uuid
    :return: json with query and region on success and error message if uuid wasn't registered
    """
    try:
        query, region = storage.get(uuid)
        return {'query': query, 'region': region}
    except StorageError:
        raise HTTPException(status_code=404, detail=f'no query found by uuid {uuid}')


@app.get("/stat")
def stat(uuid: str, start: str, finish: str) -> dict:
    """Gets adverts for uuid on time interval [start; finish]

    :param uuid: registered uuid
    :param start: the beginning of the interval; must me parsable by datetime.fromisoformat;
    can be accurate up to minutes
    :param finish: the ending of the interval; format is the same as for start
    :return: error message if uuid wasn't registered or arguments are ill-formed;
    timestamps and amount on success
    """
    got = get(uuid)
    query, region = got['query'], got['region']

    try:
        adverts = get_adverts(query, region, start, finish)
        return {'counter': len(adverts), 'timestamps': adverts}
    except DatetimeParseError:
        raise HTTPException(status_code=400, detail='wrong format of start and/or finish')
    except Timeout:
        raise HTTPException(status_code=503, detail='unable to connect to craigslist')


@app.get("/top")
def top(uuid: str, amount: Optional[int] = 5, sort: Optional[str] = None) -> dict:
    """Gets top amount adverts with respect to sort

    :param uuid: registered uuid
    :param amount: amount of adverts; 5 by default; shouldn't be more than 120 because
    function only gets the first page of adverts
    :param sort: sorting criteria, either 'date' or 'rel' (relevance); 'date' by default
    :return: error message if uuid wasn't registered or arguments are ill-formed;
    list of urls on success; length of list may be shorter than amount if there less
    than amount adverts for given request
    """
    if amount <= 0 or amount > 120:
        raise HTTPException(status_code=400, detail='amount must be between 1 and 120')
    if sort is None:
        sort = 'date'
    elif sort != 'date' and sort != 'rel':
        raise HTTPException(status_code=400, detail='sort must be either \'date\' or \'rel\'')

    got = get(uuid)
    query, region = got['query'], got['region']
    try:
        adverts = get_top_adverts(query, region, amount, sort)
        return {'adverts': adverts}
    except Timeout:
        raise HTTPException(status_code=503, detail='unable to connect to craigslist')
