import os
from pathlib import PurePath
# pip install hickory

script = PurePath('.').joinpath('fetch_yahoo.py')


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


def schedule_script():
    """Schedules 'fetch_yahoo' script using Hickory."""
    times = get_fetch_times()
    os.system(f"hickory schedule {script} --every={times}")


def kill_script():
    """Kills 'fetch_yahoo' script using Hickory."""
    os.system(f"hickory kill {script}")


if __name__ == '__main__':
    schedule_script()
