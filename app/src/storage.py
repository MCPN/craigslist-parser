from uuid import uuid1
from typing import Tuple, Optional

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

CONNECTION_STRING = 'dbname=postgres user=postgres'


class StorageError(Exception):
    pass


class Storage:
    """Wrapper for PostgreSQL DB"""

    def __init__(self, host: Optional[str] = None, password: Optional[str] = None) -> None:
        connection = CONNECTION_STRING
        if host is not None:
            connection += f' host={host}'
        if password is not None:
            connection += f' password={password}'

        self.conn = psycopg2.connect(connection)
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with self.conn.cursor() as cursor:
            cursor.execute('CREATE TABLE IF NOT EXISTS test (uuid VARCHAR PRIMARY KEY, query VARCHAR, region VARCHAR)')

    def add(self, query: str, region: str) -> str:
        uuid = uuid1().hex
        with self.conn.cursor() as cursor:
            cursor.execute('INSERT INTO test (uuid, query, region) VALUES (%s, %s, %s)', (uuid, query, region))
        return uuid

    def get(self, uuid: str) -> Tuple[str, str]:
        with self.conn.cursor() as cursor:
            cursor.execute('SELECT query, region FROM test WHERE uuid = (%s) LIMIT 1', (uuid,))
            result = cursor.fetchall()
            if not result:
                raise StorageError
            return result[0]
