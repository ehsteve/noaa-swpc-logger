import urllib.request
import datetime
import os
import tempfile
from pathlib import Path
from shutil import copyfile

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
OUTPUT_FILE = 'noaa-swpc.log'

file_dict = {'Geophysical Alert Message': 'https://services.swpc.noaa.gov/text/wwv.txt',
             'Summary of Space Weather Observations': 'https://services.swpc.noaa.gov/text/solar-regions.txt',
             'Advisory Outlook': 'https://services.swpc.noaa.gov/text/advisory-outlook.txt'}


def get_data(url):
    """Given a url, download the file and compare to a previously downloaded file.
    Returns None if the file is the same as the previous download."""

    fname = os.path.basename(url)
    new_file = tempfile.NamedTemporaryFile().name
    urllib.request.urlretrieve(url, new_file)

    past_file = Path(fname)
    if past_file.is_file():  # check if there is a past file to compare to
        if are_files_the_same(past_file, new_file):
            return None
        else:
            copyfile(new_file, past_file)
            with open(new_file, 'r') as fp:
                text = fp.read().splitlines()
                return text
    else:  # there is no past file so just return the contents
        copyfile(new_file, past_file)
        with open(new_file, 'r') as fp:
            text = fp.read().splitlines()
            return text


def are_files_the_same(filename1, filename2):
    """Compare two files, return True if the two files are the same and False
    if they are not."""

    text1 = open(filename1, 'r').read().splitlines()
    text2 = open(filename2, 'r').read().splitlines()
    print(text1)
    print(text2)
    diff = set(text1).difference(text2)
    print(diff)
    return len(diff) == 0


def parse_wwv(text):
    """Parse the Geophysical Alert Message file. Released daily."""
    lines = [line for line in text if len(line) > 2]
    date = datetime.datetime.strptime(lines[1][9:], "%Y %b %d %H%M UTC")
    messages = text[7:]
    return date, messages


def parse_advisory_outlook(text):
    """Parse the Advisory outlook Message file. Released daily"""
    lines = [line for line in text if len(line) > 2]
    date = datetime.datetime.strptime(lines[1][9:], "%Y %b %d %H%M UTC")
    messages = lines[11:]
    return date, messages


def parse_solar_regions(text):
    """Parse the solar regions file. Released daily"""
    date = datetime.datetime.strptime(text[1][9:], "%Y %b %d %H%M UTC")
    date_obs = datetime.datetime.strptime(text[8][23:], "%Y %b %d")

    # header = lines[11][1:].split()
    messages = []
    messages.append("Date       " + text[11][1:])
    for l in text[12:]:
        this_message = f'{date_obs:%Y-%m-%d} {l}'
        messages.append(this_message)

    return date, messages


def parse_weekly(text):
    """Parse the Weekly Highlights and Forecasts file. Released daily."""
    lines = os.linesep.join([s for s in text.splitlines() if s]).split('\n')


with open(OUTPUT_FILE, 'a') as f:

    for key, url in file_dict.items():
        print(key)
        txt = get_data(url)
        if txt is not None:
            if key == 'Geophysical Alert Message':
                date, messages = parse_wwv(txt)
            elif key == 'Summary of Space Weather Observations':
                date, messages = parse_solar_regions(txt)
            elif key == 'Advisory Outlook':
                date, messages = parse_advisory_outlook(txt)
            for msg in messages:
                if len(msg) > 1:  # get rid of lines that only have newline character
                    f.write(f"{date:%Y-%m-%d %H:%M:%S} noaa-swpc ({key}): {msg}\n")
