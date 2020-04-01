#!/usr/bin/python3

'''
webcrawler.py - searches for all webpages on a site and creates their list
INPUT: URL of the homepage
OUTPUT: list of URLs
'''

import logging
import requests, time, re
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
    urls = [x.get('href') for x in hrefs] # get only URLs

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
            if isUpceWebsite(url):
                if containsDomain(url) != True:
                    logging.info("Domain added to: {}".format(url))
                    url = addDomain(url, 'https://www.upce.cz')

                if url not in ret_urls: # check for duplicates
                    ret_urls.append(url)

    return ret_urls


def containsDomain(url):
    '''
    checks whether url is whole or just a subdirectory
    '''
    if url[:4] == 'http':
        return True


def addDomain(subdirectory, domain): # adds domain to subdirectory to create full url
    '''
    adds given domain to url without any
    '''
    url = domain + subdirectory
    return url


def isUpceWebsite(url):
    'returns True for upce.cz webpages'
    ret_val = True if 'en' in url[:3] or 'upce.cz' in url else False
    if not ret_val:
        logging.info("Url not in Upce domain: {}".format(url))
    return ret_val


if __name__ == '__main__':
    remove_patterns = [
        re.compile("^mailto:"),
        re.compile("^https://(www.)?youtube.com"),
        re.compile("^https://(www.)?linkedin.com"),
        re.compile("^https://(www.)?instagram.com"),
    ]

    visited = dict()
    toVisit = list()

    toVisit = crawl('https://www.upce.cz/en')
    toVisit = filter_urls(toVisit, remove_patterns)
    
    for url in toVisit:
        if url not in visited.keys():
            print('Checking: {}'.format(url))
            visited.setdefault(url, {'statusCode': requests.get(url).status_code})
            print(visited[url]['statusCode'])
            time.sleep(2)
    ...