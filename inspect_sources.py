#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
Run analyses on collected image sources.

@author: Hugo Sousa (hugosousa@dcc.ufmg.br)
'''

from argparse import ArgumentParser
from tldextract import extract
from urlparse import urlparse

import json
import os


# Add command line arguments.
parser = ArgumentParser()

parser.add_argument('json_folder', type=str,
                    help='Path of the folder that contains the JSON files.')
parser.add_argument('--c', action='store_true',
                    help='Indicates if the JSON file was generated from a '
                    'CSV file with image data.')

args = parser.parse_args()


def get_files():
    json_filenames = []
    for json_f in os.listdir(args.json_folder):
        if os.path.isfile(os.path.join(args.json_folder, json_f)):
            if json_f.endswith('.json'):
                json_filenames.append(os.path.join(args.json_folder, json_f))

    return json_filenames


def main():
    json_filenames = get_files()
    source_freq = {}
    sites = {}

    for filename in json_filenames:
        json_file = open(filename, 'r')
        data = json.load(json_file)

        for img_id in data:
            if not args.c and 'sources' not in data[img_id]:
                continue

            source_data = data[img_id] if args.c else data[img_id]['sources']

            for source, date in source_data:
                domain = extract(source).domain
                netloc = str(urlparse(source).netloc)

                if domain not in sites:
                    sites[domain] = [netloc]
                elif netloc not in sites[domain]:
                    sites[domain].append(netloc)

                source_freq[domain] = source_freq.get(domain, 0) + 1

        json_file.close()

    source_freq_list = sorted(
        ((v, k) for k, v in source_freq.items()), reverse=True)

    print('FREQUENCY\tDOMAIN\tWEBSITES')
    for pair in source_freq_list:
        print('{}\t{}\t{}'.format(pair[0], pair[1], sites[pair[1]]))


main()
