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
from datetime import datetime

logging.basicConfig(level=logging.INFO)
#logging.disable(logging.INFO)

def crawl(resPage):
    '''
    finds all links on a page and inputs them in a list
    INPUT: requests object (crawled page)
    OUTPUT: list of links, url of crawled page
    '''
    parent = resPage.url
    page = resPage
    soup = BeautifulSoup(page.text, features='html.parser')
    hrefs = soup.find_all('a', href=True)
    urls = [x.get('href') for x in hrefs if x.get('href')] # get only URLs
    patterns = read_pattern('webcrawler_remove.txt')
    to_remove = list()
    for url in urls:
        for p in patterns:
            if p.search(url):
                logging.info('Removing: {}'.format(url))
                to_remove.append(url)
    for url in to_remove:
            urls.remove(url)
    return urls, parent


def filter_urls(urls, filter_patterns = []):
    '''
    filters urls in two groups (to be checked, to be crawled and checked)
    '''
    to_check = []
    to_crawl = []
    for url in urls:
        for p in filter_patterns: # remove unwanted links
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
    '''
    adds domain to link if it is only a subdirectory and not whole url
    Input: string (whole url or a subdirectory), string (domain)
    Output: whole url (domain + subdirectory)
    '''
    patterns = [
        (re.compile("^/"), base_domain),
        (re.compile("/$"), ""),
        (re.compile('^node'), '{}en/node'.format(base_domain)),
        (re.compile('^en'), base_domain)
    ]
    ret_url = url
    for p in patterns:
        ret_url = p[0].sub(p[1], ret_url)

    if ret_url != url:
        logging.info("URL: {} normalized to {}".format(url, ret_url))
    return ret_url


def read_pattern(file):
    '''
    loads patterns from a text file as regexes
    Input: text file
    Output: list of regexes
    '''
    ret = []
    with open(file) as f:
        for l in f:
            ret.append(re.compile(l.strip()))
    return ret

def check_url(resPage, parent):
    '''
    checks statusCode of url and returns a dictionary of status code,
    parent webpage and timestamp of the check
    Input: url, parentpage
    Output: dictionary in dictionary with status code and parent of the urls
    e.g. {'checked url': {'status code': '404', 'parent': 'http://www.where.from.leads.link.to.this.url'}}
    '''

    logging.info('Checking: {}'.format(url))
    ret = {
            url: {'status_code': requests.get(url).status_code,
                'parent': parent,
                'time': datetime.now().strftime('%A %b %d, %Y - %H:%M:%S')}
            }

    return ret


if __name__ == '__main__':
    patterns = read_pattern('webcrawler_check.txt')

    result = dict()
    crawlBank = ['http://www.upce.cz/en']
    crawlBankSizeBefore = len(crawlBank)
    crawlBankSizeAfter = 2

    while crawlBankSizeAfter > crawlBankSizeBefore:
        crawlBankSizeBefore = crawlBankSizeAfter
        tempBank = [x for x in result.keys()]
        for bankUrl in crawlBank:
            if bankUrl not in tempBank:
                resPage = requests.get(bankUrl)
                newLinks, parent = crawl(resPage)
                toCheck, toCrawl = filter_urls(newLinks, patterns)

                for url in toCheck:
                    temp = [x for x in result.keys()]
                    if url not in temp:
                        temp.append(url)
                        result.update(check_url(url, parent))
                        time.sleep(1)

                for url in toCrawl:
                    temp = [x for x in result.keys()]
                    if url not in temp:
                        temp.append(url)
                        result.update(check_url(url, parent))
                        time.sleep(1)
                        logging.info('Adding to crawlBank: {}'.format(url))
                        crawlBank.append(url)
        crawlBankSizeAfter = len(crawlBank)

    with open('data.json', 'w') as db:
        json.dump(result, db)
