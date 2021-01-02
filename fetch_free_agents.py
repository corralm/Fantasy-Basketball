import os
import traceback
from time import perf_counter
from time import sleep

import pandas as pd
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from yagmail import SMTP

import credentials

# create project directories
os.makedirs('data', exist_ok=True)
os.makedirs('screenshots', exist_ok=True)

# define CSV path
cwd = os.getcwd()
csv_path = ''.join((cwd, '/data/espn_free_agents.csv'))


def create_driver():
    """Creates headless Firefox WebDriver instance."""
    options = Options()
    options.headless = True
    return Firefox(executable_path='/usr/local/bin/geckodriver', options=options)


driver = create_driver()


def take_screenshot():
    """Saves a screenshot of the current window in the 'screenshots' directory."""
    timestamp = f"{pd.Timestamp('today'):%Y-%m-%d %I-%M %p}"
    path = ''.join((
        './screenshots/', 'screenshot ', timestamp, '.png')
    )
    driver.save_screenshot(path)


def load_url():
    """Navigates to Free Agents page."""
    base_url = 'https://fantasy.espn.com/basketball/'
    free_agents = 'players/add?leagueId=1079777210'
    url = base_url + free_agents
    driver.get(url)
    sleep(5)


def espn_login():
    """Logs into ESPN Fantasy Basketball."""
    actions = ActionChains(driver)
    # move to input box and enter username
    actions.move_by_offset(500, 225)
    actions.send_keys(credentials.espn_usr)
    # move to next input box and enter password
    actions.move_by_offset(0, 50)  # 500, 275
    actions.send_keys(Keys.TAB + credentials.espn_pwd)
    # move to "Log In" button and enter
    actions.send_keys(Keys.TAB + Keys.ENTER)
    actions.perform()
    sleep(3)


def create_dataframe():
    """Returns pandas DataFrame from Free Agents HTML."""
    html = driver.page_source
    # data is split into two tables and must be concatenated
    df1 = pd.read_html(html)[0]
    df2 = pd.read_html(html)[1]
    return pd.concat([df1, df2], axis=1)


def clean_dataframe(df):
    """Returns clean DataFrame."""
    df.columns = df.columns.droplevel(0)
    df.drop(columns=['action', 'opp', 'STATUS'], inplace=True)
    df.rename(columns={'type': 'Type', '%ROST': '%rost'}, inplace=True)
    return df


def add_player_abbr(df):
    """Adds player abbreviated name column."""
    abbreviated_names = []
    for p in df['Player']:
        first = p.split(' ')[0]
        last_init = p.split(' ')[1][0]
        abbreviated_names.append((' '.join((first, last_init))) + '.')
    df.insert(1, 'name', abbreviated_names)
    return df


def add_timestamp_column(df):
    """Add 'time_fetched' column to DataFrame."""
    timestamp = pd.Timestamp('today')
    df['time_fetched'] = timestamp
    return df


def highly_rostered_players(df):
    """Returns DataFrame with highly rostered free agents."""
    pct_rost = 30
    return df.loc[df['%rost'] >= pct_rost, ['name', '%rost', 'time_fetched']]


def players_to_send(rost_df, sent_df):
    """Returns True if there are players to email."""
    today = pd.Timestamp('today')
    wk_ago = pd.Timedelta(days=7)
    # 1. player hasn't been sent
    # 2. player was sent but more than 7 days ago
    to_send = rost_df.loc[~(rost_df['name'].isin(sent_df['name'])) |
                          (rost_df['name'].isin(sent_df['name'])) &
                          (sent_df['time_fetched'] <= (today - wk_ago))]
    return not to_send.empty


def send_email(rost_df):
    """Sends an email with the latest highly-rostered free agent."""
    recipient = credentials.recipient
    sender = credentials.sender
    subject = 'ESPN Free Agent Alert'
    body = rost_df.to_dict(orient='index')
    yag = SMTP(sender, oauth2_file="./oauth2_creds.json")
    yag.send(
        to=recipient,
        subject=subject,
        contents=body
    )


def to_csv(df):
    """Writes a CSV file in the 'data' directory."""
    df.to_csv(csv_path, index=False)


def main():
    """Run script."""
    tic = perf_counter()
    try:
        load_url()
        espn_login()
        df = create_dataframe()
        clean_df = clean_dataframe(df)
        clean_df = add_player_abbr(clean_df)
        clean_df = add_timestamp_column(clean_df)
        rost_df = highly_rostered_players(clean_df)
        # if a CSV with sent players doesn't exists
        if os.path.isfile(csv_path):
            sent_df = pd.read_csv(csv_path, parse_dates=['time_fetched'])
            # check if the players have been sent in the past 7 days
            if players_to_send(rost_df, sent_df):
                send_email(rost_df)
                to_csv(rost_df)
        else:
            # send an email if a CSV doesn't exists
            send_email(rost_df)
            to_csv(rost_df)
    except:
        traceback.print_exc()
        take_screenshot()
    finally:
        driver.quit()
        toc = perf_counter()
        duration = (toc - tic) / 60
        print(f"{pd.Timestamp('today'):%Y-%m-%d %I-%M %p} \
        Finished in {duration:0.3f} seconds ")


if __name__ == '__main__':
    main()
