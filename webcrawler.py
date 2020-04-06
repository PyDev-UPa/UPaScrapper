#!/usr/bin/python3

'''
webcrawler.py - searches for all webpages on a site and creates their list
INPUT: URL of the homepage
OUTPUT: list of URLs
'''

import logging
import requests, time, re, json
import pyperclip # for testing only
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


def crawl(url):
    '''
    finds all links on a page and inputs them in a list
    INPUT: url
    OUTPUT: list of links
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features='html.parser')
    hrefs = soup.find_all('a', href=True)
    urls = [x.get('href') for x in hrefs if x.get('href') != ''] # get only URLs
    patterns = read_pattern('webcrawler_remove.txt')
    to_remove = list()
    for url in urls:
        print(url)
        for p in patterns:
            if p.search(url):
                logging.info('Removing: {}'.format(url))
                to_remove.append(url)
    for url in to_remove:
            urls.remove(url)
    return urls


def filter_urls(urls, remove_patterns = []):
    '''
    filters urls in two groups (to be checked, to be crawled and checked)
    '''
    to_check = []
    to_crawl = []
    for url in urls:
        for p in remove_patterns: # remove unwanted links
            if p.search(url):
                url = normalize_url(url)
                logging.info("Url only to be checked: {}".format(url))
                if url not in to_check:
                    to_check.append(url)
                break
        else:
            url = normalize_url(url)
            if url not in to_crawl: # check for duplicates
                logging.info('Url to be checked and crawled: {}'.format(url))
                to_crawl.append(url)

    return to_check, to_crawl

def normalize_url(url, base_domain="https://www.upce.cz/"):
    patterns = [
        (re.compile("^/"), base_domain),
        (re.compile("/$"), ""),
        (re.compile('^node'), '{}en/node'.format(base_domain))
    ]
    ret_url = url
    for p in patterns:
        ret_url = p[0].sub(p[1], ret_url)

    if ret_url != url:
        logging.info("URL: {} normalized to {}".format(url, ret_url))
    return ret_url


def read_pattern(file):
    ret = []
    with open(file) as f:
        for l in f.readlines():
            ret.append(re.compile(l.strip()))
    return ret


if __name__ == '__main__':
    patterns = read_pattern('webcrawler_check.txt')

    visited = dict()
    toCrawl = list()

    toCrawl = crawl('https://www.upce.cz/en')
    toCheck, toCrawl = filter_urls(toCrawl, patterns)

    for url in toCrawl:
        if url not in visited.keys():
            print('Checking: {}'.format(url))
            visited.setdefault(url, {'statusCode': requests.get(url).status_code})
            visited[url].setdefault('mother', 'https://www.upce.cz/en')
            print(visited[url]['statusCode'])
            time.sleep(2)
    with open('data.json', 'w') as db:
        json.dump(visited, db)
