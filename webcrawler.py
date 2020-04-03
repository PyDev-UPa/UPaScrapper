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
    return urls


def filter_urls(urls, remove_patterns = []):
    ret_urls = []
    for url in urls:
        for p in remove_patterns: # remove unwanted links
            if p.search(url):
                logging.info("Removing url: {}".format(url))
                urls.remove(url)
                break
        else:
            url = normalize_url(url)
            if url not in ret_urls: # check for duplicates
                ret_urls.append(url)

    return ret_urls


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


def read_remove_pattern(file = "webcrawler_remove.txt"):
    ret = []
    with open(file) as f:
        for l in f.readlines():
            ret.append(re.compile(l.strip()))
    return ret


if __name__ == '__main__':
    remove_patterns = read_remove_pattern()

    visited = dict()
    toVisit = list()

    toVisit = crawl('https://www.upce.cz/en')
    toVisit = filter_urls(toVisit, remove_patterns)

    for url in toVisit:
        if url not in visited.keys():
            print('Checking: {}'.format(url))
            visited.setdefault(url, {'statusCode': requests.get(url).status_code})
            visited[url].setdefault('mother', 'https://www.upce.cz/en')
            print(visited[url]['statusCode'])
            time.sleep(2)
    with open('data.json', 'w') as db:
        json.dump(visited, db)
