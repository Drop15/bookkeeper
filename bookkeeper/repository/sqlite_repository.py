"""
Модуль описывает репозиторий, работающий с SQLite
"""

from typing import Any
from bookkeeper.repository.abstract_repository import AbstractRepository, T
from inspect import get_annotations

import sqlite3

DB_FILE = 'bookkeeper/db/client.db'


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий с SQLite.
    """

    db_file: str
    table_name: str
    cls: type
    fields: dict[str, type]

    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls
        self.create_table()

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES ({p})',
                values
            )
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            raw_res = cur.execute(
                f"SELECT * FROM {self.table_name} WHERE pk={pk}"
            )
            res = self.__parse_query_to_class(raw_res.fetchone())
        con.close()
        return res

    def get_all(self, where: dict[str, Any] | None = None, subquery: str | None = None) -> list[T | None]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query = f"SELECT * FROM {self.table_name}"
            if where is not None:
                query += " WHERE " + ' AND '.join(
                    [f"{key} = {value}"
                     for key, value in where.items()
                     if value is not None
                     and isinstance(value, int) or isinstance(value, float)] +
                    [f"{key} = '{value}'"
                     for key, value in where.items()
                     if value is not None
                     and not (isinstance(value, int) or isinstance(value, float))]
                )
            if subquery is not None:
                query += " " + subquery

            raw_res = cur.execute(query)
            res = raw_res.fetchall()
        con.close()
        out = [self.__parse_query_to_class(res[pk]) for pk in range(len(res))]
        return out

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            sql_query = f"UPDATE {self.table_name} SET "
            sql_query += ','.join(
                [f"{attr} = {val}"
                 for attr, val in obj.__dict__.items()
                 if attr != 'pk' and val is not None
                 and isinstance(val, int) or isinstance(val, float)] +
                [f"{attr} = '{val}'"
                 for attr, val in obj.__dict__.items()
                 if attr != 'pk' and val is not None
                 and not (isinstance(val, int) or isinstance(val, float))]
            )
            sql_query += f" WHERE pk={obj.pk}"
            cur.execute(sql_query)
        con.close()

    def delete(self, pk: int) -> None:
        if pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f"DELETE FROM {self.table_name} WHERE pk={pk}"
            )
        con.close()

    def create_table(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query = f"CREATE TABLE IF NOT EXISTS {self.table_name} "
            query += "(pk INTEGER PRIMARY KEY, "
            query += ', '.join(list(self.fields.keys())) + ')'
            cur.execute(query)
        con.close()

    def drop_table(self) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        con.close()

    def __parse_query_to_class(self, query: tuple[Any] | None) -> T | None:
        if query is not None:
            query_dict = dict(zip({"pk": int} | self.fields, query))
            out = self.cls(**query_dict)
        else:
            out = None
        return out

    @classmethod
    def repository_factory(cls, models: list[type], db_file: str | None = None) -> dict[type, type]:
        return {model: cls(model, db_file for model in models}
