#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Collect sources where images have previously appeared on, for a set of JSON
files describing a set of images.

@author: Hugo Sousa (hugosousa@dcc.ufmg.br)
'''


from argparse import ArgumentParser

import google_crawler as gc
import json
import os


# Add command line arguments.
parser = ArgumentParser()

parser.add_argument('json_folder', type=str,
                    help='Path of the folder that contains the JSON files.')
parser.add_argument('min_share', type=int,
                    help='Minimum share number of the images to collect '
                    'sources for.')
parser.add_argument('pages', type=int,
                    help='Number of search result pages to go through.')
parser.add_argument('sleep_min', type=float,
                    help='Minimum number of seconds to sleep between \
                    requests.')
parser.add_argument('sleep_max', type=float,
                    help='Maximum number of seconds to sleep between \
                    requests.')

args = parser.parse_args()

SOURCES_FOLDER = os.path.join(args.json_folder, 'sources')


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

        links = gc.generate_links(imgs_data)

        for img_id in links:
            img_name = imgs_data[img_id]['imageID']
            print('\t[+] Image {}'.format(img_name))

            if imgs_data[img_id]['shareNumber'] >= args.min_share:
                sources = gc.get_sources(
                    links[img_id], args.sleep_min, args.sleep_max, args.pages)
                imgs_data[img_id]['sources'] = sources

                fact_checked = gc.is_fact_checked(sources)
                imgs_data[img_id]['fact_checked'] = fact_checked

        output_name = json_f.replace('data', 'sources')
        output_file = open(os.path.join(SOURCES_FOLDER, output_name), 'w')

        json.dump({int(x): imgs_data[x] for x in imgs_data.keys(
        )}, output_file, indent=4, sort_keys=True)

        output_file.close()


def main():
    '''
        Main function.
    '''

    init()
    collect_sources()


main()
