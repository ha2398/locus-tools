#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Collect sources where images have previously appeared on, for a set of JSON
files describing a set of images.

@author: Hugo Sousa (hugosousa@dcc.ufmg.br)
'''


from argparse import ArgumentParser
from bs4 import BeautifulSoup
from contextlib import closing
from time import sleep
from random import uniform

import json
import os
import urllib.request
import sys


# Add command line arguments.
parser = ArgumentParser()

parser.add_argument('json_folder', type=str,
                    help='Path of the folder that contains the JSON files.')
parser.add_argument('n_images', type=int,
                    help='Number of images to create links for')
parser.add_argument('sleep_min', type=float,
                    help='Minimum number of seconds to sleep between \
                    requests.')
parser.add_argument('sleep_max', type=float,
                    help='Maximum number of seconds to sleep between \
                    requests.')

args = parser.parse_args()

SOURCES_FOLDER = os.path.join(args.json_folder, 'sources')

URL = 'http://images.google.com.br/searchbyimage?image_url=' + \
      'http://www.monitor-de-whatsapp.dcc.ufmg.br/data/images/{}'

DOMAIN = 'www.google.com.br'

USER_AGENT = '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'''

PROXY_IP = '149.28.118.14'
PROXY_PORT = '8080'

PROXIES = {
    'http': 'http://{}:{}'.format(PROXY_IP, PROXY_PORT),
    'https': 'https://{}:{}'.format(PROXY_IP, PROXY_PORT)
}


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
    # handler = urllib.request.ProxyHandler(PROXIES)
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    try:
        with closing(opener.open(url)) as open_url:
            html = open_url.read().decode()
    except urllib.error.HTTPError as http_error:
        print(http_error, '\tURL:', url)
        exit()

    # html = opener.open(url).read().decode()
    slow_down()
    return html


def get_page_sources(html):
    '''
        Get image sources on a particular page.

        @html: (string) Page HTML content.

        @return: (string list) List of sources of the image on the page.
    '''

    soup = BeautifulSoup(html, 'html.parser')
    return [link.a.get('href') for link in soup.find_all('h3', {'class': 'r'})]


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
        print('\t\t[+] Search result page {}'.format(page))
        page += 1

        sources += get_page_sources(html)
        html = get_next_page(html)

        if html is None:
            break

    return sources


def generate_links(imgs_data):
    '''
        Generate Google Search by Image links.

        @imgs_data: (dict) JSON dict with images data.

        @return: (string list) List with the Google Search by Image links.
    '''

    links = {}
    for img_n in range(1, args.n_images + 1):
        if str(img_n) in imgs_data:
            links[str(img_n)] = URL.format(imgs_data[str(img_n)]['imageID'])
        else:
            break

    return links


def init():
    '''
        Initialize script.
    '''

    if not os.path.exists(SOURCES_FOLDER):
        os.makedirs(SOURCES_FOLDER)


def collect_sources():
    '''
        Collect sources where images have previously appeared on.
    '''

    # Get input files.
    json_filenames = []
    for json_f in os.listdir(args.json_folder):
        if os.path.isfile(os.path.join(args.json_folder, json_f)):
            if json_f.endswith('.json'):
                json_filenames.append(json_f)

    # Generate sources.
    for json_f in sorted(json_filenames):
        print('[+] File {}'.format(json_f))
        json_f_path = os.path.join(args.json_folder, json_f)

        json_file = open(json_f_path, 'r')
        imgs_data = json.load(json_file)
        json_file.close()

        links = generate_links(imgs_data)
        output = {}

        for img_id in links:
            img_name = imgs_data[img_id]['imageID']
            print('\t[+] Image {}'.format(img_name))
            sources = get_sources(links[img_id])
            output[img_id] = {}
            output[img_id]['sources'] = sources
            output[img_id]['imageID'] = img_name

        output_name = json_f.replace('data', 'sources')
        output_file = open(os.path.join(SOURCES_FOLDER, output_name), 'w')

        json.dump(output, output_file)
        output_file.close()


def main():
    '''
        Main function.
    '''

    init()
    collect_sources()


main()
