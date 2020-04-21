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

logging.basicConfig(filename='webcrawler-{}.log'.format(datetime.now().strftime('%b-%d-%H:%M')), level=logging.INFO)
#logging.disable(logging.INFO)

def crawl(resPage):
    '''
    finds all links on a page and inputs them in a list
    INPUT: url
    OUTPUT: list of links, url of crawled page
    '''
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
    urls = [normalize_url(x) for x in urls]
    return urls


def filter_urls(urls, filter_patterns = []):
    '''
    filters urls in two groups (to be checked, to be crawled and checked)
    '''
    to_check = []
    to_crawl = []
    for url in urls:
        for p in filter_patterns: # pick urls to be further crawled 
            if p.search(url):
                if url not in to_crawl:
#                    logging.info(f"Url to be crawled: {url}")
                    to_crawl.append(url)
                break
        else:
            if url not in to_check:
#                logging.info('Url to be checked: {}'.format(url))
                to_check.append(url)

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
        pass
#        logging.info("URL: {} normalized to {}".format(url, ret_url))
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

def check_url(url, parent):
    '''
    checks statusCode of url and returns a dictionary of status code,
    parent webpage and timestamp of the check
    Input: url, parentpage
    Output: dictionary in dictionary with status code and parent of the urls
    e.g. {'checked url': {'status code': '404', 'parent': 'http://www.where.from.leads.link.to.this.url'}}
    '''

    logging.info('Checking: {}'.format(url))
    try:
        checkPage = requests.get(url, timeout=10)
        ret = {
            url: {'status_code': checkPage.status_code,
                'parent': parent,
                }}
    except OSError:
        ret = {
            url: {'error': 'requests fail',
                'parent': parent,
                }}
    except requests.exceptions.Timeout:
        ret = {
            url: {'error': 'requests timed out',
                'parent': parent,
                }}
    except UnicodeError:
        ret = {
            url: {'error': 'requests UnicodeError',
                'parent': parent,
                }}
        ret
    return ret


if __name__ == '__main__':
    patterns = read_pattern('webcrawler_crawl.txt')

    result = dict()
    crawlBank = ['https://www.upce.cz/en']
    crawled = []

    while len(crawlBank) > 0:
        logging.info(f'-------------------')
        logging.info(f'The size of the bank is: {len(crawlBank)}')
        logging.info(f'Next url to be crawled is: {crawlBank[0]}')
        logging.info(f'I have already crawled {len(crawled)} urls.')
        logging.info(f'the crawled pages are {crawled}.')
        logging.info(f'-------------------')
        bankUrl = crawlBank.pop(0)
        if bankUrl not in crawled:
            logging.info(f'Crawling: {bankUrl}')
            try:
                resPage = requests.get(bankUrl, timeout=10)
                newLinks = crawl(resPage)
                toCheck, toCrawl = filter_urls(newLinks, patterns)

                for url in toCheck:
                    checked = [x for x in result.keys()]
                    if url not in checked:
                        result.update(check_url(url, bankUrl))
                        time.sleep(1)

                addToCrawlBank = []
                for url in toCrawl:
                    if url not in crawled:
                        result.update(check_url(url, bankUrl))
                        time.sleep(1)
                        if url not in addToCrawlBank:
                            addToCrawlBank.append(url)

                for url in addToCrawlBank:
                    if url not in crawlBank or url not in crawled:
                        crawlBank.append(url)
                        logging.info('Adding to crawlBank: {}'.format(url))
            
            except requests.exceptions.Timeout:
                logging.info(f'{url} not reached in time')
            finally:
                crawled.append(bankUrl)

    with open('data.json', 'w') as db:
        json.dump(result, db)
