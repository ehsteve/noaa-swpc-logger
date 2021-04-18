# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import urllib.request
import datetime
import os

DATEFORMAT = '%Y-%m-%d %H:%M:%S'


def download_and_read_file(url):
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    return text


def parse_wwv(text):
    """Parse the Geophysical Alert Message file. Released daily."""
    lines = os.linesep.join([s for s in text.splitlines() if s]).split('\n')
    date = datetime.datetime.strptime(lines[1][9:], "%Y %b %d %H%M UTC")
    messages = lines[7:]
    return date, messages

def parse_advisory_outlook(text):
    lines = os.linesep.join([s for s in text.splitlines() if s]).split('\n')
    date = datetime.datetime.strptime(lines[1][9:], "%Y %b %d %H%M UTC")
    messages = lines[11:]
    return date, messages

def parse_solar_regions(text):
    lines = os.linesep.join([s for s in text.splitlines() if s]).split('\n')
    date = datetime.datetime.strptime(lines[1][9:], "%Y %b %d %H%M UTC")
    date_obs = datetime.datetime.strptime(lines[8][23:], "%Y %b %d")

    # header = lines[11][1:].split()
    messages = []
    messages.append("Date       " + lines[11][1:])
    for l in lines[12:]:
        this_message = f'{date_obs:%Y-%m-%d} {l}'
        messages.append(this_message)

    return date, messages

def parse_weekly(text):
    """Parse the Weekly Highlights and Forecasts"""
    lines = os.linesep.join([s for s in text.splitlines() if s]).split('\n')


with open('noaa-swpc.log', 'w') as f:

    txt = download_and_read_file('https://services.swpc.noaa.gov/text/wwv.txt')
    date, messages = parse_wwv(txt)

    for msg in messages:
        f.write(f"{date:%Y-%m-%d %H:%M:%S} noaa-swpc (Geophysical Alert Message): {msg}\n")

    #txt = download_and_read_file('https://services.swpc.noaa.gov/text/weekly.txt')
    #week, date, messages = parse_weekly(txt)

    #for msg in messages:
    #    f.write(f"{date:%Y-%m-%d %H:%M:%S} noaa-swpc (Weekly Highlights and Forecasts) [{week}]: {msg}\n")


    txt = download_and_read_file('https://services.swpc.noaa.gov/text/solar-regions.txt')
    date, messages = parse_solar_regions(txt)

    for msg in messages:
        f.write(f"{date:%Y-%m-%d %H:%M:%S} noaa-swpc (Summary of Space Weather Observations): {msg}\n")

    txt = download_and_read_file('https://services.swpc.noaa.gov/text/advisory-outlook.txt')
    date, messages = parse_advisory_outlook(txt)

    for msg in messages:
        f.write(f"{date:%Y-%m-%d %H:%M:%S} noaa-swpc (Advisory Outlook): {msg}\n")

