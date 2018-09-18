#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Collect sources where images have previously appeared on, for a CSV file
describing a set of images.

@author: Hugo Sousa (hugosousa@dcc.ufmg.br)
'''


from argparse import ArgumentParser
from bs4 import BeautifulSoup
from contextlib import closing
from datetime import date, timedelta
from json import dump
from time import sleep
from random import uniform

import urllib.request


# Add command line arguments.
parser = ArgumentParser()

parser.add_argument('csv_filename', type=str,
                    help='Path of the CSV file with the image data.')
parser.add_argument('n_pages', type=int, default=10,
                    help='Number of search result pages to collect \
                    for each image.')
parser.add_argument('sleep_min', type=float, default=31,
                    help='Minimum number of seconds to sleep between \
                    requests.')
parser.add_argument('sleep_max', type=float, default=35,
                    help='Maximum number of seconds to sleep between \
                    requests.')

args = parser.parse_args()

URL = 'http://images.google.com.br/searchbyimage?image_url=' + \
      'http://www.monitor-de-whatsapp.dcc.ufmg.br/data/images/{}'

DOMAIN = 'www.google.com.br'

USER_AGENT = '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'''

MONTHS = {y: (x + 1) for (x, y) in enumerate(['jan', 'fev', 'mar',
                                              'abr', 'mai', 'jun',
                                              'jul', 'ago', 'set',
                                              'out', 'nov', 'dez'])}


def process_url(url):
    '''
        Process URL assuring it has the proper format.

        @url: (string) URL.

        @return: (string) Processed URL.
    '''

    if url.find('http') < 0:
        url = 'https://' + url

    return url


def get_html(url):
    '''
        Get the HTML string corresponding to a particular URL.

        @url: (string) URL.

        @return: (string) HTML string.
    '''

    url = process_url(url)
    headers = [('User-Agent', USER_AGENT)]
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        with closing(opener.open(url)) as open_url:
            html = open_url.read().decode()
    except urllib.error.HTTPError as http_error:
        print(http_error, '\tURL:', url)
        exit()

    slow_down()
    return html


def parse_date(raw_date):
    '''
        Parse a raw date string and return a formatted date string.

        @raw_date: (string) Raw date string.

        @return: (string) Formatted date string.
    '''

    pieces = raw_date.split()

    if len(pieces) == 5:  # x de x de x
        year = int(pieces[4])
        month = MONTHS[pieces[2]]
        day = int(pieces[0])

        return date(year, month, day).isoformat()
    elif len(pieces) == 3:  # x x atrás
        offset = int(pieces[0])
        return (date.today() - timedelta(days=offset)).isoformat()
    else:  # unknown
        return ''


def get_page_sources(html):
    '''
        Get image sources on a particular page.

        @html: (string) Page HTML content.

        @return: (string list) List of sources of the image on the page.
    '''

    soup = BeautifulSoup(html, 'html.parser')

    links = [link.a.get('href')
             for link in soup.find_all('h3', {'class': 'r'})]
    dates = [parse_date(date.span.string.split(' - ')[1])
             if date.span is not None else ''
             for date in soup.find_all('span', {'class': 'st'})]

    return list(zip(links, dates))


def get_next_page(html):
    '''
        Get the HTML content for the next search result page.

        @html: (string) HTML content of current page.

        @return: (string) HTML content of next page.
    '''

    soup = BeautifulSoup(html, 'html.parser')
    next_page = soup.find_all('a', {'class': 'pn', 'id': 'pnnext'})

    if len(next_page) == 0:
        return None

    next_page_link = DOMAIN + next_page[0].get('href')
    return get_html(next_page_link)


def slow_down():
    '''
        Sleeps for awhile after each request, so the crawler looks slightly
        more human.
    '''

    sleep(uniform(args.sleep_min, args.sleep_max))


def get_sources(url):
    '''
        Get all source links where the image has appeared on.

        @url: (string) HTML of the first result page for the image.

        @return: (string list) List of all the source links where the image has
        appeared on.
    '''

    html = get_html(url)
    sources = []

    # Only look for links where the image has appeared on.
    html = html[html.find('Páginas que incluem imagens correspondentes'):]

    page = 1
    while True:  # Look for other sources in the rest of the result pages.
        print('\t[+] Search result page {}'.format(page))
        page += 1

        if page > args.n_pages:
            break

        sources += get_page_sources(html)
        html = get_next_page(html)

        if html is None:
            break

    return sources


def generate_links(ids):
    '''
        Generate Google Search by Image links.

        @ids: (list) List with image IDs.

        @return: (dict) Dict with the Google Search by Image links.
    '''

    links = {}

    for i in ids:
        links[i] = URL.format(i)

    return links


def collect_sources():
    '''
        Collect sources where images have previously appeared on.
    '''

    with open(args.csv_filename, 'r') as f:
        ids = [row.split(',')[0] for row in f]

    links = generate_links(ids)
    imgs_sources = {}

    # Collect sources
    for img_id in links:
        print('[+] Image {}'.format(img_id))
        sources = get_sources(links[img_id])
        imgs_sources[img_id] = sources

    csv_name = args.csv_filename.split('/')[-1]
    output_filename = csv_name[:csv_name.find('.')] + '_sources.json'
    output_file = open(output_filename, 'w')
    dump(imgs_sources, output_file, indent=4)
    output_file.close()


def main():
    '''
        Main function.
    '''

    collect_sources()


main()
