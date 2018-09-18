#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
Run analyses on collected image sources.

@author: Hugo Sousa (hugosousa@dcc.ufmg.br)
'''

from argparse import ArgumentParser
from tldextract import extract

import json
import os


# Add command line arguments.
parser = ArgumentParser()

parser.add_argument('json_folder', type=str,
                    help='Path of the folder that contains the JSON files.')

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

    for filename in json_filenames:
        json_file = open(filename, 'r')
        data = json.load(json_file)

        for img_id in data:
            if 'sources' not in data[img_id]:
                continue

            for source, date in data[img_id]['sources']:
                domain = extract(source).domain
                source_freq[domain] = source_freq.get(domain, 0) + 1

        json_file.close()

    source_freq_list = sorted(
        ((v, k) for k, v in source_freq.items()), reverse=True)

    print('FREQUENCY\tDOMAIN')
    for pair in source_freq_list:
        print('{}\t{}'.format(pair[0], pair[1]))


main()
