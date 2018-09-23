#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Collect sources where yesterday's images have previously appeared on, based
on a JSON file that describes these images.

@author: Hugo Sousa (hugosousa@dcc.ufmg.br)
'''


from argparse import ArgumentParser
from datetime import datetime, timedelta
from json import dump, load

import google_crawler as gc


# Add command line arguments.
parser = ArgumentParser()

parser.add_argument('-p', type=int, default=10,
                    help='Max number of search result pages per image.')
parser.add_argument('-min', type=float, default=31,
                    help='Minimum number of seconds to sleep between \
                    requests.')
parser.add_argument('-max', type=float, default=35,
                    help='Maximum number of seconds to sleep between \
                    requests.')

args = parser.parse_args()

MONTHS = {x + 1: y for (x, y) in enumerate(['Jan', 'Fev', 'Mar',
                                            'Abr', 'Mai', 'Jun',
                                            'Jul', 'Ago', 'Set',
                                            'Out', 'Nov', 'Dez'])}
ROOT_FOLDER = '/scratch1/gustavojota/'
OUTPUT_FOLDER = '/scratch1/hugo/img_sources/'
LOG_NAME = 'collect_latest.log'


def get_today_filename():
    yesterday = datetime.today() - timedelta(days=1)
    month = MONTHS[yesterday.month]
    day = yesterday.day
    return 'images_data_{}{}_Final.json'.format(month, day)


def get_sources(url):
    '''
        Get all source links where the image has appeared on.

        @url: (string) HTML of the first result page for the image.

        @return: (string list) List of all the source links where the image has
        appeared on.
    '''

    html = gc.get_html(url, args.min, args.max)
    sources = []

    # Only look for links where the image has appeared on.
    html = html[html.find('Páginas que incluem imagens correspondentes'):]

    page = 1
    while True:  # Look for other sources in the rest of the result pages.
        print('\t[+] Search result page {}'.format(page))
        page += 1

        if page > args.p:
            break

        sources += gc.get_page_sources(html)
        html = gc.get_next_page(html, args.min, args.max)

        if html is None:
            break

    return sources


def main():
    today_filename = get_today_filename()
    input_filename = ROOT_FOLDER + today_filename

    with open(input_filename, 'r') as input_file:  # Input file
        imgs_data = load(input_file)
        links = gc.generate_links(imgs_data, 0)

        for img_id in links:
            img_name = imgs_data[img_id]['imageID']
            print('[+] Image{}'.format(img_name))

            if imgs_data[img_id]['shareNumber'] > 1:
                sources = get_sources(links[img_id])
                imgs_data[img_id]['sources'] = sources

    output_name = OUTPUT_FOLDER + today_filename

    with open(output_name, 'w') as output:
        dump({int(x): imgs_data[x] for x in imgs_data.keys()},
             output, indent=4, sort_keys=True)


main()
