#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Given a JSON file describing images and a number of desired images to analyze,
this script generates Google Search by Image links for each image.

@author: Hugo Sousa (hugosousa@dcc.ufmg.br)
'''


import argparse
import json


URL = 'http://images.google.com/searchbyimage?image_url=' + \
      'http://www.monitor-de-whatsapp.dcc.ufmg.br/data/images/{}'


# Add command line arguments.
parser = argparse.ArgumentParser()

parser.add_argument('json_file', type=str, help='Name of input JSON file.')
parser.add_argument('n_images', type=int,
                    help='Number of images to create links for')

args = parser.parse_args()


def generate_links(imgs_data):
    '''
        Generate Google Search by Image links.

        @imgs_data: (dict) JSON dict with images data.

        @return: (string list) List with the Google Search by Image links.
    '''

    links = []
    for img_n in range(1, args.n_images + 1):
        if str(img_n) in imgs_data:
            links.append(URL.format(imgs_data[str(img_n)]['imageID']))
        else:
            break

    return links


def main():
    '''
        Main function.
    '''

    with open(args.json_file, 'r') as input_file:
        imgs_data = json.load(input_file)

    links = generate_links(imgs_data)

    for link in links:
        print(link)


main()
