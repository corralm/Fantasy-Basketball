import os
from pathlib import PurePath
# pip install hickory

yahoo = PurePath('.').joinpath('fetch_yahoo.py')
espn = PurePath('.').joinpath('fetch_free_agents.py')
scripts = [yahoo, espn]


def get_fetch_times():
    """Returns string of fetch times for Hickory scheduling."""
    # from 5:00am to 11:55pm
    hours = range(5, 24)
    minutes = range(0, 60, 5)
    times = '@'
    for h in hours:
        for m in minutes:
            if m < 10:
                m = '0' + str(m)
            times += f'{h}:{m},'

    # remove last comma
    return times.rstrip(',')


def schedule_fetch_yahoo():
    """Schedules 'fetch_yahoo' script using Hickory."""
    times = get_fetch_times()
    os.system(f"hickory schedule {yahoo} --every={times}")


def schedule_fetch_free_agents():
    """Schedules 'fetch_free_agents' script using Hickory."""
    times = '@7am,5pm'
    os.system(f"hickory schedule {espn} --every={times}")


def kill_scripts():
    """Kills 'fetch_yahoo' script using Hickory."""
    for s in scripts:
        os.system(f"hickory kill {s}")


if __name__ == '__main__':
    schedule_fetch_yahoo()
    schedule_fetch_free_agents()
