from time import perf_counter
import traceback

import pandas as pd
from gazpacho import Soup
from gazpacho import get
from sqlalchemy import create_engine
from sqlalchemy.types import Float

import credentials


def make_soup():
    """Makes soup on html from Yahoo FB transactions page."""
    url = 'https://basketball.fantasysports.yahoo.com/nba/buzzindex'
    html = get(url)
    return Soup(html)


def get_trends_table():
    """Returns html from trends table."""
    soup = make_soup()
    return soup.find('table', {'class': 'Tst-table Table'}).html


def create_df():
    """Constructs and cleans DataFrame from Yahoo transaction table."""
    trends_tbl = get_trends_table()
    df = pd.read_html(trends_tbl)[0]
    df.drop(columns=['Trades', 'Adds  Drops'], inplace=True)
    df.rename(columns={'Total': 'Total'}, inplace=True)
    df.columns = df.columns.str.lower()
    df.index += 1
    return df


def add_team_position_column(df):
    """Add 'team_position' column to DataFrame."""
    tp_pat = r'\w{2,3}\s-\s[A-Z,]+'
    tp_sr = df['player'].str.findall(tp_pat)
    tp_lst = [tp[0] for tp in tp_sr]
    df.insert(1, 'team_position', tp_lst)
    return df


def clean_player_column(df):
    """Returns player name from 'Player' column."""
    df['player'] = (df['player']
                    .str.replace(r'.+Notes?\s+', '')
                    .str.replace(r'\s\w{2,3}\s-.+', ''))
    return df


def add_date_fetched(df):
    """Add 'date_fetched' column to DataFrame."""
    timestamp = f"{pd.Timestamp('today'):%Y-%m-%d %I-%M %p}"
    df['time_fetched'] = timestamp
    return df


def add_stats_column(df):
    """Add 'pct_of_total_adds' column to DataFrame."""
    adds_pct_tot = round(df['adds'] / df['total'].sum(), 3) * 100
    df.insert(4, 'pct_of_total_adds', adds_pct_tot)
    return df


def create_sql_engine():
    """Connects to 'fantasy' database in MySQL."""
    usr = credentials.mysql_usr
    pwd = credentials.mysql_pwd
    con = f'mysql+pymysql://{usr}:{pwd}@localhost:3306/fantasy'
    engine = create_engine(con)
    return engine


def create_df_from_last_dump(engine):
    """Constructs a DataFrame from the last data dump."""
    df = pd.read_sql(con=engine, sql="""
        SELECT *
        FROM fantasy
        WHERE time_fetched = (
            SELECT MAX(time_fetched)
            FROM fantasy
            )
        """
                     )
    return df


def compare_dfs(current_df, last_df):
    """Compares current & last DataFrames to prevent duplication.
    Returns bool"""
    current_df = current_df.reset_index(drop=True)
    # compare 'adds' column
    return current_df['adds'].equals(last_df['adds'])


def dump_to_mysql(current_df, last_df, engine):
    """Adds rows (appends if data exists) to 'fantasy' table in MySQL."""
    # add data only if it hasn't been added already
    if not compare_dfs(current_df, last_df):
        current_df.to_sql(name='fantasy', con=engine, if_exists='append',
                          index_label='buzz_index', dtype={'pct_of_total_adds': Float()})


def main():
    """Run script."""
    print("Fetching trends data from Yahoo")
    tic = perf_counter()
    try:
        current_df = create_df()
        add_team_position_column(current_df)
        clean_player_column(current_df)
        add_date_fetched(current_df)
        add_stats_column(current_df)
        engine = create_sql_engine()
        last_df = create_df_from_last_dump(engine)
        compare_dfs(current_df, last_df)
        dump_to_mysql(current_df, last_df, engine)
    except:
        traceback.print_exc()
    toc = perf_counter()
    duration = (toc - tic)
    print(f"Finished in {duration:0.3f} seconds")


if __name__ == '__main__':
    main()
