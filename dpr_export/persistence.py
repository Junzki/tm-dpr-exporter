# -*- coding:utf-8 -*-
import typing as ty
import io
import datetime
import sqlalchemy as sa
import pandas as pd
import numpy as np

COLUMN_MAP = {
    'District': 'district',
    'Division': 'division',
    'Area': 'area',
    'Club': 'club',
    'Club Name': 'club_name',
    'New': 'new_members',
    'Late Ren.': 'late_renewals',
    'Oct. Ren.': 'oct_renewals',
    'Apr. Ren.': 'apr_renewals',
    'Total Ren.': 'total_renewals',
    'Total Chart': 'total_chart',
    'Total to Date': 'total_to_date',
    'Distinguished Status': 'distinguished_status',
    'Charter Date/Suspend Date': 'charter_suspend_date'
}


def charter_or_suspend_date(in_: ty.AnyStr | ty.Any) -> np.ndarray:
    """
    - Charter 03/23/23
    - Charter 12/01/21 Susp 03/31/23
    - Susp 03/31/23

    """
    result = np.array([None, None])

    if not isinstance(in_, str):
        return result
    
    origin = in_.lower().strip()
    
    current_field = None
    
    while origin:
        try:
            text, origin = origin.split(' ', 1)
        except ValueError:
            text = origin
            origin = ''

        if text == 'charter':
            current_field = 0
            continue
        elif text == 'susp':
            current_field = 1
            continue
        else:
            if current_field is None:
                continue

            date = datetime.datetime.strptime(text, '%m/%d/%y').date()
            result[current_field] = date

    return result


def clean(origin: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(origin))
    df.drop(df.tail(1).index, inplace=True)
    df.rename(columns=COLUMN_MAP, inplace=True)

    df[['charter_date', 'suspend_date']] = df.apply(lambda x: charter_or_suspend_date(x['charter_suspend_date']),
                                                    axis=1, result_type='expand')

    return df


def unique_key(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    df[['report_year', 'report_month']] = df.apply(lambda x: (year, month), axis=1, result_type='expand')
    return df


def create_upsert_method(meta: sa.MetaData, extra_update_fields: ty.Optional[ty.Dict[str, str]],
                         constraint: str):
    """
    Create upsert method that satisfied the pandas's to_sql API.

    https://blog.alexparunov.com/upserting-update-and-insert-with-pandas
    """

    def method(table, conn, keys, data_iter):
        # select table that data is being inserted to (from pandas's context)
        sql_table = sa.Table(table.name, meta, autoload_with=conn)

        # list of dictionaries {col_name: value} of data to insert
        values_to_insert = [dict(zip(keys, data)) for data in data_iter]

        # create insert statement using postgresql dialect.
        # For other dialects, please refer to https://docs.sqlalchemy.org/en/14/dialects/
        insert_stmt = sa.dialects.postgresql.insert(sql_table).values(values_to_insert)

        # create update statement for excluded fields on conflict
        update_stmt = {exc_k.key: exc_k for exc_k in insert_stmt.excluded}
        if extra_update_fields:
            update_stmt.update(extra_update_fields)

        # create upsert statement.
        upsert_stmt = insert_stmt.on_conflict_do_update(
            constraint=constraint,  # index elements are primary keys of a table
            set_=update_stmt  # the SET part of an INSERT statement
        )

        # execute upsert statement
        conn.execute(upsert_stmt)

    return method


def save(df: pd.DataFrame, conn) -> None:
    meta = sa.MetaData()
    extra_update_fields = {"updated_at": "NOW()"}

    method = create_upsert_method(meta, extra_update_fields, constraint='district_pref_uniq')

    df.to_sql('district_perf',
              con=conn,
              index=False,
              if_exists='append',
              method=method)
