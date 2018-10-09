#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Fact check images according to their sources.

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
parser.add_argument('sleep_min', type=float,
                    help='Minimum number of seconds to sleep between \
                    requests.')
parser.add_argument('sleep_max', type=float,
                    help='Maximum number of seconds to sleep between \
                    requests.')

args = parser.parse_args()

CHECK_FOLDER = os.path.join(args.json_folder, 'fact_checks')


def init():
    '''
        Initialize script.
    '''

    if not os.path.exists(CHECK_FOLDER):
        os.makedirs(CHECK_FOLDER)


def check():
    '''
        Fact check images.
    '''

    # Get input files.
    json_filenames = []
    for json_f in os.listdir(args.json_folder):
        if os.path.isfile(os.path.join(args.json_folder, json_f)):
            if json_f.endswith('.json'):
                json_filenames.append(json_f)

    # Fact check.
    for json_f in sorted(json_filenames):
        print('[+] File {}'.format(json_f))
        json_f_path = os.path.join(args.json_folder, json_f)

        json_file = open(json_f_path, 'r')
        imgs_data = json.load(json_file)
        json_file.close()

        for img_id in imgs_data:
            img_name = imgs_data[img_id]['imageID']
            print('\t[+] Image {}'.format(img_name))

            if imgs_data[img_id].get('fact_checked'):
                sources = imgs_data[img_id]['sources']
                imgs_data[img_id]['fact_check'] = gc.get_fact_check(
                    sources, args.sleep_min, args.sleep_max)

        output_file = open(os.path.join(CHECK_FOLDER, json_f), 'w')

        json.dump({int(x): imgs_data[x] for x in imgs_data.keys(
        )}, output_file, indent=4, sort_keys=True)

        output_file.close()


def main():
    '''
        Main function.
    '''

    init()
    check()


main()
