from time import perf_counter

import pandas as pd
import yagmail
from gazpacho import Soup
from gazpacho import get
from sqlalchemy.types import Float

import credentials
import sql_engine

ENGINE = sql_engine.engine


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


def add_pct_column(df):
    """Adds 'pct_of_total_adds' column to DataFrame."""
    adds_pct_tot = round(df['adds'] / df['total'].sum(), 3) * 100
    df.insert(4, 'pct_of_total_adds', adds_pct_tot)
    return df


def add_timestamp_column(df):
    """Add 'time_fetched' column to DataFrame."""
    timestamp = pd.Timestamp('today')
    df['time_fetched'] = timestamp
    return df


def has_table(table):
    """Return True if the given backend has a table of the given name."""
    return ENGINE.has_table(table)


def create_df_from_last_dump():
    """Constructs a DataFrame from the last data dump."""
    get_last_dump = """
        SELECT *
        FROM yahoo_buzz
        WHERE time_fetched = (
            SELECT MAX(time_fetched)
            FROM yahoo_buzz
            );
        """
    last_df = pd.read_sql(con=ENGINE, sql=get_last_dump)
    return last_df


def compare_dfs(current_df, last_df):
    """Returns True if 'current_df' is identical to 'last_df'."""
    current_df = current_df.reset_index(drop=True)
    # compare 'adds' column
    return current_df['adds'].equals(last_df['adds'])


def dump_current_df_to_mysql(current_df):
    """Adds rows (appends if data exists) to a table in MySQL."""
    current_df.to_sql(name='yahoo_buzz', con=ENGINE,
                      if_exists='append', index_label='buzz_index',
                      dtype={'pct_of_total_adds': Float()})


def create_todays_buzz_df():
    """Returns DataFrame with today's buzz.
    Buzz is defined as a player in the top 10 daily adds
    that has reached >= 25 adds per minute.
    """
    buzz_sql = """
        SELECT *
        FROM yahoo_buzz_today
        WHERE player NOT IN (
            SELECT player
            FROM yahoo_buzz_email_sent
            WHERE DATE(time_fetched) = CURDATE()
            );
    """
    buzz_df = pd.read_sql(buzz_sql, con=ENGINE)
    return buzz_df


def send_email(buzz_df):
    """Sends an email with the latest trending player(s)."""
    recipient = credentials.recipient
    sender = credentials.sender
    subject = 'Yahoo Buzz Alert'
    body = buzz_df.to_dict(orient='index')
    yag = yagmail.SMTP(sender, oauth2_file="./oauth2_creds.json")
    yag.send(
        to=recipient,
        subject=subject,
        contents=body
    )


def dump_buzz_player_to_mysql(buzz_df):
    """Adds rows to MySQL for emails sent."""
    buzz_df = add_timestamp_column(buzz_df)
    buzz_df.to_sql(name='yahoo_buzz_email_sent', con=ENGINE, if_exists='append')


def main():
    """Run script."""
    tic = perf_counter()

    # fetch buzz data, create DataFrame, and clean it
    current_df = create_df()
    add_team_position_column(current_df)
    clean_player_column(current_df)
    add_pct_column(current_df)
    add_timestamp_column(current_df)

    # dump DataFrame to MySQL
    if has_table('yahoo_buzz'):
        # add data only if it hasn't been added already
        last_df = create_df_from_last_dump()
        if not compare_dfs(current_df, last_df):
            dump_current_df_to_mysql(current_df)
    else:
        # create table and dump if 'yahoo_buzz' doesn't exist
        dump_current_df_to_mysql(current_df)

    # send an email if a player is buzzing
    buzz_df = create_todays_buzz_df()
    if not buzz_df.empty:
        send_email(buzz_df)
        dump_buzz_player_to_mysql(buzz_df)

    toc = perf_counter()
    duration = (toc - tic)
    print(f"{pd.Timestamp('today'):%Y-%m-%d %I-%M %p} \
        Finished in {duration:0.3f} seconds ")


if __name__ == '__main__':
    main()
